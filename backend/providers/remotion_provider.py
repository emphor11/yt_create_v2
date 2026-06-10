import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from domain.render_spec import RenderSpec


class RemotionProviderError(Exception):
    """Raised when Remotion cannot render the requested video."""


@dataclass(frozen=True)
class RemotionRenderOutput:
    output_path: Path
    size_bytes: int
    content_type: str = "video/mp4"


class RemotionProvider:
    def __init__(self, renderer_root: str | Path, timeout_seconds: int = 180):
        self.renderer_root = Path(renderer_root)
        self.timeout_seconds = timeout_seconds

    def render(self, *, render_spec: RenderSpec, output_path: Path) -> RemotionRenderOutput:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="ytcreate-render-") as temporary_directory:
            request_path = Path(temporary_directory) / "render-request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "renderSpec": render_spec.model_dump(),
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
            raise RemotionProviderError("Remotion completed but did not create an output file.")

        size_bytes = output_path.stat().st_size
        if size_bytes <= 0:
            raise RemotionProviderError("Remotion created an empty output file.")

        return RemotionRenderOutput(output_path=output_path, size_bytes=size_bytes)

    @staticmethod
    def _format_error(stdout: str, stderr: str) -> str:
        combined = "\n".join(part for part in [stdout.strip(), stderr.strip()] if part)
        return combined[-1200:] if combined else "Remotion render failed."
