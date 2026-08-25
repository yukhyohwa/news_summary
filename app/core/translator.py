from deep_translator import GoogleTranslator
from tqdm import tqdm
import time
import re
from config.settings import TARGET_LANGUAGE

def translate_articles(articles):
    """
    Translates article titles and summaries into target language (default: English).
    """
    print(f"\n[Stage 3/5] Starting translation to {TARGET_LANGUAGE}...")
    processed_articles = []
    
    # Initialize translator
    translator = GoogleTranslator(source='auto', target=TARGET_LANGUAGE)

    for article in tqdm(articles, desc="Translating"):
        new_article = article.copy()
        
        try:
            # Check Title: Translate if it has non-ASCII (Chinese/French accents) OR 
            # if we are targeting English and it looks like it might be French.
            # For simplicity, if Target is English and text is purely ASCII, we can often skip.
            title = article.get('title', '')
            should_translate = False
            
            if title:
                if TARGET_LANGUAGE == 'zh-CN':
                    # 如果目标语言是中文，且标题中包含英文字母，则进行翻译
                    if re.search(r'[a-zA-Z]', title):
                        should_translate = True
                else:
                    # If contains non-ASCII (Chinese, Accented characters like in French)
                    if any(ord(c) > 127 for c in title):
                        should_translate = True
                    # If target is English but source source_name is lefigaro (French), we should translate
                    elif TARGET_LANGUAGE == 'en' and article.get('source_name') == 'lefigaro':
                        should_translate = True
                
            if should_translate:
                new_article['translated_title'] = translator.translate(title)
            else:
                new_article['translated_title'] = title
            
            # Summary
            summary = article.get('summary', '')[:2000]
            if summary:
                # Same check for summary but we skip if already translated title was skipped
                if should_translate:
                    new_article['translated_summary'] = translator.translate(summary)
                else:
                    new_article['translated_summary'] = summary
            else:
                new_article['translated_summary'] = ""
            
            # Simple keyword-based topic key for merging
            clean_title = re.sub(r'[^\w\s]', '', new_article['translated_title'])
            new_article['topic_key'] = clean_title[:10].strip().lower()
            
            processed_articles.append(new_article)
            time.sleep(0.3) # Slightly reduced delay

        except Exception as e:
            print(f"\n[ERR] Translation error: {e}")
            new_article['translated_title'] = article.get('title', 'N/A')
            new_article['translated_summary'] = article.get('summary', '')
            new_article['topic_key'] = None
            processed_articles.append(new_article)
            time.sleep(1)

    return processed_articles
