export default function ApproveUploadBar({ total, onRegenerate, onPublishAll, publishingAll }) {
  return (
    <div
      style={{
        display: "flex",
        gap: "12px",
        alignItems: "center",
        padding: "12px",
        background: "#f7f7f7",
        borderRadius: "8px",
        marginBottom: "16px",
      }}
    >
      <span>{total} memes generated</span>
      <button onClick={onRegenerate}>Regenerate</button>
      <button onClick={onPublishAll} disabled={publishingAll}>
        {publishingAll ? "Publishing..." : "Publish All"}
      </button>
    </div>
  );
}
