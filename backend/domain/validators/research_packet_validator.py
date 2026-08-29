from domain.research_packet import ResearchPacket
from domain.validation import ValidationResult


class ResearchPacketValidator:
    def validate(self, packet: ResearchPacket) -> ValidationResult:
        errors: list[str] = []

        if not packet.topic or not packet.topic.strip():
            errors.append("Research packet must specify a topic.")

        # Check that the packet has meaningful research content
        has_content = any(
            bool(item.strip())
            for array in [
                packet.verified_facts,
                packet.statistics,
                packet.concepts,
                packet.misconceptions,
                packet.examples,
                packet.trusted_sources,
            ]
            for item in array
            if isinstance(item, str)
        )

        if not has_content:
            errors.append("Research packet must contain at least some research data (facts, concepts, or statistics).")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
