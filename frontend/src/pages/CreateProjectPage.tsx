import type { FormEvent } from "react";
import type { RunMode } from "../api/client";

type CreateProjectPageProps = {
  topic: string;
  angle: string;
  runMode: RunMode;
  isBusy: boolean;
  onTopicChange: (topic: string) => void;
  onAngleChange: (angle: string) => void;
  onRunModeChange: (runMode: RunMode) => void;
  onSubmit: () => void;
};

export function CreateProjectPage({
  topic,
  angle,
  runMode,
  isBusy,
  onTopicChange,
  onAngleChange,
  onRunModeChange,
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
