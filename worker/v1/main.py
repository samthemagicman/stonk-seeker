from functools import lru_cache

import praw
import spacy
import urllib3
from praw import models
import database
import json
from util import reddit
import concurrent.futures

nlp = spacy.load("en_core_web_sm")

def get_mentioned_stocks(comment: str):
    doc = nlp(comment)
    stocks = []
    for ent in doc.ents:
        if ent.label_ == "ORG":
            stock = ent.text.lower()
            stocks.append(stock)
    return stocks

@lru_cache(maxsize=10000)
def get_stock_info(symbol):
    response = urllib3.request("GET", f'https://query2.finance.yahoo.com/v1/finance/search?q={symbol}')
    content = response.data
    data = json.loads(content.decode('utf8'))
    if 'quotes' in data and len(data['quotes']) > 0 and 'symbol' in data['quotes'][0] and 'shortname' in data['quotes'][0]:
        symbol = str(data['quotes'][0]['symbol'])
        shortname = str(data['quotes'][0]['shortname'])
        if len(symbol) > 5:
            symbol = None
            shortname = None
    else:
        symbol = None
        shortname = None

    return symbol, shortname


def get_symbols_from_comment(comment: str):
    stocks = get_mentioned_stocks(comment)
    # remove duplicate stock symbols
    stocks = list(set(stocks))
    shortnames: list[str] = []
    symbols: list[str] = []
    for stock in stocks:
        symbol, shortname = get_stock_info(stock)
        if stock is None or shortname is None:
            pass
        else:
            symbols.append(symbol)
            shortnames.append(shortname)
    return symbols, shortnames

try:
    subreddit_name = "wallstreetbets"
    subreddit: models.Subreddit = reddit.subreddit(subreddit_name)
    subreddit_id = database.create_subreddit(subreddit.id, subreddit_name)

    submission: praw.reddit.Submission
    submissions = []
    print("Getting submissions")
    # first get all the submissions and put them in the comments array
    for submission in subreddit.hot(limit=1000):
        submissions.append(submission)
        print("Getting submissions", len(submissions))
    print("Total submissions", len(submissions))
    # now process the submissions and get their comments
    for submission in submissions:
        submission.comment_sort = "new"
        submission.comments.replace_more(limit=None)
        comments = submission.comments.list()

        print(f"Processing {len(comments)} comments")

        processed_comments = []
        num_to_process = len(comments)
        processed = 0
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit tasks to the executor
            future_to_comment = {executor.submit(get_symbols_from_comment, comment.body): comment for comment in comments}

            # Iterate over completed futures
            for future in concurrent.futures.as_completed(future_to_comment):
                comment = future_to_comment[future]
                try:
                    # Get the result from the future
                    symbols, names = future.result()
                    print(symbols, names)
                    processed += 1
                    if len(symbols) > 0: # We won't bother inserting comments that have no mentions
                        processed_comments.append((subreddit_id, submission.id, comment.id, comment.body, comment.permalink, symbols, names))
                    print(f"Processed {processed}/{num_to_process}")
                except Exception as e:
                    print(f"Exception occurred for comment {comment.id}: {e}\n\t{comment.body}, {comment.id}")
        print(f"Inserting {len(processed_comments)}")
        database.create_many_mentions_data(processed_comments)
        print(f"Successfully inserted")

except Exception as e:
    print(e)
