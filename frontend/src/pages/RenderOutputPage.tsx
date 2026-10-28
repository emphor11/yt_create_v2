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

  if (artifact.artifact_type === "continuous_story_plan") {
    const plan = (payload.plan as Record<string, any>) || {};
    const objects = (plan.objects as Array<any>) || [];
    const events = (plan.events as Array<any>) || [];
    const durationFrames = Number(payload.duration_in_frames || plan.durationInFrames || 0);
    const fps = Number(payload.fps || plan.fps || 30);
    const durationSeconds = fps > 0 ? (durationFrames / fps).toFixed(1) : "0";
    const narrationText = typeof plan.narration?.text === "string" ? plan.narration.text : "";

    return (
      <section className="panel render-output">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <p className="section-label">Continuous Story Plan</p>
            <h2>{String(payload.story_id || plan.id || "continuous_story")}</h2>
          </div>
          <span className="status-pill status-pill--valid">Living Canvas 3.0</span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "12px", marginTop: "16px" }}>
          <div style={{ background: "var(--bg-secondary)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Total Duration</span>
            <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0", color: "var(--text-primary)" }}>{durationSeconds}s</p>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>{durationFrames.toLocaleString()} frames</span>
          </div>
          <div style={{ background: "var(--bg-secondary)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Canvas Rate</span>
            <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0", color: "var(--text-primary)" }}>{fps} FPS</p>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>1080p Broadcast</span>
          </div>
          <div style={{ background: "var(--bg-secondary)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Active Objects</span>
            <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0", color: "var(--text-primary)" }}>{objects.length}</p>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Decoupled primitives</span>
          </div>
          <div style={{ background: "var(--bg-secondary)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Choreography</span>
            <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0", color: "var(--text-primary)" }}>{events.length}</p>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Sub-frame events</span>
          </div>
        </div>

        <div style={{ marginTop: "20px" }}>
          <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "10px" }}>
            Living Canvas Objects ({objects.length})
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: "10px" }}>
            {objects.map((obj: any) => {
              const zoneColor =
                obj.layout === "split_left" ? "#38bdf8" :
                obj.layout === "split_right" ? "#a855f7" :
                obj.layout === "full_bottom" ? "#f59e0b" :
                obj.layout === "full_screen" ? "#ec4899" : "#10b981";

              return (
                <div
                  key={obj.id}
                  style={{
                    background: "var(--bg-secondary)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "8px",
                    padding: "10px 12px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "4px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <code style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-primary)" }}>{obj.id}</code>
                    <span
                      style={{
                        fontSize: "9px",
                        fontWeight: 700,
                        padding: "2px 6px",
                        borderRadius: "4px",
                        background: `${zoneColor}22`,
                        color: zoneColor,
                        border: `1px solid ${zoneColor}44`,
                        textTransform: "uppercase",
                      }}
                    >
                      {obj.layout || "center"}
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: "6px", alignItems: "center", marginTop: "2px" }}>
                    <span style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: 600 }}>
                      {obj.type}
                    </span>
                    {obj.cardProps?.title && (
                      <span style={{ fontSize: "11px", color: "var(--text-secondary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        • {obj.cardProps.title}
                      </span>
                    )}
                    {obj.imageProps?.badge && (
                      <span style={{ fontSize: "11px", color: "var(--text-secondary)" }}>
                        • [{obj.imageProps.badge}]
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {events.length > 0 && (
          <div style={{ marginTop: "24px" }}>
            <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "10px" }}>
              Audio-Visual Choreography Timeline ({events.length} Events)
            </h3>
            <div style={{ maxHeight: "320px", overflowY: "auto", border: "1px solid var(--border-color)", borderRadius: "8px", background: "var(--bg-secondary)" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border-color)", textAlign: "left", color: "var(--text-muted)" }}>
                    <th style={{ padding: "8px 12px" }}>Time</th>
                    <th style={{ padding: "8px 12px" }}>Action</th>
                    <th style={{ padding: "8px 12px" }}>Target</th>
                    <th style={{ padding: "8px 12px" }}>Speech Anchor</th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((ev: any, idx: number) => {
                    const timeSec = (Number(ev.startFrame || 0) / fps).toFixed(2);
                    return (
                      <tr key={idx} style={{ borderBottom: "1px solid var(--border-color)" }}>
                        <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "var(--text-muted)" }}>
                          {timeSec}s <span style={{ opacity: 0.6 }}>(f{ev.startFrame})</span>
                        </td>
                        <td style={{ padding: "8px 12px" }}>
                          <span
                            style={{
                              padding: "2px 6px",
                              borderRadius: "4px",
                              fontWeight: 700,
                              fontSize: "10px",
                              textTransform: "uppercase",
                              background:
                                ev.action === "enter" ? "rgba(16, 185, 129, 0.15)" :
                                ev.action === "exit" ? "rgba(239, 68, 68, 0.15)" :
                                ev.action === "connect" ? "rgba(56, 189, 248, 0.15)" :
                                "rgba(245, 158, 11, 0.15)",
                              color:
                                ev.action === "enter" ? "var(--color-valid, #10b981)" :
                                ev.action === "exit" ? "#ef4444" :
                                ev.action === "connect" ? "#38bdf8" :
                                "var(--color-warning, #f59e0b)",
                            }}
                          >
                            {ev.action}
                          </span>
                        </td>
                        <td style={{ padding: "8px 12px", fontWeight: 600, color: "var(--text-primary)" }}>{ev.targetId}</td>
                        <td style={{ padding: "8px 12px", color: "var(--text-secondary)", fontStyle: "italic", maxWidth: "340px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          "{ev.anchor || ""}"
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {narrationText && (
          <div style={{ marginTop: "20px" }}>
            <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
              Narration Voice Track Script
            </h3>
            <div
              style={{
                background: "var(--bg-secondary)",
                padding: "14px",
                borderRadius: "8px",
                border: "1px solid var(--border-color)",
                fontSize: "13px",
                lineHeight: "1.6",
                color: "var(--text-secondary)",
                maxHeight: "180px",
                overflowY: "auto",
                whiteSpace: "pre-wrap",
              }}
            >
              {narrationText}
            </div>
          </div>
        )}
      </section>
    );
  }

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
    const isSkipped = payload.status === "skipped" || artifact.status === "skipped";
    return (
      <section className="panel render-output">
        <div>
          <p className="section-label">Thumbnail Stage</p>
          <h2>{isSkipped ? "Manual Thumbnail Upload" : (typeof payload.file_name === "string" ? payload.file_name : "thumbnail.png")}</h2>
        </div>
        {isSkipped ? (
          <div style={{ marginTop: "16px", padding: "16px", background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
            <p style={{ fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
              Automated Thumbnail Generation is Skipped
            </p>
            <p style={{ fontSize: "14px", color: "var(--text-muted)" }}>
              {typeof payload.reason === "string"
                ? payload.reason
                : "Automated thumbnail generation is currently disabled. Please add or select the thumbnail manually in YouTube Studio after video upload."}
            </p>
          </div>
        ) : storageKey ? (
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
    const targetAccount = typeof payload.target_account === "string" ? payload.target_account : "test";
    const isProd = targetAccount === "production";
    const channelTitle = typeof payload.channel_title === "string" ? payload.channel_title : null;

    return (
      <section className="panel render-output">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <p className="section-label">YouTube Upload</p>
            <h2>{typeof payload.title === "string" ? payload.title : "Published Video"}</h2>
          </div>
          <span
            className="status-pill"
            style={{
              background: isProd ? "rgba(245, 158, 11, 0.15)" : "rgba(16, 185, 129, 0.15)",
              color: isProd ? "var(--color-warning, #f59e0b)" : "var(--color-valid, #10b981)",
              borderColor: isProd ? "rgba(245, 158, 11, 0.4)" : "rgba(16, 185, 129, 0.4)",
              fontWeight: 600,
              fontSize: "0.82rem",
              padding: "4px 10px",
            }}
          >
            {isProd ? "🚀 Production Channel" : "🧪 Test Channel"}
          </span>
        </div>
        {isSucceeded && youtubeUrl ? (
          <div style={{ marginTop: "16px", display: "flex", flexDirection: "column", gap: "14px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
              <span className="status-pill status-pill--valid">Uploaded</span>
              {channelTitle ? (
                <span style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                  Channel: <strong style={{ color: "var(--text-primary)" }}>{channelTitle}</strong>
                </span>
              ) : null}
              <code>Video ID: {String(payload.youtube_video_id ?? "")}</code>
            </div>
            <p style={{ margin: 0, fontSize: "15px", color: "var(--text-secondary)" }}>
              Your video is live as a private draft on YouTube ({isProd ? "Production Account" : "Test Account"}).
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
