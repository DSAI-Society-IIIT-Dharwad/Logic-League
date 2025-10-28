import React, { useEffect, useState } from "react";
import "./App.css";

export default function Dashboard() {
  const [trends, setTrends] = useState([]);
  const [sentiment, setSentiment] = useState({
    positive: 0,
    negative: 0,
    neutral: 0,
  });
  const [forecast, setForecast] = useState([]);
  const [query, setQuery] = useState("");
  const [chatResponses, setChatResponses] = useState([]);
  const [loading, setLoading] = useState(false);

  // ✅ Backend base URL — confirm backend is on this port
  const BASE_URL = "http://127.0.0.1:8000/api";

  // 🔹 Fetch all data
  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, 30000); // Refresh every 30 seconds
    return () => clearInterval(id);
  }, []);

  async function fetchAll() {
    setLoading(true);
    try {
      const [tRes, sRes, fRes] = await Promise.all([
        fetch(`${BASE_URL}/trends`).then((r) => r.json()),
        fetch(`${BASE_URL}/sentiment`).then((r) => r.json()),
        fetch(`${BASE_URL}/forecast`).then((r) => r.json()),
      ]);

      // 🧩 Fix: Always return arrays safely
      setTrends(Array.isArray(tRes) ? tRes : []);
      setForecast(Array.isArray(fRes) ? fRes : []);

      // 🧩 Fix: Handle sentiment correctly
      if (Array.isArray(sRes) && sRes.length > 0) {
        // If your sentiment CSV has columns like positive, neutral, negative
        const s = sRes[0];
        setSentiment({
          positive: Number(s.positive || 0),
          neutral: Number(s.neutral || 0),
          negative: Number(s.negative || 0),
        });
      } else if (typeof sRes === "object") {
        setSentiment(sRes);
      }
    } catch (e) {
      console.error("Error fetching data:", e);
      setTrends([]);
      setForecast([]);
      setSentiment({ positive: 0, negative: 0, neutral: 0 });
    } finally {
      setLoading(false);
    }
  }

  // 🔹 Chatbot call
  async function sendChat() {
    if (!query.trim()) return;

    const userMessage = query.trim();
    setChatResponses((prev) => [...prev, { role: "user", text: userMessage }]);
    setQuery("");

    try {
      const response = await fetch(`${BASE_URL}/chatbot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage }),
      });

      if (!response.ok) throw new Error("Chatbot request failed");

      const data = await response.json();
      setChatResponses((prev) => [
        ...prev,
        { role: "bot", text: data.answer || "No response" },
      ]);
    } catch (e) {
      console.error(e);
      setChatResponses((prev) => [
        ...prev,
        { role: "bot", text: "⚠️ Error: could not connect to chatbot" },
      ]);
    }
  }

  // 🔹 UI
  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <header className="max-w-6xl mx-auto mb-6">
        <h1 className="text-3xl font-bold">
          Real-time Trends & Sentiment Dashboard
        </h1>
        <p className="text-sm text-gray-600">
          Live trends from Reddit — topics, sentiment, forecasts and an assistant.
        </p>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-3 gap-6">
        {/* 🔹 Trends */}
        <section className="col-span-2 bg-white p-4 rounded-lg shadow-sm">
          <h2 className="text-lg font-semibold mb-2">Top Trending Topics</h2>
          {loading && <div className="text-sm text-gray-500">Refreshing...</div>}

          {trends.length === 0 ? (
            <div className="text-sm text-gray-500">No trend data available.</div>
          ) : (
            <ul>
              {trends.slice(0, 10).map((t, i) => (
                <li
                  key={i}
                  className="p-2 border-b flex justify-between items-center"
                >
                  <div>
                    <div className="font-medium">{t.topic || t.Keyword}</div>
                    <div className="text-xs text-gray-500">
                      mentions: {t.count || t.Mentions} • change:{" "}
                      {t.change_pct || t.Change || 0}%
                    </div>
                  </div>
                  <div className="text-sm text-gray-700">
                    sentiment: {t.sentiment || "—"}
                  </div>
                </li>
              ))}
            </ul>
          )}

          {/* 🔹 Forecast */}
          <div className="mt-4">
            <h3 className="font-medium">Forecast (next 30 days)</h3>
            <div className="mt-2 h-40 bg-gray-50 rounded p-2 overflow-auto">
              {forecast.length === 0 ? (
                <div className="text-sm text-gray-500">No forecast data</div>
              ) : (
                <svg
                  viewBox={`0 0 ${Math.max(300, forecast.length * 10)} 120`}
                  className="w-full h-full"
                >
                  {forecast.map((pt, idx) => {
                    const maxY = Math.max(...forecast.map((f) => f.yhat || 0));
                    const y =
                      100 -
                      Math.min(
                        100,
                        Math.max(0, (pt.yhat / (maxY || 1)) * 100)
                      );
                    const x = (idx / (forecast.length - 1 || 1)) * 100;
                    return (
                      <circle
                        key={idx}
                        cx={`${x}%`}
                        cy={`${y}%`}
                        r="2"
                        fill="#2563eb"
                      />
                    );
                  })}
                </svg>
              )}
            </div>
          </div>
        </section>

        {/* 🔹 Sentiment */}
        <aside className="bg-white p-4 rounded-lg shadow-sm">
          <h2 className="text-lg font-semibold mb-2">Sentiment Gauge</h2>

          <div className="mb-4">
            <div className="text-sm text-gray-600">Positive</div>
            <div className="text-2xl font-bold text-green-600">
              {Math.round((sentiment.positive || 0) * 100)}%
            </div>
          </div>
          <div className="mb-4">
            <div className="text-sm text-gray-600">Neutral</div>
            <div className="text-2xl font-bold text-gray-600">
              {Math.round((sentiment.neutral || 0) * 100)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Negative</div>
            <div className="text-2xl font-bold text-red-600">
              {Math.round((sentiment.negative || 0) * 100)}%
            </div>
          </div>

          <div className="mt-6">
            <h3 className="font-medium">Word Cloud (top tokens)</h3>
            <div className="mt-2 text-sm text-gray-500">(Top tokens shown)</div>
            <ul className="mt-2">
              {trends.slice(0, 8).map((t, i) => (
                <li
                  key={i}
                  className="inline-block mr-2 mb-1 px-2 py-1 bg-gray-100 rounded"
                >
                  {Array.isArray(t.top_terms)
                    ? t.top_terms.slice(0, 5).join(", ")
                    : ""}
                </li>
              ))}
            </ul>
          </div>
        </aside>

        {/* 🔹 Chatbot */}
        <section className="col-span-3 bg-white p-4 rounded-lg shadow-sm mt-2">
          <h2 className="text-lg font-semibold mb-2">Chatbot</h2>
          <div className="border rounded p-2 h-64 overflow-auto mb-2 bg-gray-50">
            {chatResponses.map((c, i) => (
              <div
                key={i}
                className={`mb-2 ${c.role === "user" ? "text-right" : "text-left"}`}
              >
                <div
                  className={`${
                    c.role === "user"
                      ? "inline-block bg-blue-500 text-white"
                      : "inline-block bg-gray-200 text-gray-900"
                  } p-2 rounded max-w-[80%]`}
                >
                  {c.text}
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 border p-2 rounded"
              placeholder="Ask about trends, e.g. 'What's trending in tech?'"
            />
            <button
              onClick={sendChat}
              className="px-4 py-2 bg-blue-600 text-white rounded"
            >
              Send
            </button>
          </div>
        </section>
      </main>

      <footer className="max-w-6xl mx-auto mt-6 text-sm text-gray-500">
        Live updates • Data refresh every 30s
      </footer>
    </div>
  );
}
