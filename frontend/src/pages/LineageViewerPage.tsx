import type { ArtifactRecord } from "../api/client";

type LineageViewerPageProps = {
  parents: Record<string, ArtifactRecord>;
  children: ArtifactRecord[];
};

export function LineageViewerPage({ parents, children }: LineageViewerPageProps) {
  const parentEntries = Object.entries(parents);

  return (
    <section className="panel lineage-viewer">
      <div>
        <p className="section-label">Lineage</p>
        <h2>Parents & Children</h2>
      </div>
      <div className="lineage-grid">
        <div>
          <h3>Parents</h3>
          {parentEntries.length > 0 ? (
            <ul className="compact-list">
              {parentEntries.map(([role, artifact]) => (
                <li key={role}>
                  <span>{role}</span>
                  <code>{artifact.id}</code>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-state">No parent artifacts.</p>
          )}
        </div>
        <div>
          <h3>Children</h3>
          {children.length > 0 ? (
            <ul className="compact-list">
              {children.map((artifact) => (
                <li key={artifact.id}>
                  <span>{artifact.artifact_type}</span>
                  <code>{artifact.id}</code>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-state">No child artifacts.</p>
          )}
        </div>
      </div>
    </section>
  );
}

