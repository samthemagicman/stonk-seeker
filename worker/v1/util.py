import praw
import pika

reddit = praw.Reddit(
    client_id="SZj3fjzqYfaKSBOHqDYs3w",
    client_secret="ZnuAV4Q9lJsZYwD9Xxq18-PhBXaQAg",
    user_agent="scrape",
)

if (reddit.read_only):
    print("Successfully connected to Reddit API")
else:
    raise Exception("Failed to connect to Reddit API")
    exit()

# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=pika.PlainCredentials('rabbitmq', 'rabbitmq')))
# comment_channel = connection.channel()
# comment_channel.queue_declare(queue='comments')
