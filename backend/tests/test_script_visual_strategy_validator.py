from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea, VisualStrategyBeat
from domain.validators.script_visual_strategy_validator import ScriptVisualStrategyValidator


def test_validator_accepts_valid_strategy() -> None:
    strategy = ScriptVisualStrategy(
        thesis="Renting is superior.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="The Cost Equation",
                focus_concept="Opportunity Cost",
                core_teaching_point="Show unrecoverable costs comparison",
                narration="Renting has unrecoverable costs but buying has higher ones.",
                visual_sequence=[
                    VisualStrategyBeat(
                        beat_id="beat_01",
                        preferred_component="SplitComparison",
                        visual_goal="Compare rent cost vs buying cost",
                        component_data={
                            "left_role": "product_price",
                            "left_label": "Rent cost",
                            "left_value": 30000,
                            "left_unit": "INR",
                            "right_role": "monthly_payment",
                            "right_label": "Buy cost",
                            "right_value": 75000,
                            "right_unit": "INR",
                        },
                    ),
                    VisualStrategyBeat(
                        beat_id="beat_02",
                        preferred_component="Typography",
                        visual_goal="Show cost focus phrase",
                    ),
                ],
            )
        ],
    )
    result = ScriptVisualStrategyValidator().validate(strategy)
    assert result.status == "valid"
    assert not result.errors


def test_validator_rejects_unsupported_component() -> None:
    strategy = ScriptVisualStrategy(
        thesis="Renting is superior.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="The Cost Equation",
                focus_concept="Opportunity Cost",
                core_teaching_point="Show costs",
                narration="Renting vs Buying.",
                visual_sequence=[
                    VisualStrategyBeat(
                        beat_id="beat_01",
                        preferred_component="UnsupportedCoolEffect",
                        visual_goal="Show fireworks",
                    ),
                    VisualStrategyBeat(
                        beat_id="beat_02",
                        preferred_component="Stock Video",
                        visual_goal="Show stock video",
                    ),
                ],
            )
        ],
    )
    result = ScriptVisualStrategyValidator().validate(strategy)
    assert result.status == "blocked"
    assert "uses unsupported component" in result.errors[0]
