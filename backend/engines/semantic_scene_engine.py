import re
from dataclasses import dataclass

from domain.scene_script import SceneScript
from domain.semantic_scene import SemanticEntity, SemanticRelationship, SemanticScene
from registries.finance_domain_registry import FinanceDomainRegistry


MONEY_PATTERN = re.compile(
    r"(?P<raw>(?:₹\s*|Rs\.?\s*)?\d{1,3}(?:,\d{3})+(?:\s*/\s*month)?)",
    re.IGNORECASE,
)

PRICE_MARKERS = ("costs", "cost", "price", "full price", "total price")
MONTHLY_MARKERS = ("emi", "per month", "/month", "monthly", "installment", "instalment")


@dataclass(frozen=True)
class MoneyMention:
    raw: str
    value: int
    source_text: str


class SemanticSceneEngine:
    def __init__(self, finance_registry: FinanceDomainRegistry):
        self.finance_registry = finance_registry

    def run(self, scene_script: SceneScript) -> SemanticScene:
        mentions = self._extract_money_mentions(scene_script.narration)
        entities = self._build_entities(mentions)
        relationships = self._build_relationships(entities)
        warnings = self._build_warnings(
            mentions=mentions,
            entities=entities,
            relationships=relationships,
        )
        confidence = self._score_confidence(
            scene_script=scene_script,
            entities=entities,
            relationships=relationships,
        )
        if confidence < 0.75:
            warnings.append("low confidence under 0.75")

        return SemanticScene(
            scene_id=scene_script.scene_id,
            primary_concept=scene_script.mechanism,
            confidence=confidence,
            warnings=warnings,
            entities=entities,
            relationships=relationships,
        )

    def _extract_money_mentions(self, narration: str) -> list[MoneyMention]:
        mentions: list[MoneyMention] = []
        for match in MONEY_PATTERN.finditer(narration):
            raw = match.group("raw")
            mentions.append(
                MoneyMention(
                    raw=raw,
                    value=self._parse_money_value(raw),
                    source_text=self._source_sentence(narration, match.start(), match.end()),
                )
            )
        return mentions

    def _build_entities(self, mentions: list[MoneyMention]) -> list[SemanticEntity]:
        entities: list[SemanticEntity] = []
        role_counts: dict[str, int] = {}
        for index, mention in enumerate(mentions, start=1):
            role = self._assign_role(mention)
            role_counts[role] = role_counts.get(role, 0) + 1
            entity_id = self._entity_id(role, role_counts[role], index)
            entities.append(
                SemanticEntity(
                    id=entity_id,
                    role=role,
                    raw=mention.raw,
                    value=mention.value,
                    unit="INR",
                    source_text=mention.source_text,
                )
            )
        return entities

    def _assign_role(self, mention: MoneyMention) -> str:
        source = mention.source_text.lower()
        raw = mention.raw.lower()
        if any(marker in source for marker in MONTHLY_MARKERS) or "/month" in raw:
            return "monthly_payment"
        if any(marker in source for marker in PRICE_MARKERS):
            return "product_price"
        return "unknown_money"

    def _build_relationships(self, entities: list[SemanticEntity]) -> list[SemanticRelationship]:
        product_price = next((entity for entity in entities if entity.role == "product_price"), None)
        monthly_payment = next(
            (entity for entity in entities if entity.role == "monthly_payment"),
            None,
        )
        if product_price is None or monthly_payment is None:
            return []

        return [
            SemanticRelationship(
                type="reframes",
                from_entity_id=monthly_payment.id,
                to_entity_id=product_price.id,
            )
        ]

    def _build_warnings(
        self,
        *,
        mentions: list[MoneyMention],
        entities: list[SemanticEntity],
        relationships: list[SemanticRelationship],
    ) -> list[str]:
        warnings: list[str] = []
        unknown_entities = [entity for entity in entities if entity.role == "unknown_money"]
        if unknown_entities:
            warnings.append("ambiguous money amount")

        unknown_values: dict[int, int] = {}
        for entity in unknown_entities:
            unknown_values[entity.value] = unknown_values.get(entity.value, 0) + 1
        if any(count > 1 for count in unknown_values.values()):
            warnings.append("repeated money with unclear role")

        roles = {entity.role for entity in entities}
        if "product_price" not in roles or "monthly_payment" not in roles or not relationships:
            warnings.append("required relationship missing")
        if not mentions:
            warnings.append("no money amount detected")

        return warnings

    def _score_confidence(
        self,
        *,
        scene_script: SceneScript,
        entities: list[SemanticEntity],
        relationships: list[SemanticRelationship],
    ) -> float:
        score = 0.0
        roles = {entity.role for entity in entities}
        if {"product_price", "monthly_payment"}.issubset(roles):
            score += 0.4
        if entities and all(entity.source_text.strip() for entity in entities):
            score += 0.2
        if self.finance_registry.has_mechanism(scene_script.mechanism):
            score += 0.2
        if any(relationship.type == "reframes" for relationship in relationships):
            score += 0.2
        return round(score, 2)

    @staticmethod
    def _parse_money_value(raw: str) -> int:
        digits = re.sub(r"[^\d]", "", raw)
        return int(digits)

    @staticmethod
    def _source_sentence(narration: str, start: int, end: int) -> str:
        sentence_start = max(
            narration.rfind(".", 0, start),
            narration.rfind("!", 0, start),
            narration.rfind("?", 0, start),
        )
        sentence_end_candidates = [
            position for position in (
                narration.find(".", end),
                narration.find("!", end),
                narration.find("?", end),
            )
            if position != -1
        ]
        sentence_end = min(sentence_end_candidates) if sentence_end_candidates else len(narration)
        return narration[sentence_start + 1 : sentence_end + 1].strip()

    @staticmethod
    def _entity_id(role: str, role_count: int, mention_index: int) -> str:
        if role == "product_price" and role_count == 1:
            return "entity_price"
        if role == "monthly_payment" and role_count == 1:
            return "entity_emi"
        return f"entity_amount_{mention_index}"
