import { mediaUrl, type ArtifactRecord } from "../api/client";

type RenderOutputPageProps = {
  artifact: ArtifactRecord | null;
};

export function RenderOutputPage({ artifact }: RenderOutputPageProps) {
  const payload = artifact?.payload_json ?? {};
  const storageKey = typeof payload.storage_key === "string" ? payload.storage_key : null;
  const isVideo = artifact?.artifact_type === "video";
  const isSucceeded = payload.render_status === "succeeded";

  if (!isVideo) {
    return null;
  }

  return (
    <section className="panel render-output">
      <div>
        <p className="section-label">Render Output</p>
        <h2>scene_01.mp4</h2>
      </div>
      {isSucceeded && storageKey ? (
        <video className="video-preview" controls src={mediaUrl(storageKey)} />
      ) : (
        <p className="empty-state">Render did not produce a playable video.</p>
      )}
    </section>
  );
}
