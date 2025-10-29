import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [trends, setTrends] = useState([]);
  const [sentiment, setSentiment] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const BASE_URL = "http://127.0.0.1:8000";

  const fetchAll = async () => {
    try {
      const [tRes, sRes, fRes] = await Promise.all([
        fetch(`${BASE_URL}/api/trends`).then((r) => r.json()),
        fetch(`${BASE_URL}/api/sentiment`).then((r) => r.json()),
        fetch(`${BASE_URL}/api/forecast`).then((r) => r.json()),
      ]);

      setTrends(tRes);
      setSentiment(sRes);
      setForecast(fRes);
    } catch (err) {
      console.error("❌ API Error:", err);
    }
  };

  const askBot = async () => {
    if (!question.trim()) return;
    try {
      const res = await fetch(`${BASE_URL}/api/chatbot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setAnswer(data.answer || "No response from chatbot.");
    } catch (err) {
      setAnswer("Chatbot not reachable.");
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-indigo-100 to-purple-100 flex flex-col items-center py-10 px-4">
      {/* HEADER */}
      <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-700 via-purple-600 to-indigo-700 drop-shadow-md mb-10 text-center animate-pulse">
        Reddit Trend Analyzer 🚀
      </h1>

      <div className="grid gap-8 w-full max-w-5xl">
        {/* 🔥 Top Trends */}
        <div className="backdrop-blur-lg bg-white/40 border border-white/30 shadow-xl rounded-3xl p-6 hover:scale-[1.02] transition-all duration-300">
          <h2 className="text-2xl font-semibold text-blue-800 mb-4 flex items-center gap-2">
            <span>🔥</span> Top Reddit Trends
          </h2>
          {trends.length > 0 ? (
            <div className="flex flex-wrap gap-3">
              {trends.slice(0, 8).map((t, i) => (
                <span
                  key={i}
                  className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-4 py-2 rounded-full shadow-md hover:shadow-lg hover:scale-105 transition-all cursor-pointer"
                >
                  {t.Top_Keywords || "N/A"}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-gray-600 italic">Loading top trends...</p>
          )}
        </div>

        {/* 💬 Sentiment Summary */}
        <div className="backdrop-blur-lg bg-white/40 border border-white/30 shadow-xl rounded-3xl p-6 hover:scale-[1.02] transition-all duration-300">
          <h2 className="text-2xl font-semibold text-green-800 mb-4 flex items-center gap-2">
            <span>💬</span> Sentiment Summary
          </h2>
          {sentiment.length > 0 ? (
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 shadow-inner text-gray-700 max-h-60 overflow-y-auto text-sm">
              <pre>{JSON.stringify(sentiment[0], null, 2)}</pre>
            </div>
          ) : (
            <p className="text-gray-600 italic">No sentiment data available.</p>
          )}
        </div>

        {/* 📈 Forecast Visualization */}
        <div className="backdrop-blur-lg bg-white/40 border border-white/30 shadow-xl rounded-3xl p-6 hover:scale-[1.02] transition-all duration-300">
          <h2 className="text-2xl font-semibold text-purple-800 mb-4 flex items-center gap-2">
            <span>📈</span> Forecast (Next 30 Days)
          </h2>
          {forecast.length > 0 ? (
            <svg viewBox="0 0 300 100" className="w-full h-48">
              {forecast.map((pt, idx) => {
                const maxY = Math.max(...forecast.map((f) => f.yhat || 0));
                const y = 100 - (pt.yhat / (maxY || 1)) * 100;
                const x = (idx / (forecast.length - 1)) * 300;
                return (
                  <circle
                    key={idx}
                    cx={x}
                    cy={y}
                    r="3"
                    fill="url(#grad)"
                    className="drop-shadow-md"
                  />
                );
              })}
              <defs>
                <linearGradient id="grad" x1="0" x2="1" y1="0" y2="1">
                  <stop offset="0%" stopColor="#9333ea" />
                  <stop offset="100%" stopColor="#6366f1" />
                </linearGradient>
              </defs>
            </svg>
          ) : (
            <p className="text-gray-600 italic">No forecast data available.</p>
          )}
        </div>

        {/* 🤖 Chatbot Assistant */}
        <div className="backdrop-blur-lg bg-white/40 border border-white/30 shadow-xl rounded-3xl p-6 hover:scale-[1.02] transition-all duration-300">
          <h2 className="text-2xl font-semibold text-indigo-800 mb-4 flex items-center gap-2">
            <span>🤖</span> Ask the Data Assistant
          </h2>
          <div className="flex gap-3">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask something like: 'What are people talking about in tech?'"
              className="flex-1 border-2 border-indigo-300 focus:border-indigo-500 bg-white/60 p-3 rounded-xl text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-200 transition"
            />
            <button
              onClick={askBot}
              className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white px-6 py-2 rounded-xl shadow-md hover:shadow-lg transition"
            >
              Ask
            </button>
          </div>
          {answer && (
            <div className="mt-5 bg-white/70 border border-indigo-200 p-4 rounded-xl shadow-inner text-gray-800">
              <p className="font-medium">💡 Answer:</p>
              <p>{answer}</p>
            </div>
          )}
        </div>
      </div>

      <footer className="mt-10 text-gray-600 text-sm">
        Built with ❤️ using React + FastAPI + Tailwind CSS
      </footer>
    </div>
  );
}

export default App;
