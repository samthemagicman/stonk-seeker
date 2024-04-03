import time
from typing import List
from diskcache import Cache
from praw import models
from util import reddit
import praw
import spacy
import urllib3
import database
import json
import concurrent.futures
import axiom
import socket
cache = Cache(directory="./cache")

log_client = axiom.Client("xaat-f4b1c238-67fd-445a-b73d-6cf2411399fe", "triple-s-software-sxs6")
log_dataset = "stonkes_workers"
hostname = socket.gethostname()


def log(event_name: str, events: dict):
    events["type"] = event_name
    events["host"] = hostname
    log_client.ingest_events(dataset=log_dataset, events=[events])


nlp = spacy.load("en_core_web_sm")


def get_mentioned_stocks(comment: str) -> List[str]:
    doc = nlp(comment)
    stocks = []
    for ent in doc.ents:
        if ent.label_ == "ORG":
            stock = ent.text.lower()
            stocks.append(stock)
    return stocks


def get_stock_info(symbol_to_check):
    if symbol_to_check in cache:
        # log("symbol_cache", {"symbol": symbol_to_check, "cache_hit": True})
        sym, name = cache[symbol_to_check]
        # print("Cache hit")
        return sym, name
    else:
        log("symbol_cache", {"symbol": symbol_to_check, "cache_hit": False})
    response = urllib3.request("GET", f'https://query2.finance.yahoo.com/v1/finance/search?q={symbol_to_check}')
    content = response.data
    if response.status == 429:
        # Wait before sending more requests to finance apy
        log("finance_api_timeout", {"symbol": symbol_to_check})
        print("Finance API limit reached. Waiting...")
        time.sleep(60 * 10)
        return get_stock_info(symbol_to_check)
    data = json.loads(content.decode('utf8'))
    if 'quotes' in data and len(data['quotes']) > 0 and 'symbol' in data['quotes'][0] and 'shortname' in data['quotes'][0]:
        symbol = str(data['quotes'][0]['symbol'])
        shortname = str(data['quotes'][0]['shortname'])
    else:
        symbol = None
        shortname = None
    cache[symbol_to_check] = (symbol, shortname)
    return symbol, shortname


def get_symbols_from_comment(comment: str):
    stocks = get_mentioned_stocks(comment)
    # remove duplicate stock symbols
    stocks = list(set(stocks))
    shortnames: list[str] = []
    symbols: list[str] = []
    for stock in stocks:
        symbol, shortname = get_stock_info(stock.lower())
        if stock is not None and shortname is not None:
            symbols.append(symbol)
            shortnames.append(shortname)
    return symbols, shortnames


def start():
    log("started", {})
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
            #print("Getting submissions", len(submissions))
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
                        processed += 1
                        if len(symbols) > 0: # We won't bother inserting comments that have no mentions
                            processed_comments.append((subreddit_id, submission.id, comment.id, comment.body, comment.permalink, symbols, names))
                        #print(f"Processed {processed}/{num_to_process}")
                    except Exception as e:
                        log("comment_failed", {
                            "comment_id": comment.id,
                            "error": e
                        })
                        print(f"Exception occurred for comment {comment.id}: {e}\n\t{comment.body}, {comment.id}")
            comms_to_insert = len(processed_comments)
            print(f"Inserting {comms_to_insert}")
            database.create_many_mentions_data(processed_comments)
            log("comments_inserted", {
                "amount": comms_to_insert,
            })
            print(f"Successfully inserted")
    except Exception as e:
        print(e)


print("Starting")
start()
