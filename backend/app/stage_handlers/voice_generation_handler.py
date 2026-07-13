from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack
from domain.validators.voice_track_validator import VoiceTrackValidator
from providers.media_storage import LocalMediaStorage
from providers.voice_provider import VoiceProvider


class VoiceGenerationHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        media_storage: LocalMediaStorage,
        voice_provider: VoiceProvider,
        voice_validator: VoiceTrackValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.media_storage = media_storage
        self.voice_provider = voice_provider
        self.voice_validator = voice_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "voice_track")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "voice_generation")
        try:
            # 1. Require parent artifacts
            self.store.require_artifact(
                project_id, run_id, "review_result", for_stage="voice_generation"
            )
            
            strategy_artifact = self.store.require_artifact(
                project_id, run_id, "script_visual_strategy", for_stage="voice_generation"
            )
            strategy = ScriptVisualStrategy.model_validate(strategy_artifact.payload_json)

            hook_artifact = self.store.require_artifact(
                project_id, run_id, "hook", for_stage="voice_generation"
            )
            hook = Hook.model_validate(hook_artifact.payload_json)

            # 2. Compile full narration script text (Hook + Body Ideas)
            narration_blocks = [hook.script_text]
            for idea in strategy.ideas:
                if idea.narration.strip():
                    narration_blocks.append(idea.narration.strip())
            
            full_script_text = "\n\n".join(narration_blocks)

            # 3. Setup output file storage path
            file_name = "narration.mp3"
            storage_key = f"projects/{project_id}/runs/{run_id}/{file_name}"
            output_path = self.media_storage.ensure_parent(storage_key)

            # 4. Synthesize voice audio and word timestamps metadata
            duration_seconds, word_timestamps = self.voice_provider.synthesize(
                text=full_script_text,
                output_path=output_path,
            )

            # 5. Build and validate VoiceTrack model
            voice_track = VoiceTrack(
                voice_id=getattr(self.voice_provider, "voice_id", "Matthew"),
                audio_file_name=file_name,
                storage_key=storage_key,
                duration_seconds=duration_seconds,
                full_script_text=full_script_text,
                word_timestamps=word_timestamps,
            )

            validation = self.voice_validator.validate(voice_track)

            # 6. Save the voice_track artifact
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="voice_track",
                schema_version=voice_track.schema_version,
                payload_json=voice_track.model_dump(),
                parent_artifact_roles_json={
                    "script_visual_strategy": strategy_artifact.id,
                    "hook": hook_artifact.id,
                },
                validation_json=validation,
            )

        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "voice_generation", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "voice_generation", start_time=start)
        return artifact
