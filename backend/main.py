from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can later replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths
trends_file = "reddit_trends.csv"
sentiment_file = "reddit_sentiment_summary.csv"
forecast_file = "forecast_results.csv"

# Groq API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Chat model input
class Query(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "✅ Reddit Real-Time Trend API is running!"}

@app.get("/api/trends")
def get_trends():
    df = pd.read_csv(trends_file)
    return df.to_dict(orient="records")

@app.get("/api/sentiment")
def get_sentiment():
    df = pd.read_csv(sentiment_file)
    return df.to_dict(orient="records")

@app.get("/api/forecast")
def get_forecast():
    df = pd.read_csv(forecast_file)
    return df.to_dict(orient="records")

@app.post("/api/chatbot")
def chatbot(query: Query):
    user_question = query.question
    trends_df = pd.read_csv(trends_file)
    sentiment_df = pd.read_csv(sentiment_file)
    forecast_df = pd.read_csv(forecast_file)

    context = f"""
    Trends data sample: {trends_df.head(3).to_dict(orient='records')}
    Sentiment summary: {sentiment_df.head(3).to_dict(orient='records')}
    Forecast snapshot: {forecast_df.head(3).to_dict(orient='records')}
    """

    prompt = f"""
    You are a helpful Reddit data analyst.
    Based on this data, answer briefly and clearly.

    Data context:
    {context}

    Question:
    {user_question}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"answer": response.choices[0].message.content}

@app.get("/api/debug")
def debug_files():
    def info(path):
        if not os.path.exists(path):
            return {"exists": False}
        try:
            df = pd.read_csv(path)
            return {"exists": True, "rows": len(df), "columns": list(df.columns)}
        except Exception as e:
            return {"exists": True, "error": str(e)}

    return {
        "trends": info(trends_file),
        "sentiment": info(sentiment_file),
        "forecast": info(forecast_file)
    }
