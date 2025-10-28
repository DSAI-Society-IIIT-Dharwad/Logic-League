from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize app
app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths
trends_file = "reddit_trends.csv"
sentiment_file = "reddit_sentiment_summary.csv"
forecast_file = "forecast_results.csv"

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model for chatbot query
class Query(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "Reddit Real-Time Trend API is running 🚀"}

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

# Chatbot endpoint using Groq API
@app.post("/api/chatbot")
def chatbot(query: Query):
    user_question = query.question

    # Load CSV data
    trends_df = pd.read_csv(trends_file)
    sentiment_df = pd.read_csv(sentiment_file)
    forecast_df = pd.read_csv(forecast_file)

    # Build context for the model
    context = f"""
    Trends data sample: {trends_df.head(3).to_dict(orient='records')}
    Sentiment summary: {sentiment_df.head(3).to_dict(orient='records')}
    Forecast snapshot: {forecast_df.head(3).to_dict(orient='records')}
    """

    prompt = f"""
    You are a helpful data analyst assistant.
    Based on the data below, answer the question clearly in 2–3 sentences.

    Data context:
    {context}

    Question:
    {user_question}
    """

    # Send to Groq model
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # or "mixtral-8x7b-32768"
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.choices[0].message.content
    return {"answer": answer}

@app.get("/api/debug")
def debug_files():
    import os

    def file_info(path):
        if not os.path.exists(path):
            return {"exists": False, "error": "File not found"}
        try:
            df = pd.read_csv(path)
            return {
                "exists": True,
                "rows": len(df),
                "columns": list(df.columns),
                "sample": df.head(2).to_dict(orient="records")
            }
        except Exception as e:
            return {"exists": True, "error": str(e)}

    return {
        "trends": file_info(trends_file),
        "sentiment": file_info(sentiment_file),
        "forecast": file_info(forecast_file)
    }
