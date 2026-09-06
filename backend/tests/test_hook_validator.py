from domain.hook import Hook, VisualDirective
from domain.validators.hook_validator import HookValidator


def test_validator_accepts_valid_hook() -> None:
    hook = Hook(
        conceptual_hook="Anchor vs Engine comparison",
        script_text="Are you renting? You might think you're throwing money away. You're not.",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="Show heavy metal anchor falling in water", trigger_word=None),
            VisualDirective(beat_id="beat_02", visual_instruction="Show rocket engine firing upward", trigger_word="throwing"),
        ],
    )
    result = HookValidator().validate(hook)
    assert result.status == "valid"
    assert not result.errors


def test_validator_rejects_insufficient_visual_directives() -> None:
    hook = Hook(
        conceptual_hook="Concept Description",
        script_text="Intro spoken script",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="Only one visual instruction beat")
        ],
    )
    result = HookValidator().validate(hook)
    assert result.status == "blocked"
    assert "must contain at least 2 visual directives" in result.errors[0]


def test_validator_rejects_invalid_trigger_word() -> None:
    # 1. Missing trigger word for subsequent directive
    hook_missing = Hook(
        conceptual_hook="Concept Description",
        script_text="Intro spoken script here.",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="First beat"),
            VisualDirective(beat_id="beat_02", visual_instruction="Second beat"),
        ],
    )
    result = HookValidator().validate(hook_missing)
    assert result.status == "blocked"
    assert "is a subsequent beat and requires trigger_word" in result.errors[0]

    # 2. Trigger word not in hook script text
    hook_mismatch = Hook(
        conceptual_hook="Concept Description",
        script_text="Intro spoken script here.",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="First beat"),
            VisualDirective(beat_id="beat_02", visual_instruction="Second beat", trigger_word="nonexistent"),
        ],
    )
    result_err = HookValidator().validate(hook_mismatch)
    assert result_err.status == "blocked"
    assert "does not exist in the script text" in result_err.errors[0]


def test_validator_normalizes_beat_01_trigger_word() -> None:
    # beat_01 having extraneous trigger_word (e.g. from schema hallucination or "null") is normalized to None
    hook = Hook(
        conceptual_hook="Concept Description",
        script_text="Intro spoken script here.",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="First beat", trigger_word="asset_query"),
            VisualDirective(beat_id="beat_02", visual_instruction="Second beat", trigger_word="script"),
        ],
    )
    result = HookValidator().validate(hook)
    assert result.status == "valid"
    assert hook.visual_directives[0].trigger_word is None
    assert hook.visual_directives[1].trigger_word == "script"


def test_component_registry_polymorphic_beat_schema() -> None:
    from registries.component_registry import ComponentRegistry

    schemas = ComponentRegistry.get_polymorphic_beat_schema(is_hook=True)
    assert len(schemas) == len(ComponentRegistry.HOOK_COMPONENTS)
    assert len(ComponentRegistry.get_polymorphic_beat_schema(is_hook=False)) == len(ComponentRegistry.CANONICAL_COMPONENTS)
    for variant in schemas:
        props = variant["properties"]
        # trigger_word and asset_query must be nullable
        assert props["trigger_word"]["nullable"] is True
        assert props["asset_query"]["nullable"] is True
        # trigger_word must not be strictly required
        assert "trigger_word" not in variant["required"]
        # visual_instruction must not be emitted
        assert "visual_instruction" not in props



