import { useEffect, useState } from "react";
import {
  createProject,
  listArtifactChildren,
  listArtifactParents,
  listProjects,
  listRunArtifacts,
  listRuns,
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
  const [title, setTitle] = useState("");
  const [isBusy, setIsBusy] = useState(false);
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
      const created = await createProject(title);
      const nextProjects = await listProjects();
      setProjects(nextProjects);
      setTitle("");
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

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="section-label">YTCreate V2</p>
          <h1>Artifact Infrastructure</h1>
        </div>
        <p>
          Project and run records are now backed by SQLite. Artifacts can be inspected
          through run-scoped JSON and role-map lineage.
        </p>
      </header>

      {error ? <div className="error-banner">{error}</div> : null}

      <div className="dashboard-grid">
        <aside className="sidebar">
          <CreateProjectPage
            title={title}
            isBusy={isBusy}
            onTitleChange={setTitle}
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
        />
      </div>
    </div>
  );
}

