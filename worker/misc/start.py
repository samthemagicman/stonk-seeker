import subprocess

def start_publisher():
    subprocess.run(["python", "get_comments.py"])

def start_consumer():
    subprocess.run(["python", "process_comments.py"])

def start_ticker():
    subprocess.run(["python", "process_tickers.py"])

if __name__ == "__main__":
    start_publisher()
    start_ticker()
    start_consumer()