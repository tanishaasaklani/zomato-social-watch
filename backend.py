import os
import json
from xpoz import XpozClient

import feedparser
from google_play_scraper import reviews, Sort
from dotenv import load_dotenv
from zomato_classifier import classify_social_post
from email_utils import send_email_alert

load_dotenv()

def fetch_reddit_posts():

    posts = []

    try:

        api_key = os.getenv("XPOZ_API_KEY")

        client = XpozClient(api_key)

        results = client.reddit.search_posts(
            "zomato",
            sort="new",
            time="month"
        )

        for post in results.data:

            title = getattr(post, "title", "")
            body = getattr(post, "selftext", "") or ""

            full_text = title
            if body:
                full_text += "\n" + body

            # Ignore empty posts
            if not full_text:
                continue

            # Ignore unrelated posts
            if "zomato" not in full_text.lower():
                continue

            posts.append({
                "source": "reddit",
                "text": full_text,
                "author": post.author_username,
                "timestamp": str(post.created_at_date)
            })

        client.close()

    except Exception as e:
        print(f"Reddit error: {e}")

    return posts



def fetch_x_posts():

    posts = []

    try:

        api_key = os.getenv("XPOZ_API_KEY")

        client = XpozClient(api_key)

        results = client.twitter.search_posts(
            "zomato",
            start_date="2026-06-01"
        )

        for post in results.data:

            posts.append({
                "source": "twitter",
                "text": post.text,
                "author": post.author_username,
                "timestamp": str(post.created_at)
            })

        client.close()

    except Exception as e:
        print(f"X/Twitter error: {e}")

    return posts

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
        + fetch_x_posts()
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
    


def save_classified_post(post, result):

    filename = "classified_posts.json"

    existing_posts = []

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                existing_posts = json.load(f)
            except:
                existing_posts = []

    existing_posts.append({
        "source": post["source"],
        "author": post["author"],
        "timestamp": post["timestamp"],
        "text": post["text"],
        "category": result["category"],
        "priority": result["priority"],
        "score": result["score"],
        "action": result["action"],
        "summary": result["summary"]
    })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_posts, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":

    all_posts = get_all_posts()

    print(f"\nFetched {len(all_posts)} posts.\n")

    new_posts_found = False

    for post in all_posts[:30]:

        if already_processed(post["text"]):
            continue

        new_posts_found = True

        print("=" * 80)
        print(f"SOURCE: {post['source']}")
        print(f"AUTHOR: {post['author']}")
        print(f"TIME: {post['timestamp']}")
        print(f"\nTEXT:\n{post['text']}\n")


        result = classify_social_post(post["text"])

        save_classified_post(post, result)

        print("CLASSIFICATION:")
        print(result)

        # Send email only for HIGH priority cases
        if result["escalate"]:
            send_email_alert(
                subject="HIGH PRIORITY ZOMATO ALERT",
                body=post["text"]
            )

        print()

    if not new_posts_found:
        print("\nNo new posts found.")
