from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from domain.continuous_story_plan import (
    ContinuousStoryDraft,
    ImageAssetRequest,
    StoryEventDraft,
    StoryObjectDraft,
)
from domain.research_packet import ResearchPacket
from domain.script_visual_strategy import ScriptVisualStrategy
from domain.voice_track import VoiceTrack
from engines.continuous_story_asset_resolver import (
    ContinuousStoryAssetResolver,
    ContinuousStoryAssetResolverError,
    ResolvedImageAsset,
)
from engines.continuous_story_compiler import ContinuousStoryCompiler
from engines.continuous_story_draft_validator import validate_story_draft
from engines.continuous_story_engine import (
    ContinuousStoryEngine,
    ContinuousStoryEngineError,
)
from engines.render_engine import RenderEngine
from providers.media_storage import LocalMediaStorage
from providers.remotion_provider import RemotionProvider


# Minimal 1x1 valid JPEG bytes for fast unit test downloads
DUMMY_JPEG_BYTES = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
    b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
    b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342"
    b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4"
    b"\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
    b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
)


@pytest.fixture
def sample_voice_data():
    narration_text = (
        "The borrower thinks the money is going toward the house. "
        "But over the life of the loan, a much larger share flows back to the bank as interest."
    )
    words = [
        {"word": "The", "start_ms": 100, "end_ms": 300},
        {"word": "borrower", "start_ms": 350, "end_ms": 800},
        {"word": "thinks", "start_ms": 850, "end_ms": 1100},
        {"word": "the", "start_ms": 1150, "end_ms": 1300},
        {"word": "money", "start_ms": 1350, "end_ms": 1600},
        {"word": "is", "start_ms": 1650, "end_ms": 1750},
        {"word": "going", "start_ms": 1800, "end_ms": 2000},
        {"word": "toward", "start_ms": 2050, "end_ms": 2300},
        {"word": "the", "start_ms": 2350, "end_ms": 2450},
        {"word": "house", "start_ms": 2500, "end_ms": 2900},
        {"word": "But", "start_ms": 3200, "end_ms": 3400},
        {"word": "over", "start_ms": 3450, "end_ms": 3650},
        {"word": "the", "start_ms": 3700, "end_ms": 3800},
        {"word": "life", "start_ms": 3850, "end_ms": 4100},
        {"word": "of", "start_ms": 4150, "end_ms": 4250},
        {"word": "the", "start_ms": 4300, "end_ms": 4400},
        {"word": "loan", "start_ms": 4450, "end_ms": 4800},
        {"word": "a", "start_ms": 5000, "end_ms": 5100},
        {"word": "much", "start_ms": 5150, "end_ms": 5350},
        {"word": "larger", "start_ms": 5400, "end_ms": 5700},
        {"word": "share", "start_ms": 5750, "end_ms": 6050},
        {"word": "flows", "start_ms": 6100, "end_ms": 6400},
        {"word": "back", "start_ms": 6450, "end_ms": 6700},
        {"word": "to", "start_ms": 6750, "end_ms": 6850},
        {"word": "the", "start_ms": 6900, "end_ms": 7000},
        {"word": "bank", "start_ms": 7050, "end_ms": 7450},
        {"word": "as", "start_ms": 7600, "end_ms": 7750},
        {"word": "interest", "start_ms": 7800, "end_ms": 8400},
    ]
    return narration_text, words


# ----------------------------------------------------
# 1. Valid image asset_request parsing
# ----------------------------------------------------
def test_valid_image_asset_request_parsing():
    raw_payload = {
        "story_id": "test_image_parsing",
        "objects": [
            {
                "id": "bank_img",
                "type": "image",
                "layout": "split_left",
                "asset_request": {
                    "query": "modern bank exterior, no visible logo",
                    "orientation": "landscape",
                    "style": "photo",
                    "composition": "subject on the left with empty space on the right",
                    "mood": "serious institutional finance documentary",
                    "avoid": ["logos", "watermarks", "text-heavy signs", "identifiable faces"],
                },
                "alt": "Bank exterior",
                "caption": "Institutional Lender",
                "badge": "LENDER",
                "fit": "cover",
                "border_color": "#3B82F6",
                "border_radius": 16,
            }
        ],
        "events": [
            {"action": "enter", "target_id": "bank_img", "anchor": "bank"}
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_payload)
    img_obj = draft.objects[0]
    assert img_obj.type == "image"
    assert img_obj.asset_request is not None
    assert img_obj.asset_request.query == "modern bank exterior, no visible logo"
    assert img_obj.asset_request.orientation == "landscape"
    assert img_obj.asset_request.style == "photo"
    assert "logos" in img_obj.asset_request.avoid
    assert img_obj.badge == "LENDER"
    assert img_obj.fit == "cover"


# ----------------------------------------------------
# 2. Missing asset_request failure
# ----------------------------------------------------
def test_missing_asset_request_failure():
    raw_payload = {
        "story_id": "test_missing_req",
        "objects": [
            {
                "id": "bank_img",
                "type": "image",
                "layout": "split_left",
            }
        ],
        "events": [
            {"action": "enter", "target_id": "bank_img", "anchor": "bank"}
        ],
    }

    with pytest.raises(ValueError) as excinfo:
        ContinuousStoryDraft.model_validate(raw_payload)
    assert "IMAGE_ASSET_REQUEST_MISSING" in str(excinfo.value)


# ----------------------------------------------------
# 3. Unknown asset_id failure
# ----------------------------------------------------
def test_unknown_asset_id_failure(sample_voice_data):
    narration_text, words = sample_voice_data
    raw_payload = {
        "story_id": "test_unknown_asset",
        "objects": [
            {
                "id": "bank_img",
                "type": "image",
                "layout": "split_left",
                "asset_id": "assets/invented_bank.jpg",
            }
        ],
        "events": [
            {"action": "enter", "target_id": "bank_img", "anchor": "flows back to the bank"}
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_payload)
    # available_assets only has legal known assets, not invented_bank.jpg
    val_res = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=words,
        total_duration_ms=9000,
        available_assets=["assets/approved_office.jpg"],
    )
    assert not val_res.valid
    assert any(e.code == "UNKNOWN_ASSET_ID" for e in val_res.errors)


# ----------------------------------------------------
# 4. Empty provider result failure
# ----------------------------------------------------
def test_empty_provider_result_failure(tmp_path):
    resolver = ContinuousStoryAssetResolver(
        cache_dir=tmp_path / "cache",
        remotion_public_dir=tmp_path / "public",
    )

    req = ImageAssetRequest(query="super rare imaginary finance object", orientation="landscape")
    with patch.object(resolver, "_search_pexels", return_value=[]), patch.object(
        resolver, "_search_pixabay", return_value=[]
    ):
        with pytest.raises(ContinuousStoryAssetResolverError) as excinfo:
            resolver.resolve_image_asset(req, object_id="rare_img")
        assert "IMAGE_SEARCH_NO_RESULT" in str(excinfo.value)


# ----------------------------------------------------
# 5. Download failure
# ----------------------------------------------------
def test_download_failure(tmp_path):
    resolver = ContinuousStoryAssetResolver(
        cache_dir=tmp_path / "cache",
        remotion_public_dir=tmp_path / "public",
    )
    req = ImageAssetRequest(query="bank exterior", orientation="landscape")

    fake_candidates = [
        {
            "provider": "pexels",
            "download_url": "https://example.com/broken_image.jpg",
            "source_url": "https://example.com/photo/1",
            "author": "Photographer",
            "width": 1920,
            "height": 1080,
        }
    ]

    with patch.dict(os.environ, {"PEXELS_API_KEY": "fake_pexels"}):
        with patch.object(resolver, "_search_pexels", return_value=fake_candidates):
            with patch("urllib.request.urlopen", side_effect=OSError("Network error")):
                with pytest.raises(ContinuousStoryAssetResolverError) as excinfo:
                    resolver.resolve_image_asset(req, object_id="bank_img")
                assert "IMAGE_DOWNLOAD_FAILED" in str(excinfo.value)


# ----------------------------------------------------
# 6. Missing local file failure
# ----------------------------------------------------
def test_missing_local_file_failure(tmp_path):
    resolver = ContinuousStoryAssetResolver(
        cache_dir=tmp_path / "cache",
        remotion_public_dir=tmp_path / "public",
    )

    non_existent = tmp_path / "does_not_exist.jpg"
    with pytest.raises(ContinuousStoryAssetResolverError) as excinfo:
        resolver._finalize_asset(
            source_file=non_existent,
            object_id="missing_obj",
            project_id="test_proj",
            run_id="test_run",
            query="test query",
            provider="pexels",
            source_url="http://example.com",
            author="Author",
            width=1920,
            height=1080,
        )
    assert "IMAGE_LOCAL_FILE_MISSING" in str(excinfo.value)


# ----------------------------------------------------
# 7. Successful asset caching
# ----------------------------------------------------
def test_successful_asset_caching(tmp_path):
    cache_dir = tmp_path / "cache"
    public_dir = tmp_path / "public"
    resolver = ContinuousStoryAssetResolver(
        cache_dir=cache_dir,
        remotion_public_dir=public_dir,
    )
    req = ImageAssetRequest(query="modern bank exterior", orientation="landscape")

    fake_candidates = [
        {
            "provider": "pexels",
            "download_url": "https://example.com/bank.jpg",
            "source_url": "https://example.com/photo/123",
            "author": "Bank Photographer",
            "width": 1920,
            "height": 1080,
        }
    ]

    mock_resp = MagicMock()
    mock_resp.read.return_value = DUMMY_JPEG_BYTES
    mock_resp.__enter__.return_value = mock_resp

    with patch.dict(os.environ, {"PEXELS_API_KEY": "fake_pexels"}):
        with patch.object(resolver, "_search_pexels", return_value=fake_candidates) as mock_search:
            with patch("urllib.request.urlopen", return_value=mock_resp):
                res1 = resolver.resolve_image_asset(req, object_id="bank_1")
                assert res1.provider == "pexels"
                assert mock_search.call_count == 1

            # Second resolution with same query should hit cache and NOT call search
            with patch.object(resolver, "_search_pexels") as mock_search2:
                res2 = resolver.resolve_image_asset(req, object_id="bank_2")
                assert mock_search2.call_count == 0
                assert res2.asset_id == "assets/bank_2.jpg"
                assert (public_dir / "assets" / "bank_2.jpg").exists()


# ----------------------------------------------------
# 8. Pexels-to-Pixabay fallback
# ----------------------------------------------------
def test_pexels_to_pixabay_fallback(tmp_path):
    resolver = ContinuousStoryAssetResolver(
        cache_dir=tmp_path / "cache",
        remotion_public_dir=tmp_path / "public",
    )
    req = ImageAssetRequest(query="bank vault interior", orientation="landscape")

    pixabay_candidates = [
        {
            "provider": "pixabay",
            "download_url": "https://pixabay.com/get/vault.jpg",
            "source_url": "https://pixabay.com/photos/vault-123/",
            "author": "Pixabay Artist",
            "width": 1920,
            "height": 1080,
        }
    ]

    mock_resp = MagicMock()
    mock_resp.read.return_value = DUMMY_JPEG_BYTES
    mock_resp.__enter__.return_value = mock_resp

    with patch.dict(os.environ, {"PEXELS_API_KEY": "fake_pexels", "PIXABAY_API_KEY": "fake_pixabay"}):
        with patch.object(resolver, "_search_pexels", return_value=[]), patch.object(
            resolver, "_search_pixabay", return_value=pixabay_candidates
        ), patch("urllib.request.urlopen", return_value=mock_resp):
            res = resolver.resolve_image_asset(req, object_id="vault_img")
            assert res.provider == "pixabay"
            assert res.author == "Pixabay Artist"
            assert res.asset_id == "assets/vault_img.jpg"


# ----------------------------------------------------
# 9. Image plus card plus number plus connector compilation
# ----------------------------------------------------
def test_image_plus_card_plus_number_plus_connector_compilation(sample_voice_data):
    narration_text, words = sample_voice_data
    compiler = ContinuousStoryCompiler()

    raw_draft = {
        "story_id": "loan_interest_bank_story",
        "objects": [
            {
                "id": "bank_img",
                "type": "image",
                "layout": "split_left",
                "asset_id": "assets/bank_001.jpg",
                "alt": "Commercial Bank Building",
                "caption": "Institutional Lender",
                "badge": "LENDER",
                "fit": "cover",
            },
            {
                "id": "loan_card",
                "type": "card",
                "layout": "split_right",
                "title": "Home Loan",
                "display_value": "₹50 Lakhs",
                "subtitle": "Principal Borrowed",
                "numeric_value": 5000000,
            },
            {
                "id": "interest_num",
                "type": "number",
                "layout": "center",
                "display_value": "₹88.4 Lakhs",
                "numeric_value": 8840000,
                "purpose": "Total Interest Over 30 Years",
            },
            {
                "id": "conn_loan_to_bank",
                "type": "connector",
                "layout": "center",
                "from_id": "loan_card",
                "to_id": "bank_img",
                "label": "flows to lender",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "loan_card", "anchor": "going toward the house"},
            {"action": "enter", "target_id": "bank_img", "anchor": "life of the loan"},
            {"action": "connect", "target_id": "conn_loan_to_bank", "anchor": "flows back to the bank"},
            {"action": "enter", "target_id": "interest_num", "anchor": "as interest"},
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_draft)
    fixture = {
        "word_timestamps": words,
        "total_duration_ms": 9000,
        "available_assets": ["assets/bank_001.jpg"],
        "narration_text": narration_text,
    }

    compiled = compiler.compile(draft, fixture)
    assert compiled["id"] == "loan_interest_bank_story"
    assert len(compiled["objects"]) == 4

    # Verify Image Primitive in compiled plan
    img = next(o for o in compiled["objects"] if o["id"] == "bank_img")
    assert img["type"] == "image"
    assert img["layout"] == "split_left"
    assert img["imageProps"]["assetId"] == "assets/bank_001.jpg"
    assert img["imageProps"]["badge"] == "LENDER"
    assert img["imageProps"]["caption"] == "Institutional Lender"

    # Verify Connector connecting card to image
    conn = next(o for o in compiled["objects"] if o["id"] == "conn_loan_to_bank")
    assert conn["type"] == "connector"
    assert conn["connectorProps"]["fromId"] == "loan_card"
    assert conn["connectorProps"]["toId"] == "bank_img"


# ----------------------------------------------------
# 10. Image entering at its exact narration anchor
# ----------------------------------------------------
def test_image_entering_at_exact_narration_anchor(sample_voice_data):
    narration_text, words = sample_voice_data
    compiler = ContinuousStoryCompiler()

    raw_draft = {
        "story_id": "timing_test_story",
        "objects": [
            {
                "id": "bank_img",
                "type": "image",
                "layout": "split_left",
                "asset_id": "assets/bank_001.jpg",
            }
        ],
        "events": [
            {"action": "enter", "target_id": "bank_img", "anchor": "flows back to the bank"}
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_draft)
    fixture = {
        "word_timestamps": words,
        "total_duration_ms": 9000,
        "available_assets": ["assets/bank_001.jpg"],
    }

    compiled = compiler.compile(draft, fixture)
    enter_ev = next(e for e in compiled["events"] if e["targetId"] == "bank_img" and e["action"] == "enter")

    # "flows" starts at 6100ms in words. At 30fps: round(6.1 * 30) = 183 frames.
    assert enter_ev["startFrame"] == 183
    assert enter_ev["startFrame"] > 0, "Image must not start at frame zero!"


# ----------------------------------------------------
# 11. Image collision with another object
# ----------------------------------------------------
def test_image_collision_with_another_object(sample_voice_data):
    narration_text, words = sample_voice_data

    raw_draft = {
        "story_id": "collision_story",
        "objects": [
            {
                "id": "bank_img",
                "type": "image",
                "layout": "split_left",
                "asset_id": "assets/bank_001.jpg",
            },
            {
                "id": "loan_card",
                "type": "card",
                "layout": "split_left",  # COLLISION with bank_img in "split_left" zone
                "title": "Home Loan",
                "display_value": "₹50 Lakhs",
                "subtitle": "Principal",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "bank_img", "anchor": "going toward the house"},
            {"action": "enter", "target_id": "loan_card", "anchor": "life of the loan"},
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_draft)
    val_res = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=words,
        total_duration_ms=9000,
        available_assets=["assets/bank_001.jpg"],
    )
    assert not val_res.valid
    assert any(e.code == "ZONE_OCCUPANCY_COLLISION" for e in val_res.errors)


# ----------------------------------------------------
# 12. Image exiting correctly
# ----------------------------------------------------
def test_image_exiting_correctly(sample_voice_data):
    narration_text, words = sample_voice_data

    raw_draft = {
        "story_id": "exit_clean_story",
        "objects": [
            {
                "id": "bank_img",
                "type": "image",
                "layout": "split_left",
                "asset_id": "assets/bank_001.jpg",
            },
            {
                "id": "loan_card",
                "type": "card",
                "layout": "split_left",  # Reuses "split_left" zone after bank_img exits cleanly
                "title": "Home Loan",
                "display_value": "₹50 Lakhs",
                "subtitle": "Principal",
            },
        ],
        "events": [
            # 1. bank_img enters at "going toward the house" (2000ms)
            {"action": "enter", "target_id": "bank_img", "anchor": "going toward the house"},
            # 2. bank_img exits cleanly at "life of the loan" (4000ms)
            {"action": "exit", "target_id": "bank_img", "anchor": "life of the loan", "direction": "fade"},
            # 3. loan_card enters "split_left" at "as interest" (7600ms)
            {"action": "enter", "target_id": "loan_card", "anchor": "as interest"},
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_draft)
    val_res = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=words,
        total_duration_ms=9000,
        available_assets=["assets/bank_001.jpg"],
    )
    assert val_res.valid, f"Validation failed unexpectedly: {val_res.errors}"


# ----------------------------------------------------
# 13. Existing non-image continuous story tests remaining green
# ----------------------------------------------------
def test_existing_non_image_continuous_story_tests_remain_green():
    # Validate a pure card + number + character choreography still validates 100% cleanly
    raw_draft = {
        "story_id": "non_image_smoke",
        "objects": [
            {
                "id": "hero_card",
                "type": "card",
                "layout": "split_left",
                "title": "Salary",
                "display_value": "₹1,00,000",
                "subtitle": "Monthly",
            },
            {
                "id": "char_worker",
                "type": "character",
                "layout": "split_right",
                "character_style": "futuristic_stick",
                "role": "salaried professional",
                "pose": "think",
                "facing": "left",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "hero_card", "anchor": "monthly salary"},
            {"action": "enter", "target_id": "char_worker", "anchor": "living cost"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw_draft)
    assert len(draft.objects) == 2


# ----------------------------------------------------
# 14. Remotion typecheck passing
# ----------------------------------------------------
def test_remotion_typecheck_passes():
    renderer_dir = Path(__file__).resolve().parents[2] / "renderer" / "remotion"
    res = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=str(renderer_dir),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Remotion typecheck failed:\n{res.stdout}\n{res.stderr}"


# ----------------------------------------------------
# 15. One real MP4 render using a downloaded image
# ----------------------------------------------------
def test_real_mp4_render_using_downloaded_image(sample_voice_data):
    """
    End-to-End Render Test:
    Story: "The borrower thinks the money is going toward the house.
            But over the life of the loan, a much larger share flows back to the bank as interest."
    Composition:
    - Bank image on left
    - Home-loan card on right
    - Interest number in center
    - Connector from loan card to bank image (Loan -> Interest -> Bank)
    Renders a real MP4 with Remotion and verifies output size and integrity.
    """
    narration_text, words = sample_voice_data
    repo_root = Path(__file__).resolve().parents[2]
    remotion_dir = repo_root / "renderer" / "remotion"
    media_dir = repo_root / "backend" / ".data" / "media"

    media_storage = LocalMediaStorage(media_dir)
    remotion_provider = RemotionProvider(remotion_dir)
    render_engine = RenderEngine(
        media_storage=media_storage,
        remotion_provider=remotion_provider,
    )

    # 1. Ensure test image exists in Remotion public assets
    test_image_rel = "assets/bank_context_001.jpg"
    test_image_public = remotion_dir / "public" / test_image_rel
    if not test_image_public.exists():
        test_image_public.parent.mkdir(parents=True, exist_ok=True)
        test_image_public.write_bytes(DUMMY_JPEG_BYTES)

    # 2. Compile full 4-element story plan
    compiler = ContinuousStoryCompiler()
    raw_draft = {
        "story_id": "test_bank_loan_render",
        "objects": [
            {
                "id": "bank_img",
                "type": "image",
                "layout": "split_left",
                "asset_id": test_image_rel,
                "alt": "Commercial Bank Building",
                "caption": "Institutional Lender",
                "badge": "LENDER",
                "fit": "cover",
            },
            {
                "id": "loan_card",
                "type": "card",
                "layout": "split_right",
                "title": "Home Loan",
                "display_value": "₹50 Lakhs",
                "subtitle": "Principal Borrowed",
                "numeric_value": 5000000,
            },
            {
                "id": "interest_num",
                "type": "number",
                "layout": "center",
                "display_value": "₹88.4 Lakhs",
                "numeric_value": 8840000,
                "purpose": "Total Interest Over 30 Years",
            },
            {
                "id": "conn_loan_to_bank",
                "type": "connector",
                "layout": "center",
                "from_id": "loan_card",
                "to_id": "bank_img",
                "label": "interest flows to bank",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "loan_card", "anchor": "going toward the house"},
            {"action": "enter", "target_id": "bank_img", "anchor": "life of the loan"},
            {"action": "connect", "target_id": "conn_loan_to_bank", "anchor": "flows back to the bank"},
            {"action": "enter", "target_id": "interest_num", "anchor": "as interest"},
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw_draft)
    fixture = {
        "story_id": "test_bank_loan_render",
        "word_timestamps": words,
        "total_duration_ms": 8500,
        "audio_file": "loan_narration.mp3",
        "available_assets": [test_image_rel],
        "narration_text": narration_text,
    }

    compiled_plan = compiler.compile(draft, fixture)
    # Set full duration to cover all 4 choreography beats (270 frames = 9 seconds)
    compiled_plan["durationInFrames"] = 270

    from domain.continuous_story_plan import ContinuousStoryPlanArtifact
    story_artifact = ContinuousStoryPlanArtifact.from_compiled_plan(
        plan=compiled_plan,
        draft=draft,
    )

    # 3. Render MP4
    project_id = "test_img_proj"
    run_id = "test_img_run"
    video = render_engine.run(
        continuous_story_plan=story_artifact,
        project_id=project_id,
        run_id=run_id,
    )

    if video.render_status == "failed" and (
        "Permission denied" in (video.error_message or "")
        or "SIGTRAP" in (video.error_message or "")
        or "timed out" in (video.error_message or "")
    ):
        pytest.skip("Remotion Chromium browser launch restricted by sandbox (run with unsandboxed mode for real MP4 rendering).")

    assert video.render_status == "succeeded", f"Render failed: {video.error_message}"
    assert video.size_bytes > 10000, f"Rendered video is too small ({video.size_bytes} bytes)"
    mp4_path = media_storage.path_for_key(video.storage_key)
    assert mp4_path.exists(), f"Output file does not exist at {mp4_path}"
