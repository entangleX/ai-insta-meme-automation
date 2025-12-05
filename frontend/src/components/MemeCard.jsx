export default function MemeCard({ image, caption, onPublish, publishing }) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        padding: "12px",
        borderRadius: "8px",
        maxWidth: 360,
      }}
    >
      <img src={image} alt={caption} style={{ width: "100%" }} />
      <p style={{ marginTop: 8 }}>{caption}</p>
      <button onClick={onPublish} disabled={publishing} style={{ marginTop: 8 }}>
        {publishing ? "Publishing..." : "Publish to Instagram"}
      </button>
    </div>
  );
}
