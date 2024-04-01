import pika
import spacy
from termcolor import colored
import json

import database

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=pika.PlainCredentials('rabbitmq', 'rabbitmq')));
channel = connection.channel()
channel.queue_declare(queue='comments')
channel.queue_declare(queue='tickers')

nlp = spacy.load("en_core_web_trf")

# Initialize an empty dictionary to keep count of organizations mentioned

def process_comments(ch, method, properties, body: bytes):
    commentObj = json.loads(body.decode('utf-8'))
    comment = commentObj["comment"]
    comment_id = commentObj["comment_id"]
    post_id = commentObj["post_id"]
    time = commentObj["time"]

    print(colored(f"Processing new comment {comment}", "blue"))
    doc = nlp(comment)
    stocks = []
    for ent in doc.ents:
        #print(f'{colored(ent.text, "green")} {ent.label_}')
        if ent.label_ == "ORG":
            stock = ent.text.lower()
            stocks.append(stock)
    if len(stocks) == 0:
        print(colored("No stocks mentioned", "red"))
    else:
        channel.basic_publish(exchange='', routing_key='tickers', body=json.dumps(
            {
                "stocks": stocks,
                "post_id": post_id,
                "comment_id": comment_id,
                "comment": comment,
                "time": time
            }
        ))


print(colored("Waiting for new comments...", "green"))
channel.basic_consume(queue='comments', on_message_callback=process_comments, auto_ack=True)
channel.start_consuming()