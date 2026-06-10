export type ArtifactStatus = "valid" | "warning" | "blocked" | "failed";

export type ValidationResult = {
  status: ArtifactStatus;
  errors: string[];
  warnings: string[];
};

export type ProjectRecord = {
  id: string;
  title: string;
  created_at: string;
};

export type PipelineRunRecord = {
  id: string;
  project_id: string;
  created_at: string;
  mode: "deterministic";
};

export type ArtifactRecord = {
  id: string;
  project_id: string;
  run_id: string;
  artifact_type: string;
  schema_version: string;
  payload_json: Record<string, unknown>;
  parent_artifact_roles_json: Record<string, string>;
  validation_json: ValidationResult;
  status: ArtifactStatus;
  created_at: string;
};

export type CreateProjectResponse = {
  project: ProjectRecord;
  run: PipelineRunRecord;
  topic_request_artifact: ArtifactRecord;
};

export type RunStageResponse = {
  artifact_id: string;
  artifact: ArtifactRecord;
  validation: ValidationResult;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const detail = "detail" in errorBody ? String(errorBody.detail) : response.statusText;
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export function listProjects(): Promise<ProjectRecord[]> {
  return request<ProjectRecord[]>("/projects");
}

export function createProject(topic: string, angle: string): Promise<CreateProjectResponse> {
  return request<CreateProjectResponse>("/projects", {
    method: "POST",
    body: JSON.stringify({ topic, angle }),
  });
}

export function listRuns(projectId: string): Promise<PipelineRunRecord[]> {
  return request<PipelineRunRecord[]>(`/projects/${projectId}/runs`);
}

export function listRunArtifacts(
  projectId: string,
  runId: string
): Promise<ArtifactRecord[]> {
  return request<ArtifactRecord[]>(`/projects/${projectId}/runs/${runId}/artifacts`);
}

export function runScriptBrief(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/script_brief`, {
    method: "POST",
  });
}

export function runNarrativeArc(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/narrative_arc`, {
    method: "POST",
  });
}

export function runScriptDraft(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/script_draft`, {
    method: "POST",
  });
}

export function runSceneScript(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/scene_script`, {
    method: "POST",
  });
}

export function runSemanticScene(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/semantic_scene`, {
    method: "POST",
  });
}

export function runVisualEventSequence(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(
    `/projects/${projectId}/runs/${runId}/run/visual_event_sequence`,
    {
      method: "POST",
    }
  );
}

export function runVisualPlan(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/visual_plan`, {
    method: "POST",
  });
}

export function runTiming(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/timing`, {
    method: "POST",
  });
}

export function runRenderSpec(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/render_spec`, {
    method: "POST",
  });
}

export function runRender(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/render`, {
    method: "POST",
  });
}

export function mediaUrl(storageKey: string): string {
  return `${API_BASE_URL}/media/${storageKey}`;
}

export function listArtifactParents(
  artifactId: string
): Promise<{ artifact_id: string; parents: Record<string, ArtifactRecord> }> {
  return request<{ artifact_id: string; parents: Record<string, ArtifactRecord> }>(
    `/artifacts/${artifactId}/parents`
  );
}

export function listArtifactChildren(
  artifactId: string
): Promise<{ artifact_id: string; children: ArtifactRecord[] }> {
  return request<{ artifact_id: string; children: ArtifactRecord[] }>(
    `/artifacts/${artifactId}/children`
  );
}
