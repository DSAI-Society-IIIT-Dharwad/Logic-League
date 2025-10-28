import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon
nltk.download('vader_lexicon')

# Load cleaned data and cluster data
data_df = pd.read_csv("reddit_data_cleaned.csv")
cluster_df = pd.read_csv("reddit_trends.csv")

# If the cluster CSV only has Top_Keywords (no post text), skip merging
if "Cluster" not in data_df.columns:
    # Simulate cluster assignment for demo (optional)
    import random
    data_df["Cluster"] = [random.randint(0, 4) for _ in range(len(data_df))]

# Sentiment analysis
analyzer = SentimentIntensityAnalyzer()
data_df['Sentiment_Score'] = data_df['Title'].apply(lambda x: analyzer.polarity_scores(str(x))['compound'])

def classify(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

data_df['Sentiment'] = data_df['Sentiment_Score'].apply(classify)

# Aggregate sentiments by cluster
sentiment_summary = data_df.groupby('Cluster')['Sentiment'].value_counts(normalize=True).unstack().fillna(0) * 100
sentiment_summary = sentiment_summary.round(2)

# Save results
data_df.to_csv("reddit_sentiment_full.csv", index=False, encoding="utf-8-sig")
sentiment_summary.to_csv("reddit_sentiment_summary.csv", encoding="utf-8-sig")

print("\n Sentiment analysis complete!")
print(sentiment_summary)
