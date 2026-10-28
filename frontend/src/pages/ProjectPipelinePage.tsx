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
  onRunResearch: () => void;
  onRunNarrativePlan: () => void;
  onRunHook: () => void;
  onRunScriptVisualStrategy: () => void;
  onRunQualityReview: () => void;
  onRunVoiceGeneration: () => void;
  onRunContinuousStory: () => void;
  onRunVideoAssembly: () => void;
  onRunRender: () => void;
  onResumeContinuousStory: () => void;
  onRunFullPipeline: () => void;
  onRunYoutubeMetadata: () => void;
  onRunThumbnail: () => void;
  onRunYoutubeUpload: (targetAccount?: "test" | "production") => void;
  onRegenerateDescendants: () => void;
  isRunningStage: boolean;
  runningStageName?: string | null;
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
  onRunResearch,
  onRunNarrativePlan,
  onRunHook,
  onRunScriptVisualStrategy,
  onRunQualityReview,
  onRunVoiceGeneration,
  onRunContinuousStory,
  onRunVideoAssembly,
  onRunRender,
  onResumeContinuousStory,
  onRunFullPipeline,
  onRunYoutubeMetadata,
  onRunThumbnail,
  onRunYoutubeUpload,
  onRegenerateDescendants,
  isRunningStage,
  runningStageName,
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
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <p className="section-label">Pipeline Actions</p>
            <h2>Choreography & Execution</h2>
          </div>
          {isRunningStage && (
            <div style={{ display: "flex", alignItems: "center", gap: "8px", background: "rgba(56, 189, 248, 0.15)", border: "1px solid #38bdf8", padding: "6px 14px", borderRadius: "20px" }}>
              <span className="spinner" style={{ display: "inline-block", width: "12px", height: "12px", border: "2px solid #38bdf8", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 1s linear infinite" }} />
              <span style={{ fontSize: "12px", fontWeight: 700, color: "#38bdf8" }}>
                {runningStageName || "Running pipeline..."}
              </span>
            </div>
          )}
        </div>

        {/* Highlighted Automated Workflows */}
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", margin: "14px 0 18px", padding: "12px", background: "var(--bg-secondary)", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
          <button
            className="primary-button"
            disabled={!selectedRun || isRunningStage}
            onClick={onResumeContinuousStory}
            style={{
              background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              color: "#ffffff",
              fontWeight: 700,
              padding: "10px 18px",
              boxShadow: "0 4px 12px rgba(16, 185, 129, 0.3)",
            }}
            type="button"
            title="Runs Stage 7 (Continuous Story) and Stage 8 (Render) sequentially — exactly like resume_rent_vs_buy"
          >
            ⚡ Resume Continuous Story & Render
          </button>

          <button
            className="primary-button"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunFullPipeline}
            style={{
              background: "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
              color: "#ffffff",
              fontWeight: 700,
              padding: "10px 18px",
              boxShadow: "0 4px 12px rgba(59, 130, 246, 0.3)",
            }}
            type="button"
            title="Runs the entire pipeline sequentially: Research -> Narrative -> Hook -> Strategy -> Review -> Voiceover -> Continuous Story -> Render"
          >
            🚀 Run Full Pipeline (End-to-End)
          </button>
        </div>

        <p style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" }}>
          Individual Stages
        </p>
        <div className="stage-actions">
          <button
            className="primary-button"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunResearch}
            type="button"
          >
            Run Research
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunNarrativePlan}
            type="button"
          >
            Run NarrativePlan
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunHook}
            type="button"
          >
            Run Hook
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunScriptVisualStrategy}
            type="button"
          >
            Run Strategy
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunQualityReview}
            type="button"
          >
            Run Review
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunVoiceGeneration}
            type="button"
          >
            Run Voiceover
          </button>
          <button
            className="primary-button"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunContinuousStory}
            style={{
              background: "#10b981",
              borderColor: "#10b981",
              color: "#000000",
              fontWeight: 700,
            }}
            type="button"
            title="Stage 7: Generates Continuous Story Plan with Dynamic Living Canvas"
          >
            🎨 Run Continuous Story
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunVideoAssembly}
            type="button"
          >
            Run Assembly
          </button>
          <button
            className="primary-button"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunRender}
            style={{
              background: "#0f172a",
              borderColor: "#334155",
              color: "#38bdf8",
              fontWeight: 700,
            }}
            type="button"
          >
            🎬 Run Render
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunYoutubeMetadata}
            type="button"
          >
            Run YT Metadata
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={onRunThumbnail}
            type="button"
          >
            Run Thumbnail
          </button>
          <button
            className="primary-button secondary"
            disabled={!selectedRun || isRunningStage}
            onClick={() => onRunYoutubeUpload("test")}
            type="button"
            title="Uploads private draft video to your Testing YouTube Channel"
          >
            🧪 Upload (Test)
          </button>
          <button
            className="primary-button"
            style={{ background: "#dc2626", borderColor: "#dc2626", color: "#ffffff" }}
            disabled={!selectedRun || isRunningStage}
            onClick={() => {
              const confirmed = window.confirm(
                `Are you sure you want to upload this video to your REAL PRODUCTION YouTube Channel?\n\nProject: ${project?.title || "Selected Video"}`
              );
              if (confirmed) {
                onRunYoutubeUpload("production");
              }
            }}
            type="button"
            title="Uploads video to your Real / Production YouTube Channel"
          >
            🚀 Upload (Real)
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
