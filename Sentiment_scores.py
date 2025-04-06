import feedparser
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import os

# ================================================
# 1. Initialize VADER Sentiment Analyzer
# ================================================
analyzer = SentimentIntensityAnalyzer()

# Function to Analyze Sentiment of a given text headline
def analyze_sentiment(text):
    sentiment = analyzer.polarity_scores(text)
    compound = sentiment['compound']  # Normalized score from -1 (negative) to +1 (positive)

    # Classification based on VADER thresholds:
    # compound ≥ 0.05  → Positive
    # compound ≤ -0.05 → Negative
    # otherwise        → Neutral
    if compound >= 0.05:
        classification = 'Positive'
    elif compound <= -0.05:
        classification = 'Negative'
    else:
        classification = 'Neutral'
    
    return compound, classification  # Return both score and label

# ================================================
# 2. Companies to Analyze (Using Yahoo Finance and CNBC)
# ================================================
# Dictionary format: {Company Name: Stock Ticker}
# These tickers are used to build the RSS URL for Yahoo Finance
companies = {
    "Tesla": "TSLA",
    "23&Me": "ME",
    "Disney": "DIS"
}

# ================================================
# 3. Configuration Parameters
# ================================================
max_headlines = 100           # Max headlines to retrieve per company per news source
delay_between_requests = 3    # Seconds to wait between scraping calls

# Initialize DataFrame to hold all headline-level sentiment results
all_data = pd.DataFrame(columns=['Company', 'Sentiment Score', 'Sentiment'])

# ================================================
# 4. RSS Scraping Function
# ================================================
def scrape_rss(url, max_headlines=100):
    feed = feedparser.parse(url)
    headlines = []

    # Extract headline titles (article titles) only
    for entry in feed.entries:
        headlines.append({'title': entry.title})
        if len(headlines) >= max_headlines:
            break

    print(f"Found {len(headlines)} headlines from {url}")
    return headlines

# ================================================
# 5. Collect and Analyze News Headlines for Each Company
# ================================================
for company, symbol in companies.items():
    print(f"\nScraping news for {company} ({symbol})...")

    company_data = []  # Store sentiment for this company

    # --- 5.1 Yahoo Finance RSS Feed ---
    yahoo_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    headlines = scrape_rss(yahoo_url, max_headlines)
    for headline in headlines:
        title = headline['title']
        sentiment_score, sentiment = analyze_sentiment(title)
        company_data.append([company, sentiment_score, sentiment])

    # --- 5.2 CNBC RSS Feed (general feed, not company-specific) ---
    cnbc_url = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    headlines = scrape_rss(cnbc_url, max_headlines)
    for headline in headlines:
        title = headline['title']
        sentiment_score, sentiment = analyze_sentiment(title)
        company_data.append([company, sentiment_score, sentiment])

    # Append this company's data to the master DataFrame
    df = pd.DataFrame(company_data, columns=['Company', 'Sentiment Score', 'Sentiment'])
    all_data = pd.concat([all_data, df], ignore_index=True)

# ================================================
# 6. Calculate Sentiment Summary Statistics
# ================================================
summary_data = []

# For each company, calculate:
# - Number of positive/negative/neutral articles
# - Average (mean) compound sentiment score
for company in companies.keys():
    company_df = all_data[all_data['Company'] == company]

    # Count article sentiment classifications
    positive_count = company_df['Sentiment'].value_counts().get('Positive', 0)
    negative_count = company_df['Sentiment'].value_counts().get('Negative', 0)
    neutral_count = company_df['Sentiment'].value_counts().get('Neutral', 0)

    # Compute average sentiment score
    # Formula: sentiment_avg = sum(compound_scores) / total_headlines
    overall_sentiment_score = company_df['Sentiment Score'].mean() if not company_df.empty else 0

    # Append company summary row
    summary_data.append([
        company,
        positive_count,
        negative_count,
        neutral_count,
        overall_sentiment_score
    ])

# Convert summary results into a clean DataFrame
summary_df = pd.DataFrame(summary_data, columns=[
    'Company', 'Positive Count', 'Negative Count', 'Neutral Count', 'Overall Sentiment Score'
])

# ================================================
# 7. Export Summary to CSV
# ================================================
output_file = 'sentiment_summary.csv'

# Overwrite CSV file with fresh results
summary_df.to_csv(output_file, index=False)

print(f"\nSentiment summary saved to {output_file} (overwritten).")

# ================================================
# 8. Final Console Output
# ================================================
print("\nSentiment Summary:")
print(summary_df)

