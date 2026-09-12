import type { FormEvent } from "react";
import type { DurationProfile, RunMode, VisualMode } from "../api/client";

type CreateProjectPageProps = {
  topic: string;
  angle: string;
  runMode: RunMode;
  durationProfile: DurationProfile;
  visualMode: VisualMode;
  isBusy: boolean;
  onTopicChange: (topic: string) => void;
  onAngleChange: (angle: string) => void;
  onRunModeChange: (runMode: RunMode) => void;
  onDurationProfileChange: (durationProfile: DurationProfile) => void;
  onVisualModeChange: (visualMode: VisualMode) => void;
  onSubmit: () => void;
};

export function CreateProjectPage({
  topic,
  angle,
  runMode,
  durationProfile,
  visualMode,
  isBusy,
  onTopicChange,
  onAngleChange,
  onRunModeChange,
  onDurationProfileChange,
  onVisualModeChange,
  onSubmit,
}: CreateProjectPageProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form className="panel create-project" onSubmit={handleSubmit}>
      <div>
        <p className="section-label">Project</p>
        <h2>Create Project</h2>
      </div>
      <label className="field">
        <span>Topic</span>
        <input
          value={topic}
          onChange={(event) => onTopicChange(event.target.value)}
          placeholder="Why Monthly Payments Feel Cheap"
        />
      </label>
      <label className="field">
        <span>Angle</span>
        <input
          value={angle}
          onChange={(event) => onAngleChange(event.target.value)}
          placeholder="How EMIs hide total cost"
        />
      </label>
      <fieldset className="field mode-field">
        <legend>Target Duration</legend>
        <div className="mode-options">
          <label
            className={
              durationProfile === "short_2min" ? "mode-option active" : "mode-option"
            }
          >
            <input
              checked={durationProfile === "short_2min"}
              name="duration-profile"
              onChange={() => onDurationProfileChange("short_2min")}
              type="radio"
            />
            <span>Short (2 min)</span>
          </label>
          <label
            className={
              durationProfile === "long_5min" ? "mode-option active" : "mode-option"
            }
          >
            <input
              checked={durationProfile === "long_5min"}
              name="duration-profile"
              onChange={() => onDurationProfileChange("long_5min")}
              type="radio"
            />
            <span>Long (5 min)</span>
          </label>
        </div>
      </fieldset>
      <fieldset className="field mode-field">
        <legend>Visual System</legend>
        <div className="mode-options">
          <label
            className={
              visualMode === "composition" ? "mode-option active" : "mode-option"
            }
          >
            <input
              checked={visualMode === "composition"}
              name="visual-mode"
              onChange={() => onVisualModeChange("composition")}
              type="radio"
            />
            <span>Composition (New)</span>
          </label>
          <label
            className={
              visualMode === "legacy" ? "mode-option active" : "mode-option"
            }
          >
            <input
              checked={visualMode === "legacy"}
              name="visual-mode"
              onChange={() => onVisualModeChange("legacy")}
              type="radio"
            />
            <span>Legacy System</span>
          </label>
        </div>
      </fieldset>
      <fieldset className="field mode-field">
        <legend>Mode</legend>
        <div className="mode-options">
          <label className={runMode === "deterministic" ? "mode-option active" : "mode-option"}>
            <input
              checked={runMode === "deterministic"}
              name="run-mode"
              onChange={() => onRunModeChange("deterministic")}
              type="radio"
            />
            <span>Deterministic</span>
          </label>
          <label className={runMode === "ai" ? "mode-option active" : "mode-option"}>
            <input
              checked={runMode === "ai"}
              name="run-mode"
              onChange={() => onRunModeChange("ai")}
              type="radio"
            />
            <span>AI</span>
          </label>
        </div>
      </fieldset>
      <button
        className="primary-button"
        disabled={isBusy || !topic.trim() || !angle.trim()}
        type="submit"
      >
        Create
      </button>
    </form>
  );
}
