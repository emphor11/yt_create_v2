import { useEffect, useState } from "react";
import {
  createProject,
  listArtifactChildren,
  listArtifactParents,
  listProjects,
  listRunArtifacts,
  listRuns,
  runNarrativeArc,
  runSceneScript,
  runSemanticScene,
  runScriptBrief,
  runScriptDraft,
  runVisualEventSequence,
  runVisualPlan,
  type ArtifactRecord,
  type PipelineRunRecord,
  type ProjectRecord,
} from "../api/client";
import { CreateProjectPage } from "./CreateProjectPage";
import { ProjectPipelinePage } from "./ProjectPipelinePage";

export function ProjectListPage() {
  const [projects, setProjects] = useState<ProjectRecord[]>([]);
  const [selectedProject, setSelectedProject] = useState<ProjectRecord | null>(null);
  const [runs, setRuns] = useState<PipelineRunRecord[]>([]);
  const [selectedRun, setSelectedRun] = useState<PipelineRunRecord | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactRecord[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState<ArtifactRecord | null>(null);
  const [parents, setParents] = useState<Record<string, ArtifactRecord>>({});
  const [children, setChildren] = useState<ArtifactRecord[]>([]);
  const [topic, setTopic] = useState("");
  const [angle, setAngle] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [isRunningStage, setIsRunningStage] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    refreshProjects();
  }, []);

  async function refreshProjects() {
    setError(null);
    try {
      const records = await listProjects();
      setProjects(records);
    } catch (requestError) {
      setError((requestError as Error).message);
    }
  }

  async function handleCreateProject() {
    setIsBusy(true);
    setError(null);
    try {
      const created = await createProject(topic, angle);
      const nextProjects = await listProjects();
      setProjects(nextProjects);
      setTopic("");
      setAngle("");
      await selectProject(created.project);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setIsBusy(false);
    }
  }

  async function selectProject(project: ProjectRecord) {
    setSelectedProject(project);
    setSelectedArtifact(null);
    setParents({});
    setChildren([]);
    setError(null);
    try {
      const runRecords = await listRuns(project.id);
      setRuns(runRecords);
      const firstRun = runRecords[0] ?? null;
      setSelectedRun(firstRun);
      if (firstRun) {
        const artifactRecords = await listRunArtifacts(project.id, firstRun.id);
        setArtifacts(artifactRecords);
      } else {
        setArtifacts([]);
      }
    } catch (requestError) {
      setError((requestError as Error).message);
    }
  }

  async function selectRun(run: PipelineRunRecord) {
    if (!selectedProject) {
      return;
    }
    setSelectedRun(run);
    setSelectedArtifact(null);
    setParents({});
    setChildren([]);
    setError(null);
    try {
      const artifactRecords = await listRunArtifacts(selectedProject.id, run.id);
      setArtifacts(artifactRecords);
    } catch (requestError) {
      setError((requestError as Error).message);
    }
  }

  async function selectArtifact(artifact: ArtifactRecord) {
    setSelectedArtifact(artifact);
    setError(null);
    try {
      const [parentResponse, childResponse] = await Promise.all([
        listArtifactParents(artifact.id),
        listArtifactChildren(artifact.id),
      ]);
      setParents(parentResponse.parents);
      setChildren(childResponse.children);
    } catch (requestError) {
      setError((requestError as Error).message);
    }
  }

  async function handleRunScriptBrief() {
    if (!selectedProject || !selectedRun) {
      return;
    }
    setIsRunningStage(true);
    setError(null);
    try {
      const response = await runScriptBrief(selectedProject.id, selectedRun.id);
      const artifactRecords = await listRunArtifacts(selectedProject.id, selectedRun.id);
      setArtifacts(artifactRecords);
      await selectArtifact(response.artifact);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setIsRunningStage(false);
    }
  }

  async function handleRunNarrativeArc() {
    if (!selectedProject || !selectedRun) {
      return;
    }
    setIsRunningStage(true);
    setError(null);
    try {
      const response = await runNarrativeArc(selectedProject.id, selectedRun.id);
      const artifactRecords = await listRunArtifacts(selectedProject.id, selectedRun.id);
      setArtifacts(artifactRecords);
      await selectArtifact(response.artifact);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setIsRunningStage(false);
    }
  }

  async function handleRunScriptDraft() {
    if (!selectedProject || !selectedRun) {
      return;
    }
    setIsRunningStage(true);
    setError(null);
    try {
      const response = await runScriptDraft(selectedProject.id, selectedRun.id);
      const artifactRecords = await listRunArtifacts(selectedProject.id, selectedRun.id);
      setArtifacts(artifactRecords);
      await selectArtifact(response.artifact);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setIsRunningStage(false);
    }
  }

  async function handleRunSceneScript() {
    if (!selectedProject || !selectedRun) {
      return;
    }
    setIsRunningStage(true);
    setError(null);
    try {
      const response = await runSceneScript(selectedProject.id, selectedRun.id);
      const artifactRecords = await listRunArtifacts(selectedProject.id, selectedRun.id);
      setArtifacts(artifactRecords);
      await selectArtifact(response.artifact);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setIsRunningStage(false);
    }
  }

  async function handleRunSemanticScene() {
    if (!selectedProject || !selectedRun) {
      return;
    }
    setIsRunningStage(true);
    setError(null);
    try {
      const response = await runSemanticScene(selectedProject.id, selectedRun.id);
      const artifactRecords = await listRunArtifacts(selectedProject.id, selectedRun.id);
      setArtifacts(artifactRecords);
      await selectArtifact(response.artifact);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setIsRunningStage(false);
    }
  }

  async function handleRunVisualEventSequence() {
    if (!selectedProject || !selectedRun) {
      return;
    }
    setIsRunningStage(true);
    setError(null);
    try {
      const response = await runVisualEventSequence(selectedProject.id, selectedRun.id);
      const artifactRecords = await listRunArtifacts(selectedProject.id, selectedRun.id);
      setArtifacts(artifactRecords);
      await selectArtifact(response.artifact);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setIsRunningStage(false);
    }
  }

  async function handleRunVisualPlan() {
    if (!selectedProject || !selectedRun) {
      return;
    }
    setIsRunningStage(true);
    setError(null);
    try {
      const response = await runVisualPlan(selectedProject.id, selectedRun.id);
      const artifactRecords = await listRunArtifacts(selectedProject.id, selectedRun.id);
      setArtifacts(artifactRecords);
      await selectArtifact(response.artifact);
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setIsRunningStage(false);
    }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="section-label">YTCreate V2</p>
          <h1>VisualPlan</h1>
        </div>
        <p>
          Choose SplitComparison and map semantic numbers into traceable component props.
        </p>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <div className="dashboard-grid">
        <aside className="sidebar">
          <CreateProjectPage
            topic={topic}
            angle={angle}
            isBusy={isBusy}
            onTopicChange={setTopic}
            onAngleChange={setAngle}
            onSubmit={handleCreateProject}
          />
          <section className="panel">
            <div>
              <p className="section-label">Projects</p>
              <h2>Project List</h2>
            </div>
            {projects.length > 0 ? (
              <div className="button-list">
                {projects.map((project) => (
                  <button
                    className={
                      project.id === selectedProject?.id ? "list-button active" : "list-button"
                    }
                    key={project.id}
                    onClick={() => selectProject(project)}
                    type="button"
                  >
                    <span>{project.title}</span>
                    <code>{project.id}</code>
                  </button>
                ))}
              </div>
            ) : (
              <p className="empty-state">No projects created yet.</p>
            )}
          </section>
        </aside>

        <ProjectPipelinePage
          project={selectedProject}
          runs={runs}
          selectedRun={selectedRun}
          artifacts={artifacts}
          selectedArtifact={selectedArtifact}
          parents={parents}
          children={children}
          onRunSelect={selectRun}
          onArtifactSelect={selectArtifact}
          onRunScriptBrief={handleRunScriptBrief}
          onRunNarrativeArc={handleRunNarrativeArc}
          onRunScriptDraft={handleRunScriptDraft}
          onRunSceneScript={handleRunSceneScript}
          onRunSemanticScene={handleRunSemanticScene}
          onRunVisualEventSequence={handleRunVisualEventSequence}
          onRunVisualPlan={handleRunVisualPlan}
          isRunningStage={isRunningStage}
        />
      </div>
    </div>
  );
}
