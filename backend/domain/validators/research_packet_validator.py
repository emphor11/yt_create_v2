from domain.research_packet import ResearchPacket
from domain.validation import ValidationResult


class ResearchPacketValidator:
    def validate(self, packet: ResearchPacket) -> ValidationResult:
        errors: list[str] = []

        if len(packet.verified_facts) < 3:
            errors.append("Research packet must contain at least 3 verified facts.")
        if len(packet.statistics) < 1:
            errors.append("Research packet must contain at least 1 statistic.")
        if len(packet.concepts) < 2:
            errors.append("Research packet must contain at least 2 key concepts.")
        if len(packet.trusted_sources) < 1:
            errors.append("Research packet must contain at least 1 trusted source.")

        # Ensure strings aren't just whitespace
        for idx, fact in enumerate(packet.verified_facts):
            if not fact.strip():
                errors.append(f"Fact at index {idx} cannot be empty.")
        for idx, stat in enumerate(packet.statistics):
            if not stat.strip():
                errors.append(f"Statistic at index {idx} cannot be empty.")
        for idx, concept in enumerate(packet.concepts):
            if not concept.strip():
                errors.append(f"Concept at index {idx} cannot be empty.")
        for idx, src in enumerate(packet.trusted_sources):
            if not src.strip():
                errors.append(f"Trusted source at index {idx} cannot be empty.")

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")
