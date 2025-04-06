import pandas as pd

# ================================================
# 1. Manual Input of Tweet Volumes
# ================================================
# Input raw tweet volume for each company
# These values represent the number of tweets for each company in a time period
tweet_volumes = {
    "Disney": 250000,   
    "23&me": 400000,    
    "Tesla": 320000
}

# ================================================
# 2. Calculate Average Volume
# ================================================
# Compute the average volume across all companies
# Formula: average_volume = (sum of all volumes) / number of companies
total_volume = sum(tweet_volumes.values())
average_volume = total_volume / len(tweet_volumes)

print(f"Average Volume = {average_volume:.1f}")

# ================================================
# 3. Calculate Relative Volume and Map to Score
# ================================================
# Function to assign a score based on relative volume (as a percentage of average)
# Scoring scale:
# > 200% of avg  → 10
# 150–200%       → 8
# 100–150%       → 6
# 50–100%        → 4
# < 50%          → 2
def calculate_score(relative_volume):
    if relative_volume > 200:
        return 10
    elif 150 <= relative_volume <= 200:
        return 8
    elif 100 <= relative_volume < 150:
        return 6
    elif 50 <= relative_volume < 100:
        return 4
    elif relative_volume < 50:
        return 2
    else:
        return 0

# ================================================
# 4. Calculate and Store Results
# ================================================
results = []

for company, volume in tweet_volumes.items():
    # Formula: relative_volume = (company_volume / average_volume) × 100
    relative_volume = (volume / average_volume) * 100
    
    # Determine score based on relative volume
    score = calculate_score(relative_volume)
    
    # Store results in list
    results.append([company, relative_volume, score])

# ================================================
# 5. Convert Results to DataFrame
# ================================================
df = pd.DataFrame(results, columns=['Company', 'Relative Volume (%)', 'Score'])

# ================================================
# 6. Save Output to CSV File (Overwrite Mode)
# ================================================
output_file = 'twitter_volume_scores.csv'

# Save DataFrame to CSV, overwriting existing file
df.to_csv(output_file, index=False)
print(f"\nTwitter Volume Scores saved to {output_file} (overwritten).")

# ================================================
# 7. Print Final Output
# ================================================
print("\nTwitter Volume Scores:")
print(df)


