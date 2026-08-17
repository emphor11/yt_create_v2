import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from domain.validation import ValidationResult
from providers.media_storage import LocalMediaStorage


def make_client(tmp_path) -> tuple[TestClient, ArtifactStore, LocalMediaStorage]:
    store = ArtifactStore(tmp_path / "assembly_test.db")
    store.initialize()
    
    media_path = tmp_path / "media"
    media_storage = LocalMediaStorage(media_path)
    
    app = create_app()
    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: build_pipeline_service(
        store,
        llm_provider=None,
    )
    return TestClient(app), store, media_storage


def setup_project_ready_for_assembly(store: ArtifactStore) -> tuple[str, str]:
    project = store.create_project("Assembly Test Project")
    run = store.create_run(project.id, mode="ai")

    # 1. Save Hook
    hook_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json={
            "conceptual_hook": "Golden Handcuffs",
            "script_text": "First word second word third word.",
            "visual_directives": [
                {
                    "beat_id": "hook_beat_1",
                    "visual_instruction": "Clock animation zooming in.",
                    "onscreen_text": "Illusion of security"
                }
            ]
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 2. Save ScriptVisualStrategy
    strategy_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json={
            "thesis": "Financial freedom over salary",
            "ideas": [
                {
                    "idea_id": "idea_01",
                    "title": "Lifestyle Trap",
                    "focus_concept": "Lifestyle Inflation",
                    "core_teaching_point": "Expenses rise with salary.",
                    "narration": "Fourth word fifth word sixth word.",
                    "visual_sequence": [
                        {
                            "beat_id": "body_beat_1",
                            "preferred_component": "SplitComparison",
                            "visual_goal": "Show rent vs buy",
                            "asset_query": "renting apartment",
                            "notes": None,
                            "component_data": {
                                "left_label": "Rent",
                                "left_value": 3000,
                                "left_unit": "USD",
                                "right_label": "Buy",
                                "right_value": 5000,
                                "right_unit": "USD",
                                "left_role": "rent",
                                "right_role": "buy"
                            }
                        }
                    ]
                }
            ]
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 3. Save VoiceTrack (Polly outputs)
    voice_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="voice_track",
        schema_version="1",
        payload_json={
            "voice_id": "Matthew",
            "audio_file_name": "narration.mp3",
            "storage_key": "runs/run_xxx/narration.mp3",
            "duration_seconds": 6.0,
            "full_script_text": "First word second word third word.\n\nFourth word fifth word sixth word.",
            "word_timestamps": [
                {"word": "First", "start_ms": 0, "end_ms": 500},
                {"word": "word", "start_ms": 500, "end_ms": 1000},
                {"word": "second", "start_ms": 1000, "end_ms": 1500},
                {"word": "word", "start_ms": 1500, "end_ms": 2000},
                {"word": "third", "start_ms": 2000, "end_ms": 2500},
                {"word": "word", "start_ms": 2500, "end_ms": 3000},
                {"word": "Fourth", "start_ms": 3000, "end_ms": 3500},
                {"word": "word", "start_ms": 3500, "end_ms": 4000},
                {"word": "fifth", "start_ms": 4000, "end_ms": 4500},
                {"word": "word", "start_ms": 4500, "end_ms": 5000},
                {"word": "sixth", "start_ms": 5000, "end_ms": 5500},
                {"word": "word", "start_ms": 5500, "end_ms": 6000}
            ]
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    return project.id, run.id


def test_video_assembly_pipeline_stage(tmp_path):
    client, store, media_storage = make_client(tmp_path)
    project_id, run_id = setup_project_ready_for_assembly(store)
    
    # Create the mock narration file on disk
    mock_audio_path = media_storage.ensure_parent("runs/run_xxx/narration.mp3")
    mock_audio_path.write_bytes(b"mock audio data")
    
    # Also write to the real backend media directory to support the build_pipeline_service resolution
    real_media_path = Path("/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/runs/run_xxx/narration.mp3")
    real_media_path.parent.mkdir(parents=True, exist_ok=True)
    real_media_path.write_bytes(b"mock audio data")

    # Trigger stage execution with mocked asset resolver to avoid network requests
    from unittest.mock import patch
    from domain.video_assembly_props import AssetReference
    
    mock_asset = AssetReference(
        asset_id="asset_body_beat_1",
        asset_type="video",
        source="pexels",
        query="renting apartment",
        local_path=str(tmp_path / "mock_video.mp4"),
        url="http://example.com/mock.mp4",
        asset_status="cached",
    )
    
    # Write a dummy mock video file to disk so that local path resolution exists
    (tmp_path / "mock_video.mp4").write_bytes(b"mock video data")

    with patch("engines.video_assembly.asset_resolver.AssetResolver.resolve_asset", return_value=mock_asset):
        response = client.post(
            f"/projects/{project_id}/runs/{run_id}/run/video_assembly"
        )
    assert response.status_code == 200, f"Error: {response.text}"

    data = response.json()
    assert data["artifact"]["artifact_type"] == "render_spec"
    assert data["validation"]["status"] == "valid"

    # Fetch and verify RenderSpec payload from database
    artifact = store.get_artifact(data["artifact_id"])
    payload = artifact.payload_json

    assert payload["composition"] == "VideoAssembly"
    assert payload["fps"] == 30
    assert payload["duration_frames"] == 180  # 6.0 seconds * 30 fps

    # Verify frame spans structure and contiguity
    spans = payload["frame_spans"]
    assert len(spans) == 2  # 1 Hook beat + 1 body beat
    
    assert spans[0]["event_id"] == "scene_001"
    assert spans[0]["start_frame"] == 0
    assert spans[0]["end_frame"] > 0

    assert spans[1]["event_id"] == "scene_002"
    assert spans[1]["start_frame"] == spans[0]["end_frame"]
    assert spans[1]["end_frame"] == 180

    # Verify typed properties are present
    props = payload["props"]
    assert "scenes" in props
    assert "audio" in props
    assert len(props["scenes"]) == 2
    assert props["audio"]["audio_file_name"] == "narration.mp3"

    # Verify rendering-specific component props
    scenes = props["scenes"]
    assert scenes[0]["component"]["component_id"] == "Typography"
    assert scenes[0]["component"]["props"]["text"] == "Illusion of security"
    assert scenes[0]["component"]["props"]["subtitle"] == "First word second word third word."

    assert scenes[1]["component"]["component_id"] == "SplitComparison"
    assert scenes[1]["component"]["props"]["leftLabel"] == "Rent"
    assert scenes[1]["component"]["props"]["leftValue"] == 3000
