from domain.hook import Hook, VisualDirective
from domain.validators.hook_validator import HookValidator


def test_validator_accepts_valid_hook() -> None:
    hook = Hook(
        conceptual_hook="Anchor vs Engine comparison",
        script_text="Are you renting? You might think you're throwing money away. You're not.",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="Show heavy metal anchor falling in water", onscreen_text="RENTING = WASTED MONEY?"),
            VisualDirective(beat_id="beat_02", visual_instruction="Show rocket engine firing upward", onscreen_text="THE LIQUID ENGINE"),
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
