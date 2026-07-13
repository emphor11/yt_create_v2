import pytest

from domain.research_packet import ResearchPacket
from engines.narrative_plan_engine import NarrativePlanEngine, NarrativePlanEngineError
from providers.llm_provider import LLMJsonRequest, LLMJsonResponse, LLMProviderMetadata


class StaticTestLLMProvider:
    def __init__(self, payload: dict):
        self.payload = payload
        self.last_request: LLMJsonRequest | None = None

    def generate_json(self, request: LLMJsonRequest) -> LLMJsonResponse:
        self.last_request = request
        return LLMJsonResponse(
            payload=self.payload,
            metadata=LLMProviderMetadata(
                provider="static-test",
                model="static-test-model",
            ),
        )


def valid_narrative_plan_payload() -> dict:
    return {
        "thesis": "Renting is smarter in high-cost cities",
        "target_pain_point": "Fear of renting",
        "conceptual_hook": "The 5% Rule analogy",
        "narrative_arc_type": "Problem-Agitation-Solution",
        "scene_beats": [
            {
                "scene_id": "scene_01",
                "title": "Introduction",
                "focus_concept": "Opportunity Cost",
                "core_teaching_point": "Show unrecoverable costs of buying vs renting",
            },
            {
                "scene_id": "scene_02",
                "title": "Deep Dive",
                "focus_concept": "The 5% Rule",
                "core_teaching_point": "Math behind renting superiority",
            },
            {
                "scene_id": "scene_03",
                "title": "Conclusion",
                "focus_concept": "Mobility Benefit",
                "core_teaching_point": "Relocate for 30% higher salary",
            },
        ],
    }


def test_narrative_plan_engine_returns_valid_narrative_plan() -> None:
    provider = StaticTestLLMProvider(valid_narrative_plan_payload())
    engine = NarrativePlanEngine(provider)

    result = engine.run(
        ResearchPacket(
            topic="Renting vs Buying",
            audience="young professionals",
            channel="FinanceShorts",
            verified_facts=["Fact 1", "Fact 2", "Fact 3"],
            statistics=["Stat 1"],
            concepts=["Concept 1", "Concept 2"],
            trusted_sources=["Source 1"],
        )
    )

    assert result.narrative_plan.thesis == "Renting is smarter in high-cost cities"
    assert len(result.narrative_plan.scene_beats) == 3
    assert result.provider_metadata.provider == "static-test"
    assert provider.last_request is not None
    assert provider.last_request.schema_name == "NarrativePlan"
    assert provider.last_request.messages[0].role == "system"


def test_narrative_plan_engine_raises_error_for_invalid_shape() -> None:
    provider = StaticTestLLMProvider({"thesis": "Only a thesis"})
    engine = NarrativePlanEngine(provider)

    with pytest.raises(NarrativePlanEngineError, match="invalid NarrativePlan JSON") as exc:
        engine.run(
            ResearchPacket(
                topic="Renting vs Buying",
                audience="young professionals",
                channel="FinanceShorts",
                verified_facts=["Fact 1", "Fact 2", "Fact 3"],
                statistics=["Stat 1"],
                concepts=["Concept 1", "Concept 2"],
                trusted_sources=["Source 1"],
            )
        )

    assert exc.value.raw_payload == {"thesis": "Only a thesis"}
    assert exc.value.provider_metadata is not None
