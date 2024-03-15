import psycopg
from psycopg.types import datetime

conn = psycopg.connect("postgresql://postgres:postgres@localhost:5433/postgres")


class CommentExistsError(Exception):
    pass


def create_subreddit(name: str) -> str:
    """
    This function is used to create a new subreddit in the database.

    Parameters:
    name (str): The name of the subreddit to be created.

    Returns:
    int: The id of the newly created subreddit.
    """
    cur = conn.execute("SELECT id FROM subreddits WHERE name = %s", (name,), prepare=True)
    subreddit = cur.fetchone()
    if subreddit is None:
        cur = conn.execute("INSERT INTO subreddits (name) VALUES (%s) RETURNING id", (name,), prepare=True)
        subreddit = cur.fetchone()
        conn.commit()
    return subreddit[0]


def create_post(id: str, link: str, subreddit_id: str):
    cur = conn.execute("INSERT INTO posts (id, link, subreddit_id) VALUES (%s, %s, %s)", (id, link, subreddit_id), prepare=True)
    if (cur.rowcount == 0):
        raise Exception("Failed to create post")
    conn.commit()
    return id


def get_or_create_post(id: str, link: str, subreddit_id: str) -> str:
    """
    This function is used to get a post from the database or create a new one if it doesn't exist.

    Parameters:
    id (str): The id of the post to be retrieved or created.
    body (str): The body of the post to be created.
    subreddit_id (str): The id of the subreddit where the post is located.

    Returns:
    str: The id of the retrieved or newly created post.
    """
    cur = conn.execute("SELECT id FROM posts WHERE id = %s", (id,), prepare=True)
    post = cur.fetchone()
    if post is None:
        return create_post(id, link, subreddit_id)
    return post[0]


def comment_exists(comment_id: str) -> bool:
    return conn.execute("SELECT * FROM comments WHERE id = %s", (comment_id,), prepare=True).fetchone() is not None


def create_comment(id: str, body: str, post_id: str, permalink: str, created_at) -> str:
    cur = conn.execute("INSERT INTO comments (id, body, post_id, permalink, created_at) VALUES (%s, %s, %s, %s, %s)", (id, body, post_id, permalink, created_at), prepare=True)
    if cur.rowcount == 0:
        raise Exception("Failed to create comment")
    conn.commit()
    return id


def create_stock_mention(comment_id: str, symbols: list[str], company_names: list[str]):
    cur = conn.cursor()
    for i, symbol in enumerate(symbols):
        cur.execute("INSERT INTO stock_mentions (comment_id, symbol, company_name) VALUES (%s, %s, %s)", (comment_id, symbol, company_names[i]))
    if (cur.rowcount == 0):
        raise Exception("Failed to create stock mention")
    conn.commit()

#
# def create_comment(comment_id: str, comment: str, tickers: list[str], company_names: list[str]):
#     if (comment_exists(comment_id)):
#         raise CommentExistsError("Comment already exists")
#     conn.execute("SELECT create_comment(%s, %s, %s, %s)", (comment_id, comment, tickers, company_names))
#     conn.commit()
