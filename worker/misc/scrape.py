import praw
import spacy
from praw.models.comment_forest import CommentForest
from praw import models
from termcolor import colored
import os

# List of stock names to tickers
stockTickers = {
    "apple": "aapl",
    "tesla": "tsla",
    "amazon": "amzn",
    "facebook": "meta",
    "google": "goog",
    "googl": "goog",
    "microsoft": "msft",
    "netflix": "nflx",
    "nvidia": "nvda",
    "Super Micro Computer": "smci",
}

reddit = praw.Reddit(
    client_id="SZj3fjzqYfaKSBOHqDYs3w",
    client_secret="ZnuAV4Q9lJsZYwD9Xxq18-PhBXaQAg",
    user_agent="scrape",
)

if (reddit.read_only):
    print("Successfully connected to Reddit API")
else:
    print("Failed to connect to Reddit API")
    exit()

nlp = spacy.load("en_core_web_trf")

# Initialize an empty dictionary to keep count of organizations mentioned
orgs_count = {}

subreddit: models.Subreddit = reddit.subreddit("wallstreetbets")

comment: models.Comment
for comment in subreddit.stream.comments():
    os.system('cls')
    print(colored("Processing new comment:", "blue"))
    print(f"- {comment.body}\n\n")
    submission: models.Submission = comment.submission
    doc = nlp(comment.body)
    for ent in doc.ents:
        #print(f'{colored(ent.text, "green")} {ent.label_}')
        if ent.label_ == "ORG":
            stock = ent.text.lower()
            if (stock in stockTickers):
                stock = stockTickers[stock]
            if stock in orgs_count:
                orgs_count[stock] += 1
            else:
                orgs_count[stock] = 1
    orgs_count = dict(sorted(orgs_count.items(), key=lambda item: item[1], reverse=True))
    # update output
    for i, (org, count) in enumerate(orgs_count.items()):
        # if i >= 10:
        #     break
        print(f"{org.upper()}\t{count}")

exit()

submission: praw.reddit.Submission
for submission in subreddit.hot(limit=1):
    print(colored(submission.title, "red"))
    comment: models.Comment
    for comment in submission.comments:
        if isinstance(comment, models.MoreComments):
            continue
        colors = ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

        doc = nlp(comment.body)
        for ent in doc.ents:
            print(f'{colored(ent.text, "green")} {ent.label_}')
            if ent.label_ == "ORG":
                stock = ent.text.lower()
                if (stock in stockTickers):
                    stock = stockTickers[stock]
                if stock in orgs_count:
                    orgs_count[stock] += 1
                else:
                    orgs_count[stock] = 1

# Sort the dictionary by the counts
orgs_count = dict(sorted(orgs_count.items(), key=lambda item: item[1], reverse=True))
# Print the organizations and their counts
org: str
for org, count in orgs_count.items():
    print(f"{org.upper()}: {count}")
