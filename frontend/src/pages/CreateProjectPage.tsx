import type { FormEvent } from "react";

type CreateProjectPageProps = {
  topic: string;
  angle: string;
  isBusy: boolean;
  onTopicChange: (topic: string) => void;
  onAngleChange: (angle: string) => void;
  onSubmit: () => void;
};

export function CreateProjectPage({
  topic,
  angle,
  isBusy,
  onTopicChange,
  onAngleChange,
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
