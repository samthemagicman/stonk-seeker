import psycopg
import os
import asyncio
import asyncpg

conn_str = os.getenv("DATABASE_URL", "postgres://postgres.gijsepyttxkktikcoicg:rxi3D7*qSRW!UCm@aws-0-us-west-1.pooler.supabase.com:5432/postgres")
conn = psycopg.connect(conn_str)
# Create a function that takes a list of tuples and inserts them into the database
# The arguments to the function should be the list of tuples in the format:
# [(comment_id, post_id, timestamp, comment_body, comment_permalink, symbols, company_names), ...]
async def create_many_mentions_data(data):
    conn2 = await asyncpg.connect(conn_str)
    stm = await conn2.prepare("CALL insert_post_comment_and_mentions ($1, $2, $3, TO_TIMESTAMP($4), $5, $6, $7, $8)")
    await stm.executemany(data)
    # for comment in data:
    #     cur.execute("CALL insert_post_comment_and_mentions (%s, %s::text, %s::text, %s::text, %s::text, %s, %s)", comment)
    # conn.commit()

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