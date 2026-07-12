from pathlib import Path


def load_prompt(filename: str) -> str:
    """Load a static prompt template from the assets directory."""
    assets_root = Path(__file__).resolve().parent
    prompt_path = assets_root / "prompts" / filename
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt asset file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8").strip()
