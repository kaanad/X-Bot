import tweepy
import os
import sys
from datetime import datetime, timezone, timedelta

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

# --- Load posted tweets ---
posted_tweets_content = []
try:
    with open(POSTED_TWEETS_FILE, "r", encoding="utf-8") as f:
        posted_tweets_content = [line.strip() for line in f if line.strip()]
    print(f"✅ Found {len(posted_tweets_content)} previously posted tweets")
except FileNotFoundError:
    print("✅ No previous posts found - starting fresh")
    posted_tweets_content = []
except Exception as e:
    print(f"⚠️ Error loading posted tweets: {e}")
    posted_tweets_content = []

# --- Simple approach: Post the next tweet in sequence ---
def get_next_tweet():
    # Find how many tweets have been posted
    posted_count = len(posted_tweets_content)
    
    # The next tweet to post is simply the next one in the list
    next_tweet_index = posted_count
    
    # Handle case where we've posted all tweets (restart cycle)
    if next_tweet_index >= len(all_tweets):
        print("🔄 All tweets posted! Starting fresh cycle...")
        # Clear the posted tweets file
        try:
            with open(POSTED_TWEETS_FILE, "w", encoding="utf-8") as f:
                f.write("")
            print("✅ Cleared posted tweets log - restarting from beginning")
            posted_tweets_content.clear()
            next_tweet_index = 0
        except Exception as e:
            print(f"⚠️ Could not clear posted tweets log: {e}")
            next_tweet_index = 0
    
    tweet_to_post = all_tweets[next_tweet_index]
    
    # Calculate day and fact info for display
    day_number = (next_tweet_index // 2) + 1
    fact_number = (next_tweet_index % 2) + 1
    
    print(f"📋 Next: Day {day_number} Fact {fact_number} (Tweet #{next_tweet_index + 1})")
    print(f"📝 Tweet: {tweet_to_post[:60]}...")
    print(f"📊 Progress: {posted_count + 1}/{len(all_tweets)} after posting")
    
    return tweet_to_post, next_tweet_index, day_number, fact_number

# --- Check if specific tweet content already exists in posted tweets ---
def is_already_posted(tweet_content):
    for posted_line in posted_tweets_content:
        # Check if the tweet content exists in the posted line (after the tweet ID)
        if ": " in posted_line and tweet_content in posted_line.split(": ", 1)[1]:
            return True
    return False

# --- Post the tweet ---
def post_tweet(tweet_content, tweet_index, day, fact):
    if is_already_posted(tweet_content):
        print(f"⚠️ Day {day} Fact {fact} already posted, skipping...")
        return True
    
    print(f"📤 Posting Day {day} Fact {fact}: {tweet_content}")
    
    try:
        response = client.create_tweet(text=tweet_content)
        tweet_id = response.data['id']
        print(f"✅ Tweet posted successfully!")
        print(f"🔗 Tweet ID: {tweet_id}")
        print(f"🔗 Tweet URL: https://twitter.com/user/status/{tweet_id}")
        
        # Log the successful post
        try:
            with open(POSTED_TWEETS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{tweet_id}: {tweet_content}\n")
            print(f"✅ Logged Day {day} Fact {fact}")
            
        except Exception as e:
            print(f"⚠️ Could not log tweet: {e}")
        
        return True
        
    except tweepy.Forbidden as e:
        if "duplicate" in str(e).lower():
            print(f"⚠️ Duplicate tweet detected: {tweet_content[:50]}...")
            # Mark it as posted to avoid posting again
            try:
                with open(POSTED_TWEETS_FILE, "a", encoding="utf-8") as f:
                    f.write(f"duplicate: {tweet_content}\n")
                print("✅ Marked duplicate tweet as posted")
            except Exception as log_error:
                print(f"⚠️ Could not log duplicate: {log_error}")
            return True
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
    # Get current IST time for logging
    ist = timezone(timedelta(hours=5, minutes=30))
    current_time_ist = datetime.now(ist)
    print(f"🕐 Current IST time: {current_time_ist.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get the next tweet to post
    tweet_to_post, tweet_index, day, fact = get_next_tweet()
    
    # Post the tweet
    success = post_tweet(tweet_to_post, tweet_index, day, fact)
    
    if success:
        print(f"🎉 Day {day} Fact {fact} posted successfully!")
        
        # Show what's next
        next_index = tweet_index + 1
        if next_index < len(all_tweets):
            next_day = (next_index // 2) + 1
            next_fact = (next_index % 2) + 1
            print(f"⏭️ Next scheduled: Day {next_day} Fact {next_fact}")
        else:
            print("🏁 Next run will complete the cycle!")
            
    else:
        print("💥 Bot execution failed")
    
    print("🏁 Bot finished")
