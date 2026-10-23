"""
test_continuous_story_stock_video.py — Comprehensive Unit & Integration Tests for Stock Video Primitive.

Tests:
1. Valid stock_video draft and compilation (cut enter/exit, durationFrames 0, 1920x1080, stockVideoProps).
2. Rejection of non-fullscreen layout (STOCK_VIDEO_INVALID_LAYOUT).
3. Rejection of forbidden primitive fields (card, chart, number, connector fields).
4. Validation of exactly one enter and one exit event with cut behavior.
5. Exit anchor must occur strictly after enter anchor.
6. Temporal exclusivity against other surface elements (MACRO_LAYOUT_COLLISION).
7. Temporal exclusivity against connectors (STOCK_VIDEO_CONNECTOR_COLLISION).
8. VIDEO_ASSET_REQUEST_MISSING when neither request nor ID is provided.
9. VIDEO_SEARCH_NO_RESULT when video search yields no candidates.
10. VIDEO_DURATION_TOO_SHORT when footage duration is less than visible interval.
11. VIDEO_DOWNLOAD_FAILED on download errors.
12. Caching and staging into Remotion public assets.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import pydantic

from domain.continuous_story_plan import ContinuousStoryDraft, VideoAssetRequest
from engines.continuous_story_draft_validator import validate_story_draft
from engines.continuous_story_compiler import ContinuousStoryCompiler
from engines.continuous_story_asset_resolver import (
    ContinuousStoryAssetResolver,
    ContinuousStoryAssetResolverError,
)


@pytest.fixture
def loan_fixture() -> dict:
    fixture_path = Path(__file__).resolve().parent.parent / "fixtures" / "loan_story_fixture.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_stock_video_valid_draft_and_compilation(loan_fixture: dict):
    """1. Test valid stock_video: card before, stock_video hard cut in/out, card after."""
    raw = {
        "story_id": "stock_video_valid_test",
        "objects": [
            {
                "id": "card_intro",
                "type": "card",
                "layout": "center",
                "title": "Initial Setup",
                "subtitle": "Starting Context",
                "display_value": "₹50 Lakh",
                "numeric_value": 5000000,
            },
            {
                "id": "bank_broll",
                "type": "stock_video",
                "layout": "full_screen",
                "purpose": "Ground the banking system in reality",
                "asset_id": "assets/bank_broll.mp4",
                "fit": "cover",
                "alt": "Commercial bank exterior",
                "caption": "Commercial Banking Operations",
                "overlay_tint": "rgba(0,0,0,0.3)",
            },
            {
                "id": "card_outro",
                "type": "card",
                "layout": "center",
                "title": "Consequence",
                "subtitle": "Payment Burden",
                "display_value": "₹49,919",
                "numeric_value": 49919,
            },
        ],
        "events": [
            # Card intro: 50 lakh (2.95s) -> exits at rate rises (15.54s)
            {"action": "enter", "target_id": "card_intro", "anchor": "50 lakh"},
            {"action": "exit", "target_id": "card_intro", "anchor": "rate rises", "direction": "cut"},
            # Stock video: enters at rate rises (15.54s) -> exits at heavy burden (30.04s)
            {"action": "enter", "target_id": "bank_broll", "anchor": "rate rises", "style": "cut"},
            {"action": "exit", "target_id": "bank_broll", "anchor": "heavy burden", "direction": "cut"},
            # Card outro: enters at heavy burden (30.04s)
            {"action": "enter", "target_id": "card_outro", "anchor": "heavy burden"},
        ],
    }

    draft = ContinuousStoryDraft.model_validate(raw)
    assert draft.objects[1].type == "stock_video"
    assert draft.objects[1].layout == "full_screen"

    result = validate_story_draft(
        draft=draft,
        approved_facts=loan_fixture["approved_facts"],
        word_timestamps=loan_fixture["word_timestamps"],
        total_duration_ms=loan_fixture["total_duration_ms"],
        available_assets=["assets/bank_broll.mp4"],
    )
    assert result.valid is True
    assert len(result.errors) == 0

    compiler = ContinuousStoryCompiler()
    fixture = dict(loan_fixture)
    fixture["available_assets"] = ["assets/bank_broll.mp4"]
    compiled = compiler.compile(draft=draft, fixture=fixture)

    sv_obj = next(o for o in compiled["objects"] if o["id"] == "bank_broll")
    assert sv_obj["type"] == "stock_video"
    assert sv_obj["layout"] == "full_screen"
    assert sv_obj["width"] == 1920
    assert sv_obj["height"] == 1080
    assert sv_obj["stockVideoProps"]["assetId"] == "assets/bank_broll.mp4"
    assert sv_obj["stockVideoProps"]["fit"] == "cover"
    assert sv_obj["stockVideoProps"]["caption"] == "Commercial Banking Operations"

    sv_enter_ev = next(e for e in compiled["events"] if e["targetId"] == "bank_broll" and e["action"] == "enter")
    sv_exit_ev = next(e for e in compiled["events"] if e["targetId"] == "bank_broll" and e["action"] == "exit")

    assert sv_enter_ev["style"] == "cut"
    assert sv_enter_ev["durationFrames"] == 0
    assert sv_exit_ev["direction"] == "cut"
    assert sv_exit_ev["durationFrames"] == 0


def test_stock_video_rejects_non_fullscreen_layout():
    """2. Stock video must reject any layout other than full_screen."""
    raw = {
        "story_id": "stock_video_layout_test",
        "objects": [
            {
                "id": "invalid_video",
                "type": "stock_video",
                "layout": "center",
                "asset_request": {"query": "bank building"},
            }
        ],
        "events": [],
    }
    with pytest.raises(pydantic.ValidationError) as exc_info:
        ContinuousStoryDraft.model_validate(raw)
    assert "layout must be 'full_screen'" in str(exc_info.value)


def test_stock_video_rejects_forbidden_fields():
    """3. Stock video rejects card, number, chart, connector, or character fields."""
    raw = {
        "story_id": "stock_video_forbidden_fields_test",
        "objects": [
            {
                "id": "invalid_video",
                "type": "stock_video",
                "layout": "full_screen",
                "title": "Bank Title Not Allowed",
                "asset_request": {"query": "bank building"},
            }
        ],
        "events": [],
    }
    with pytest.raises(pydantic.ValidationError) as exc_info:
        ContinuousStoryDraft.model_validate(raw)
    assert "cannot specify card field 'title'" in str(exc_info.value)


def test_stock_video_requires_exactly_one_enter_and_exit(loan_fixture: dict):
    """4. Stock video must have exactly one enter and one exit event with cut behavior."""
    # Missing exit event
    raw_missing_exit = {
        "story_id": "missing_exit_test",
        "objects": [
            {
                "id": "video_1",
                "type": "stock_video",
                "layout": "full_screen",
                "asset_id": "assets/test.mp4",
            }
        ],
        "events": [
            {"action": "enter", "target_id": "video_1", "anchor": "50 lakh", "style": "cut"}
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw_missing_exit)
    res = validate_story_draft(
        draft=draft,
        word_timestamps=loan_fixture["word_timestamps"],
        available_assets=["assets/test.mp4"],
    )
    assert res.valid is False
    assert any(e.code == "STOCK_VIDEO_EVENT_COUNT" for e in res.errors)

    # Invalid transition style (fade instead of cut)
    raw_fade_transition = {
        "story_id": "fade_transition_test",
        "objects": [
            {
                "id": "video_1",
                "type": "stock_video",
                "layout": "full_screen",
                "asset_id": "assets/test.mp4",
            }
        ],
        "events": [
            {"action": "enter", "target_id": "video_1", "anchor": "50 lakh", "style": "fade"},
            {"action": "exit", "target_id": "video_1", "anchor": "rate rises", "direction": "cut"},
        ],
    }
    draft2 = ContinuousStoryDraft.model_validate(raw_fade_transition)
    res2 = validate_story_draft(
        draft=draft2,
        word_timestamps=loan_fixture["word_timestamps"],
        available_assets=["assets/test.mp4"],
    )
    assert res2.valid is False
    assert any(e.code == "STOCK_VIDEO_INVALID_TRANSITION" for e in res2.errors)


def test_stock_video_exit_must_be_strictly_after_enter(loan_fixture: dict):
    """5. Exit anchor must occur strictly after enter anchor."""
    raw = {
        "story_id": "exit_before_enter_test",
        "objects": [
            {
                "id": "video_1",
                "type": "stock_video",
                "layout": "full_screen",
                "asset_id": "assets/test.mp4",
            }
        ],
        "events": [
            # Enter at 15.54s ("rate rises"), Exit at 2.95s ("50 lakh")
            {"action": "enter", "target_id": "video_1", "anchor": "rate rises", "style": "cut"},
            {"action": "exit", "target_id": "video_1", "anchor": "50 lakh", "direction": "cut"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw)
    res = validate_story_draft(
        draft=draft,
        word_timestamps=loan_fixture["word_timestamps"],
        available_assets=["assets/test.mp4"],
    )
    assert res.valid is False
    assert any(e.code == "EXIT_BEFORE_OBJECT_ENTER" for e in res.errors)


def test_stock_video_temporal_exclusivity_surface_elements(loan_fixture: dict):
    """6. Stock video cannot overlap with another surface element (card, chart, etc.)."""
    raw = {
        "story_id": "surface_collision_test",
        "objects": [
            {
                "id": "card_active",
                "type": "card",
                "layout": "center",
                "title": "Overlapping Card",
                "subtitle": "Conflict",
                "display_value": "₹50 Lakh",
                "numeric_value": 5000000,
            },
            {
                "id": "video_broll",
                "type": "stock_video",
                "layout": "full_screen",
                "asset_id": "assets/test.mp4",
            },
        ],
        "events": [
            # Card active from 2.95s ("50 lakh") -> exits at 30.04s ("heavy burden")
            {"action": "enter", "target_id": "card_active", "anchor": "50 lakh"},
            {"action": "exit", "target_id": "card_active", "anchor": "heavy burden", "direction": "fade"},
            # Video enters at 15.54s ("rate rises") -> exits at 30.04s ("heavy burden")
            # Overlaps card_active between 15.54s and 30.04s!
            {"action": "enter", "target_id": "video_broll", "anchor": "rate rises", "style": "cut"},
            {"action": "exit", "target_id": "video_broll", "anchor": "heavy burden", "direction": "cut"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw)
    res = validate_story_draft(
        draft=draft,
        word_timestamps=loan_fixture["word_timestamps"],
        available_assets=["assets/test.mp4"],
    )
    assert res.valid is False
    assert any(e.code == "MACRO_LAYOUT_COLLISION" for e in res.errors)


def test_stock_video_temporal_exclusivity_connectors(loan_fixture: dict):
    """7. Stock video cannot coexist with any active connector."""
    raw = {
        "story_id": "connector_collision_test",
        "objects": [
            {
                "id": "card_a",
                "type": "card",
                "layout": "split_left",
                "title": "A",
                "subtitle": "A",
                "display_value": "1",
                "numeric_value": 1,
            },
            {
                "id": "card_b",
                "type": "card",
                "layout": "split_right",
                "title": "B",
                "subtitle": "B",
                "display_value": "2",
                "numeric_value": 2,
            },
            {
                "id": "ab_conn",
                "type": "connector",
                "layout": "center",
                "from_id": "card_a",
                "to_id": "card_b",
                "label": "Flow",
            },
            {
                "id": "video_broll",
                "type": "stock_video",
                "layout": "full_screen",
                "asset_id": "assets/test.mp4",
            },
        ],
        "events": [
            {"action": "enter", "target_id": "card_a", "anchor": "50 lakh"},
            {"action": "enter", "target_id": "card_b", "anchor": "50 lakh"},
            {"action": "connect", "target_id": "ab_conn", "anchor": "starts at"},
            # Video enters at rate rises while connector is still active!
            {"action": "enter", "target_id": "video_broll", "anchor": "rate rises", "style": "cut"},
            {"action": "exit", "target_id": "video_broll", "anchor": "heavy burden", "direction": "cut"},
        ],
    }
    draft = ContinuousStoryDraft.model_validate(raw)
    res = validate_story_draft(
        draft=draft,
        word_timestamps=loan_fixture["word_timestamps"],
        available_assets=["assets/test.mp4"],
    )
    assert res.valid is False
    assert any(e.code == "STOCK_VIDEO_CONNECTOR_COLLISION" for e in res.errors)


def test_video_resolver_missing_request():
    """8. Fails loudly with VIDEO_ASSET_REQUEST_MISSING when neither request nor ID is provided."""
    resolver = ContinuousStoryAssetResolver(
        pexels_api_key="mock",
        pixabay_api_key="mock",
    )
    with pytest.raises(ContinuousStoryAssetResolverError) as exc_info:
        resolver.resolve_video_asset(
            None,  # type: ignore
            object_id="test_video",
            project_id="test_proj",
        )
    assert "VIDEO_ASSET_REQUEST_MISSING" in str(exc_info.value)


def test_video_resolver_search_no_results():
    """9. Fails loudly with VIDEO_SEARCH_NO_RESULT when providers return no hits."""
    resolver = ContinuousStoryAssetResolver(
        pexels_api_key="mock_pexels",
        pixabay_api_key="mock_pixabay",
    )
    req = VideoAssetRequest(query="nonexistent query 123456xyz")

    with patch.object(resolver, "_search_pexels_video", return_value=[]), \
         patch.object(resolver, "_search_pixabay_video", return_value=[]):
        with pytest.raises(ContinuousStoryAssetResolverError) as exc_info:
            resolver.resolve_video_asset(
                req,
                object_id="test_video",
                project_id="test_proj",
            )
        assert "VIDEO_SEARCH_NO_RESULT" in str(exc_info.value)


def test_video_resolver_duration_too_short():
    """10. Fails loudly with VIDEO_DURATION_TOO_SHORT when clip is shorter than required duration."""
    resolver = ContinuousStoryAssetResolver(
        pexels_api_key="mock_pexels",
        pixabay_api_key="mock_pixabay",
    )
    req = VideoAssetRequest(query="bank exterior")

    # Mock provider returning 5-second clip when 15 seconds are required
    short_candidate = [{
        "provider": "pexels",
        "download_url": "https://example.com/short.mp4",
        "source_url": "https://pexels.com/video/1",
        "author": "Creator",
        "width": 1920,
        "height": 1080,
        "duration": 5.0,
    }]

    with patch.object(resolver, "_search_pexels_video", return_value=short_candidate):
        with pytest.raises(ContinuousStoryAssetResolverError) as exc_info:
            resolver.resolve_video_asset(
                req,
                object_id="test_video",
                project_id="test_proj",
                required_duration_seconds=15.0,
            )
        assert "VIDEO_DURATION_TOO_SHORT" in str(exc_info.value)


def test_video_resolver_download_failure(tmp_path: Path):
    """11. Fails loudly with VIDEO_DOWNLOAD_FAILED on network/corrupt download errors."""
    resolver = ContinuousStoryAssetResolver(
        pexels_api_key="mock_pexels",
        pixabay_api_key="mock_pixabay",
        cache_dir=tmp_path / "cache",
        remotion_public_dir=tmp_path / "remotion",
    )
    req = VideoAssetRequest(query="bank exterior")
    candidate = [{
        "provider": "pexels",
        "download_url": "https://example.com/corrupt.mp4",
        "source_url": "https://pexels.com/video/1",
        "author": "Creator",
        "width": 1920,
        "height": 1080,
        "duration": 20.0,
    }]

    mock_resp = MagicMock()
    mock_resp.read.return_value = b"not a valid mp4 header"
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = False

    with patch.object(resolver, "_search_pexels_video", return_value=candidate), \
         patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(ContinuousStoryAssetResolverError) as exc_info:
            resolver.resolve_video_asset(
                req,
                object_id="test_video",
                project_id="test_proj",
            )
        assert "VIDEO_DOWNLOAD_FAILED" in str(exc_info.value)


def test_video_resolver_caching_and_staging(tmp_path: Path):
    """12. Successful download caches the video and stages it to Remotion public assets."""
    cache_dir = tmp_path / "cache"
    remotion_dir = tmp_path / "remotion"
    resolver = ContinuousStoryAssetResolver(
        pexels_api_key="mock_pexels",
        pixabay_api_key="mock_pixabay",
        cache_dir=cache_dir,
        remotion_public_dir=remotion_dir,
    )
    req = VideoAssetRequest(query="bank exterior")

    candidate = [{
        "provider": "pexels",
        "download_url": "https://example.com/good.mp4",
        "source_url": "https://pexels.com/video/1",
        "author": "Creator",
        "width": 1920,
        "height": 1080,
        "duration": 20.0,
    }]

    # Valid MP4 header with 'ftyp' at offset 4
    fake_mp4_bytes = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 100
    mock_resp = MagicMock()
    mock_resp.read.return_value = fake_mp4_bytes
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = False

    with patch.object(resolver, "_search_pexels_video", return_value=candidate), \
         patch("urllib.request.urlopen", return_value=mock_resp):
        resolved = resolver.resolve_video_asset(
            req,
            object_id="bank_clip",
            project_id="proj_123",
            required_duration_seconds=10.0,
        )

        assert resolved.asset_id == "assets/bank_clip.mp4"
        assert resolved.provider == "pexels"
        assert resolved.duration == 20.0
        assert (remotion_dir / resolved.local_path).exists()
        assert (cache_dir / "vid_bank_exterior.mp4").exists()
