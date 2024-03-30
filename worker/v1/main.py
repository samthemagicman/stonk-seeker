from functools import lru_cache

import praw
import spacy
import urllib3
from praw import models
import database
import json
from util import reddit
import concurrent.futures
import time

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

def start():
    try:
        subreddit_name = "wallstreetbets"
        subreddit: models.Subreddit = reddit.subreddit(subreddit_name)
        subreddit_id = database.create_subreddit(subreddit.id, subreddit_name)

        processed_comments = []
        processed = 0
        for comment in subreddit.stream.comments():
            try:
                # Get the result from the future
                symbols, names = get_symbols_from_comment(comment.body)
                if len(symbols) > 0: # We won't bother inserting comments that have no mentions
                    print(f"Comment {comment.id} has {len(symbols)} mentions")
                    processed = processed + 1
                    processed_comments.append((subreddit_id, comment.link_id, comment.id, comment.body, comment.permalink, symbols, names))
                
                if processed >= 100:
                    print(processed, processed > 100)
                    print(f"Inserting {len(processed_comments)}")
                    database.create_many_mentions_data(processed_comments)
                    print(f"Successfully inserted")
                    processed_comments = []
            except Exception as e:
                print(f"Exception occurred for comment {comment.id}: {e}\n\t{comment.body}, {comment.id}")
    except Exception as e:
        print(e)

print("Starting")
while True:
    start()
    time.sleep(60 * 60)