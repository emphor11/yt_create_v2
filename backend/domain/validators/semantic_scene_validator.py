from domain.scene_script import SceneScript
from domain.semantic_scene import SemanticScene
from domain.validation import ValidationResult
from registries.finance_domain_registry import FinanceDomainRegistry


REQUIRED_ROLES = {"product_price", "monthly_payment"}
FORBIDDEN_DOWNSTREAM_KEYS = {
    "visual_events",
    "component",
    "props",
    "timed_spans",
    "render_spec",
    "frames",
}


class SemanticSceneValidator:
    def __init__(self, finance_registry: FinanceDomainRegistry):
        self.finance_registry = finance_registry

    def validate(
        self,
        semantic_scene: SemanticScene,
        *,
        scene_script: SceneScript,
    ) -> ValidationResult:
        errors: list[str] = []

        if semantic_scene.scene_id != scene_script.scene_id:
            errors.append("SemanticScene scene_id must match SceneScript scene_id.")
        if semantic_scene.primary_concept != scene_script.mechanism:
            errors.append("SemanticScene primary_concept must match SceneScript mechanism.")
        if not self.finance_registry.has_mechanism(semantic_scene.primary_concept):
            errors.append("SemanticScene primary_concept must be a supported finance mechanism.")

        if semantic_scene.confidence < 0 or semantic_scene.confidence > 1:
            errors.append("SemanticScene confidence must be between 0 and 1.")

        roles = {entity.role for entity in semantic_scene.entities}
        missing_roles = REQUIRED_ROLES - roles
        for role in sorted(missing_roles):
            errors.append(f"SemanticScene missing required role: {role}.")

        entity_ids = set()
        for entity in semantic_scene.entities:
            if not entity.id.strip():
                errors.append("Semantic entity id is required.")
            if entity.id in entity_ids:
                errors.append(f"Duplicate semantic entity id: {entity.id}.")
            entity_ids.add(entity.id)
            if not entity.role.strip():
                errors.append(f"Semantic entity {entity.id} role is required.")
            if not entity.raw.strip():
                errors.append(f"Semantic entity {entity.id} raw value is required.")
            if entity.value <= 0:
                errors.append(f"Semantic entity {entity.id} value must be positive.")
            if entity.unit != "INR":
                errors.append(f"Semantic entity {entity.id} unit must be INR.")
            if not entity.source_text.strip():
                errors.append(f"Semantic entity {entity.id} source_text is required.")

        product_price = next(
            (entity for entity in semantic_scene.entities if entity.role == "product_price"),
            None,
        )
        monthly_payment = next(
            (entity for entity in semantic_scene.entities if entity.role == "monthly_payment"),
            None,
        )
        reframes_relationship = next(
            (
                relationship
                for relationship in semantic_scene.relationships
                if relationship.type == "reframes"
            ),
            None,
        )
        if product_price is not None and monthly_payment is not None:
            if reframes_relationship is None:
                errors.append("SemanticScene requires a reframes relationship.")
            elif (
                reframes_relationship.from_entity_id != monthly_payment.id
                or reframes_relationship.to_entity_id != product_price.id
            ):
                errors.append(
                    "SemanticScene reframes relationship must point from monthly_payment to product_price."
                )

        for relationship in semantic_scene.relationships:
            if relationship.from_entity_id not in entity_ids:
                errors.append(
                    f"Relationship {relationship.type} references unknown from_entity_id."
                )
            if relationship.to_entity_id not in entity_ids:
                errors.append(
                    f"Relationship {relationship.type} references unknown to_entity_id."
                )

        if semantic_scene.confidence < 0.75 and "low confidence under 0.75" not in semantic_scene.warnings:
            errors.append("SemanticScene low confidence must be reported in warnings.")

        leaked_keys = FORBIDDEN_DOWNSTREAM_KEYS.intersection(semantic_scene.model_dump().keys())
        if leaked_keys:
            errors.append(
                "SemanticScene must not contain downstream fields: "
                + ", ".join(sorted(leaked_keys))
                + "."
            )

        if errors:
            return ValidationResult(
                status="blocked",
                errors=errors,
                warnings=semantic_scene.warnings,
            )
        if semantic_scene.warnings:
            return ValidationResult(status="warning", warnings=semantic_scene.warnings)

        return ValidationResult(status="valid")
