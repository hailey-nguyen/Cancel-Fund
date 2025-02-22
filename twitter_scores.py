import pandas as pd

# ================================================
# 1. Manual Input of Tweet Volumes
# ================================================
# Input tweet volumes for company A,B,C
tweet_volumes = {
    "Delta": 880000,   
    "Bybit": 245000,    
    "Tesla": 300000
}

# ================================================
# 2. Calculate Average Volume
# ================================================
total_volume = sum(tweet_volumes.values())
average_volume = total_volume / len(tweet_volumes)
print(f"Average Volume = {average_volume:.1f}")

# ================================================
# 3. Calculate Relative Volume and Score
# ================================================
def calculate_score(relative_volume):
    # Apply the scoring scale
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

# Store the results
results = []

for company, volume in tweet_volumes.items():
    # Calculate Relative Volume
    relative_volume = (volume / average_volume) * 100
    
    # Get the Score
    score = calculate_score(relative_volume)
    
    # Append to Results
    results.append([company, relative_volume, score])

# ================================================
# 4. Convert to DataFrame
# ================================================
df = pd.DataFrame(results, columns=['Company', 'Relative Volume (%)', 'Score'])

# ================================================
# 5. Save to CSV (Overwrite Mode)
# ================================================
output_file = 'twitter_volume_scores.csv'

# Overwrite the CSV file
df.to_csv(output_file, index=False)
print(f"\nTwitter Volume Scores saved to {output_file} (overwritten).")

# Display Final Summary
print("\nTwitter Volume Scores:")
print(df)
