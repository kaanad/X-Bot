import tweepy
import os
import random
import sys
from datetime import datetime

print(f"🤖 Twitter Bot started at {datetime.now()}")

# --- Load API credentials from environment variables ---
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Check if all credentials are present
if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN]):
    print("❌ Missing Twitter API credentials")
    print("Please check your GitHub repository secrets")
    sys.exit(1)

print("✅ All credentials found")

# --- Authenticate with Tweepy ---
try:
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    # Test authentication
    me = client.get_me()
    print(f"✅ Authenticated as: @{me.data.username}")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    sys.exit(1)

# --- Load tweets from file ---
TWEETS_FILE = "tweets.txt"
POSTED_TWEETS_FILE = "posted_tweets.txt"

try:
    with open(TWEETS_FILE, "r", encoding="utf-8") as f:
        all_tweets = [line.strip() for line in f if line.strip()]
    print(f"✅ Loaded {len(all_tweets)} total tweets")
except Exception as e:
    print(f"❌ Error loading tweets: {e}")
    sys.exit(1)

# Load posted tweets to avoid duplicates
posted_tweets_content = set()
if os.path.exists(POSTED_TWEETS_FILE):
    try:
        with open(POSTED_TWEETS_FILE, "r", encoding="utf-8") as f:
            # Extract just the tweet content from "ID: tweet" format
            for line in f:
                if ": " in line:
                    tweet_content = line.split(": ", 1)[1].strip()
                    posted_tweets_content.add(tweet_content)
        print(f"✅ Found {len(posted_tweets_content)} previously posted tweets")
    except Exception as e:
        print(f"⚠️ Error reading posted tweets: {e}")

# Get available tweets (not yet posted)
available_tweets = [tweet for tweet in all_tweets if tweet not in posted_tweets_content]

# If all tweets have been posted, reset and start over
if not available_tweets:
    print("🔄 All tweets have been posted! Starting fresh cycle...")
    available_tweets = all_tweets
    # Clear the posted tweets file for a fresh start
    try:
        with open(POSTED_TWEETS_FILE, "w", encoding="utf-8") as f:
            f.write("")  # Clear the file
        print("✅ Reset posted tweets log")
    except Exception as e:
        print(f"⚠️ Could not reset posted tweets log: {e}")

print(f"✅ {len(available_tweets)} tweets available to post")

# --- Post a random tweet ---
def post_tweet():
    if not available_tweets:
        print("❌ No tweets available to post")
        return False
    
    tweet = random.choice(available_tweets)
    print(f"📝 Attempting to post: {tweet[:50]}...")
    
    try:
        response = client.create_tweet(text=tweet)
        tweet_id = response.data['id']
        print(f"✅ Tweet posted successfully!")
        print(f"🔗 Tweet ID: {tweet_id}")
        
        # Log the successful post
        try:
            with open(POSTED_TWEETS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{tweet_id}: {tweet}\n")
            print("✅ Logged successful post")
        except Exception as e:
            print(f"⚠️ Could not log tweet: {e}")
        
        return True
        
    except tweepy.Forbidden as e:
        print(f"❌ Forbidden error (duplicate or policy violation): {e}")
        return False
    except tweepy.TooManyRequests:
        print("❌ Rate limit exceeded. Try again later.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# --- Main execution ---
if __name__ == "__main__":
    success = post_tweet()
    
    if success:
        print("🎉 Bot completed successfully!")
        print(f"⏰ Next scheduled run: Check GitHub Actions")
    else:
        print("💥 Bot execution failed")
        # Don't exit with error for duplicate tweets, just log it
        print("ℹ️ This is normal if tweet was a duplicate or rate limited")
    
    print("🏁 Bot finished")
