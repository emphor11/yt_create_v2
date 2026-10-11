import { useState } from "react";
import type { ArtifactRecord } from "../api/client";

type ArtifactViewerPageProps = {
  artifact: ArtifactRecord | null;
};

export function ArtifactViewerPage({ artifact }: ArtifactViewerPageProps) {
  const [viewMode, setViewMode] = useState<"structured" | "raw">("structured");

  if (!artifact) {
    return (
      <section className="panel artifact-viewer">
        <div>
          <p className="section-label">Artifact</p>
          <h2>Viewer</h2>
        </div>
        <p className="empty-state">Select an artifact to inspect its details.</p>
      </section>
    );
  }

  const payload = artifact.payload_json as Record<string, any>;
  const isStoryboard = artifact.artifact_type === "storyboard";
  const isCompiledWorld = artifact.artifact_type === "compiled_world";
  const isVisualIntent = artifact.artifact_type === "visual_intent";
  const hasStructuredView = isStoryboard || isCompiledWorld || isVisualIntent;

  return (
    <section className="panel artifact-viewer">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div>
          <p className="section-label">{artifact.artifact_type}</p>
          <h2>{artifact.id}</h2>
        </div>
        {hasStructuredView && (
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              className={`primary-button ${viewMode === "structured" ? "" : "secondary"}`}
              style={{ padding: "6px 12px", fontSize: "13px" }}
              onClick={() => setViewMode("structured")}
              type="button"
            >
              Structured View
            </button>
            <button
              className={`primary-button ${viewMode === "raw" ? "" : "secondary"}`}
              style={{ padding: "6px 12px", fontSize: "13px" }}
              onClick={() => setViewMode("raw")}
              type="button"
            >
              Raw JSON
            </button>
          </div>
        )}
      </div>

      {viewMode === "raw" || !hasStructuredView ? (
        <pre className="json-view">{JSON.stringify(artifact, null, 2)}</pre>
      ) : isStoryboard ? (
        <StoryboardView payload={payload} />
      ) : isCompiledWorld ? (
        <CompiledWorldView payload={payload} />
      ) : isVisualIntent ? (
        <VisualIntentView payload={payload} />
      ) : (
        <pre className="json-view">{JSON.stringify(artifact, null, 2)}</pre>
      )}
    </section>
  );
}

function StoryboardView({ payload }: { payload: Record<string, any> }) {
  const beats: any[] = payload.beats || [];

  // Collect all unique elements declared across beats (or legacy objects if present)
  const elementsMap: Record<string, any> = {};
  for (const beat of beats) {
    if (beat.elements) {
      for (const el of beat.elements) {
        if (!elementsMap[el.object_id] || el.primitive_type) {
          elementsMap[el.object_id] = el;
        }
      }
    }
  }
  const elements = Object.values(elementsMap);
  const legacyObjects: any[] = payload.objects || [];
  const displayObjects = elements.length > 0 ? elements : legacyObjects;

  // Count total actions across all beats
  const totalActions = beats.reduce((acc, b) => {
    if (b.elements) {
      return acc + b.elements.reduce((sum: number, el: any) => sum + (el.actions?.length || 0), 0);
    }
    return acc + (b.actions?.length || 0);
  }, 0);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* World Identity Summary */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px" }}>
        <div style={{ padding: "12px", background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>WORLD ID</p>
          <code style={{ fontSize: "14px", fontWeight: 600 }}>{payload.world_id || "unknown"}</code>
        </div>
        <div style={{ padding: "12px", background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>EDITORIAL BEATS</p>
          <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0" }}>{beats.length}</p>
        </div>
        <div style={{ padding: "12px", background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>VISUAL ELEMENTS</p>
          <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0" }}>{displayObjects.length}</p>
        </div>
        <div style={{ padding: "12px", background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>TOTAL ACTIONS</p>
          <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0" }}>{totalActions}</p>
        </div>
      </div>

      {/* Editorial Beats */}
      <div>
        <h3 style={{ fontSize: "15px", marginBottom: "10px", color: "var(--text-primary)" }}>
          Choreographed Editorial Beats ({beats.length})
        </h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {beats.map((beat) => {
            const beatElements: any[] = beat.elements || [];
            const beatActions: any[] = beat.actions || [];

            return (
              <div
                key={beat.beat_id}
                style={{
                  padding: "14px",
                  background: "var(--bg-secondary)",
                  borderRadius: "8px",
                  border: "1px solid var(--border-color)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                  <code style={{ fontWeight: 700, fontSize: "13px" }}>{beat.beat_id}</code>
                  {beat.transition_kind && (
                    <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                      Transition: <strong>{beat.transition_kind}</strong>
                    </span>
                  )}
                </div>

                {beat.visual_goal && (
                  <p style={{ margin: "0 0 6px", fontSize: "12px", color: "var(--accent-color, #3b82f6)", fontWeight: 500 }}>
                    🎯 {beat.visual_goal}
                  </p>
                )}

                <p style={{ margin: "0 0 10px", fontSize: "14px", lineHeight: "1.4", color: "var(--text-primary)" }}>
                  "{beat.narration}"
                </p>

                {/* Elements & their actions */}
                {beatElements.length > 0 && (
                  <div style={{ marginTop: "10px" }}>
                    <p style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", marginBottom: "6px" }}>
                      Participating Elements ({beatElements.length}):
                    </p>
                    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                      {beatElements.map((el: any) => (
                        <div
                          key={el.object_id}
                          style={{
                            padding: "6px 10px",
                            background: "var(--bg-tertiary)",
                            borderRadius: "6px",
                            border: "1px solid var(--border-color)",
                            fontSize: "12px",
                          }}
                        >
                          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                            {el.primitive_type && (
                              <span
                                style={{
                                  padding: "1px 6px",
                                  borderRadius: "4px",
                                  fontSize: "10px",
                                  fontWeight: 600,
                                  textTransform: "uppercase",
                                  background: "var(--border-color)",
                                  color: "var(--text-primary)",
                                }}
                              >
                                {el.primitive_type}
                              </span>
                            )}
                            <code style={{ fontWeight: 600 }}>{el.object_id}</code>
                            {el.parent_object_id && (
                              <span style={{ color: "var(--text-muted)", fontSize: "11px" }}>
                                ↳ inside <code>{el.parent_object_id}</code>
                              </span>
                            )}
                            {el.macro_zone && (
                              <span style={{ color: "var(--text-muted)", fontSize: "11px" }}>
                                [{el.macro_zone}]
                              </span>
                            )}
                          </div>

                          {el.actions && el.actions.length > 0 && (
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginTop: "4px" }}>
                              {el.actions.map((act: any) => (
                                <span
                                  key={act.action_id}
                                  style={{
                                    padding: "2px 6px",
                                    borderRadius: "3px",
                                    fontSize: "11px",
                                    background: "var(--bg-primary)",
                                    border: "1px solid var(--border-color)",
                                  }}
                                >
                                  <strong>{act.action_type}</strong> on trigger: "<em>{act.trigger_word}</em>"
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Legacy Actions (if old artifact format) */}
                {beatActions.length > 0 && beatElements.length === 0 && (
                  <div style={{ marginTop: "8px" }}>
                    <p style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", marginBottom: "4px" }}>
                      Speech Actions ({beatActions.length}):
                    </p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                      {beatActions.map((act: any) => (
                        <span
                          key={act.action_id}
                          style={{
                            padding: "3px 8px",
                            borderRadius: "4px",
                            fontSize: "12px",
                            background: "var(--bg-tertiary)",
                            border: "1px solid var(--border-color)",
                          }}
                        >
                          <strong>{act.action_type}</strong> <code>{act.target_node_id}</code> on trigger: "<em>{act.trigger_word}</em>"
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function CompiledWorldView({ payload }: { payload: Record<string, any> }) {
  const primitives: Record<string, any> = payload.primitives || {};
  const speechAnchors: any[] = payload.speech_anchors || [];
  const animationTracks: any[] = payload.animation_tracks || [];
  const canvas = payload.canvas_config || {};

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Overview Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px" }}>
        <div style={{ padding: "12px", background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>CANVAS CONFIG</p>
          <p style={{ fontSize: "14px", fontWeight: 600, margin: "4px 0 0" }}>
            {canvas.width || 1920}x{canvas.height || 1080} @ {canvas.fps || 30}fps
          </p>
        </div>
        <div style={{ padding: "12px", background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>TOTAL DURATION</p>
          <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0" }}>
            {payload.total_duration_frames} frames <span style={{ fontSize: "12px", fontWeight: 400 }}>({((payload.total_duration_frames || 0) / (canvas.fps || 30)).toFixed(1)}s)</span>
          </p>
        </div>
        <div style={{ padding: "12px", background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>COMPILED PRIMITIVES</p>
          <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0" }}>{Object.keys(primitives).length}</p>
        </div>
        <div style={{ padding: "12px", background: "var(--bg-secondary)", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
          <p style={{ fontSize: "12px", color: "var(--text-muted)", margin: 0 }}>SPEECH ANCHORS</p>
          <p style={{ fontSize: "18px", fontWeight: 700, margin: "4px 0 0" }}>{speechAnchors.length}</p>
        </div>
      </div>

      {/* Speech Anchors */}
      <div>
        <h3 style={{ fontSize: "15px", marginBottom: "10px", color: "var(--text-primary)" }}>
          Global Speech Timing Anchors ({speechAnchors.length})
        </h3>
        <div style={{ maxHeight: "240px", overflowY: "auto", border: "1px solid var(--border-color)", borderRadius: "6px" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
            <thead>
              <tr style={{ background: "var(--bg-tertiary)", textAlign: "left" }}>
                <th style={{ padding: "8px" }}>Anchor ID</th>
                <th style={{ padding: "8px" }}>Word</th>
                <th style={{ padding: "8px" }}>Global Frame</th>
                <th style={{ padding: "8px" }}>Time (ms)</th>
              </tr>
            </thead>
            <tbody>
              {speechAnchors.map((sa) => (
                <tr key={sa.anchor_id} style={{ borderTop: "1px solid var(--border-color)" }}>
                  <td style={{ padding: "6px 8px" }}><code>{sa.anchor_id}</code></td>
                  <td style={{ padding: "6px 8px" }}><strong>"{sa.text}"</strong></td>
                  <td style={{ padding: "6px 8px" }}>Frame {sa.global_frame}</td>
                  <td style={{ padding: "6px 8px" }}>{sa.start_ms} - {sa.end_ms}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Compiled Primitives */}
      <div>
        <h3 style={{ fontSize: "15px", marginBottom: "10px", color: "var(--text-primary)" }}>
          Compiled Primitives with Local Geometry ({Object.keys(primitives).length})
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "10px" }}>
          {Object.entries(primitives).map(([pid, p]: [string, any]) => (
            <div
              key={pid}
              style={{
                padding: "10px",
                background: "var(--bg-secondary)",
                borderRadius: "6px",
                border: "1px solid var(--border-color)",
                fontSize: "12px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                <code>{pid}</code>
                <span style={{ color: "var(--text-muted)" }}>{p.primitive_type}</span>
              </div>
              {p.local_geometry && (
                <div style={{ color: "var(--text-secondary)" }}>
                  x: {Math.round(p.local_geometry.x)} | y: {Math.round(p.local_geometry.y)} | w: {Math.round(p.local_geometry.width)} | h: {Math.round(p.local_geometry.height)}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function VisualIntentView({ payload }: { payload: Record<string, any> }) {
  const sequences: any[] = payload.sequences || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <h3 style={{ fontSize: "15px", color: "var(--text-primary)", margin: 0 }}>
        Visual Intent Sequences ({sequences.length})
      </h3>
      {sequences.map((seq, idx) => (
        <div
          key={seq.idea_id || idx}
          style={{
            padding: "14px",
            background: "var(--bg-secondary)",
            borderRadius: "8px",
            border: "1px solid var(--border-color)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
            <code>Idea: {seq.idea_id}</code>
            <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>{(seq.intents || []).length} intents</span>
          </div>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "10px" }}>
            "{seq.narration}"
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {(seq.intents || []).map((intent: any) => (
              <div
                key={intent.intent_id}
                style={{
                  padding: "8px 12px",
                  background: "var(--bg-tertiary)",
                  borderRadius: "6px",
                  fontSize: "12px",
                }}
              >
                <div style={{ fontWeight: 600, color: "var(--text-primary)", marginBottom: "2px" }}>
                  {intent.intent_id}: {intent.what_viewer_must_understand}
                </div>
                {intent.measurements && intent.measurements.length > 0 && (
                  <div style={{ color: "var(--text-muted)", marginTop: "4px" }}>
                    Measurements: {intent.measurements.map((m: any) => `${m.raw_value} (${m.numeric_value} ${m.unit || ""})`).join(", ")}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
