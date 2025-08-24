# 🚀 X (Twitter) Automation Bot — Fixed for API v2

import tweepy
import os
import schedule
import time

# --- User Credentials ---
API_KEY = "95OjPJY6deD7JmVbJmhOKUSM8"
API_SECRET = "3TwPmxv47hS3FVUGCUgGR2LUqVU8oRPo6w2mVnePZ6YlCWZj8F"
ACCESS_TOKEN = "1307953549880549377-WzUBFjhcQhHSbaPERUc7vBVjvJGm7W"
ACCESS_TOKEN_SECRET = "ADw7wjahPkgo14fM9XLQj7h7FwvefX1NQHPYULF7QjeaJ"

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAE3y3gEAAAAAiMhvX0xr7cv%2Fuj9%2FfG4q7JiGagE%3DRaNeBJXDAeHElR1lS7A05iYOe1CwZaaTM4t9ouPl78stxtr1Bv "

# --- Bot Configuration ---
TWEETS_FILE = "tweets.txt"
POSTED_TWEETS_FILE = "posted_tweets.txt"

# --- Global State ---
tweet_list = []
posted_tweets = []

# --- Functions ---

def authenticate_bot():
    """Authenticate with X using OAuth1a and v2 API."""
    try:
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        me = client.get_me()
        print(f"✅ Authentication successful! Connected as: @{me.data.username}")
        return client
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def load_posted_tweets():
    """Load previously posted tweets to avoid duplicates."""
    if not os.path.exists(POSTED_TWEETS_FILE):
        return []
    try:
        with open(POSTED_TWEETS_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
            # Each line format: tweet_id: tweet_text
            return [":".join(line.split(":")[1:]).strip() for line in lines if line.strip()]
    except Exception as e:
        print(f"⚠️ Warning: Could not load posted tweets: {e}")
        return []

def save_posted_tweet(message, tweet_id):
    """Save posted tweet to file for tracking."""
    try:
        with open(POSTED_TWEETS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{tweet_id}: {message}\n")
    except Exception as e:
        print(f"⚠️ Warning: Could not save posted tweet: {e}")

def get_tweets_from_file(file_path):
    """Read tweets from file separated by blank lines."""
    tweets = []
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}. Creating a template...")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# Add your tweets here, separated by blank lines\n\n")
            f.write("Your first tweet goes here!\n\n")
            f.write("Your second tweet goes here!\n\n")
        return tweets
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Split tweets by blank lines, keep lines starting with #
            tweet_parts = [tweet.strip() for tweet in content.split("\n\n") if tweet.strip()]
            tweets.extend(tweet_parts)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
    print(f"📌 Loaded {len(tweets)} tweets from {file_path}")
    return tweets

def post_tweet(client, message):
    """Post a tweet using API v2."""
    if client is None:
        print("❌ Cannot post tweet. Client is not available.")
        return False
    try:
        response = client.create_tweet(text=message)
        tweet_id = response.data['id']
        print(f"✅ Tweet posted: {message}")
        print(f"🔗 Tweet URL: https://twitter.com/user/status/{tweet_id}")
        save_posted_tweet(message, tweet_id)
        return True
    except tweepy.Forbidden as e:
        print(f"❌ Forbidden error: {e}")
        if "duplicate" in str(e).lower():
            print("💡 Skipping duplicate tweet.")
        return False
    except tweepy.TooManyRequests as e:
        print(f"❌ Rate limit exceeded: {e}")
        return False
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return False

def post_next_tweet():
    """Post the next tweet from the queue."""
    global client, tweet_list
    if not tweet_list:
        print("✅ No more tweets left to post. Stopping scheduler.")
        return schedule.CancelJob

    tweet_to_post = tweet_list.pop(0)
    success = post_tweet(client, tweet_to_post)

    if not success:
        # Put it back if failed (e.g., duplicate)
        tweet_list.insert(0, tweet_to_post)
        print("🔄 Tweet will be retried later.")
    return

def check_api_access():
    """Check if the current API access level supports posting tweets."""
    global client
    if client is None:
        return False
    try:
        me = client.get_me()
        return True
    except Exception as e:
        print(f"❌ API access check failed: {e}")
        return False

# --- Main Execution ---
if __name__ == "__main__":
    print("🚀 Starting X Automation Bot (API v2)...")

    if BEARER_TOKEN == "YOUR_BEARER_TOKEN":
        print("❌ ERROR: Please add your Bearer Token.")
        exit(1)

    client = authenticate_bot()

    if client and check_api_access():
        posted_tweets = load_posted_tweets()
        print(f"📋 Loaded {len(posted_tweets)} previously posted tweets.")

        tweet_list = get_tweets_from_file(TWEETS_FILE)

        # Remove duplicates
        tweet_list = [t for t in tweet_list if t not in posted_tweets]

        if not tweet_list:
            print("⚠️ No new tweets to post. All tweets already posted.")
        else:
            print(f"📌 {len(tweet_list)} new tweets ready to post.")

            print("📝 Posting the first tweet immediately...")
            post_next_tweet()

            if tweet_list:
                schedule.every().day.at("06:00").do(post_next_tweet)
                schedule.every().day.at("20:00").do(post_next_tweet)
                print("✅ Bot running. Scheduled tweets for 6:00 AM and 8:00 PM daily.")
                print("   Press CTRL+C to stop")

                try:
                    while True:
                        if not schedule.jobs:
                            print("✅ All tweets have been posted. Shutting down.")
                            break
                        schedule.run_pending()
                        time.sleep(60)
                except KeyboardInterrupt:
                    print("\n🛑 Bot stopped by user.")
            else:
                print("✅ All tweets have been posted. Shutting down.")
    else:
        print("❌ Failed to initialize bot. Check credentials and API access level.")

    print("👋 Bot has stopped.")
