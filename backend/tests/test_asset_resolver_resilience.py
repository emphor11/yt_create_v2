import os
from unittest.mock import patch, MagicMock
import urllib.error
import pytest
from pathlib import Path
from engines.video_assembly.asset_resolver import AssetResolver, AssetResolverError


def test_asset_resolver_skips_failing_first_candidate(tmp_path: Path):
    resolver = AssetResolver(cache_dir=tmp_path)
    
    # Candidate 1 will fail with 403, Candidate 2 will succeed
    candidate_links = [
        "https://videos.pexels.com/video-files/dead/dead.mp4",
        "https://videos.pexels.com/video-files/live/live.mp4",
    ]
    
    mock_mp4_bytes = b"\x00\x00\x00 ftypisom\x00\x00\x02\x00" + b"\x00" * 100

    with patch.dict(os.environ, {"PEXELS_API_KEY": "fake_key"}):
        with patch.object(resolver, "_search_pexels", return_value=candidate_links):
            with patch.object(resolver, "_is_video_compliant", return_value=True):
                with patch.object(resolver, "_get_video_fps", return_value=30.0):
                    
                    def mock_urlopen(req, timeout=20):
                        url = req.full_url if hasattr(req, "full_url") else str(req)
                        if "dead.mp4" in url:
                            raise urllib.error.HTTPError(url, 403, "Forbidden", {}, None)
                        
                        mock_resp = MagicMock()
                        mock_resp.read.return_value = mock_mp4_bytes
                        mock_resp.__enter__.return_value = mock_resp
                        mock_resp.__exit__.return_value = None
                        return mock_resp

                    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
                        asset = resolver.resolve_asset(
                            asset_id="test_skip_01",
                            preferred_component="StockVideo",
                            asset_query="person reviewing documents",
                        )
                        assert asset is not None
                        assert asset.url == "https://videos.pexels.com/video-files/live/live.mp4"
                        assert asset.source == "pexels"
                        assert asset.asset_status == "cached"
                        assert Path(asset.local_path).exists()


def test_asset_resolver_falls_back_to_pixabay_when_pexels_fails(tmp_path: Path):
    resolver = AssetResolver(cache_dir=tmp_path)
    
    pexels_links = ["https://videos.pexels.com/video-files/dead/dead.mp4"]
    pixabay_links = ["https://pixabay.com/videos/download/pixabay_live.mp4"]
    mock_mp4_bytes = b"\x00\x00\x00 ftypisom\x00\x00\x02\x00" + b"\x00" * 100

    with patch.dict(os.environ, {"PEXELS_API_KEY": "fake_pexels", "PIXABAY_API_KEY": "fake_pixabay"}):
        with patch.object(resolver, "_search_pexels", return_value=pexels_links):
            with patch.object(resolver, "_search_pixabay", return_value=pixabay_links):
                with patch.object(resolver, "_is_video_compliant", return_value=True):
                    with patch.object(resolver, "_get_video_fps", return_value=30.0):
                        
                        def mock_urlopen(req, timeout=20):
                            url = req.full_url if hasattr(req, "full_url") else str(req)
                            if "pexels.com" in url:
                                raise urllib.error.HTTPError(url, 403, "Forbidden", {}, None)
                            
                            mock_resp = MagicMock()
                            mock_resp.read.return_value = mock_mp4_bytes
                            mock_resp.__enter__.return_value = mock_resp
                            mock_resp.__exit__.return_value = None
                            return mock_resp

                        with patch("urllib.request.urlopen", side_effect=mock_urlopen):
                            asset = resolver.resolve_asset(
                                asset_id="test_pixabay_01",
                                preferred_component="StockVideo",
                                asset_query="person reviewing documents",
                            )
                            assert asset is not None
                            assert asset.url == "https://pixabay.com/videos/download/pixabay_live.mp4"
                            assert asset.source == "pixabay"
                            assert asset.asset_status == "cached"


def test_asset_resolver_raises_when_all_candidates_fail(tmp_path: Path):
    resolver = AssetResolver(cache_dir=tmp_path)
    candidate_links = ["https://videos.pexels.com/video-files/dead1.mp4", "https://videos.pexels.com/video-files/dead2.mp4"]

    with patch.dict(os.environ, {"PEXELS_API_KEY": "fake_key"}):
        with patch.object(resolver, "_search_pexels", return_value=candidate_links):
            with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError("url", 403, "Forbidden", {}, None)):
                with pytest.raises(AssetResolverError) as exc_info:
                    resolver.resolve_asset(
                        asset_id="test_fail_all",
                        preferred_component="StockVideo",
                        asset_query="test query",
                    )
                assert "Failed to download or validate any stock asset" in str(exc_info.value)
