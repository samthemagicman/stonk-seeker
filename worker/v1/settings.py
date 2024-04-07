import argparse
import socket

cache_location = "./cache"
banned_cache_location = "./banned_cache"
banned_symbols = ['lol', 'ath', 'ai', 'ipo', 'fed', 'pce', 'ev', 'cnbc'] # List of common words that go to wrong thing

axiom_client_id = "xaat-f4b1c238-67fd-445a-b73d-6cf2411399fe"
axiom_org_id = "triple-s-software-sxs6"
axiom_dataset = "stonkes_workers"

hostname = socket.gethostname()

comments_processing_workers = 1
comments_gathering_workers = 2

parser = argparse.ArgumentParser()
parser.add_argument("--subreddit", type=str)
parser.add_argument("--subreddits", nargs="+")
parser.add_argument("--only-use-cache", type=bool)
args = parser.parse_args()
subreddit_to_scrape = args.subreddit
only_use_cache = args.only_use_cache
subreddits = ['wallstreetbets', 'stocks', 'investing']# vars(args)['subreddits']

db_batch_insert_size=1000