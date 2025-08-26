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

# Force start from Day 1 - Clear any existing posted tweets log
POSTED_TWEETS_FILE = "posted_tweets.txt"
print("🔄 Starting fresh from Day 1 - clearing previous posts")

# Clear the posted tweets file to start over
try:
    with open(POSTED_TWEETS_FILE, "w", encoding="utf-8") as f:
        f.write("")  # Clear the file
    print("✅ Cleared posted tweets log - starting from Day 1")
    posted_count = 0
    posted_tweets_content = []
except Exception as e:
    print(f"⚠️ Could not clear posted tweets log: {e}")
    posted_count = 0
    posted_tweets_content = []

# Start from Day 1 Fact 1
next_tweet_to_post = all_tweets[0]  # First tweet (Day 1 Fact 1)
next_tweet_index = 0

print(f"✅ Starting fresh from Day 1 Fact 1")
print(f"📝 First tweet: {next_tweet_to_post[:60]}...")
print(f"📊 Progress: 0/{len(all_tweets)} tweets posted - Starting fresh!")

# --- Post the next tweet ---
def post_next_tweet():
    print(f"📤 Posting tweet #{next_tweet_index + 1}: {next_tweet_to_post}")
    
    try:
        response = client.create_tweet(text=next_tweet_to_post)
        tweet_id = response.data['id']
        print(f"✅ Tweet posted successfully!")
        print(f"🔗 Tweet ID: {tweet_id}")
        
        # Log the successful post
        try:
            with open(POSTED_TWEETS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{tweet_id}: {next_tweet_to_post}\n")
            print(f"✅ Logged tweet #{next_tweet_index + 1}")
            
            # Verify the file was written
            if os.path.exists(POSTED_TWEETS_FILE):
                with open(POSTED_TWEETS_FILE, "r", encoding="utf-8") as f:
                    lines = len(f.readlines())
                print(f"✅ Posted tweets file now has {lines} entries")
            
        except Exception as e:
            print(f"⚠️ Could not log tweet: {e}")
        
        return True
        
    except tweepy.Forbidden as e:
        if "duplicate" in str(e).lower():
            print(f"⚠️ Tweet already posted before: {next_tweet_to_post[:50]}...")
            # Mark it as posted to avoid posting again
            try:
                with open(POSTED_TWEETS_FILE, "a", encoding="utf-8") as f:
                    f.write(f"duplicate: {next_tweet_to_post}\n")
                print("✅ Marked duplicate tweet as posted")
            except Exception as log_error:
                print(f"⚠️ Could not log duplicate: {log_error}")
            return True  # Consider it successful to continue sequence
        else:
            print(f"❌ Forbidden error: {e}")
            return False
    except tweepy.TooManyRequests:
        print("❌ Rate limit exceeded. Try again later.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# --- Main execution ---
if __name__ == "__main__":
    success = post_next_tweet()
    
    if success:
        print("🎉 Bot completed successfully!")
        remaining_tweets = len(all_tweets) - (posted_count + 1)
        if remaining_tweets > 0:
            print(f"📊 Progress: {posted_count + 1}/{len(all_tweets)} tweets posted")
            print(f"⏭️ Next run will post tweet #{next_tweet_index + 2}")
        else:
            print("🏁 Cycle complete! Next run will start fresh")
    else:
        print("💥 Bot execution failed")
    
    print("🏁 Bot finished")
