import os
import time
import argparse
from config.settings import RSS_FEEDS
from app.core.fetcher import fetch_all_feeds
from app.core.translator import translate_articles
from app.core.processor import (
    deduplicate_and_merge_articles,
    filter_articles,
    apply_keyword_categorization,
    load_categories,
)
from app.core.news_db import init_news_db, save_news_articles
from app.core.renderer import write_markdown_file
from app.core.mailer import send_report_email


def run_news_pipeline(days=1, start_date=None, end_date=None):
    """Fetch, filter, translate, deduplicate, categorize, and persist news."""
    print("\n>>> Running News Aggregation Task...")
    raw_articles = fetch_all_feeds(RSS_FEEDS)
    if not raw_articles:
        return {}
    filtered = filter_articles(raw_articles, days=days, start_date=start_date, end_date=end_date)
    if not filtered:
        return {}
    translated = translate_articles(filtered)
    unique = deduplicate_and_merge_articles(translated)
    categorized_data = apply_keyword_categorization(unique)
    save_news_articles(categorized_data)

    keyword_map = load_categories()
    categorized = {cat: [] for cat in keyword_map.keys()}
    categorized.setdefault("Others", [])
    for article in categorized_data:
        category = article.get("category", "Others")
        categorized.setdefault(category, []).append(article)
    return categorized


def main():
    parser = argparse.ArgumentParser(description="News RSS Digest")
    parser.add_argument("--days", type=int, default=1, help="Fetch news from the last N days")
    parser.add_argument("--mail", action="store_true", help="Send the generated report by email")
    args = parser.parse_args()

    start_time = time.time()
    print("===========================================")
    print("=== Global News Digest ===")
    print("===========================================")
    init_news_db()
    categorized_news = run_news_pipeline(days=args.days)
    report_path = write_markdown_file(categorized_news)
    if report_path:
        print(f"[OK] Report generated: {report_path}")
        if args.mail:
            if not os.getenv("NEWS_DIGEST_SENDER_PASSWORD"):
                print("[WARN] NEWS_DIGEST_SENDER_PASSWORD is not set; email was not sent.")
            else:
                send_report_email(report_path)
                print("[SUCCESS] Email sent successfully.")
    else:
        print("[FAIL] Failed to generate report.")
    print(f"\nTotal Time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
