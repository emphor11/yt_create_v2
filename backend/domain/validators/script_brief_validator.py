from domain.script_brief import ScriptBrief
from domain.topic_request import TopicRequest
from domain.validation import ValidationResult
from registries.finance_domain_registry import FinanceDomainRegistry


class ScriptBriefValidator:
    def __init__(self, finance_registry: FinanceDomainRegistry):
        self.finance_registry = finance_registry

    def validate(
        self,
        script_brief: ScriptBrief,
        *,
        topic_request: TopicRequest,
    ) -> ValidationResult:
        errors: list[str] = []

        if not script_brief.thesis.strip():
            errors.append("Thesis is required.")
        if script_brief.topic != topic_request.topic:
            errors.append("ScriptBrief topic must match TopicRequest topic.")
        if script_brief.angle != topic_request.angle:
            errors.append("ScriptBrief angle must match TopicRequest angle.")
        if script_brief.recurring_example != "₹80,000 phone":
            errors.append("Recurring example must be the concrete MVP example: ₹80,000 phone.")
        if not script_brief.primary_mechanisms:
            errors.append("At least one mechanism is required.")

        for mechanism in script_brief.primary_mechanisms:
            if not self.finance_registry.has_mechanism(mechanism):
                errors.append(f"Unsupported mechanism: {mechanism}.")

        if not script_brief.scene_functions:
            errors.append("At least one scene function is required.")

        for scene_function in script_brief.scene_functions:
            if not scene_function.scene_id.strip():
                errors.append("Scene function scene_id is required.")
            if not scene_function.label.strip():
                errors.append("Scene function label is required.")
            if not scene_function.purpose.strip():
                errors.append("Scene function purpose is required.")
            if not self.finance_registry.has_mechanism(scene_function.mechanism):
                errors.append(f"Unsupported scene function mechanism: {scene_function.mechanism}.")
            if scene_function.mechanism not in script_brief.primary_mechanisms:
                errors.append(
                    f"Scene function mechanism {scene_function.mechanism} must appear in primary mechanisms."
                )

        if errors:
            return ValidationResult(status="blocked", errors=errors)

        return ValidationResult(status="valid")

