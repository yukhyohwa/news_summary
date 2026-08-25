
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_NAME = 'news_data.db'
DB_PATH = os.path.join(DATA_DIR, DB_NAME)

def get_news_db_connection():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    return sqlite3.connect(DB_PATH)

def init_news_db():
    conn = get_news_db_connection()
    cursor = conn.cursor()
    
    # News Articles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT UNIQUE,          -- Unique link to prevent duplicates
            title TEXT,
            translated_title TEXT,
            summary TEXT,
            translated_summary TEXT,
            pub_date TEXT,
            category TEXT,
            source_name TEXT,
            source_link TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_news_articles(articles):
    """
    Saves new articles to the database.
    Skips duplicates based on the link.
    """
    if not articles:
        return

    init_news_db()
    conn = get_news_db_connection()
    cursor = conn.cursor()
    
    saved_count = 0
    for article in articles:
        # article format from pipeline
        # sources is a list of dicts, we take the first one for simplicity or join them
        source_name = article['sources'][0]['name'] if article.get('sources') else 'Unknown'
        source_link = article['sources'][0]['link'] if article.get('sources') else ''
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO news_articles 
                (link, title, translated_title, summary, translated_summary, pub_date, category, source_name, source_link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.get('link'),
                article.get('title'),
                article.get('translated_title'),
                article.get('summary'),
                article.get('translated_summary'),
                article.get('pub_date'),
                article.get('category', 'Others'),
                source_name,
                source_link
            ))
            if cursor.rowcount > 0:
                saved_count += 1
        except sqlite3.Error as e:
            print(f"Error saving article {article.get('link')}: {e}")
            
    conn.commit()
    conn.close()
    if saved_count > 0:
        print(f"[*] Saved {saved_count} new unique articles to news_data.db")
    return saved_count
