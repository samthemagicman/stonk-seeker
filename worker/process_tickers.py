import json
from datetime import datetime

import pika
from termcolor import colored
import database
import urllib3
import json

stockSymbols = {
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

# Can update this to use the NASDAQ CSV file https://www.nasdaq.com/market-activity/stocks/screener?exchange=NASDAQ&render=download
def get_stock_info(symbol):
    response = urllib3.request("GET", f'https://query2.finance.yahoo.com/v1/finance/search?q={symbol}')
    content = response.data
    data = json.loads(content.decode('utf8'))
    if 'quotes' in data and len(data['quotes']) > 0 and 'symbol' in data['quotes'][0] and 'shortname' in data['quotes'][0]:
        symbol = str(data['quotes'][0]['symbol'])
        shortname = str(data['quotes'][0]['shortname'])
        if len(symbol) > 5:
            symbol = None
            shortname = None
    else:
        symbol = None
        shortname = None

    return symbol, shortname

# def get_ticker(company):
#     url = f"https://query2.finance.yahoo.com/v1/finance/search?q={company}"
#     response = requests.get(url)
#     print(response)
#     data = response.json()
    
#     if 'quotes' in data and len(data['quotes']) > 0:
#         first_symbol = data['quotes'][0]['symbol']
#         return str(first_symbol)
#     else:
#         return None

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=pika.PlainCredentials('rabbitmq', 'rabbitmq')));
channel = connection.channel()
channel.queue_declare(queue='tickers')

def process_tickers(ch, method, properties, body: bytes):
    bodyObj = json.loads(body.decode('utf-8'))
    stocks: list[str] = bodyObj["stocks"]
    comment_id = bodyObj["comment_id"]
    comment = bodyObj["comment"]
    time = bodyObj["time"]
    print(f"Checking stock: {colored(stocks, 'green')}")

    for stock in stocks:
        if (stock in stockSymbols):
            symbol = stockSymbols[stock]
            stocks.remove(stock)
            stocks.append(symbol)

    #remove duplicate stock symbols
    stocks = list(set(stocks))

    shortnames: list[str] = []
    symbols: list[str] = []
    for stock in stocks:
        symbol, shortname = get_stock_info(stock)
        if (stock is None or shortname is None):
            print(f"Failed to get ticker for {colored(stock, 'red')}")
        else:
            symbols.append(symbol)
            shortnames.append(shortname)
            print(f"Received ticker: {colored(symbols, 'green')}")

    try:
        database.create_stock_mention(comment_id, symbols, shortnames, datetime.utcfromtimestamp(time))
    except Exception as e:
        print(colored(f"Failed to create stock mention: {e}", "red"))


print(colored("Waiting for new tickers...", "green"))
channel.basic_consume(queue='tickers', on_message_callback=process_tickers, auto_ack=True)
channel.start_consuming()