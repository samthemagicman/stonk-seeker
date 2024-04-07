import subprocess

def start_scraping(subreddit):
    try:
        subprocess.run(["python", "-u", "main.py"] + ["--subreddit"] + [subreddit], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("Error: The specified program was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    for subreddit in ["wallstreetbets", "stocks", "investing"]:
        start_scraping(subreddit)
