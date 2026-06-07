import type { ArtifactRecord } from "../api/client";

type ArtifactViewerPageProps = {
  artifact: ArtifactRecord | null;
};

export function ArtifactViewerPage({ artifact }: ArtifactViewerPageProps) {
  return (
    <section className="panel artifact-viewer">
      <div>
        <p className="section-label">Artifact</p>
        <h2>Viewer</h2>
      </div>
      {artifact ? (
        <pre className="json-view">{JSON.stringify(artifact, null, 2)}</pre>
      ) : (
        <p className="empty-state">Select an artifact to inspect its stored JSON.</p>
      )}
    </section>
  );
}

