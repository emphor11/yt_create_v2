from domain.research_packet import ResearchPacket
from domain.validators.research_packet_validator import ResearchPacketValidator


def test_validator_accepts_valid_packet() -> None:
    packet = ResearchPacket(
        topic="Affordable Monthly Payments",
        audience="millennials",
        channel="FinanceWeekly",
        verified_facts=["Fact 1", "Fact 2", "Fact 3"],
        statistics=["Stat 1"],
        concepts=["Concept 1", "Concept 2"],
        misconceptions=["Misconception 1"],
        examples=["Example 1"],
        trusted_sources=["Source 1"],
    )
    result = ResearchPacketValidator().validate(packet)
    assert result.status == "valid"
    assert not result.errors


def test_validator_rejects_missing_required_items() -> None:
    # Insufficient facts, stats, concepts, sources
    packet = ResearchPacket(
        topic="Affordable Monthly Payments",
        audience="millennials",
        channel="FinanceWeekly",
        verified_facts=["Fact 1"],
        statistics=[],
        concepts=["Concept 1"],
        trusted_sources=[],
    )
    result = ResearchPacketValidator().validate(packet)
    assert result.status == "blocked"
    assert "must contain at least 3 verified facts" in result.errors[0]
    assert "must contain at least 1 statistic" in result.errors[1]
    assert "must contain at least 2 key concepts" in result.errors[2]
    assert "must contain at least 1 trusted source" in result.errors[3]
