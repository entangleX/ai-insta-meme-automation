import { useEffect, useState } from "react";
import api from "../api/backend";

export default function MemeReviewPage() {
  const [dates, setDates] = useState([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [trends, setTrends] = useState([]);
  const [selectedTrend, setSelectedTrend] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [publishing, setPublishing] = useState(false);

  // Fetch available dates
  useEffect(() => {
    const fetchDates = async () => {
      try {
        const res = await api.get("/dates");
        setDates(res.data.dates || []);
        if (res.data.dates && res.data.dates.length > 0) {
          setSelectedDate(res.data.dates[0]);
        }
      } catch (err) {
        setError(err?.response?.data?.detail || err.message);
      }
    };
    fetchDates();
  }, []);

  // Fetch trends when date changes
  useEffect(() => {
    if (selectedDate) {
      fetchTrends(selectedDate);
    }
  }, [selectedDate]);

  const fetchTrends = async (date) => {
    setLoading(true);
    setError("");
    try {
      const res = await api.get(`/trends?date=${date}`);
      setTrends(res.data.trends || []);
      setSelectedTrend(null);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTrendSelect = async (trend) => {
    setLoading(true);
    setError("");
    try {
      const res = await api.get(`/trend?date=${selectedDate}&topic=${encodeURIComponent(trend.topic)}`);
      setSelectedTrend(res.data);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!selectedTrend) return;
    
    setPublishing(true);
    setError("");
    try {
      const res = await api.post("/publish", {
        date: selectedDate,
        topic: selectedTrend.topic,
        caption: selectedTrend.caption
      });
      alert(`Successfully published! Media ID: ${res.data.media_id}`);
      // Refresh trends to update status
      fetchTrends(selectedDate);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setPublishing(false);
    }
  };

  const getImageUrl = (trend) => {
    if (!trend || !trend.image_path) return null;
    // Extract topic from image path or use trend topic
    const topic = trend.topic;
    return `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/image/${selectedDate}/${encodeURIComponent(topic)}`;
  };

  return (
    <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>Meme Review & Publish</h1>

      {/* Date Selection */}
      <div style={{ marginBottom: "24px" }}>
        <label htmlFor="date-select" style={{ marginRight: "12px", fontWeight: "bold" }}>
          Select Date:
        </label>
        <select
          id="date-select"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          style={{ padding: "8px", fontSize: "16px", minWidth: "200px" }}
        >
          {dates.map((date) => (
            <option key={date} value={date}>
              {date}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div style={{ color: "red", marginBottom: "16px", padding: "12px", background: "#ffe6e6", borderRadius: "4px" }}>
          {error}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: "24px" }}>
        {/* Trends List */}
        <div style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "16px", maxHeight: "600px", overflowY: "auto" }}>
          <h2 style={{ marginTop: 0 }}>Topics</h2>
          {loading && <p>Loading...</p>}
          {!loading && trends.length === 0 && (
            <p style={{ color: "#666" }}>No trends found for this date. Generate memes first!</p>
          )}
          {trends.map((trend, idx) => (
            <div
              key={idx}
              onClick={() => handleTrendSelect(trend)}
              style={{
                padding: "12px",
                marginBottom: "8px",
                cursor: "pointer",
                borderRadius: "4px",
                background: selectedTrend?.topic === trend.topic ? "#e3f2fd" : "#f5f5f5",
                border: selectedTrend?.topic === trend.topic ? "2px solid #2196f3" : "1px solid #ddd",
                transition: "all 0.2s"
              }}
            >
              <div style={{ fontWeight: "bold", marginBottom: "4px" }}>{trend.topic}</div>
              <div style={{ fontSize: "12px", color: "#666" }}>{trend.category}</div>
              {trend.generated && (
                <div style={{ fontSize: "11px", color: "green", marginTop: "4px" }}>✓ Generated</div>
              )}
            </div>
          ))}
        </div>

        {/* Selected Trend Details */}
        <div style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "24px" }}>
          {!selectedTrend ? (
            <div style={{ textAlign: "center", color: "#666", padding: "40px" }}>
              Select a topic from the list to view details
            </div>
          ) : (
            <>
              <h2 style={{ marginTop: 0 }}>{selectedTrend.topic}</h2>
              
              <div style={{ marginBottom: "16px" }}>
                <strong>Category:</strong> {selectedTrend.category}
              </div>

              <div style={{ marginBottom: "16px" }}>
                <strong>Description:</strong>
                <p style={{ marginTop: "8px", lineHeight: "1.6" }}>{selectedTrend.description}</p>
              </div>

              {selectedTrend.caption && (
                <div style={{ marginBottom: "16px" }}>
                  <strong>Caption:</strong>
                  <p style={{ marginTop: "8px", fontStyle: "italic", color: "#555" }}>
                    {selectedTrend.caption}
                  </p>
                </div>
              )}

              {getImageUrl(selectedTrend) && (
                <div style={{ marginBottom: "24px" }}>
                  <img
                    src={getImageUrl(selectedTrend)}
                    alt={selectedTrend.topic}
                    style={{
                      maxWidth: "100%",
                      borderRadius: "8px",
                      border: "1px solid #ddd",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
                    }}
                  />
                </div>
              )}

              <button
                onClick={handlePublish}
                disabled={publishing || !getImageUrl(selectedTrend)}
                style={{
                  padding: "12px 24px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  background: publishing ? "#ccc" : "#2196f3",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: publishing || !getImageUrl(selectedTrend) ? "not-allowed" : "pointer",
                  width: "100%"
                }}
              >
                {publishing ? "Publishing..." : "Post to Instagram"}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
