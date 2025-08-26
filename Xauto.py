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

# --- Determine which tweet to post based on current time ---
def determine_next_tweet():
    # Get current time in IST
    ist = timezone(timedelta(hours=5, minutes=30))
    current_time_ist = datetime.now(ist)
    current_hour = current_time_ist.hour
    
    print(f"🕐 Current IST time: {current_time_ist.strftime('%H:%M:%S')}")
    
    # Determine if this is morning (9:17 AM - Fact1) or evening (9:17 PM - Fact2) run
    is_morning_run = current_hour < 12  # Morning run if before noon
    
    # Find which day we're on based on posted tweets
    posted_count = len(posted_tweets_content)
    
    # Each day has 2 facts, so:
    # Day 1: tweets 0,1 (Fact1, Fact2)
    # Day 2: tweets 2,3 (Fact1, Fact2)
    # Day 3: tweets 4,5 (Fact1, Fact2) - current day based on posted_tweets.txt
    
    current_day = (posted_count // 2) + 1
    
    if is_morning_run:
        # Morning: post Fact1 of current day
        tweet_index = (current_day - 1) * 2  # First fact of the day
        fact_type = "Fact1"
    else:
        # Evening: post Fact2 of current day
        tweet_index = (current_day - 1) * 2 + 1  # Second fact of the day
        fact_type = "Fact2"
    
    # Handle case where we've posted all tweets (cycle complete)
    if tweet_index >= len(all_tweets):
        # Start over from Day 1
        current_day = 1
        if is_morning_run:
            tweet_index = 0  # Day 1 Fact1
            fact_type = "Fact1"
        else:
            tweet_index = 1  # Day 1 Fact2
            fact_type = "Fact2"
        
        print("🔄 Cycle complete! Starting fresh from Day 1")
        # Clear posted tweets log
        try:
            with open(POSTED_TWEETS_FILE, "w", encoding="utf-8") as f:
                f.write("")
            print("✅ Cleared posted tweets log")
        except Exception as e:
            print(f"⚠️ Could not clear posted tweets log: {e}")
    
    tweet_to_post = all_tweets[tweet_index]
    
    print(f"📋 Day {current_day} {fact_type} (Tweet #{tweet_index + 1})")
    print(f"📝 Tweet to post: {tweet_to_post[:60]}...")
    print(f"📊 Progress: {posted_count}/{len(all_tweets)} tweets posted")
    
    return tweet_to_post, tweet_index, current_day, fact_type

# --- Check if tweet was already posted ---
def is_already_posted(tweet_content):
    for posted_line in posted_tweets_content:
        if tweet_content in posted_line:
            return True
    return False

# --- Post the tweet ---
def post_tweet(tweet_content, tweet_index, day, fact_type):
    if is_already_posted(tweet_content):
        print(f"⚠️ Day {day} {fact_type} already posted, skipping...")
        return True
    
    print(f"📤 Posting Day {day} {fact_type}: {tweet_content}")
    
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
            print(f"✅ Logged Day {day} {fact_type}")
            
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
    # Determine what to post
    tweet_to_post, tweet_index, day, fact_type = determine_next_tweet()
    
    # Post the tweet
    success = post_tweet(tweet_to_post, tweet_index, day, fact_type)
    
    if success:
        print(f"🎉 Day {day} {fact_type} posted successfully!")
        
        # Calculate next tweet info
        next_posted_count = len(posted_tweets_content) + 1
        remaining_tweets = len(all_tweets) - next_posted_count
        
        if remaining_tweets > 0:
            next_day = ((next_posted_count) // 2) + 1
            next_fact = "Fact1" if (next_posted_count) % 2 == 0 else "Fact2"
            print(f"📊 Progress: {next_posted_count}/{len(all_tweets)} tweets posted")
            print(f"⏭️ Next scheduled: Day {next_day} {next_fact}")
        else:
            print("🏁 Cycle will be complete after next post!")
    else:
        print("💥 Bot execution failed")
    
    print("🏁 Bot finished")
