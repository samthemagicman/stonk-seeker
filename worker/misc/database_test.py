import database
import random

try:
    subredditId = database.create_subreddit(f"wallstreetbets{random.randint(0, 1000)}")
    postId = database.create_post(f"{random.randint(0, 1000)}", "This is a test post", subredditId)
    commentId = database.create_comment(str(random.randint(0, 1000)), "This is a test comment", postId, "https://www.reddit.com/r/wallstreetbets/comments/1")
    database.create_stock_mention(commentId, ["GME", "AAPL"], ["GameStop", "Apple"])
except database.CommentExistsError as e:
    print(e)