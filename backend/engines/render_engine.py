import subprocess

from domain.render_spec import RenderSpec
from domain.continuous_story_plan import ContinuousStoryPlanArtifact
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

    def run(
        self,
        *,
        render_spec: RenderSpec | None = None,
        continuous_story_plan: ContinuousStoryPlanArtifact | None = None,
        project_id: str,
        run_id: str,
    ) -> Video:
        if continuous_story_plan is not None:
            scene_id = continuous_story_plan.story_id
            fps = continuous_story_plan.fps
            duration_frames = continuous_story_plan.duration_in_frames

            # Stage audio if storage key is provided and resolvable
            if continuous_story_plan.audio_storage_key:
                source_audio_path = self.media_storage.path_for_key(continuous_story_plan.audio_storage_key)
                if source_audio_path.exists():
                    self.remotion_provider.stage_public_asset(
                        source_audio_path,
                        continuous_story_plan.audio_file_name,
                    )

            file_name = f"{scene_id}.mp4"
            storage_key = f"projects/{project_id}/runs/{run_id}/{file_name}"
            output_path = self.media_storage.ensure_parent(storage_key)

            try:
                render_output = self.remotion_provider.render(
                    story_plan=continuous_story_plan.plan,
                    output_path=output_path,
                )
            except (OSError, RemotionProviderError, TimeoutError, subprocess.SubprocessError) as error:
                return self._failed_video_direct(scene_id, file_name, fps, duration_frames, str(error))

            return Video(
                scene_id=scene_id,
                render_status="succeeded",
                file_name=file_name,
                storage_key=storage_key,
                content_type=render_output.content_type,
                size_bytes=render_output.size_bytes,
                fps=fps,
                duration_frames=duration_frames,
            )
        else:
            if render_spec is None:
                raise ValueError("Either render_spec or continuous_story_plan must be provided to RenderEngine.run()")
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
    def _failed_video_direct(
        scene_id: str, file_name: str, fps: int, duration_frames: int, error_message: str
    ) -> Video:
        return Video(
            scene_id=scene_id,
            render_status="failed",
            file_name=file_name,
            content_type="video/mp4",
            fps=fps,
            duration_frames=duration_frames,
            error_message=error_message[-1200:] or "Render failed.",
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
