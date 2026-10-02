import json
import re
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_artifact_store, get_pipeline_service
from app.main import create_app
from app.pipeline_service import build_pipeline_service
from artifact_store.sqlite_store import ArtifactStore
from domain.composition_plan import (
    FullCompositionPlan,
    HookCompositionPlan,
    IdeaCompositionPlan,
    CompositionBeat,
)
from domain.hook import Hook
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea, VoiceCue
from domain.validation import ValidationResult
from domain.video_assembly_props import AssetReference
from engines.ssml_validator import SSMLValidator
from providers.media_storage import LocalMediaStorage


def _generate_mp3_bytes(duration_sec: float) -> bytes:
    """Generates valid 24kHz mono MP3 bytes of exact duration using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-t", f"{duration_sec:.2f}",
        "-c:a", "libmp3lame",
        "-f", "mp3",
        "pipe:1"
    ]
    res = subprocess.run(cmd, capture_output=True, check=True)
    return res.stdout


def _setup_e2e_client_and_store(tmp_path: Path):
    db_path = tmp_path / "e2e_test.db"
    store = ArtifactStore(db_path)
    store.initialize()

    media_dir = tmp_path / "media"
    media_storage = LocalMediaStorage(media_dir)

    app = create_app()
    service = build_pipeline_service(store, llm_provider=None)

    # Wire media storage to stage handlers
    from domain.pipeline_stage import PipelineStage
    voice_handler = service.router._handlers[PipelineStage.VOICE_GENERATION]
    voice_handler.media_storage = media_storage

    assembly_handler = service.router._handlers[PipelineStage.VIDEO_ASSEMBLY]
    assembly_handler.media_storage = media_storage

    app.dependency_overrides[get_artifact_store] = lambda: store
    app.dependency_overrides[get_pipeline_service] = lambda: service

    client = TestClient(app)
    return client, store, media_storage


def _create_e2e_project_artifacts(
    store: ArtifactStore,
    hook_voice_cues: list[VoiceCue] | None = None,
    idea_voice_cues: list[VoiceCue] | None = None,
    special_text: bool = False,
) -> tuple[str, str]:
    project = store.create_project("Wealth Unpacked E2E Test")
    run = store.create_run(project.id, mode="ai")

    # 1. Research Packet
    res_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="research_packet",
        schema_version="1",
        payload_json={
            "topic": "Home Loan Amortization Secrets",
            "audience": "investors",
            "channel": "Wealth Unpacked",
            "verified_facts": ["Long tenure increases interest by over 200%."],
            "statistics": [],
            "concepts": ["Amortization", "Compound Debt"],
            "trusted_sources": ["RBI Report"],
        },
        parent_artifact_roles_json={},
        validation_json=ValidationResult(status="valid"),
    )

    # 2. Narrative Plan
    plan_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="narrative_plan",
        schema_version="1",
        payload_json={
            "thesis": "A lower monthly EMI is a psychological trap that doubles your total interest.",
            "target_pain_point": "High loan EMI burden",
            "conceptual_hook": "The 30-Year Illusion",
            "narrative_arc_type": "Problem-Agitation-Solution",
            "scene_beats": [
                {
                    "scene_id": "scene_01",
                    "title": "The Hidden Cost",
                    "focus_concept": "Amortization",
                    "core_teaching_point": "Tenure extension increases total repayment.",
                }
            ],
        },
        parent_artifact_roles_json={"research_packet": res_art.id},
        validation_json=ValidationResult(status="valid"),
    )

    # 3. Hook Artifact (with voice cues)
    hook_script = (
        "AT&T & Verizon < 5% yield > competitors with hidden fees."
        if special_text
        else "On paper, a lower monthly EMI looks like relief. Until you calculate the real cost."
    )
    hook_cues = (
        hook_voice_cues
        if hook_voice_cues is not None
        else [
            VoiceCue(anchor="relief", pause_after_ms=400),
            VoiceCue(anchor="real cost", rate=92, volume_db=2),
        ]
    )
    hook_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="hook",
        schema_version="1",
        payload_json={
            "conceptual_hook": "The 30-Year Illusion",
            "script_text": hook_script,
            "voice_cues": [c.model_dump() for c in hook_cues],
        },
        parent_artifact_roles_json={"research_packet": res_art.id, "narrative_plan": plan_art.id},
        validation_json=ValidationResult(status="valid"),
    )

    # 4. ScriptVisualStrategy with FullCompositionPlan (multi-visual trigger words)
    idea_narration = (
        "Banks stretch your loan tenure to thirty years. The monthly burden drops, but total interest explodes."
    )
    idea_cues = (
        idea_voice_cues
        if idea_voice_cues is not None
        else [
            VoiceCue(anchor="thirty years", rate=88),
            VoiceCue(anchor="explodes", pause_after_ms=500),
        ]
    )

    comp_plan = FullCompositionPlan(
        thesis="A lower monthly EMI is a psychological trap that doubles your total interest.",
        visual_mode="composition",
        hook_plan=HookCompositionPlan(
            hook_id="hook",
            narration=hook_script,
            beats=[
                CompositionBeat(
                    beat_id="beat_hook_01",
                    composition_id="metric_hero",
                    visual_goal="Show initial relief metric",
                    trigger_word=None,
                    composition_data={
                        "hero_value": "45000",
                        "hero_unit": "INR",
                        "hero_label": "Reduced EMI",
                    },
                ),
                CompositionBeat(
                    beat_id="beat_hook_02",
                    composition_id="broll_caption",
                    visual_goal="Atmospheric contrast",
                    trigger_word="relief" if not special_text else "yield",
                    asset_requirement="optional_broll",
                    asset_query="stressed person calculating bills",
                    composition_data={"caption_text": "The illusion of relief"},
                ),
                CompositionBeat(
                    beat_id="beat_hook_03",
                    composition_id="calculation_story",
                    visual_goal="Reveal true cost",
                    trigger_word="calculate" if not special_text else "hidden",
                    composition_data={
                        "initial_value": 45000,
                        "multiplier": 2.4,
                        "result_value": 108000,
                        "calculation_label": "Real Cost Calculation",
                    },
                ),
            ],
        ),
        ideas=[
            IdeaCompositionPlan(
                idea_id="idea_01",
                narration=idea_narration,
                beats=[
                    CompositionBeat(
                        beat_id="beat_idea_01_01",
                        composition_id="broll_caption",
                        visual_goal="Bank tenure expansion",
                        trigger_word=None,
                        composition_data={"caption_text": "Tenure expansion trap"},
                    ),
                    CompositionBeat(
                        beat_id="beat_idea_01_02",
                        composition_id="calculation_story",
                        visual_goal="Show 30 years calculation",
                        trigger_word="thirty",
                        composition_data={
                            "initial_value": 15,
                            "multiplier": 2.0,
                            "result_value": 30,
                            "calculation_label": "Tenure Doubled",
                        },
                    ),
                    CompositionBeat(
                        beat_id="beat_idea_01_03",
                        composition_id="metric_hero",
                        visual_goal="Monthly burden drops",
                        trigger_word="monthly",
                        composition_data={
                            "hero_value": "-25%",
                            "hero_label": "Monthly Relief",
                        },
                    ),
                    CompositionBeat(
                        beat_id="beat_idea_01_04",
                        composition_id="growth_trajectory",
                        visual_goal="Interest explosion trajectory",
                        trigger_word="explodes",
                        composition_data={
                            "start_value": 1000000,
                            "end_value": 3200000,
                            "timeframe": "30 Years",
                            "trajectory_label": "Total Cumulative Interest",
                        },
                    ),
                ],
            )
        ],
    )

    strat_art = store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="script_visual_strategy",
        schema_version="1",
        payload_json={
            "thesis": "A lower monthly EMI is a psychological trap that doubles your total interest.",
            "ideas": [
                {
                    "idea_id": "idea_01",
                    "title": "The Hidden Cost",
                    "focus_concept": "Amortization",
                    "core_teaching_point": "Tenure extension increases total repayment.",
                    "narration": idea_narration,
                    "voice_cues": [c.model_dump() for c in idea_cues],
                }
            ],
            "composition_plan": comp_plan.model_dump(),
        },
        parent_artifact_roles_json={
            "hook": hook_art.id,
            "narrative_plan": plan_art.id,
            "research_packet": res_art.id,
        },
        validation_json=ValidationResult(status="valid"),
    )

    # 5. Review Result (Stage 5 approved)
    store.save_artifact(
        project_id=project.id,
        run_id=run.id,
        artifact_type="review_result",
        schema_version="1",
        payload_json={
            "approved": True,
            "checks": [{"name": "Concept Alignment", "status": "passed", "message": "Ok"}],
        },
        parent_artifact_roles_json={"script_visual_strategy": strat_art.id},
        validation_json=ValidationResult(status="valid"),
    )

    return project.id, run.id


def _build_polly_mock(recorded_calls: list[dict]):
    """Builds a realistic mock for AWS Polly supporting dual-stream MP3 and JSON speech marks."""
    client = MagicMock()

    def mock_synthesize_speech(*args, **kwargs):
        recorded_calls.append(kwargs)
        fmt = kwargs.get("OutputFormat")
        text = kwargs.get("Text", "")
        text_type = kwargs.get("TextType", "text")

        clean_text = re.sub(r"<[^>]+>", " ", text)
        words = clean_text.split()
        total_dur = max(2.5, len(words) * 0.35)

        if fmt == "mp3":
            mp3_data = _generate_mp3_bytes(total_dur)
            stream_mock = MagicMock()
            stream_mock.read.return_value = mp3_data
            return {"AudioStream": stream_mock}
        elif fmt == "json":
            lines = []
            cur_ms = 100
            cur_char = 0
            step_ms = int((total_dur * 1000 - 200) / max(1, len(words)))
            for w in words:
                w_clean = re.sub(r"[^\w]", "", w)
                if not w_clean:
                    continue
                lines.append(
                    json.dumps({
                        "time": cur_ms,
                        "type": "word",
                        "start": cur_char,
                        "end": cur_char + len(w_clean),
                        "value": w_clean,
                    })
                )
                cur_ms += step_ms
                cur_char += len(w) + 1

            if text_type == "ssml":
                lines.append(
                    json.dumps({
                        "time": 400,
                        "type": "ssml",
                        "value": "pause_mark",
                    })
                )

            json_stream = MagicMock()
            json_stream.read.return_value = "\n".join(lines).encode("utf-8")
            return {"AudioStream": json_stream}
        return {}

    client.synthesize_speech.side_effect = mock_synthesize_speech
    return client


def test_e2e_full_pipeline_voice_cues_to_assembly(tmp_path: Path):
    """
    End-to-End Verification:
    Stage 3/4 (Hook & Script with VoiceCues) ->
    Stage 6 (VoiceGeneration with Polly Neural SSML dual-stream) ->
    Stage 7 (VideoAssembly with FullCompositionPlan multi-visual trigger words).
    """
    client, store, media_storage = _setup_e2e_client_and_store(tmp_path)
    project_id, run_id = _create_e2e_project_artifacts(store)

    recorded_polly_calls: list[dict] = []
    mock_polly = _build_polly_mock(recorded_polly_calls)

    # 1. Execute Voice Generation Stage
    with patch("boto3.client", return_value=mock_polly):
        resp_voice = client.post(f"/projects/{project_id}/runs/{run_id}/run/voice_generation")
    assert resp_voice.status_code == 200, f"Voice generation failed: {resp_voice.text}"

    voice_artifact = resp_voice.json()["artifact"]
    assert voice_artifact["artifact_type"] == "voice_track"
    assert voice_artifact["status"] == "valid"

    voice_payload = voice_artifact["payload_json"]
    assert len(voice_payload["word_timestamps"]) > 0
    assert "audio_file_name" in voice_payload
    assert voice_payload["duration_seconds"] > 0

    # Verify that Polly was called with valid SSML
    ssml_calls = [c for c in recorded_polly_calls if c.get("TextType") == "ssml"]
    assert len(ssml_calls) > 0, "Polly was never called with TextType='ssml'"

    validator = SSMLValidator()
    for call in ssml_calls:
        ssml_text = call.get("Text", "")
        assert ssml_text.startswith("<speak>") and ssml_text.endswith("</speak>")
        val_res = validator.validate(ssml_text)
        assert val_res.is_valid, f"Compiled SSML failed strict validation: {val_res.errors}"
        # Verify Neural disallowed tags like <emphasis> or pitch are never produced
        assert "<emphasis" not in ssml_text
        assert "pitch=" not in ssml_text

    # Verify audio file exists on media storage
    audio_path = media_storage.path_for_key(voice_payload["storage_key"])
    assert audio_path.exists()
    assert audio_path.stat().st_size > 0

    # 2. Execute Video Assembly Stage
    mock_asset = AssetReference(
        asset_id="mock_asset",
        asset_type="video",
        source="pexels",
        query="stressed person calculating bills",
        local_path=str(tmp_path / "mock_video.mp4"),
        url="http://example.com/mock.mp4",
        asset_status="cached",
    )
    (tmp_path / "mock_video.mp4").write_bytes(b"mock video data")

    with patch(
        "engines.video_assembly.asset_resolver.AssetResolver.resolve_asset",
        return_value=mock_asset,
    ):
        resp_assembly = client.post(f"/projects/{project_id}/runs/{run_id}/run/video_assembly")
    assert resp_assembly.status_code == 200, f"Video assembly failed: {resp_assembly.text}"

    assembly_data = resp_assembly.json()
    assert assembly_data["artifact"]["artifact_type"] == "render_spec"
    assert assembly_data["validation"]["status"] == "valid"

    render_spec = store.get_artifact(assembly_data["artifact_id"]).payload_json
    assert render_spec["composition"] == "VideoAssembly"
    assert render_spec["fps"] == 30

    # Total visual beats: 3 hook beats + 4 body idea beats = 7 beats
    scenes = render_spec["props"]["scenes"]
    assert len(scenes) == 7, f"Expected 7 scenes for 7 visual beats, got {len(scenes)}"

    # Verify frame continuity and contiguity (no gaps, no overlaps)
    for i in range(len(scenes)):
        if i > 0:
            assert scenes[i]["start_frame"] == scenes[i - 1]["end_frame"], (
                f"Gap or overlap between scene {i-1} and {i}: "
                f"end={scenes[i-1]['end_frame']}, start={scenes[i]['start_frame']}"
            )
        assert scenes[i]["end_frame"] > scenes[i]["start_frame"]


def test_e2e_voice_generation_with_polly_invalid_ssml_retry(tmp_path: Path):
    """
    Verifies resilience: if AWS Polly rejects SSML with InvalidSsml,
    the provider automatically retries with plain text fallback, and assembly still succeeds.
    """
    client, store, media_storage = _setup_e2e_client_and_store(tmp_path)
    project_id, run_id = _create_e2e_project_artifacts(store)

    recorded_polly_calls: list[dict] = []
    base_mock = _build_polly_mock(recorded_polly_calls)

    # Intercept: throw InvalidSsmlException on first SSML call
    def mock_synthesize_with_invalid_ssml(*args, **kwargs):
        text_type = kwargs.get("TextType")
        if text_type == "ssml":
            raise Exception("InvalidSsmlException: The SSML provided is not valid XML")
        return base_mock.synthesize_speech(*args, **kwargs)

    mock_client = MagicMock()
    mock_client.synthesize_speech.side_effect = mock_synthesize_with_invalid_ssml

    with patch("boto3.client", return_value=mock_client):
        resp_voice = client.post(f"/projects/{project_id}/runs/{run_id}/run/voice_generation")
    assert resp_voice.status_code == 200, f"Voice generation failed on fallback: {resp_voice.text}"

    voice_artifact = resp_voice.json()["artifact"]
    assert voice_artifact["status"] == "valid"

    # Now verify Video Assembly succeeds on the plain-text fallback track
    mock_asset = AssetReference(
        asset_id="mock_asset",
        asset_type="video",
        source="pexels",
        query="query",
        local_path=str(tmp_path / "mock.mp4"),
        url="http://example.com/mock.mp4",
        asset_status="cached",
    )
    (tmp_path / "mock.mp4").write_bytes(b"dummy")

    with patch(
        "engines.video_assembly.asset_resolver.AssetResolver.resolve_asset",
        return_value=mock_asset,
    ):
        resp_assembly = client.post(f"/projects/{project_id}/runs/{run_id}/run/video_assembly")
    assert resp_assembly.status_code == 200


def test_e2e_xml_character_escaping_in_pipeline(tmp_path: Path):
    """
    Verifies that scripts containing financial XML characters (&, <, >, $)
    are escaped safely in SSML without breaking Polly or trigger word matching.
    """
    client, store, media_storage = _setup_e2e_client_and_store(tmp_path)
    project_id, run_id = _create_e2e_project_artifacts(store, special_text=True)

    recorded_polly_calls: list[dict] = []
    mock_polly = _build_polly_mock(recorded_polly_calls)

    with patch("boto3.client", return_value=mock_polly):
        resp_voice = client.post(f"/projects/{project_id}/runs/{run_id}/run/voice_generation")
    assert resp_voice.status_code == 200

    # Ensure & was properly escaped to &amp; and < to &lt; in the hook chunk
    ssml_texts = [c["Text"] for c in recorded_polly_calls if c.get("TextType") == "ssml"]
    assert any("&amp;" in ssml for ssml in ssml_texts), "Expected &amp; in compiled SSML"
    assert any("&lt;" in ssml for ssml in ssml_texts), "Expected &lt; in compiled SSML"

    validator = SSMLValidator()
    for ssml in ssml_texts:
        val = validator.validate(ssml)
        assert val.is_valid, f"Escaped SSML failed validation: {val.errors}"


def test_e2e_backward_compatibility_no_voice_cues(tmp_path: Path):
    """
    Verifies that legacy or plain scripts with zero voice_cues
    still compile to valid <speak> SSML and proceed seamlessly through both stages.
    """
    client, store, media_storage = _setup_e2e_client_and_store(tmp_path)
    project_id, run_id = _create_e2e_project_artifacts(
        store,
        hook_voice_cues=[],
        idea_voice_cues=[],
    )

    recorded_polly_calls: list[dict] = []
    mock_polly = _build_polly_mock(recorded_polly_calls)

    with patch("boto3.client", return_value=mock_polly):
        resp_voice = client.post(f"/projects/{project_id}/runs/{run_id}/run/voice_generation")
    assert resp_voice.status_code == 200

    mock_asset = AssetReference(
        asset_id="mock_asset",
        asset_type="video",
        source="pexels",
        query="query",
        local_path=str(tmp_path / "mock.mp4"),
        url="http://example.com/mock.mp4",
        asset_status="cached",
    )
    (tmp_path / "mock.mp4").write_bytes(b"dummy")

    with patch(
        "engines.video_assembly.asset_resolver.AssetResolver.resolve_asset",
        return_value=mock_asset,
    ):
        resp_assembly = client.post(f"/projects/{project_id}/runs/{run_id}/run/video_assembly")
    assert resp_assembly.status_code == 200
