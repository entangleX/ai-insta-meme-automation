import { useEffect, useState, useCallback } from "react";
import api from "../api/backend";
import MemeCard from "../components/MemeCard";
import ApproveUploadBar from "../components/ApproveUploadBar";

export default function MemeDashboard() {
  const [memes, setMemes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [publishingId, setPublishingId] = useState("");
  const [publishingAll, setPublishingAll] = useState(false);

  const fetchMemes = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.post("/generate_memes");
      if (res.data.status === "success") {
        alert(`Generated ${res.data.generated_images}/${res.data.total_trends} memes for ${res.data.date}`);
        // Redirect to review page
        window.location.href = "/review";
      } else {
        setError(res.data.message || "Generation failed");
      }
    } catch (err) {
      console.error("Error generating memes:", err);
      const errorMsg = err?.response?.data?.detail || err?.response?.data?.message || err.message || "Network Error";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMemes();
  }, [fetchMemes]);

  const handlePublish = async (image, caption) => {
    setPublishingId(image);
    setError("");
    try {
      await api.post("/publish", { image_url: image, caption });
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setPublishingId("");
    }
  };

  const handlePublishAll = async () => {
    setPublishingAll(true);
    setError("");
    try {
      for (const item of memes) {
        for (let i = 0; i < item.images.length; i++) {
          const image = item.images[i];
          const caption = item.captions[i];
          await api.post("/publish", { image_url: image, caption });
        }
      }
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setPublishingAll(false);
    }
  };

  return (
    <div>
      <h1>Meme Generator Dashboard</h1>
      <ApproveUploadBar
        total={memes.reduce((sum, m) => sum + m.images.length, 0)}
        onRegenerate={fetchMemes}
        onPublishAll={handlePublishAll}
        publishingAll={publishingAll}
      />
      {loading && <p>Loading memes...</p>}
      {error && (
        <div style={{ color: "red", padding: "12px", background: "#ffe6e6", borderRadius: "4px", marginBottom: "16px" }}>
          <strong>Error:</strong> {error}
        </div>
      )}
      {memes.map((item, idx) => (
        <div key={idx} style={{ marginBottom: "24px" }}>
          <h2>Topic: {item.topic}</h2>
          <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
            {item.images.map((img, i) => (
              <MemeCard
                key={`${img}-${i}`}
                image={img}
                caption={item.captions[i]}
                publishing={publishingId === img}
                onPublish={() => handlePublish(img, item.captions[i])}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
