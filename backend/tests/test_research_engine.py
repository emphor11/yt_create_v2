import pytest

from domain.generate_video_request import GenerateVideoRequest
from engines.research_engine import ResearchEngine, ResearchEngineError
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


def valid_research_payload() -> dict:
    return {
        "schema_version": "1",
        "topic": "Tax Savings on Home Loans",
        "audience": "young professionals",
        "channel": "FinanceShorts",
        "verified_facts": ["Fact 1", "Fact 2", "Fact 3"],
        "statistics": ["Stat 1"],
        "concepts": ["Concept 1", "Concept 2"],
        "misconceptions": ["Misconception 1"],
        "examples": ["Example 1"],
        "trusted_sources": ["Source 1"],
    }


def test_research_engine_returns_valid_research_packet() -> None:
    provider = StaticTestLLMProvider(valid_research_payload())
    engine = ResearchEngine(provider)

    result = engine.run(
        GenerateVideoRequest(
            topic="Tax Savings on Home Loans",
            audience="young professionals",
            channel="FinanceShorts",
        )
    )

    assert result.research_packet.topic == "Tax Savings on Home Loans"
    assert result.research_packet.verified_facts == ["Fact 1", "Fact 2", "Fact 3"]
    assert result.provider_metadata.provider == "static-test"
    assert provider.last_request is not None
    assert provider.last_request.schema_name == "ResearchPacket"
    assert provider.last_request.messages[0].role == "system"


def test_research_engine_raises_error_for_invalid_shape() -> None:
    # Missing required keys
    provider = StaticTestLLMProvider({"topic": "Tax Savings on Home Loans"})
    engine = ResearchEngine(provider)

    with pytest.raises(ResearchEngineError, match="invalid ResearchPacket JSON") as exc:
        engine.run(
            GenerateVideoRequest(
                topic="Tax Savings on Home Loans",
                audience="young professionals",
                channel="FinanceShorts",
            )
        )

    assert exc.value.raw_payload == {"topic": "Tax Savings on Home Loans"}
    assert exc.value.provider_metadata is not None
