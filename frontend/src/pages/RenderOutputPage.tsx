import { mediaUrl, type ArtifactRecord } from "../api/client";

type RenderOutputPageProps = {
  artifact: ArtifactRecord | null;
};

export function RenderOutputPage({ artifact }: RenderOutputPageProps) {
  if (!artifact) {
    return null;
  }

  const payload = artifact.payload_json ?? {};
  const storageKey = typeof payload.storage_key === "string" ? payload.storage_key : null;

  if (artifact.artifact_type === "video") {
    const isSucceeded = payload.render_status === "succeeded";
    return (
      <section className="panel render-output">
        <div>
          <p className="section-label">Render Output</p>
          <h2>{typeof payload.file_name === "string" ? payload.file_name : "video.mp4"}</h2>
        </div>
        {isSucceeded && storageKey ? (
          <video
            className="video-preview"
            controls
            src={`${mediaUrl(storageKey)}?t=${artifact.created_at}`}
            style={{ width: "100%", borderRadius: "8px", marginTop: "16px" }}
          />
        ) : (
          <p className="empty-state">Render did not produce a playable video.</p>
        )}
      </section>
    );
  }

  if (artifact.artifact_type === "thumbnail") {
    return (
      <section className="panel render-output">
        <div>
          <p className="section-label">Thumbnail Output</p>
          <h2>{typeof payload.file_name === "string" ? payload.file_name : "thumbnail.png"}</h2>
        </div>
        {storageKey ? (
          <div style={{ marginTop: "16px" }}>
            <img
              src={`${mediaUrl(storageKey)}?t=${artifact.created_at}`}
              alt="Generated Thumbnail"
              style={{
                width: "100%",
                maxWidth: "640px",
                aspectRatio: "16/9",
                borderRadius: "8px",
                border: "1px solid rgba(255, 255, 255, 0.15)",
                display: "block",
              }}
            />
            <p style={{ marginTop: "8px", fontSize: "14px", color: "var(--text-muted, #888)" }}>
              Dimensions: {String(payload.width ?? 1280)}x{String(payload.height ?? 720)} •{" "}
              {payload.size_bytes ? `${Math.round(Number(payload.size_bytes) / 1024)} KB` : ""}
            </p>
          </div>
        ) : (
          <p className="empty-state">Thumbnail output file was not found.</p>
        )}
      </section>
    );
  }

  if (artifact.artifact_type === "youtube_upload") {
    const youtubeUrl = typeof payload.youtube_url === "string" ? payload.youtube_url : null;
    const isSucceeded = payload.upload_status === "succeeded";
    return (
      <section className="panel render-output">
        <div>
          <p className="section-label">YouTube Upload</p>
          <h2>{typeof payload.title === "string" ? payload.title : "Published Video"}</h2>
        </div>
        {isSucceeded && youtubeUrl ? (
          <div style={{ marginTop: "16px", display: "flex", flexDirection: "column", gap: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <span className="status-pill status-pill--valid">Uploaded</span>
              <code>Video ID: {String(payload.youtube_video_id ?? "")}</code>
            </div>
            <p style={{ margin: 0, fontSize: "16px" }}>
              Your video is ready on YouTube!
            </p>
            <a
              href={youtubeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="primary-button"
              style={{
                display: "inline-block",
                textAlign: "center",
                maxWidth: "260px",
                textDecoration: "none",
                padding: "10px 20px",
              }}
            >
              Watch on YouTube ↗
            </a>
          </div>
        ) : (
          <p className="empty-state">
            {typeof payload.error_message === "string"
              ? `Upload failed: ${payload.error_message}`
              : "Upload is pending or failed."}
          </p>
        )}
      </section>
    );
  }

  if (artifact.artifact_type === "youtube_metadata") {
    const title = typeof payload.title === "string" ? payload.title : "";
    const description = typeof payload.description === "string" ? payload.description : "";
    const tags = Array.isArray(payload.tags) ? (payload.tags as string[]) : [];
    const concept = typeof payload.thumbnail_concept === "string" ? payload.thumbnail_concept : "";

    return (
      <section className="panel render-output">
        <div>
          <p className="section-label">YouTube SEO Metadata</p>
          <h2>{title}</h2>
        </div>
        <div style={{ marginTop: "16px", display: "flex", flexDirection: "column", gap: "16px" }}>
          {concept && (
            <div>
              <p style={{ margin: "0 0 6px 0", fontSize: "12px", textTransform: "uppercase", color: "#888" }}>
                Thumbnail Concept
              </p>
              <div style={{ fontWeight: 700, fontSize: "18px", color: "#FACC15" }}>{concept}</div>
            </div>
          )}

          <div>
            <p style={{ margin: "0 0 6px 0", fontSize: "12px", textTransform: "uppercase", color: "#888" }}>
              Description & Chapters
            </p>
            <pre
              style={{
                background: "rgba(0, 0, 0, 0.3)",
                padding: "12px",
                borderRadius: "6px",
                whiteSpace: "pre-wrap",
                fontFamily: "inherit",
                fontSize: "14px",
                lineHeight: "1.5",
                maxHeight: "240px",
                overflowY: "auto",
              }}
            >
              {description}
            </pre>
          </div>

          {tags.length > 0 && (
            <div>
              <p style={{ margin: "0 0 6px 0", fontSize: "12px", textTransform: "uppercase", color: "#888" }}>
                Tags ({tags.length})
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {tags.map((t, i) => (
                  <span
                    key={i}
                    style={{
                      background: "rgba(255, 255, 255, 0.08)",
                      padding: "4px 10px",
                      borderRadius: "12px",
                      fontSize: "12px",
                    }}
                  >
                    #{t}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    );
  }

  return null;
}
