import time
from typing import List
from diskcache import Cache
import asyncpraw
from asyncpraw.models import MoreComments
import spacy
import urllib3
import database
import json
import concurrent.futures
import axiom
import asyncio
import settings
import praw
from praw.models import Subreddit
from settings import comments_gathering_workers, comments_processing_workers, hostname, subreddits

cache = Cache(directory=settings.cache_location)
banned_cache = Cache(directory=settings.banned_cache_location)

for banned in settings.banned_symbols:
    banned_cache[banned] = True

log_client = axiom.Client(settings.axiom_client_id, settings.axiom_org_id)

processed_comments = []
num_processed = 0
nlp = spacy.load("en_core_web_sm")
pool = concurrent.futures.ThreadPoolExecutor()


def log(event_name: str, events: dict):
    events["type"] = event_name
    events["host"] = hostname
    log_client.ingest_events(dataset=settings.axiom_dataset, events=[events])


def get_mentioned_stocks(comment: str) -> List[str]:
    doc = nlp(comment)
    stocks = []
    for ent in doc.ents:
        if ent.label_ == "ORG":
            stock = ent.text.lower()
            stocks.append(stock)
    return stocks


def get_stock_info(symbol_to_check):
    if symbol_to_check in banned_cache:
        return None, None
    if symbol_to_check in cache:
        # log("symbol_cache", {"symbol": symbol_to_check, "cache_hit": True})
        sym, name = cache[symbol_to_check]
        # print("Cache hit")
        return sym, name
    elif settings.only_use_cache:
        return None, None
    else:
        print(f"Cache miss {symbol_to_check}")
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


def process_comment(comment, subreddit_id, submission_id):
    try:
        symbols, names = get_symbols_from_comment(comment.body)
        if len(symbols) > 0:  # We won't bother inserting comments that have no mentions
            processed_comments.append(
                (subreddit_id, submission_id, comment.id, comment.created_utc, comment.body, comment.permalink, symbols, names))
    except Exception as e:
        log("comment_failed", {
            "comment_id": comment.id,
            "error": e
        })
        print(f"Exception occurred for comment {comment.id}: {e}\n\t{comment.body}, {comment.id}")


def process_comments(comments, subreddit_id, submission_id):
    for comment in comments:
        try:
            symbols, names = get_symbols_from_comment(comment.body)
            if len(symbols) > 0:  # We won't bother inserting comments that have no mentions
                processed_comments.append(
                    (subreddit_id, submission_id, comment.id, comment.body, comment.permalink, symbols, names))
        except Exception as e:
            log("comment_failed", {
                "comment_id": comment.id,
                "error": e
            })
            print(f"Exception occurred for comment {comment.id}: {e}\n\t{comment.body}, {comment.id}")


async def get_comments_from_submission_queue(queue, comment_queue):
    while True:
        submission = await queue.get()
        try:
            comments = await submission.comments()
            # await comments.replace_more(limit=None)
            comments = await comments.list()
            
            while len(comments) != 0:
                comment = comments.pop(0)
                if isinstance(comment, MoreComments):
                    more_comments = await comment.comments()
                    comments.extend(more_comments)
                else:
                    comment_queue.put_nowait((comment, submission.id))
            # print(f"Got {len(comments)} comments")
            # queue.put(comments)
        except Exception as e:
            print(f"Exception occurred in get_comments: {e}")
            await asyncio.sleep(5)
        queue.task_done()


async def process_comment_queue(comment_queue, subreddit_id, loop):
    global num_processed
    while True:
        (comment, submission_id) = await comment_queue.get()
        try:
            await loop.run_in_executor(pool, process_comment, comment, subreddit_id, submission_id)
            num_processed += 1
            if len(processed_comments) > 1000:
                processed_comments_copy = processed_comments.copy()
                processed_comments.clear()
                await insert_comments_to_db(processed_comments_copy)

            # with concurrent.futures.ThreadPoolExecutor() as pool:
            #     await loop.run_in_executor(pool, process_comments3, comments, subreddit_id, submission)
            #     processed_comments.append(*resu)
            # await process_comments2(comments, subreddit_id, submission, loop)
            # await process_comments(comments, subreddit_id, submission)
            # resu = await comments_util.process_comments2(comments, subreddit_id, submission, loop)
            # processed_comments.append(*resu)
        except Exception as e:
            print(e)
        comment_queue.task_done()


async def print_state(comment_queue, queue):
    global num_processed
    while True:
        print(f"Submissions left {queue.qsize()}")
        print(f"Comments left: {comment_queue.qsize()}")
        print(f"Processed comments: {len(processed_comments)}")
        print(f"Total processed: {num_processed}")
        await asyncio.sleep(0.5)


def create_workers(comment_queue, queue, subreddit_id, loop):
    get_comment_tasks = []
    process_comment_tasks = []
    for i in range(comments_gathering_workers):
        task = asyncio.create_task(get_comments_from_submission_queue(queue, comment_queue))
        get_comment_tasks.append(task)
    for i in range(comments_processing_workers):
        task = asyncio.create_task(process_comment_queue(comment_queue, subreddit_id, loop))
        process_comment_tasks.append(task)
    return get_comment_tasks, process_comment_tasks


def cancel_tasks(*args):
    for task in args:
        task.cancel()


async def insert_comments_to_db(comments: List[str]):
    print(f"Inserting {len(comments)} comments to db")
    log("inserting_comments", {"num_comments": len(comments)})
    await database.create_many_mentions_data(comments)


async def bulk_insert_comments():
    num_comments = len(processed_comments)
    for i in range(0, num_comments, settings.db_batch_insert_size):
        batch = processed_comments[i:i + settings.db_batch_insert_size]
        await database.create_many_mentions_data(batch)
    processed_comments.clear()


async def start(subreddit_name):
    loop = asyncio.get_running_loop()
    log("started", {})
    reddit = praw.Reddit(client_id="SZj3fjzqYfaKSBOHqDYs3w", client_secret="ZnuAV4Q9lJsZYwD9Xxq18-PhBXaQAg", user_agent="scrape")
    subreddit: Subreddit = reddit.subreddit(subreddit_name)
    subreddit_id = database.create_subreddit(subreddit.id, subreddit_name)

    submission: asyncpraw.reddit.Submission

    queue = asyncio.Queue()
    comment_queue = asyncio.Queue()
    get_comments_tasks, process_comments_tasks = create_workers(comment_queue, queue, subreddit_id, loop)
    state_task = asyncio.create_task(print_state(comment_queue, queue))

    for comment in subreddit.stream.comments():
        try:
            comment_queue.put_nowait(comment)
        except Exception as e:
            print(f"Exception occurred in main loop: {e}")


print("Starting")
if __name__ == '__main__':
    if subreddits is None:
        print(f"Processing stocks")
        asyncio.run(start('stocks'))
    else:
        for subreddit in subreddits:
            print(f"Processing {subreddit}")
            asyncio.run(start(subreddit))