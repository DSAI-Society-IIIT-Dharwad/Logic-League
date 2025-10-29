# 🧠 Reddit Trend Analyzer

### 📊 Real-Time AI System for Public Sentiment & Trend Forecasting

A dynamic AI system that **analyzes Reddit posts in real-time**, detects **trending topics**, evaluates **public sentiment**, and **forecasts future trends** using AI.  
Built for **Inter Hackathon 2025**, this project demonstrates how social media insights can power decision-making in **finance**, **media**, and **policy** domains.

---

## 🚀 Features

- 🔥 **Top Trend Detection** — Finds trending Reddit topics automatically.  
- 💬 **Sentiment Analysis** — Classifies sentiment (positive / neutral / negative).  
- 📈 **Forecasting** — Predicts topic popularity for the next 30 days.  
- 🤖 **AI Chatbot Assistant** — Ask natural-language questions about trends and insights.  
- 🎨 **Modern React Dashboard** — Interactive frontend built with React + Tailwind CSS.  
- ⚙️ **FastAPI Backend** — Lightweight backend that serves insights to the frontend.  
- 🧹 **CSV-based Data Pipeline** — Reddit data cleaned, processed, and visualized.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React.js, Tailwind CSS |
| **Backend** | FastAPI (Python) |
| **Data Analysis** | Pandas, NLTK, spaCy, VADER, Prophet |
| **Visualization** | Recharts / Chart.js |
| **Chatbot** | OpenAI API / Local LLM |
| **Database** | CSV / Local File Storage |
| **Deployment** | Localhost / Streamlit / Vercel |

---

## ⚙️ Getting Started

### Step 1 — Clone the repository

### Step 2 - Generate API key from Groq API Key dashboard and add it to ```.env``` file in the backend folder.

### Step 3 — Backend setup (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Step 4 — Frontend setup (React)
```bash
cd frontend
npm install
npm start
```

## 📷 Dashboard Preview 

![Dashboard Preview](./frontend/public/Frontend%20UI-1.png)

![Dashboard Preview](./frontend/public/Frontend%20UI-2.png)
