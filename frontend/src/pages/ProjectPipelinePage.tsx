import type {
  ArtifactRecord,
  PipelineRunRecord,
  PipelineStageSummary,
  ProjectRecord,
} from "../api/client";
import { ArtifactViewerPage } from "./ArtifactViewerPage";
import { LineageViewerPage } from "./LineageViewerPage";
import { RenderOutputPage } from "./RenderOutputPage";

type ProjectPipelinePageProps = {
  project: ProjectRecord | null;
  runs: PipelineRunRecord[];
  selectedRun: PipelineRunRecord | null;
  artifacts: ArtifactRecord[];
  stageSummaries: PipelineStageSummary[];
  selectedArtifact: ArtifactRecord | null;
  parents: Record<string, ArtifactRecord>;
  children: ArtifactRecord[];
  onRunSelect: (run: PipelineRunRecord) => void;
  onArtifactSelect: (artifact: ArtifactRecord) => void;
  onRunScriptBrief: () => void;
  onRunNarrativeArc: () => void;
  onRunScriptDraft: () => void;
  onRunSceneScript: () => void;
  onRunSemanticScene: () => void;
  onRunVisualEventSequence: () => void;
  onRunVisualPlan: () => void;
  onRunTiming: () => void;
  onRunRenderSpec: () => void;
  onRunRender: () => void;
  onRegenerateDescendants: () => void;
  isRunningStage: boolean;
};

export function ProjectPipelinePage({
  project,
  runs,
  selectedRun,
  artifacts,
  stageSummaries,
  selectedArtifact,
  parents,
  children,
  onRunSelect,
  onArtifactSelect,
  onRunScriptBrief,
  onRunNarrativeArc,
  onRunScriptDraft,
  onRunSceneScript,
  onRunSemanticScene,
  onRunVisualEventSequence,
  onRunVisualPlan,
  onRunTiming,
  onRunRenderSpec,
  onRunRender,
  onRegenerateDescendants,
  isRunningStage,
}: ProjectPipelinePageProps) {
  if (!project) {
    return (
      <section className="panel project-pipeline">
        <p className="empty-state">Create or select a project to inspect its run.</p>
      </section>
    );
  }

  return (
    <div className="project-pipeline">
      <section className="panel">
        <div>
          <p className="section-label">Selected Project</p>
          <h2>{project.title}</h2>
        </div>
        <div className="meta-grid">
          <span>Project ID</span>
          <code>{project.id}</code>
          <span>Created</span>
          <code>{project.created_at}</code>
        </div>
      </section>

      <section className="panel">
        <div>
          <p className="section-label">Runs</p>
          <h2>Pipeline Runs</h2>
        </div>
        {runs.length > 0 ? (
          <div className="button-list">
            {runs.map((run) => (
              <button
                className={run.id === selectedRun?.id ? "list-button active" : "list-button"}
                key={run.id}
                onClick={() => onRunSelect(run)}
                type="button"
              >
                <span>{run.mode}</span>
                <code>{run.id}</code>
              </button>
            ))}
          </div>
        ) : (
          <p className="empty-state">No runs found.</p>
        )}
      </section>

      <section className="panel">
        <div>
          <p className="section-label">Status</p>
          <h2>Validation Summary</h2>
        </div>
        {stageSummaries.length > 0 ? (
          <div className="stage-summary">
            {stageSummaries.map((summary) => (
              <div className="stage-summary-row" key={summary.stage}>
                <span>{summary.stage}</span>
                <code className={`status-pill status-pill--${summary.status}`}>
                  {summary.status}
                </code>
                <code>
                  {summary.error_count} errors / {summary.warning_count} warnings
                </code>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-state">No status summary available.</p>
        )}
      </section>

      <section className="panel">
        <div>
          <p className="section-label">Artifacts</p>
          <h2>Run Artifacts</h2>
        </div>
        <div className="stage-actions">
          <button
            className="primary-button"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunScriptBrief}
            type="button"
          >
            Run ScriptBrief
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunNarrativeArc}
            type="button"
          >
            Run NarrativeArc
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunScriptDraft}
            type="button"
          >
            Run ScriptDraft
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunSceneScript}
            type="button"
          >
            Run SceneScript
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunSemanticScene}
            type="button"
          >
            Run SemanticScene
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunVisualEventSequence}
            type="button"
          >
            Run VisualEventSequence
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunVisualPlan}
            type="button"
          >
            Run VisualPlan
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunTiming}
            type="button"
          >
            Run Timing
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunRenderSpec}
            type="button"
          >
            Run RenderSpec
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunRender}
            type="button"
          >
            Run Render
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedArtifact || isRunningStage}
            onClick={onRegenerateDescendants}
            type="button"
          >
            Clear Descendants
          </button>
        </div>
        {artifacts.length > 0 ? (
          <div className="button-list">
            {artifacts.map((artifact) => (
              <button
                className={
                  artifact.id === selectedArtifact?.id ? "list-button active" : "list-button"
                }
                key={artifact.id}
                onClick={() => onArtifactSelect(artifact)}
                type="button"
              >
                <span>{artifact.artifact_type}</span>
                <code>{artifact.status}</code>
              </button>
            ))}
          </div>
        ) : (
          <p className="empty-state">No artifacts stored in this run yet.</p>
        )}
      </section>

      <RenderOutputPage artifact={selectedArtifact} />
      <ArtifactViewerPage artifact={selectedArtifact} />
      <LineageViewerPage parents={parents} children={children} />
    </div>
  );
}
