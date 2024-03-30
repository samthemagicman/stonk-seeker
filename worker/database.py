import psycopg
from psycopg.types import datetime

conn = psycopg.connect("postgres://postgres:postgres@localhost:5433/postgres")

class CommentExistsError(Exception):
    pass


def create_subreddit(id: str, name: str) -> str:
    """
    This function is used to create a new subreddit in the database.

    Parameters:
    name (str): The name of the subreddit to be created.

    Returns:
    int: The id of the newly created subreddit.
    """
    cur = conn.execute("SELECT id FROM subreddits WHERE id = %s", (id,), prepare=True)
    subreddit = cur.fetchone()
    if subreddit is None:
        cur = conn.execute("INSERT INTO subreddits (id, name) VALUES (%s, %s) RETURNING id", (id, name,), prepare=True)
        subreddit = cur.fetchone()
        conn.commit()
    return subreddit[0]


def create_subreddit2(name: str) -> str:
    """
    This function is used to create a new subreddit in the database.

    Parameters:
    name (str): The name of the subreddit to be created.

    Returns:
    int: The id of the newly created subreddit.
    """
    query = """
                WITH ins AS (
                    INSERT INTO subreddits (name)
                    SELECT '%(name)s'
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM subreddits
                        WHERE name = '%(name)s'
                    )
                    RETURNING id
                )
                SELECT id FROM subreddits WHERE name = '%(name)s'
                UNION ALL
                SELECT id FROM ins;
            """
    cur = conn.execute(query, {'name': name}, prepare=True)
    subreddit = cur.fetchone()
    conn.commit()
    return subreddit[0]


def create_mentions_data(
        post_id: str,
        comment_id: str,
        comment_body: str,
        comment_permalink: str,
        symbols: list[str],
        companies: list[str]
):
    cur = conn.execute("CALL insert_post_comment_and_mentions (%s::text, %s::text, %s::text, %s::text, %s, %s)", (comment_id, post_id, comment_body, comment_permalink, symbols, companies))
    conn.commit()

# Create a function that takes a list of tuples and inserts them into the database
# The arguments to the function should be the list of tuples in the format:
# [(comment_id, post_id, comment_body, comment_permalink, symbols, company_names), ...]
def create_many_mentions_data(
        data: list[(str, str, str, str, str, list[str], list[str])]
):
    cur = conn.cursor()
    for comment in data:
        cur.execute("CALL insert_post_comment_and_mentions (%s, %s::text, %s::text, %s::text, %s::text, %s, %s)", comment)
    conn.commit()


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

def post_exists(post_id: str) -> bool:
    return conn.execute("SELECT * FROM posts WHERE id = %s", (post_id,), prepare=True).fetchone() is not None

def create_comment(id: str, body: str, post_id: str, permalink: str, created_at) -> str:
    cur = conn.execute("INSERT INTO comments (id, body, post_id, permalink, created_at) VALUES (%s, %s, %s, %s, %s)", (id, body, post_id, permalink, created_at), prepare=True)
    if cur.rowcount == 0:
        raise Exception("Failed to create comment")
    conn.commit()
    return id

def count_post_comments(post_id: str) -> int:
    cur = conn.execute("SELECT COUNT(*) FROM comments WHERE post_id = (%s)", (post_id,), prepare=True)
    row = cur.fetchone()
    if row is None:
        return 0
    return row[0]

def create_stock_mention(comment_id: str, symbols: list[str], company_names: list[str], created_at):
    cur = conn.cursor()
    for i, symbol in enumerate(symbols):
        cur.execute("INSERT INTO stock_mentions (comment_id, symbol, company_name, created_at) VALUES (%s, %s, %s, %s)", (comment_id, symbol, company_names[i], created_at))
    if (cur.rowcount == 0):
        raise Exception("Failed to create stock mention")
    conn.commit()

#
# def create_comment(comment_id: str, comment: str, tickers: list[str], company_names: list[str]):
#     if (comment_exists(comment_id)):
#         raise CommentExistsError("Comment already exists")
#     conn.execute("SELECT create_comment(%s, %s, %s, %s)", (comment_id, comment, tickers, company_names))
#     conn.commit()
