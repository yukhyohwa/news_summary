# News Summary

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

`news-digest` is a standalone global news aggregation and reporting tool. It is responsible only for the news workflow that was previously part of the combined `news-market-digest` application:

- Fetching articles from configurable RSS feeds
- Filtering articles by date and blocked keywords
- Translating article titles and summaries
- Deduplicating and merging similar stories
- Categorizing stories with keyword rules
- Persisting articles in a dedicated SQLite database
- Rendering a Markdown news report
- Optionally delivering the report by email

Market data, fund monitoring, bond analysis, arbitrage scanners, and market reports belong to the separate [`market-digest`](https://github.com/yukhyohwa/market-digest) project and are not executed by this project.

## Features

### Multi-source RSS aggregation

RSS sources are configured in `config/settings.py`. The default configuration includes:

- MarketWatch / Dow Jones top stories
- Financial Times global economy

Additional RSS or Atom feeds can be added to the `RSS_FEEDS` list. The fetcher normalizes feed entries into a common article structure and continues processing when an individual source is unavailable.

### Date filtering and content filtering

The command-line `--days` option limits the input window. The pipeline then excludes entries matching `BLOCKED_KEYWORDS` in their title or summary. This keeps the report focused and prevents unwanted categories from reaching translation and rendering.

### Translation, deduplication, and categorization

The processing pipeline is intentionally ordered as follows:

1. Fetch raw entries from all configured feeds.
2. Filter entries by date and blocked terms.
3. Translate eligible titles and summaries to the configured target language.
4. Detect duplicate or closely related stories and merge them where possible.
5. Apply keyword-based category rules.
6. Save the resulting unique articles to SQLite.
7. Render a category-based Markdown report.

Categories are maintained in `config/categories.json`. The renderer also supports an `Others` category for articles that do not match a configured rule.

### Historical storage

Articles are stored locally so that later runs can recognize previously seen stories and preserve a historical news record. The database is independent from the market project's database.

## Project structure

```text
news-digest/
├── main.py
├── app/
│   ├── __init__.py
│   └── core/
│       ├── __init__.py
│       ├── fetcher.py       # RSS/Atom feed retrieval and normalization
│       ├── processor.py     # Filtering, deduplication, merging, categorization
│       ├── translator.py    # Article title and summary translation
│       ├── renderer.py      # Markdown news report generation
│       ├── news_db.py       # SQLite schema and article persistence
│       └── mailer.py        # Optional SMTP report delivery
├── config/
│   ├── __init__.py
│   ├── settings.py          # Local feed, filter, translation, and mail settings
│   └── categories.json      # Category keyword definitions
├── data/
│   └── news_data.db         # News-only SQLite database
├── output/
│   └── News_Summary_YYYY-MM-DD.md
└── requirements.txt
```

## Requirements

- Windows, Linux, or macOS
- Python 3.11 or newer recommended
- Network access to the configured RSS feeds
- Network access to the translation service used by `deep-translator`
- Optional SMTP access when email delivery is enabled

The main dependencies are declared in `requirements.txt`, including `feedparser`, `deep-translator`, `tqdm`, `requests`, `beautifulsoup4`, `python-dotenv`, and Markdown/image-related utilities used by the application.

## Installation

From the project directory:

```bash
python -m pip install -r requirements.txt
```

Using a virtual environment is recommended:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

## Usage

Fetch the default one-day news window and generate a report:

```bash
python main.py
```

Fetch articles from the last three days:

```bash
python main.py --days 3
```

Send the generated report by email after successful generation:

```bash
python main.py --mail
```

The `--mail` option does not replace report generation; it runs the normal pipeline first and then attempts delivery.

Display available command-line options:

```bash
python main.py --help
```

## Configuration

### RSS feeds

Edit `config/settings.py`:

```python
RSS_FEEDS = [
    "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "https://www.ft.com/global-economy?format=rss",
]
```

### Blocked keywords

Add words or phrases to `BLOCKED_KEYWORDS` when stories containing those terms should be excluded. Matching is applied to the article title and summary.

### Translation language

`TARGET_LANGUAGE` controls the requested output language. The default is English:

```python
TARGET_LANGUAGE = "en"
```

### Category rules

Update `config/categories.json` to change category names and keyword mappings. Keep the file valid JSON after editing it. Unmatched stories are assigned to `Others`.

### Email delivery

Do not put passwords, app passwords, API keys, or tokens into source files. Configure email delivery with environment variables instead:

```text
NEWS_DIGEST_SENDER_EMAIL=[REDACTED]
NEWS_DIGEST_SENDER_PASSWORD=[REDACTED]
NEWS_DIGEST_RECEIVERS=recipient@example.com
```

For multiple recipients, separate addresses with commas:

```text
NEWS_DIGEST_RECEIVERS=one@example.com,two@example.com
```

The SMTP server and port are currently configured for Gmail SMTP over SSL. Adapt `SMTP_SERVER` and `SMTP_PORT` in `config/settings.py` if another provider is required.

## Data and generated files

- SQLite database: `data/news_data.db`
- Markdown reports: `output/News_Summary_YYYY-MM-DD.md`
- Optional images or supporting report assets: under `output/`

The news database must remain inside this project. `news-digest` must not read or write `market-digest/data/finance_data.db`.

## Troubleshooting

### No articles are returned

Check that:

1. The feed URL is reachable in a browser or with a normal HTTP request.
2. The source still exposes RSS or Atom XML.
3. The selected `--days` window is not too narrow.
4. The blocked keyword list is not filtering the entire result set.

### Translation fails or is slow

Translation depends on an external service. Retry with a stable network connection, reduce the number of days, and check whether the provider is temporarily rate-limiting requests.

### The report is generated but email is not sent

Confirm that all required `NEWS_DIGEST_*` variables are available to the same shell or Windows Task Scheduler account that runs Python. Never print or commit the password while debugging.

### Existing articles appear again

The database is the deduplication history. Do not delete `data/news_data.db` unless resetting the news history is intentional. Back it up before schema or data maintenance.

## Relationship with market-digest

The projects are intentionally separated:

| Responsibility | Project | Database |
|---|---|---|
| RSS news, translation, categorization, news reports | `news-digest` | `data/news_data.db` |
| Market data, funds, bonds, commodities, arbitrage, market reports | `market-digest` | `data/finance_data.db` |

Neither project should rely on the other project's SQLite file or import its news/market pipeline modules.

## Disclaimer

This software aggregates third-party content and produces informational summaries. RSS availability, article licensing, translation quality, and external data accuracy are not guaranteed. The output is for research and information purposes only and is not investment, legal, or financial advice.
