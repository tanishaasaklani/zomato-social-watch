import feedparser
from google_play_scraper import reviews, Sort
from dotenv import load_dotenv
from zomato_classifier import classify_social_post
import feedparser
from google_play_scraper import reviews, Sort
from dotenv import load_dotenv
from zomato_classifier import classify_social_post
from email_utils import send_email_alert

load_dotenv()

def fetch_reddit_posts():
    return []


def fetch_playstore_reviews():
    posts = []

    try:
        result, _ = reviews(
            "com.application.zomato",
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=10
        )

        for review in result:
            posts.append({
                "source": "playstore",
                "text": review["content"],
                "author": review["userName"],
                "timestamp": str(review["at"])
            })

    except Exception as e:
        print(f"Play Store error: {e}")

    return posts

def fetch_rss_feeds():
    posts = []

    try:
        rss_urls = [
            "https://news.google.com/rss/search?q=zomato",
        ]

        for url in rss_urls:
            feed = feedparser.parse(url)

            for entry in feed.entries[:10]:
                posts.append({
                    "source": "rss",
                    "text": entry.title,
                    "author": getattr(entry, "author", "Unknown"),
                    "timestamp": getattr(entry, "published", "Unknown")
                })

    except Exception as e:
        print(f"RSS error: {e}")

    return posts

def get_all_posts():
    return (
        fetch_reddit_posts()
        + fetch_rss_feeds()
        + fetch_playstore_reviews()
    )

def already_processed(text):
    with open("processed_posts.txt", "a+", encoding="utf-8") as f:
        f.seek(0)
        seen = f.read().splitlines()

        if text in seen:
            return True

        f.write(text + "\n")
        return False
    

if __name__ == "__main__":
    all_posts = get_all_posts()

    print(f"\nFetched {len(all_posts)} posts.\n")

    for post in all_posts[:5]:

        if already_processed(post["text"]):
            continue
       
        print("=" * 80)
        print(f"SOURCE: {post['source']}")
        print(f"AUTHOR: {post['author']}")
        print(f"TIME: {post['timestamp']}")
        print(f"\nTEXT:\n{post['text']}\n")

#         test_post = """
# I ordered from Zomato yesterday and got severe food poisoning.
# Three people in my family are vomiting after eating.
# This is dangerous.
# """
        result = classify_social_post(post["text"])
        #result = classify_social_post(test_post)

        print("CLASSIFICATION:")
        print(result)

        # Send email only for HIGH priority cases
        if result["escalate"]:
            send_email_alert(
                subject="HIGH PRIORITY ZOMATO ALERT",
                body=post["text"]
                #body=test_post
            )

        print()