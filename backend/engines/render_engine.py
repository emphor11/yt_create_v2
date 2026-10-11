from pathlib import Path
import subprocess

from domain.render_spec import RenderSpec
from domain.video import Video
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionProvider, RemotionProviderError


class RenderEngine:
    def __init__(
        self,
        *,
        media_storage: LocalMediaStorage,
        remotion_provider: RemotionProvider,
    ):
        self.media_storage = media_storage
        self.remotion_provider = remotion_provider

    def run(self, *, render_spec: RenderSpec, project_id: str, run_id: str) -> Video:
        file_name = f"{render_spec.scene_id}.mp4"
        storage_key = f"projects/{project_id}/runs/{run_id}/{file_name}"
        output_path = self.media_storage.ensure_parent(storage_key)

        try:
            render_output = self.remotion_provider.render(
                render_spec=render_spec,
                output_path=output_path,
            )
        except Exception as error:
            return self._failed_video(render_spec, file_name, str(error))

        return Video(
            scene_id=render_spec.scene_id,
            render_status="succeeded",
            file_name=file_name,
            storage_key=storage_key,
            content_type=render_output.content_type,
            size_bytes=render_output.size_bytes,
            fps=render_spec.fps,
            duration_frames=render_spec.duration_frames,
        )

    def run_world(
        self,
        *,
        compiled_world_payload: dict[str, Any],
        project_id: str,
        run_id: str,
        audio_path: Path | None = None,
    ) -> Video:
        world_id = compiled_world_payload.get("world_id", "world")
        file_name = f"{world_id}_{project_id}.mp4"
        storage_key = f"projects/{project_id}/runs/{run_id}/{file_name}"
        output_path = self.media_storage.ensure_parent(storage_key)

        fps = compiled_world_payload.get("canvas_config", {}).get("fps", 30)
        duration_frames = compiled_world_payload.get("total_duration_frames", 300)

        try:
            render_output = self.remotion_provider.render_world(
                compiled_world=compiled_world_payload,
                output_path=output_path,
            )
            if audio_path and Path(audio_path).exists():
                self._mux_audio(video_path=output_path, audio_path=Path(audio_path))
        except Exception as error:
            return Video(
                scene_id=world_id,
                render_status="failed",
                file_name=file_name,
                content_type="video/mp4",
                fps=fps,
                duration_frames=duration_frames,
                error_message=str(error)[-1200:] or "Render failed.",
            )

        size_bytes = output_path.stat().st_size if output_path.exists() else render_output.size_bytes
        return Video(
            scene_id=world_id,
            render_status="succeeded",
            file_name=file_name,
            storage_key=storage_key,
            content_type=render_output.content_type,
            size_bytes=size_bytes,
            fps=fps,
            duration_frames=duration_frames,
        )

    @staticmethod
    def _mux_audio(*, video_path: Path, audio_path: Path) -> None:
        temp_output = video_path.with_name(f"temp_mux_{video_path.name}")
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            str(temp_output),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0 and temp_output.exists() and temp_output.stat().st_size > 0:
            temp_output.replace(video_path)

    @staticmethod
    def _failed_video(render_spec: RenderSpec, file_name: str, error_message: str) -> Video:
        return Video(
            scene_id=render_spec.scene_id,
            render_status="failed",
            file_name=file_name,
            content_type="video/mp4",
            fps=render_spec.fps,
            duration_frames=render_spec.duration_frames,
            error_message=error_message[-1200:] or "Render failed.",
        )
