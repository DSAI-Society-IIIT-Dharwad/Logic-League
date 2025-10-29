# reddit_forecast.py
# Phase 5: Forecasting Trend Evolution (with saved plot)

import pandas as pd
import re
from prophet import Prophet
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ===============================
# CONFIGURATION
# ===============================
DATA_FILE = "reddit_data_cleaned.csv"  # cleaned file from previous phase
TOPIC_KEYWORDS = ["openai", "microsoft", "chatgpt"]  # keywords to forecast
FORECAST_DAYS = 30
OUTPUT_CSV = "forecast_results.csv"
OUTPUT_PLOT = "forecast_plot.png"

# ===============================
# LOAD DATA
# ===============================
print(" Loading cleaned Reddit data...")
df = pd.read_csv(DATA_FILE, encoding="utf-8")

# Try to find text column dynamically
text_col = None
for col in df.columns:
    if "clean" in col.lower() or "text" in col.lower() or "title" in col.lower():
        text_col = col
        break

if not text_col:
    raise ValueError("No text column found. Please ensure cleaned text column exists.")

print(f" Using text column: {text_col}")

# ===============================
# FILTER DATA BY TOPIC KEYWORDS
# ===============================
pattern = "|".join(TOPIC_KEYWORDS)
print(f" Filtering posts containing any of: {TOPIC_KEYWORDS}")

topic_df = df[df[text_col].str.contains(pattern, case=False, na=False)]
if topic_df.empty:
    raise ValueError("No matching posts found for the given keywords.")

# Ensure datetime format
topic_df["Created_UTC"] = pd.to_datetime(topic_df["Created_UTC"], errors="coerce")
topic_df = topic_df.dropna(subset=["Created_UTC"])

# ===============================
# GROUP BY DATE (POST COUNTS)
# ===============================
daily_counts = (
    topic_df.groupby(topic_df["Created_UTC"].dt.date)
    .size()
    .reset_index(name="y")
)
daily_counts.rename(columns={"Created_UTC": "ds"}, inplace=True)
print(f" Time series prepared with {len(daily_counts)} data points")

# ===============================
# TRAIN PROPHET MODEL
# ===============================
print("Training Prophet model...")
model = Prophet(
    daily_seasonality=True,
    weekly_seasonality=True,
    yearly_seasonality=False
)
model.fit(daily_counts)

# Create future dataframe for forecasting
future = model.make_future_dataframe(periods=FORECAST_DAYS)
forecast = model.predict(future)

# ===============================
# SAVE FORECAST & PLOT
# ===============================
forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_csv(OUTPUT_CSV, index=False)

print(" Forecast complete! Generating and saving plot...")

fig = model.plot(forecast)
plt.title("Forecasted Trend of Topics: " + ", ".join(TOPIC_KEYWORDS))
plt.xlabel("Date")
plt.ylabel("Predicted Mentions")

# Save the plot
plt.savefig(OUTPUT_PLOT, format="png", dpi=300, bbox_inches="tight")
plt.show()

print("\n Forecasting complete!")
print(f"Results saved to: {OUTPUT_CSV}")
print(f"Plot saved to: {OUTPUT_PLOT}")
