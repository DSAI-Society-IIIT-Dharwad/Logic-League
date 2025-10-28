import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
from datetime import datetime

# =============================
# Load Cleaned Data
# =============================
try:
    df = pd.read_csv("reddit_data_cleaned.csv", encoding="utf-8")
except Exception:
    df = pd.read_csv("reddit_data_cleaned.csv", encoding="latin-1")

# Check what columns exist
print("Columns in CSV:", df.columns.tolist())

# Normalize column names
df.columns = [c.strip().lower() for c in df.columns]

# Ensure we have a title/text column
if "title_cleaned" in df.columns:
    text_col = "title_cleaned"
elif "title" in df.columns:
    text_col = "title"
else:
    raise KeyError("No suitable text column found (need 'Title' or 'Title_Cleaned').")

# Ensure we have timestamp
if "created_utc" not in df.columns:
    df["created_utc"] = datetime.now()

# Drop missing or short text
df = df.dropna(subset=[text_col])
df = df[df[text_col].str.len() > 10]

print(f"Loaded {len(df)} posts for trend analysis")

# =============================
# TF-IDF Vectorization
# =============================
tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
X = tfidf.fit_transform(df[text_col])

# =============================
# Clustering (KMeans)
# =============================
num_clusters = 5
km = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
km.fit(X)

df["Cluster"] = km.labels_

# =============================
# Extract Top Keywords Per Cluster
# =============================
terms = np.array(tfidf.get_feature_names_out())
cluster_keywords = {}

for i in range(num_clusters):
    cluster_center = km.cluster_centers_[i]
    top_indices = cluster_center.argsort()[-10:][::-1]
    top_terms = [terms[idx] for idx in top_indices]
    cluster_keywords[i] = top_terms

# =============================
# Identify Trending Terms by Frequency Over Time
# =============================
df["Created_UTC"] = pd.to_datetime(df["created_utc"])
df["Date"] = df["Created_UTC"].dt.date

# Flatten all terms per day
daily_keywords = {}
for day, texts in df.groupby("Date")[text_col]:
    words = " ".join(texts).split()
    common = [w for w, _ in Counter(words).most_common(10)]
    daily_keywords[day] = common

# =============================
# Save Results
# =============================
trends = []
for c, words in cluster_keywords.items():
    trends.append({"Cluster": c, "Top_Keywords": ", ".join(words)})

trend_df = pd.DataFrame(trends)
trend_df.to_csv("reddit_trends.csv", index=False, encoding="utf-8")

print("\n Top Trending Topics Detected ")
print(trend_df)

print("\n Daily Keyword Trends:")
for day, words in daily_keywords.items():
    print(f"{day}: {', '.join(words)}")

print("\n Trend data saved as reddit_trends.csv")
