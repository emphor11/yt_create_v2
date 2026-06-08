import pytest
from pydantic import ValidationError

from domain.scene_script import SceneScript, SceneStoryState
from domain.semantic_scene import SemanticScene
from domain.validators.semantic_scene_validator import SemanticSceneValidator
from engines.semantic_scene_engine import SemanticSceneEngine
from registries.finance_domain_registry import FinanceDomainRegistry


def make_scene_script(
    narration: str = "The phone costs ₹80,000. But the EMI is shown as ₹6,667 per month.",
    mechanism: str = "payment_pain_reduction",
) -> SceneScript:
    return SceneScript(
        scene_id="scene_01",
        topic="Why Monthly Payments Feel Cheap",
        angle="How EMIs hide total cost",
        thesis=(
            "Monthly payments can make an expensive purchase feel cheaper by reducing "
            "payment pain and shifting attention away from the total price."
        ),
        mechanism=mechanism,
        scene_function_label="full_price_vs_monthly_payment",
        arc_phases=["curiosity", "comfort", "reversal", "realization"],
        narrative_purpose=(
            "Move the viewer from noticing the smaller EMI number to realizing that "
            "monthly framing reduces the pain of the full price."
        ),
        narration=narration,
        story_state=SceneStoryState(recurring_example="₹80,000 phone"),
    )


def run_semantic_scene(scene_script: SceneScript):
    registry = FinanceDomainRegistry()
    semantic_scene = SemanticSceneEngine(registry).run(scene_script)
    validation = SemanticSceneValidator(registry).validate(
        semantic_scene,
        scene_script=scene_script,
    )
    return semantic_scene, validation


def role_map(semantic_scene):
    return {entity.role: entity for entity in semantic_scene.entities}


def test_semantic_scene_engine_extracts_mvp_roles_and_relationship() -> None:
    scene_script = make_scene_script()

    semantic_scene, validation = run_semantic_scene(scene_script)
    roles = role_map(semantic_scene)

    assert validation.status == "valid"
    assert semantic_scene.scene_id == "scene_01"
    assert semantic_scene.primary_concept == "payment_pain_reduction"
    assert semantic_scene.confidence == 1.0
    assert semantic_scene.warnings == []
    assert roles["product_price"].id == "entity_price"
    assert roles["product_price"].raw == "₹80,000"
    assert roles["product_price"].value == 80000
    assert roles["product_price"].unit == "INR"
    assert roles["product_price"].source_text == "The phone costs ₹80,000."
    assert roles["monthly_payment"].id == "entity_emi"
    assert roles["monthly_payment"].raw == "₹6,667"
    assert roles["monthly_payment"].value == 6667
    assert roles["monthly_payment"].source_text == (
        "But the EMI is shown as ₹6,667 per month."
    )
    assert semantic_scene.relationships[0].type == "reframes"
    assert semantic_scene.relationships[0].from_entity_id == "entity_emi"
    assert semantic_scene.relationships[0].to_entity_id == "entity_price"


@pytest.mark.parametrize(
    "narration",
    [
        "The phone costs ₹80,000. But the EMI is shown as ₹6,667 per month.",
        "The phone costs Rs. 80,000. But the EMI is shown as Rs. 6,667 per month.",
        "The phone costs 80,000. But the EMI is 6,667/month.",
        "The phone price is ₹ 80,000. The monthly installment is ₹ 6,667.",
        "The full price is Rs 80,000. The monthly payment is Rs 6,667.",
    ],
)
def test_emi_fixture_role_accuracy_is_100_percent(narration: str) -> None:
    scene_script = make_scene_script(narration=narration)

    semantic_scene, validation = run_semantic_scene(scene_script)
    roles = role_map(semantic_scene)

    assert validation.status == "valid"
    assert roles["product_price"].value == 80000
    assert roles["monthly_payment"].value == 6667
    assert semantic_scene.relationships[0].type == "reframes"


def test_semantic_scene_blocks_missing_monthly_payment_role() -> None:
    scene_script = make_scene_script(narration="The phone costs ₹80,000.")

    semantic_scene, validation = run_semantic_scene(scene_script)

    assert validation.status == "blocked"
    assert "SemanticScene missing required role: monthly_payment." in validation.errors
    assert "required relationship missing" in semantic_scene.warnings
    assert "low confidence under 0.75" in semantic_scene.warnings


def test_semantic_scene_warns_for_ambiguous_extra_money() -> None:
    scene_script = make_scene_script(
        narration=(
            "The phone costs ₹80,000. A case is ₹2,000. "
            "But the EMI is shown as ₹6,667 per month."
        )
    )

    semantic_scene, validation = run_semantic_scene(scene_script)

    assert validation.status == "warning"
    assert "ambiguous money amount" in validation.warnings
    assert any(entity.role == "unknown_money" for entity in semantic_scene.entities)


def test_semantic_scene_warns_for_repeated_unclear_money() -> None:
    scene_script = make_scene_script(
        narration=(
            "The phone costs ₹80,000. A fee is ₹2,000. Another charge is ₹2,000. "
            "The EMI is ₹6,667 per month."
        )
    )

    semantic_scene, validation = run_semantic_scene(scene_script)

    assert validation.status == "warning"
    assert "repeated money with unclear role" in validation.warnings


def test_semantic_scene_blocks_unsupported_mechanism() -> None:
    scene_script = make_scene_script(mechanism="unsupported_mechanism")

    _semantic_scene, validation = run_semantic_scene(scene_script)

    assert validation.status == "blocked"
    assert "SemanticScene primary_concept must be a supported finance mechanism." in validation.errors


def test_semantic_scene_rejects_downstream_fields() -> None:
    payload = {
        "scene_id": "scene_01",
        "primary_concept": "payment_pain_reduction",
        "confidence": 1.0,
        "warnings": [],
        "entities": [],
        "relationships": [],
        "visual_events": [],
    }

    with pytest.raises(ValidationError):
        SemanticScene.model_validate(payload)
