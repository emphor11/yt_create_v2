import io
import os
import json
import logging
import urllib.request
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class ImageGenerationError(Exception):
    """Raised when an image provider fails to generate an image."""


class ImageGenerationProvider(ABC):
    @abstractmethod
    def generate_image(self, prompt: str, negative_prompt: str = "") -> bytes:
        """Generates an image from a prompt and returns raw image bytes."""


class HuggingFaceImageProvider(ImageGenerationProvider):
    def __init__(self, token: str, models: list[str] | None = None):
        self.token = token.strip()
        self.models = models or [
            "black-forest-labs/FLUX.1-dev",
            "black-forest-labs/FLUX.1-schnell",
            "stabilityai/stable-diffusion-xl-base-1.0",
        ]

    def generate_image(self, prompt: str, negative_prompt: str = "") -> bytes:
        from huggingface_hub import InferenceClient

        client = InferenceClient(api_key=self.token)
        last_exc = None

        for model in self.models:
            try:
                logger.info("Attempting Hugging Face text_to_image with model: %s", model)
                img = client.text_to_image(prompt, model=model)
                buf = io.BytesIO()
                # Save as PNG
                img.save(buf, format="PNG")
                return buf.getvalue()
            except Exception as exc:
                logger.warning("Hugging Face model %s failed: %s", model, exc)
                last_exc = exc

        raise ImageGenerationError(f"All Hugging Face models failed. Last error: {last_exc}") from last_exc


class GeminiImageProvider(ImageGenerationProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image"):
        self.api_key = api_key.strip()
        self.model = model.strip()

    def generate_image(self, prompt: str, negative_prompt: str = "") -> bytes:
        import base64

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"]
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if not candidates:
                    raise ImageGenerationError(f"Gemini returned no candidates: {data}")
                parts = candidates[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "inlineData" in p:
                        b64_data = p["inlineData"].get("data", "")
                        return base64.b64decode(b64_data)
                raise ImageGenerationError("No inlineData image found in Gemini response.")
        except Exception as exc:
            raise ImageGenerationError(f"Gemini image generation failed: {exc}") from exc


class StockImageThumbnailProvider(ImageGenerationProvider):
    """Fallback provider that searches Pexels for a pristine high-resolution photo matching the prompt."""

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()

    def generate_image(self, prompt: str, negative_prompt: str = "") -> bytes:
        # Extract keywords from prompt for stock photo search
        words = [w.strip() for w in prompt.replace(",", " ").split() if len(w) > 3]
        # Pick 3-4 impactful keywords
        query = " ".join(words[:4]) if words else "business finance stress"
        encoded = urllib.parse.quote(query)
        url = f"https://api.pexels.com/v1/search?query={encoded}&per_page=5"
        req = urllib.request.Request(url, headers={"Authorization": self.api_key, "User-Agent": "Mozilla/5.0"})

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                photos = data.get("photos", [])
                if not photos:
                    raise ImageGenerationError(f"No stock photos found for query '{query}'")

                # Prefer high-resolution landscape photo
                best_photo = photos[0]
                for p in photos:
                    if (p.get("width") or 0) > (p.get("height") or 0):
                        best_photo = p
                        break

                src = best_photo.get("src", {})
                img_url = src.get("large2x") or src.get("large") or src.get("original")
                if not img_url:
                    raise ImageGenerationError("Stock photo has no image URL.")

                req_img = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_img, timeout=20) as img_resp:
                    return img_resp.read()
        except Exception as exc:
            raise ImageGenerationError(f"Stock photo fallback failed: {exc}") from exc


class CompositeImageProvider(ImageGenerationProvider):
    def __init__(self, providers: list[tuple[str, ImageGenerationProvider]]):
        self.providers = providers
        self.last_provider_used: str | None = None

    def generate_image(self, prompt: str, negative_prompt: str = "") -> bytes:
        if not self.providers:
            raise ImageGenerationError("No image generation providers configured.")

        errors: list[str] = []
        for name, provider in self.providers:
            try:
                logger.info("Trying image generation provider: %s", name)
                img_bytes = provider.generate_image(prompt, negative_prompt=negative_prompt)
                if img_bytes and len(img_bytes) > 1000:
                    self.last_provider_used = name
                    logger.info("Successfully generated thumbnail using provider: %s", name)
                    return img_bytes
            except Exception as exc:
                logger.warning("Provider '%s' failed: %s", name, exc)
                errors.append(f"{name}: {exc}")

        raise ImageGenerationError(f"All image providers failed: {'; '.join(errors)}")


def build_image_generation_provider() -> CompositeImageProvider:
    providers: list[tuple[str, ImageGenerationProvider]] = []

    # 1. Hugging Face FLUX.1 (User's primary selection)
    hf_token = os.getenv("HF_TOKEN", "").strip() or os.getenv("HUGGINGFACE_API_KEY", "").strip()
    if hf_token:
        providers.append(("huggingface_flux", HuggingFaceImageProvider(token=hf_token)))

    # 2. Gemini Image Generation
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    if gemini_key:
        providers.append(("gemini_image", GeminiImageProvider(api_key=gemini_key)))

    # 3. Pexels Stock Photo Fallback
    pexels_key = os.getenv("PEXELS_API_KEY", "").strip()
    if pexels_key:
        providers.append(("pexels_stock", StockImageThumbnailProvider(api_key=pexels_key)))

    return CompositeImageProvider(providers)
