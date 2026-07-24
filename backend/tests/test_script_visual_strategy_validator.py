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
                        trigger_word="buying",
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


def test_validator_handles_dynamic_components() -> None:
    # 1. Test Valid dynamic components
    strategy_valid = ScriptVisualStrategy(
        thesis="Autonomy is key.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Concept",
                focus_concept="Opportunity Cost",
                core_teaching_point="Point",
                narration="Narration text",
                visual_sequence=[
                    VisualStrategyBeat(
                        beat_id="beat_01",
                        preferred_component="NumberCounter",
                        visual_goal="Count up",
                        component_data={
                            "start_value": 0,
                            "end_value": 100,
                            "label": "Growth",
                            "unit": "%",
                        },
                    ),
                    VisualStrategyBeat(
                        beat_id="beat_02",
                        preferred_component="Charts",
                        visual_goal="Show chart",
                        trigger_word="text",
                        component_data={
                            "chart_type": "bar",
                            "labels": ["a", "b"],
                            "values": [10, 20],
                        },
                    ),
                    VisualStrategyBeat(
                        beat_id="beat_03",
                        preferred_component="Timeline",
                        visual_goal="Show timeline steps",
                        trigger_word="narration",
                        component_data={
                            "steps": ["Step 1", "Step 2"],
                        },
                    ),
                ],
            )
        ],
    )
    result = ScriptVisualStrategyValidator().validate(strategy_valid)
    assert result.status == "valid"
    assert not result.errors

    # 2. Test Invalid dynamic components
    strategy_invalid = ScriptVisualStrategy(
        thesis="Autonomy is key.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Concept",
                focus_concept="Opportunity Cost",
                core_teaching_point="Point",
                narration="Narration text",
                visual_sequence=[
                    VisualStrategyBeat(
                        beat_id="beat_01",
                        preferred_component="NumberCounter",
                        visual_goal="Count up",
                        component_data={
                            "start_value": "not-a-number",
                            "end_value": 100,
                            "label": "Growth",
                        },
                    ),
                    VisualStrategyBeat(
                        beat_id="beat_02",
                        preferred_component="Charts",
                        visual_goal="Show chart",
                        trigger_word="text",
                        component_data={
                            "chart_type": "scatter", # invalid type
                            "labels": ["a", "b"],
                            "values": [10, 20],
                        },
                    ),
                    VisualStrategyBeat(
                        beat_id="beat_03",
                        preferred_component="Timeline",
                        visual_goal="Show timeline steps",
                        trigger_word="narration",
                        component_data={
                            "steps": [123], # invalid type
                        },
                    ),
                ],
            )
        ],
    )
    result_invalid = ScriptVisualStrategyValidator().validate(strategy_invalid)
    assert result_invalid.status == "blocked"
    assert len(result_invalid.errors) == 3
    assert any("NumberCounter beat" in e and "numeric" in e for e in result_invalid.errors)
    assert any("Charts beat" in e and "chart_type" in e for e in result_invalid.errors)
    assert any("Timeline beat" in e and "steps" in e for e in result_invalid.errors)


def test_validator_requires_trigger_word() -> None:
    # 1. Missing trigger_word for subsequent beat
    strategy_missing = ScriptVisualStrategy(
        thesis="Renting is smart.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Security",
                focus_concept="Opportunity Cost",
                core_teaching_point="Explain cost",
                narration="This is the narration text.",
                visual_sequence=[
                    VisualStrategyBeat(
                        beat_id="beat_01",
                        preferred_component="Typography",
                        visual_goal="Goal 1",
                    ),
                    VisualStrategyBeat(
                        beat_id="beat_02",
                        preferred_component="Typography",
                        visual_goal="Goal 2",
                        # missing trigger_word
                    ),
                ],
            )
        ],
    )
    result = ScriptVisualStrategyValidator().validate(strategy_missing)
    assert result.status == "blocked"
    assert "is a subsequent beat and requires trigger_word" in result.errors[0]

    # 2. Trigger word not in narration
    strategy_not_in_narration = ScriptVisualStrategy(
        thesis="Renting is smart.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Security",
                focus_concept="Opportunity Cost",
                core_teaching_point="Explain cost",
                narration="This is the narration text.",
                visual_sequence=[
                    VisualStrategyBeat(
                        beat_id="beat_01",
                        preferred_component="Typography",
                        visual_goal="Goal 1",
                    ),
                    VisualStrategyBeat(
                        beat_id="beat_02",
                        preferred_component="Typography",
                        visual_goal="Goal 2",
                        trigger_word="nonexistentword",
                    ),
                ],
            )
        ],
    )
    result_err = ScriptVisualStrategyValidator().validate(strategy_not_in_narration)
    assert result_err.status == "blocked"
    assert "does not exist in the narration text" in result_err.errors[0]


