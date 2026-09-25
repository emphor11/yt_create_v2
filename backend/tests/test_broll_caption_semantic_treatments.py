from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, BrollCaptionData
from engines.video_assembly.composition_resolver import CompositionResolver
from domain.visual_intent import (
    VisualIntent,
    SemanticEntity,
    CausalStructure,
)


def test_broll_caption_data_accepts_all_new_fields() -> None:
    data = BrollCaptionData(
        caption="Risk comes from not knowing what you are doing.",
        emphasis_phrase="not knowing what you are doing",
        author="Warren Buffett",
        header_label="CORE INVESTMENT PRINCIPLE",
        variant="quote",
        source_context="Chairman, Berkshire Hathaway",
        polarity="critical",
    )
    assert data.caption == "Risk comes from not knowing what you are doing."
    assert data.emphasis_phrase == "not knowing what you are doing"
    assert data.author == "Warren Buffett"
    assert data.header_label == "CORE INVESTMENT PRINCIPLE"
    assert data.variant == "quote"
    assert data.source_context == "Chairman, Berkshire Hathaway"
    assert data.polarity == "critical"


def test_broll_caption_backward_compatibility() -> None:
    data = BrollCaptionData(
        caption="Inflation quietly destroys cash purchasing power.",
    )
    assert data.caption == "Inflation quietly destroys cash purchasing power."
    assert data.emphasis_phrase is None
    assert data.author is None
    assert data.header_label is None
    assert data.variant is None
    assert data.source_context is None
    assert data.polarity is None


def test_broll_caption_allowed_variants_in_registry() -> None:
    defn = CompositionRegistry.get("broll_caption")
    assert defn is not None
    assert "statement" in defn.allowed_variants
    assert "quote" in defn.allowed_variants
    assert "ambient_broll" in defn.allowed_variants
    assert "standard" in defn.allowed_variants






def test_composition_resolver_broll_caption_maps_all_props() -> None:
    resolver = CompositionResolver()
    spec = resolver.resolve_composition(
        composition_id="broll_caption",
        composition_data={
            "caption": "An investment in knowledge pays the best interest.",
            "emphasis_phrase": "pays the best interest",
            "author": "Benjamin Franklin",
            "header_label": "HISTORICAL MAXIM",
            "variant": "quote",
            "source_context": "Way to Wealth (1758)",
            "polarity": "positive",
        },
    )
    assert spec.component_id == "BrollCaption"
    assert spec.props["caption"] == "An investment in knowledge pays the best interest."
    assert spec.props["emphasisPhrase"] == "pays the best interest"
    assert spec.props["author"] == "Benjamin Franklin"
    assert spec.props["headerLabel"] == "HISTORICAL MAXIM"
    assert spec.props["variant"] == "quote"
    assert spec.props["sourceContext"] == "Way to Wealth (1758)"
    assert spec.props["polarity"] == "positive"


def test_broll_caption_schema_required_invariants() -> None:
    schema = CompositionRegistry.get_data_schema("broll_caption")
    assert schema is not None
    required = schema["required"]
    assert set(required) == {"caption"}
    for optional_field in ["emphasis_phrase", "author", "header_label", "variant", "source_context", "polarity"]:
        assert optional_field not in required
        assert optional_field in schema["properties"]
