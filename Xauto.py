import tweepy
import os
import schedule
import time
import random

# --- Load API credentials from environment variables ---
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# --- Authenticate with Tweepy ---
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# --- Load tweets from file ---
TWEETS_FILE = "tweets.txt"
with open(TWEETS_FILE, "r", encoding="utf-8") as f:
    tweets = [line.strip() for line in f if line.strip()]

# --- Post random tweet ---
def post_tweet():
    if not tweets:
        print("⚠️ No tweets found in tweets.txt")
        return
    tweet = random.choice(tweets)
    try:
        client.create_tweet(text=tweet)
        print(f"✅ Tweet posted: {tweet}")
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")

# --- For local testing only (GitHub Actions will call post_tweet directly) ---
if __name__ == "__main__":
    post_tweet()
