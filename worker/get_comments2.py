from datetime import datetime

import praw
from praw.models.comment_forest import CommentForest
from praw import models
from termcolor import colored
import database
import json
import pika

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

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=pika.PlainCredentials('rabbitmq', 'rabbitmq')));
channel = connection.channel()
channel.queue_declare(queue='comments')

subreddit_name = "wallstreetbets"

subreddit_id = database.create_subreddit(subreddit_name)

subreddit: models.Subreddit = reddit.subreddit(subreddit_name)


def process_comments(comments: CommentForest):
    for comment in comments:
        if (isinstance(comment, models.MoreComments)):
            process_comments(comment.comments())
            continue

        if database.comment_exists(comment.id):
            print(colored(f"Comment {comment.id} already exists, skipping", "red"))
            continue
        print(colored("Sending new comment:", "blue"))
        print(f"- {comment.body}\n\n")

        submission: models.Submission = comment.submission
        post_id = database.get_or_create_post(id=submission.id, link=submission.shortlink, subreddit_id=subreddit_id)
        comment_id = database.create_comment(comment.id, comment.body, post_id, comment.permalink, datetime.utcfromtimestamp(comment.created_utc))
        channel.basic_publish(exchange='', routing_key='comments',
                              body=json.dumps({"comment": comment.body, "upvotes": comment.score, "comment_id": comment_id, "post_id": post_id}))


submission: praw.reddit.Submission
for submission in subreddit.stream.submissions():
    print(colored(submission.title, "red"))
    process_comments(submission.comments)
