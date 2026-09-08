from pathlib import Path

from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.tts_chunk import TTSChunkResult
from domain.voice_track import VoiceTrack, WordTimestamp
from domain.validators.voice_track_validator import VoiceTrackValidator
from engines.audio_merger import AudioMerger
from engines.tts_chunker import TTSChunker
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
        chunker: TTSChunker | None = None,
        audio_merger: AudioMerger | None = None,
    ) -> None:
        self.store = store
        self.media_storage = media_storage
        self.voice_provider = voice_provider
        self.voice_validator = voice_validator
        self.stage_logger = stage_logger
        self.chunker = chunker or TTSChunker()
        self.audio_merger = audio_merger or AudioMerger()

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

            # 2. Compile full narration script sections (Hook + Body Ideas)
            sections: list[tuple[str, str]] = [("hook", hook.script_text)]
            for idea in strategy.ideas:
                if idea.narration.strip():
                    sections.append((idea.idea_id, idea.narration.strip()))

            narration_blocks = [text for _, text in sections]
            full_script_text = "\n\n".join(narration_blocks)

            # 3. Setup output file storage path
            file_name = "narration.mp3"
            storage_key = f"projects/{project_id}/runs/{run_id}/{file_name}"
            output_path = self.media_storage.ensure_parent(storage_key)
            chunks_dir = output_path.parent / "chunks"

            # 4. Chunk narration using TTSChunker
            chunks = self.chunker.chunk_sections(sections)

            # 5. Synthesize chunks via voice_provider
            if hasattr(self.voice_provider, "synthesize_chunks"):
                chunk_results = self.voice_provider.synthesize_chunks(
                    chunks=chunks,
                    output_dir=chunks_dir,
                )
            else:
                # Fallback for providers that only implement synthesize()
                duration_seconds, word_timestamps = self.voice_provider.synthesize(
                    text=full_script_text,
                    output_path=output_path,
                )
                chunk_results = [
                    TTSChunkResult(
                        chunk_id="chunk_001",
                        sequence=1,
                        source_id="narration",
                        text=full_script_text,
                        audio_path=str(output_path),
                        word_timestamps=[ts.model_dump() for ts in word_timestamps],
                        duration_ms=int(duration_seconds * 1000),
                        duration_seconds=duration_seconds,
                    )
                ]

            # 6. Merge audio chunks and compute global word timestamps (Step 3)
            master_duration_seconds, global_word_timestamps = self.audio_merger.merge_chunks(
                chunk_results=chunk_results,
                output_path=output_path,
            )

            # 7. Build and validate VoiceTrack model
            voice_track = VoiceTrack(
                voice_id=getattr(self.voice_provider, "voice_id", "Matthew"),
                audio_file_name=file_name,
                storage_key=storage_key,
                duration_seconds=master_duration_seconds,
                full_script_text=full_script_text,
                word_timestamps=global_word_timestamps,
                chunks=[c.model_dump() for c in chunk_results],
            )

            validation = self.voice_validator.validate(voice_track)

            # 8. Save the voice_track artifact
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
