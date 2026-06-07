import type { FormEvent } from "react";

type CreateProjectPageProps = {
  title: string;
  isBusy: boolean;
  onTitleChange: (title: string) => void;
  onSubmit: () => void;
};

export function CreateProjectPage({
  title,
  isBusy,
  onTitleChange,
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
        <span>Title</span>
        <input
          value={title}
          onChange={(event) => onTitleChange(event.target.value)}
          placeholder="Monthly Payments"
        />
      </label>
      <button className="primary-button" disabled={isBusy || !title.trim()} type="submit">
        Create
      </button>
    </form>
  );
}

