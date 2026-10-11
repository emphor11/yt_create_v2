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
    def __init__(self, renderer_root: str | Path, timeout_seconds: int = 1800):
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
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
                start_new_session=True,
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

    def render_world(self, *, compiled_world: dict[str, Any], output_path: Path) -> RemotionRenderOutput:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="ytcreate-world-render-") as temporary_directory:
            request_path = Path(temporary_directory) / "render-world-request.json"
            request_path.write_text(
                json.dumps(
                    {
                        "world": compiled_world,
                        "outputPath": str(output_path),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            process = subprocess.Popen(
                ["node", "scripts/render-world-spec.mjs", str(request_path)],
                cwd=self.renderer_root,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                start_new_session=True,
            )
            output_lines: list[str] = []
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    output_lines.append(line)
                    clean_line = line.strip()
                    if clean_line:
                        print(clean_line, flush=True)

            process.wait(timeout=self.timeout_seconds)
            combined_output = "".join(output_lines)
            if process.returncode != 0:
                raise RemotionProviderError(
                    self._format_error(combined_output, "")
                )
        if not output_path.exists():
            raise RemotionProviderError("Remotion completed but did not create an output file.")

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
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
                start_new_session=True,
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

