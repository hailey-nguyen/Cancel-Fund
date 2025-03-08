import yfinance as yf
import pandas as pd
import openpyxl
import os

# ================================================
# 1. Input Section
# ================================================
stock_symbols = ['COIN', 'AAL', 'LUV', 'UAL', 'GM', 'VLKAF', 'BYDDY', 'TSLA', 'DAL']

rsi_scores = [35.5, 30.75, 37.43, 38.21, 35.42, 55.75, 81.67, 26.76, 29.17]
twitter_post_scores = [4, 8, 8, 8, 4, 4, 4, 4, 8]
sent_scores = [-0.118, -0.121, -0.121, -0.121, -0.0554, -0.0554, -0.0554, -0.0554, -0.121]

RSI_WEIGHT = 0.2
ANALYST_WEIGHT = 0.2
TWITTER_WEIGHT = 0.3  
SENTIMENT_WEIGHT = 0.3  
HOLDINGS_NUM = 4  
TOTAL_PORTFOLIO_ALLOCATION = 80  

# ================================================
# 2. Scoring Functions
# ================================================
def analyst_score(ar: str):
    ar = ar.lower()
    return {"strong_buy": 10, "buy": 7.5, "neutral": 5, "hold": 5, "sell": 2.5, "strong_sell": 0, "underperform": 0}.get(ar, 0)

def rsi_score(rsi: float):
    return 10 if rsi <= 30 else 8 if rsi <= 40 else 6 if rsi <= 50 else 4 if rsi <= 60 else 2 if rsi <= 70 else 0

def sentiment_score(sentiment: float):
    return 10 if sentiment < -0.5 else 8 if sentiment < -0.4 else 7 if sentiment < -0.3 else 6 if sentiment < -0.2 else 5 if sentiment < -0.1 else 4 if sentiment < 0 else 3 if sentiment < 0.1 else 2 if sentiment < 0.2 else 0

# ================================================
# 3. Get Data from Yahoo Finance using yfinance
# ================================================
def get_yfinance_data(stock_symbols):
    data = []
    for symbol in stock_symbols:
        print(f"Collecting data for {symbol}...")
        stock = yf.Ticker(symbol)
        rsi_index = stock_symbols.index(symbol)
        rsi = rsi_scores[rsi_index]
        try:
            analyst = stock.info['recommendationKey'].capitalize() if 'recommendationKey' in stock.info else "Neutral"
        except:
            analyst = "Neutral"
        data.append({'Symbol': symbol, 'RSI': rsi, 'Analyst Rating': analyst})
    return pd.DataFrame(data)

# ================================================
# 4. Main Script: Pull Data and Calculate Scores
# ================================================
df = get_yfinance_data(stock_symbols)

portfolio_data = []
for i, row in df.iterrows():
    symbol, rsi, analyst = row['Symbol'], row['RSI'], row['Analyst Rating']
    portfolio_data.append([
        symbol, rsi, analyst, rsi_score(rsi), analyst_score(analyst), 
        twitter_post_scores[i], sentiment_score(sent_scores[i]),
        (rsi_score(rsi) * RSI_WEIGHT + analyst_score(analyst) * ANALYST_WEIGHT + 
         twitter_post_scores[i] * TWITTER_WEIGHT + sentiment_score(sent_scores[i]) * SENTIMENT_WEIGHT)
    ])

df = pd.DataFrame(portfolio_data, columns=[
    'Symbol', 'RSI', 'Analyst Rating', 'RSI Score', 'Analyst Score', 
    'Twitter Post Score', 'Sentiment Score', 'Total Score'])

# ================================================
# 5. Split Data: Longs & Shorts
# ================================================
long_stocks = df[df['Symbol'].isin(stock_symbols[:7])].nlargest(HOLDINGS_NUM, 'Total Score')
short_stocks = df[df['Symbol'].isin(['TSLA', 'DAL', 'AAL'])]

total_scores = long_stocks['Total Score'].sum() + short_stocks['Total Score'].sum()
long_stocks['Weight'] = (long_stocks['Total Score'] / total_scores) * TOTAL_PORTFOLIO_ALLOCATION
short_stocks['Weight'] = (short_stocks['Total Score'] / total_scores) * TOTAL_PORTFOLIO_ALLOCATION * -1  # Display as negative

# ================================================
# 6. Overwrite Existing Excel File (Same Sheet, Two Tables)
# ================================================
output_file = "fund_holdings.xlsx"

# Delete file if corrupted
if os.path.exists(output_file):
    try:
        openpyxl.load_workbook(output_file)
    except:
        print("\n⚠️  Existing file is corrupted. Deleting and creating a new one.")
        os.remove(output_file)

# Write Long Positions first
with pd.ExcelWriter(output_file, mode='w', engine='openpyxl') as writer:
    long_stocks.to_excel(writer, sheet_name="Portfolio", index=False, startrow=0)

# Open Workbook and Add Separator
workbook = openpyxl.load_workbook(output_file)
worksheet = workbook["Portfolio"]
separator_row = worksheet.max_row + 2  # Leave one row blank
for col in range(1, worksheet.max_column + 1):
    worksheet.cell(row=separator_row, column=col, value="")  # Empty row
workbook.save(output_file)

# Append Short Positions After Separator
with pd.ExcelWriter(output_file, mode='a', engine='openpyxl', if_sheet_exists="overlay") as writer:
    short_stocks.to_excel(writer, sheet_name="Portfolio", index=False, startrow=separator_row)

print(f"\n✅ Portfolio saved to {output_file} (with long & short tables).")

# ================================================
# 7. Summary and Output
# ================================================
print("\nLong Positions:")
print(long_stocks)
print("\nShort Positions:")
print(short_stocks)
