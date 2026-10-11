from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any
from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.storyboard_foundation import WorldFoundationSpec
from domain.visual_world import VisualWorldSpec
from domain.voice_track import VoiceTrack
from compiler.world_compiler import WorldCompiler
from engines.scene_storyboarder_engine import SceneStoryboarderEngine
from domain.validation import ValidationResult
from providers.media_storage import LocalMediaStorage


class WorldCompilerHandler:
    """Stage handler for compiling VisualWorldSpec + VoiceTrack into CompiledWorldSpec."""

    def __init__(
        self,
        *,
        store: ArtifactStore,
        media_storage: LocalMediaStorage,
        stage_logger: StageLogger,
        compiler: WorldCompiler | None = None,
    ) -> None:
        self.store = store
        self.media_storage = media_storage
        self.stage_logger = stage_logger
        self.compiler = compiler or WorldCompiler()

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "compiled_world")
        if existing is not None and existing.status not in ("failed", "error"):
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "world_compiler")
        try:
            storyboard_artifact = self.store.require_artifact(
                project_id, run_id, "storyboard", for_stage="world_compiler"
            )
            sb_payload = storyboard_artifact.payload_json
            first_beat = (sb_payload.get("beats", [{}])[0] or {})
            if "elements" in first_beat:
                foundation = WorldFoundationSpec.model_validate(sb_payload)
                visual_world = SceneStoryboarderEngine.assemble_visual_world(foundation)
            elif "world_foundation" in sb_payload:
                foundation = WorldFoundationSpec.model_validate(sb_payload["world_foundation"])
                visual_world = SceneStoryboarderEngine.assemble_visual_world(foundation)
            else:
                allowed_keys = {"schema_version", "world_id", "beats", "objects", "relationships", "object_state_tracks"}
                sb_data = {
                    k: v for k, v in sb_payload.items()
                    if k in allowed_keys
                }
                visual_world = VisualWorldSpec.model_validate(sb_data)

            voice_track_artifact = self.store.require_artifact(
                project_id, run_id, "voice_track", for_stage="world_compiler"
            )
            voice_track = VoiceTrack.model_validate(voice_track_artifact.payload_json)

            # Copy Voice Track narration audio to Remotion public dir so it can play
            remotion_public_dir = Path("/Users/dakshyadav/Documents/YTcreate_V2/renderer/remotion/public")
            remotion_public_dir.mkdir(parents=True, exist_ok=True)
            if voice_track.storage_key:
                audio_source = self.media_storage.path_for_key(voice_track.storage_key)
                if audio_source.exists():
                    audio_public_filename = f"{run_id}_narration.mp3"
                    audio_public_path = remotion_public_dir / audio_public_filename
                    shutil.copy2(audio_source, audio_public_path)

            compiled_world = self.compiler.compile(
                world=visual_world,
                voice_track=voice_track,
            )

            validation = ValidationResult(
                status="valid",
                errors=[],
                warnings=[],
            )

            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="compiled_world",
                schema_version="2.0.0",
                payload_json=compiled_world.model_dump(),
                parent_artifact_roles_json={
                    "storyboard": storyboard_artifact.id,
                    "voice_track": voice_track_artifact.id,
                },
                validation_json=validation,
            )
        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "world_compiler", error=exc, start_time=start)
            raise
        self.stage_logger.log_finish(project_id, run_id, "world_compiler", start_time=start)
        return artifact
