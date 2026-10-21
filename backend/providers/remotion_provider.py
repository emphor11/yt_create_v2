import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from domain.render_spec import RenderSpec


class RemotionProviderError(Exception):
    """Raised when Remotion cannot render the requested video."""


@dataclass(frozen=True)
class RemotionRenderOutput:
    output_path: Path
    size_bytes: int
    content_type: str = "video/mp4"


class RemotionProvider:
    def __init__(self, renderer_root: str | Path, timeout_seconds: int = 600):
        self.renderer_root = Path(renderer_root)
        self.timeout_seconds = timeout_seconds

    def stage_public_asset(self, source_path: Path, filename: str) -> Path:
        """Stages an asset into Remotion's public directory for staticFile() access."""
        public_dir = self.renderer_root / "public"
        public_dir.mkdir(parents=True, exist_ok=True)
        target_path = public_dir / filename
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if not target_path.exists() or target_path.stat().st_size != source_path.stat().st_size:
            import shutil
            shutil.copy2(source_path, target_path)
        return target_path

    def render(
        self,
        *,
        render_spec: RenderSpec | None = None,
        story_plan: dict[str, Any] | None = None,
        output_path: Path,
    ) -> RemotionRenderOutput:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if story_plan is not None:
            render_spec_payload = {
                "composition": "StoryScene",
                "scene_id": story_plan.get("id", "continuous_story"),
                "fps": story_plan.get("fps", 30),
                "duration_frames": story_plan.get("durationInFrames", 380),
                "props": {"plan": story_plan},
                "plan": story_plan,
            }
        elif render_spec is not None:
            render_spec_payload = render_spec.model_dump()
        else:
            raise ValueError("Either render_spec or story_plan must be provided to RemotionProvider.render()")

        with tempfile.TemporaryDirectory(prefix="ytcreate-render-") as temporary_directory:
            request_path = Path(temporary_directory) / "render-request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "renderSpec": render_spec_payload,
                        "outputPath": str(output_path),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["node", "scripts/render-spec.mjs", str(request_path)],
                cwd=self.renderer_root,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )

        if completed.returncode != 0:
            raise RemotionProviderError(
                self._format_error(completed.stdout, completed.stderr)
            )
        if not output_path.exists():
            raise RemotionProviderError(
                "Remotion completed but did not create an output file.\n"
                + self._format_error(completed.stdout, completed.stderr)
            )

        size_bytes = output_path.stat().st_size
        if size_bytes <= 0:
            raise RemotionProviderError("Remotion created an empty output file.")

        return RemotionRenderOutput(output_path=output_path, size_bytes=size_bytes)

    def render_still(
        self,
        *,
        composition: str,
        input_props: dict[str, Any],
        output_path: Path,
    ) -> RemotionRenderOutput:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="ytcreate-still-") as temporary_directory:
            request_path = Path(temporary_directory) / "still-request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "composition": composition,
                        "inputProps": input_props,
                        "outputPath": str(output_path),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["node", "scripts/render-still.mjs", str(request_path)],
                cwd=self.renderer_root,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )

        if completed.returncode != 0:
            raise RemotionProviderError(
                self._format_error(completed.stdout, completed.stderr)
            )
        if not output_path.exists():
            raise RemotionProviderError("Remotion completed but did not create an output still image.")

        size_bytes = output_path.stat().st_size
        if size_bytes <= 0:
            raise RemotionProviderError("Remotion created an empty output still image.")

        return RemotionRenderOutput(output_path=output_path, size_bytes=size_bytes, content_type="image/png")

    @staticmethod
    def _format_error(stdout: str, stderr: str) -> str:
        combined = "\n".join(part for part in [stdout.strip(), stderr.strip()] if part)
        return combined[-1200:] if combined else "Remotion render failed."

