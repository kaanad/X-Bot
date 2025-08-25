import tweepy
import os
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

# Load posted tweets to track progress
# --- Set starting point from Day2 Fact1 ---
posted_count = 2  # Skip Day1 Fact1 and Fact2
if os.path.exists(POSTED_TWEETS_FILE):
    try:
        with open(POSTED_TWEETS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            existing_count = len([line for line in lines if line.strip()])
            # Use whichever is higher: previously posted or Day2 start
            posted_count = max(existing_count, posted_count)
        print(f"✅ Starting from tweet #{posted_count + 1}")
    except Exception as e:
        print(f"⚠️ Error reading posted tweets: {e}")
        print(f"✅ Defaulting start to tweet #{posted_count + 1}")


# Calculate which tweet to post next (sequential order)
if posted_count >= len(all_tweets):
    # All tweets have been posted, start over from the beginning
    print("🔄 All tweets have been posted! Starting fresh cycle...")
    posted_count = 0
    # Clear the posted tweets file for a fresh start
    try:
        with open(POSTED_TWEETS_FILE, "w", encoding="utf-8") as f:
            f.write("")  # Clear the file
        print("✅ Reset posted tweets log")
    except Exception as e:
        print(f"⚠️ Could not reset posted tweets log: {e}")

# Get the next tweet in sequence
next_tweet_index = posted_count
next_tweet = all_tweets[next_tweet_index]

print(f"✅ Next tweet to post: #{next_tweet_index + 1} of {len(all_tweets)}")
print(f"📝 Tweet preview: {next_tweet[:50]}...")

# --- Post the next sequential tweet ---
def post_sequential_tweet():
    print(f"📤 Posting tweet #{next_tweet_index + 1}: {next_tweet}")
    
    try:
        response = client.create_tweet(text=next_tweet)
        tweet_id = response.data['id']
        print(f"✅ Tweet posted successfully!")
        print(f"🔗 Tweet ID: {tweet_id}")
        
        # Log the successful post
        try:
            with open(POSTED_TWEETS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{tweet_id}: {next_tweet}\n")
            print(f"✅ Logged tweet #{next_tweet_index + 1}")
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
    success = post_sequential_tweet()
    
    if success:
        print("🎉 Bot completed successfully!")
        remaining_tweets = len(all_tweets) - (next_tweet_index + 1)
        if remaining_tweets > 0:
            print(f"📊 Progress: {next_tweet_index + 1}/{len(all_tweets)} tweets posted")
            print(f"⏭️ Next tweet will be: #{next_tweet_index + 2}")
        else:
            print("🏁 Cycle complete! Next run will start from Day 1")
        print(f"⏰ Next scheduled run: Check GitHub Actions")
    else:
        print("💥 Bot execution failed")
        print("ℹ️ This is normal if tweet was a duplicate or rate limited")
    
    print("🏁 Bot finished")

