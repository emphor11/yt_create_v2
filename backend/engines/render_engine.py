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
        except (OSError, RemotionProviderError, TimeoutError, subprocess.SubprocessError) as error:
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
