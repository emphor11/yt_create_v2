export type ArtifactStatus = "valid" | "warning" | "blocked" | "failed";
export type StageStatus = ArtifactStatus | "missing";
export type RunMode = "deterministic" | "ai";

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
  mode: RunMode;
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

export type PipelineStageSummary = {
  stage: string;
  artifact_type: string;
  artifact_id: string | null;
  status: StageStatus;
  error_count: number;
  warning_count: number;
  errors: string[];
  warnings: string[];
};

export type RunStatusResponse = {
  project_id: string;
  run_id: string;
  stages: PipelineStageSummary[];
};

export type ArtifactTraceNode = {
  artifact_id: string;
  artifact_type: string;
  status: ArtifactStatus;
  role_path: string;
  depth: number;
};

export type ArtifactTrace = {
  artifact_id: string;
  ancestors: ArtifactTraceNode[];
  descendants: ArtifactTraceNode[];
};

export type RegenerateDescendantsResponse = {
  artifact_id: string;
  deleted_artifacts: ArtifactRecord[];
  next_stage: string | null;
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

export type DurationProfile = "short_2min" | "long_5min";
export type VisualMode = "legacy" | "composition";

export function listProjects(): Promise<ProjectRecord[]> {
  return request<ProjectRecord[]>("/projects");
}

export function createProject(
  topic: string,
  angle: string,
  mode: RunMode = "ai",
  durationProfile: DurationProfile = "short_2min",
  visualMode: VisualMode = "composition"
): Promise<CreateProjectResponse> {
  return request<CreateProjectResponse>("/projects", {
    method: "POST",
    body: JSON.stringify({
      topic,
      angle,
      mode,
      duration_profile: durationProfile,
      visual_mode: visualMode,
    }),
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

export function getRunStatus(
  projectId: string,
  runId: string
): Promise<RunStatusResponse> {
  return request<RunStatusResponse>(`/projects/${projectId}/runs/${runId}/status`);
}

export function runResearch(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/research`, {
    method: "POST",
  });
}

export function runNarrativePlan(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/narrative_plan`, {
    method: "POST",
  });
}

export function runHook(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/hook`, {
    method: "POST",
  });
}

export function runScriptVisualStrategy(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/script_visual_strategy`, {
    method: "POST",
  });
}

export function runQualityReview(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/quality_review`, {
    method: "POST",
  });
}

export function runVoiceGeneration(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/voice_generation`, {
    method: "POST",
  });
}

export function runVideoAssembly(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/video_assembly`, {
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

export function runYoutubeMetadata(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/youtube_metadata`, {
    method: "POST",
  });
}

export function runThumbnail(
  projectId: string,
  runId: string
): Promise<RunStageResponse> {
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/thumbnail`, {
    method: "POST",
  });
}

export type YouTubeAccountInfo = {
  configured: boolean;
  channel_title: string | null;
  account_type: "test" | "production";
};

export type YouTubeStatusResponse = {
  test: YouTubeAccountInfo;
  production: YouTubeAccountInfo;
};

export function getYouTubeStatus(): Promise<YouTubeStatusResponse> {
  return request<YouTubeStatusResponse>("/youtube/status");
}

export function runYoutubeUpload(
  projectId: string,
  runId: string,
  targetAccount: "test" | "production" = "test"
): Promise<RunStageResponse> {
  const query = targetAccount === "production" ? "?target_account=production" : "?target_account=test";
  return request<RunStageResponse>(`/projects/${projectId}/runs/${runId}/run/youtube_upload${query}`, {
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

export function getArtifactTrace(artifactId: string): Promise<ArtifactTrace> {
  return request<ArtifactTrace>(`/artifacts/${artifactId}/trace`);
}

export function regenerateDescendants(
  projectId: string,
  runId: string,
  artifactId: string
): Promise<RegenerateDescendantsResponse> {
  return request<RegenerateDescendantsResponse>(
    `/projects/${projectId}/runs/${runId}/artifacts/${artifactId}/regenerate-descendants`,
    {
      method: "POST",
    }
  );
}
