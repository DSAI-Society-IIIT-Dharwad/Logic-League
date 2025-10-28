# reddit_scraper_optimized.py
# ✅ Works without installing anything
# ✅ Automatically creates unique CSV files
# ✅ Better error handling with retries
# ✅ Keeps international text, removes only emojis
# ✅ More robust rate limit handling

import urllib.request
import urllib.error
import json
import csv
import re
import time
import unicodedata
from datetime import datetime, timezone

# ===============================
# CONFIGURATION
# ===============================
SUBREDDIT = "technology"    # Change to any subreddit (e.g., "worldnews", "datascience", etc.)
TOTAL_POSTS = 500           # Total number of posts to fetch
OUTPUT_FILE = f"reddit_data_{int(time.time())}.csv"  # Unique filename each run
MAX_RETRIES = 3             # Number of retries for failed requests
RETRY_DELAY = 60            # Seconds to wait after rate limit

# ===============================
# HELPER FUNCTIONS
# ===============================

def remove_emojis(text):
    """
    Remove emojis and control characters while keeping accented letters
    and international characters
    """
    cleaned = []
    for char in text:
        # Keep character if it's not:
        # - An emoji (category starts with 'S' for symbol, specific ranges)
        # - A control character (category 'Cc') except newline, tab, carriage return
        category = unicodedata.category(char)
        
        # Remove emojis (most are in 'So' - Symbol, other)
        if category == 'So':
            continue
        # Remove other control chars except whitespace
        if category == 'Cc' and char not in '\n\r\t':
            continue
            
        cleaned.append(char)
    
    return ''.join(cleaned)

def fetch_with_retry(url, headers, max_retries=MAX_RETRIES):
    """
    Fetch URL with automatic retry on rate limits
    """
    for attempt in range(max_retries):
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
                
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Too Many Requests
                wait_time = RETRY_DELAY * (attempt + 1)  # Exponential backoff
                print(f"   Rate limited. Waiting {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            elif e.code == 403:
                print(f"   Access forbidden (403). Reddit may have blocked the request.")
                return None
            elif e.code == 404:
                print(f"   Subreddit not found (404). Check the subreddit name.")
                return None
            else:
                print(f"   HTTP Error {e.code}: {e.reason}")
                return None
                
        except urllib.error.URLError as e:
            print(f"   Network error: {e.reason}")
            if attempt < max_retries - 1:
                print(f"   Retrying in 5 seconds...")
                time.sleep(5)
            else:
                return None
                
        except Exception as e:
            print(f"   Unexpected error: {e}")
            return None
    
    print(f"   Max retries exceeded.")
    return None

# ===============================
# SETUP
# ===============================
BASE_URL = f"https://www.reddit.com/r/{SUBREDDIT}/hot.json?limit=100"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; RedditScraper/3.0)"}
posts = []
after = None
fetched = 0

print(f"Fetching posts from r/{SUBREDDIT}...")
print(f"Target: {TOTAL_POSTS} posts\n")

# ===============================
# PAGINATED SCRAPING LOOP
# ===============================
page_num = 0

while fetched < TOTAL_POSTS:
    page_num += 1
    url = BASE_URL + (f"&after={after}" if after else "")
    
    print(f"Fetching page {page_num}... (collected: {fetched}/{TOTAL_POSTS})")
    
    data = fetch_with_retry(url, HEADERS)
    
    if not data:
        print("Failed to fetch data. Stopping.")
        break

    children = data.get("data", {}).get("children", [])
    
    if not children:
        print("No more posts available.")
        break

    for post in children:
        post_data = post["data"]
        
        # Extract and clean title
        title = post_data.get("title", "").strip()
        title = remove_emojis(title)
        title = re.sub(r"\s+", " ", title)  # Normalize whitespace
        
        # Extract other fields
        author = post_data.get("author", "")
        score = post_data.get("score", 0)
        comments = post_data.get("num_comments", 0)
        
        # Format timestamp
        created_utc = datetime.fromtimestamp(
            post_data["created_utc"], tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S")
        
        post_url = "https://www.reddit.com" + post_data.get("permalink", "")
        
        # Get post text/selftext if available
        selftext = post_data.get("selftext", "")
        if selftext:
            selftext = remove_emojis(selftext)
            selftext = re.sub(r"\s+", " ", selftext)[:500]  # Limit to 500 chars
        
        posts.append({
            "Title": title,
            "Author": author,
            "Score": score,
            "Comments": comments,
            "Created_UTC": created_utc,
            "Selftext": selftext,
            "URL": post_url
        })

        fetched += 1
        if fetched >= TOTAL_POSTS:
            break

    # Get pagination token
    after = data["data"].get("after")
    if not after:
        print("Reached end of available posts.")
        break

    # Polite delay between requests
    time.sleep(2)  # Increased to 2 seconds for safety

# ===============================
# SAVE TO CSV
# ===============================
if posts:
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["Title", "Author", "Score", "Comments", "Created_UTC", "Selftext", "URL"]
            )
            writer.writeheader()
            writer.writerows(posts)

        print(f"\n[SUCCESS]")
        print(f"Successfully scraped {len(posts)} posts from r/{SUBREDDIT}")
        print(f"Saved to file: {OUTPUT_FILE}")
        
        # Quick statistics
        total_score = sum(p['Score'] for p in posts)
        total_comments = sum(p['Comments'] for p in posts)
        avg_score = total_score / len(posts) if posts else 0
        avg_comments = total_comments / len(posts) if posts else 0
        
        print(f"\n[STATISTICS]")
        print(f"Average score: {avg_score:.1f}")
        print(f"Average comments: {avg_comments:.1f}")
        print(f"Top post: {max(posts, key=lambda x: x['Score'])['Title'][:60]}...")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to save CSV: {e}")
else:
    print("\n[ERROR] No posts found to save.")