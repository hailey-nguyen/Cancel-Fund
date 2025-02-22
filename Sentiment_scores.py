import feedparser
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import os

# ================================================
# 1. Initialize VADER Sentiment Analyzer
# ================================================
analyzer = SentimentIntensityAnalyzer()

# Function to Analyze Sentiment
def analyze_sentiment(text):
    sentiment = analyzer.polarity_scores(text)
    compound = sentiment['compound']
    # Classify sentiment based on compound score
    if compound >= 0.05:
        classification = 'Positive'
    elif compound <= -0.05:
        classification = 'Negative'
    else:
        classification = 'Neutral'
    return compound, classification

# ================================================
# 2. Companies to Analyze (Using Yahoo Finance and CNBC)
# ================================================
'''
CHANGE ME
'''

companies = {
    "Tesla": "TSLA",
    "Delta Airlines": "DAL",
    "Bybit": "Bybit"
    
}

# ==================================================
max_headlines = 100  # Maximum headlines per company per source
delay_between_requests = 3  # 3 seconds delay between requests

# DataFrame to Store All Results
all_data = pd.DataFrame(columns=['Company', 'Sentiment Score', 'Sentiment'])

# ================================================
# 3. Function to Scrape RSS Feeds
# ================================================
def scrape_rss(url, max_headlines=100):
    feed = feedparser.parse(url)
    headlines = []
    for entry in feed.entries:
        headlines.append({
            'title': entry.title
        })
        if len(headlines) >= max_headlines:
            break
    
    print(f"Found {len(headlines)} headlines from {url}")
    return headlines

# ================================================
# 4. Collect Data for All Companies
# ================================================
for company, symbol in companies.items():
    print(f"\nScraping news for {company} ({symbol})...")

    # 4.1 Yahoo Finance (US)
    yahoo_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    headlines = scrape_rss(yahoo_url, max_headlines)
    company_data = []
    for headline in headlines:
        title = headline['title']
        sentiment_score, sentiment = analyze_sentiment(title)
        company_data.append([company, sentiment_score, sentiment])

    # 4.2 CNBC
    cnbc_url = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    headlines = scrape_rss(cnbc_url, max_headlines)
    for headline in headlines:
        title = headline['title']
        sentiment_score, sentiment = analyze_sentiment(title)
        company_data.append([company, sentiment_score, sentiment])

    # Combine All Data for Company
    df = pd.DataFrame(company_data, columns=['Company', 'Sentiment Score', 'Sentiment'])
    all_data = pd.concat([all_data, df], ignore_index=True)

# ================================================
# 5. Calculate Sentiment Summary for Each Company
# ================================================
summary_data = []

for company in companies.keys():
    company_df = all_data[all_data['Company'] == company]
    
    # Count Sentiments
    positive_count = company_df['Sentiment'].value_counts().get('Positive', 0)
    negative_count = company_df['Sentiment'].value_counts().get('Negative', 0)
    neutral_count = company_df['Sentiment'].value_counts().get('Neutral', 0)
    
    # Calculate Overall Sentiment Score (Average of Compound Scores)
    overall_sentiment_score = company_df['Sentiment Score'].mean() if not company_df.empty else 0
    
    # Append to Summary Data
    summary_data.append([company, positive_count, negative_count, neutral_count, overall_sentiment_score])

# Convert to DataFrame
summary_df = pd.DataFrame(summary_data, columns=[
    'Company', 'Positive Count', 'Negative Count', 'Neutral Count', 'Overall Sentiment Score'
])

# ================================================
# 6. Save Sentiment Summary to CSV (Overwrite Mode)
# ================================================
output_file = 'sentiment_summary.csv'

# Overwrite the CSV file with sentiment summary
summary_df.to_csv(output_file, index=False)
print(f"\nSentiment summary saved to {output_file} (overwritten).")

# Display Final Summary
print("\nSentiment Summary:")
print(summary_df)
