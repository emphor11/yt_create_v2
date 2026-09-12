import shutil
from pathlib import Path
from artifact_store.models import ArtifactRecord
from artifact_store.sqlite_store import ArtifactStore
from app.stage_logger import StageLogger
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack
from domain.validators.render_spec_validator import RenderSpecValidator
from engines.video_assembly_engine import VideoAssemblyEngine
from providers.media_storage import LocalMediaStorage


class VideoAssemblyHandler:
    def __init__(
        self,
        *,
        store: ArtifactStore,
        media_storage: LocalMediaStorage,
        assembly_engine: VideoAssemblyEngine,
        render_spec_validator: RenderSpecValidator,
        stage_logger: StageLogger,
    ) -> None:
        self.store = store
        self.media_storage = media_storage
        self.assembly_engine = assembly_engine
        self.render_spec_validator = render_spec_validator
        self.stage_logger = stage_logger

    def run(self, project_id: str, run_id: str) -> ArtifactRecord:
        existing = self.store.find_artifact_by_type(project_id, run_id, "render_spec")
        if existing is not None:
            return existing

        start = self.stage_logger.log_start(project_id, run_id, "video_assembly")
        try:
            # 1. Require parent artifacts
            voice_track_artifact = self.store.require_artifact(
                project_id, run_id, "voice_track", for_stage="video_assembly"
            )
            voice_track = VoiceTrack.model_validate(voice_track_artifact.payload_json)

            strategy_artifact = self.store.require_artifact(
                project_id, run_id, "script_visual_strategy", for_stage="video_assembly"
            )
            strategy = ScriptVisualStrategy.model_validate(strategy_artifact.payload_json)

            hook_artifact = self.store.require_artifact(
                project_id, run_id, "hook", for_stage="video_assembly"
            )
            hook = Hook.model_validate(hook_artifact.payload_json)

            # 2. Run the orchestrator engine (branch on visual_mode / composition_plan)
            scene_id = f"scene_{project_id}"
            raw_comp_plan = (
                strategy_artifact.payload_json.get("composition_plan")
                if isinstance(strategy_artifact.payload_json, dict)
                else None
            )

            if raw_comp_plan:
                from domain.composition_plan import FullCompositionPlan
                from engines.composition_assembly_engine import CompositionAssemblyEngine

                comp_plan = FullCompositionPlan.model_validate(raw_comp_plan)
                comp_assembly_engine = CompositionAssemblyEngine()
                render_spec = comp_assembly_engine.run(
                    scene_id=scene_id,
                    hook=hook,
                    strategy=strategy,
                    composition_plan=comp_plan,
                    voice_track=voice_track,
                )
            else:
                render_spec = self.assembly_engine.run(
                    scene_id=scene_id,
                    hook=hook,
                    strategy=strategy,
                    voice_track=voice_track,
                )

            # 3. Setup Remotion Public Folder Copying for staticFile resolution
            remotion_public_dir = Path("/Users/dakshyadav/Documents/YTcreate_V2/renderer/remotion/public")
            remotion_public_dir.mkdir(parents=True, exist_ok=True)

            # Copy Voice Track narration audio
            audio_source = self.media_storage.path_for_key(voice_track.storage_key)
            audio_public_filename = f"{run_id}_narration.mp3"
            audio_public_path = remotion_public_dir / audio_public_filename
            shutil.copy2(audio_source, audio_public_path)

            # Update audio local path to be relative to Remotion public directory
            render_spec.props.audio.local_path = audio_public_filename

            # Copy and resolve assets
            for scene in render_spec.props.scenes:
                if scene.asset:
                    if scene.asset.local_path:
                        asset_source = Path(scene.asset.local_path)
                        if asset_source.exists():
                            # Extract extension
                            ext = asset_source.suffix.lstrip(".") or ("mp4" if scene.asset.asset_type == "video" else "jpg")
                            asset_public_filename = f"{run_id}_{scene.scene_id}_{scene.asset.asset_id}.{ext}"
                            asset_public_path = remotion_public_dir / asset_public_filename
                            shutil.copy2(asset_source, asset_public_path)
                            
                            # Update asset local path to be relative to Remotion public directory
                            scene.asset.local_path = asset_public_filename
                        else:
                            # Asset is not cached/downloaded - clear local_path to prevent staticFile crash
                            scene.asset.local_path = ""
                    else:
                        scene.asset.local_path = ""

            # 4. Validate
            validation = self.render_spec_validator.validate(render_spec)

            # 5. Save the artifact record
            artifact = self.store.save_artifact(
                project_id=project_id,
                run_id=run_id,
                artifact_type="render_spec",
                schema_version=render_spec.schema_version,
                payload_json=render_spec.model_dump(),
                parent_artifact_roles_json={
                    "voice_track": voice_track_artifact.id,
                    "script_visual_strategy": strategy_artifact.id,
                    "hook": hook_artifact.id,
                },
                validation_json=validation,
            )

        except Exception as exc:
            self.stage_logger.log_error(project_id, run_id, "video_assembly", error=exc, start_time=start)
            raise

        self.stage_logger.log_finish(project_id, run_id, "video_assembly", start_time=start)
        return artifact
