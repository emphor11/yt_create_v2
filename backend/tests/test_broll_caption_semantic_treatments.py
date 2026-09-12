from typing import Any
import pytest
from registries.composition_registry import CompositionRegistry, BrollCaptionData
from engines.composition_planner_engine import (
    build_candidate_composition_data,
    merge_factual_and_presentation_data,
)
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


def test_candidate_fact_extraction_statement_quote_broll() -> None:
    # 1. Statement
    intent1 = VisualIntent(
        intent_id="intent_01",
        narration_excerpt="Compounding requires leaving money uninterrupted.",
        what_viewer_must_understand="The first rule of compounding is never interrupt it.",
        relationship_type="statement",
        key_values=["never interrupt it"],
    )
    cand1 = build_candidate_composition_data("broll_caption", intent1)
    assert cand1["variant"] == "statement"
    assert cand1["header_label"] == "CORE PRINCIPLE"
    assert cand1["caption"] == "The first rule of compounding is never interrupt it."
    assert cand1["emphasis_phrase"] == "never interrupt it"

    # 2. Quote
    intent2 = VisualIntent(
        intent_id="intent_02",
        narration_excerpt="Charlie Munger once said the big money is in waiting.",
        what_viewer_must_understand="The big money is not in buying and selling, but in waiting.",
        relationship_type="quote",
        entities=[
            SemanticEntity(name="Charlie Munger", category="person", role="author"),
            SemanticEntity(name="Poor Charlie's Almanack", category="concept", role="source"),
        ],
    )
    cand2 = build_candidate_composition_data("broll_caption", intent2)
    assert cand2["variant"] == "quote"
    assert cand2["author"] == "Charlie Munger"
    assert cand2["source_context"] == "Poor Charlie's Almanack"
    assert cand2["header_label"] == "NOTABLE PERSPECTIVE"

    # 3. Ambient B-roll
    intent3 = VisualIntent(
        intent_id="intent_03",
        narration_excerpt="Global trade routes face persistent disruptions.",
        what_viewer_must_understand="Global supply chain bottleneck overview.",
        relationship_type="broll",
    )
    cand3 = build_candidate_composition_data("broll_caption", intent3)
    assert cand3["variant"] == "ambient_broll"
    assert cand3["header_label"] == "CONTEXTUAL OVERVIEW"


def test_merge_factual_and_presentation_preserves_new_fields() -> None:
    intent = VisualIntent(
        intent_id="intent_04",
        narration_excerpt="Essential investment doctrine.",
        what_viewer_must_understand="Stay disciplined during volatility.",
        relationship_type="statement",
    )
    candidate_facts = {
        "caption": "Stay disciplined during volatility.",
        "emphasis_phrase": "Stay disciplined",
        "header_label": "INVESTMENT DISCIPLINE",
        "variant": "statement",
        "source_context": "Vanguard Principles",
        "polarity": "positive",
    }
    llm_presentation = {
        "composition_id": "broll_caption",
        "caption": "Stay disciplined during volatility and avoid emotional panic.",
    }
    merged = merge_factual_and_presentation_data("broll_caption", candidate_facts, llm_presentation, intent)
    assert merged["caption"] == "Stay disciplined during volatility and avoid emotional panic."
    assert merged["emphasis_phrase"] == "Stay disciplined"
    assert merged["header_label"] == "INVESTMENT DISCIPLINE"
    assert merged["variant"] == "statement"
    assert merged["source_context"] == "Vanguard Principles"
    assert merged["polarity"] == "positive"


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
