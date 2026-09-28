from domain.narrative_plan import NarrativePlan, SceneBeat
from domain.validators.narrative_plan_validator import NarrativePlanValidator


def test_validator_accepts_valid_plan() -> None:
    plan = NarrativePlan(
        thesis="Renting is smarter than buying in high price-to-rent environments.",
        target_pain_point="Fear of throwing money away on rent.",
        conceptual_hook="The 5% Rule of homeownership unrecoverable costs.",
        narrative_arc_type="Problem-Agitation-Solution",
        scene_beats=[
            SceneBeat(
                scene_id="scene_01",
                title="The Rent Trap Myth",
                focus_concept="Opportunity Cost of Capital",
                core_teaching_point="Show that renting pays for shelter while buying locks up capital.",
            ),
            SceneBeat(
                scene_id="scene_02",
                title="The 5% Rule Math",
                focus_concept="The 5% Rule",
                core_teaching_point="Break down property tax, maintenance, and interest costs.",
            ),
            SceneBeat(
                scene_id="scene_03",
                title="Relocation Agility",
                focus_concept="Geographic Mobility",
                core_teaching_point="Explain the salary gains from being able to easily move.",
            ),
        ],
    )
    result = NarrativePlanValidator().validate(plan)
    assert result.status == "valid"
    assert not result.errors


def test_validator_rejects_insufficient_scene_beats() -> None:
    plan = NarrativePlan(
        thesis="Thesis statement",
        target_pain_point="Pain point",
        conceptual_hook="Hook",
        narrative_arc_type="Arc",
        scene_beats=[
            SceneBeat(
                scene_id="scene_01",
                title="Hook scene",
                focus_concept="Concept A",
                core_teaching_point="Teaching point A",
            )
        ],
    )
    result = NarrativePlanValidator().validate(plan)
    assert result.status == "blocked"
    assert "must contain at least 3 scene beats" in result.errors[0]


def test_validator_accepts_enhanced_plan_with_architectural_fields() -> None:
    plan = NarrativePlan(
        thesis="Renting is smarter than buying in high price-to-rent environments.",
        target_pain_point="Fear of throwing money away on rent.",
        central_tension="Why can renting build more net worth than buying?",
        starting_belief="Buying is always an investment",
        ending_understanding="Unrecoverable costs can exceed rent",
        conceptual_hook="The 5% Rule of homeownership unrecoverable costs.",
        narrative_arc_type="Problem-Agitation-Solution",
        scene_beats=[
            SceneBeat(
                scene_id="scene_01",
                title="The Rent Trap Myth",
                scene_role="problem",
                focus_concept="Opportunity Cost of Capital",
                viewer_question="Why do people fear renting?",
                core_teaching_point="Show that renting pays for shelter while buying locks up capital.",
                key_evidence=["Fact 1"],
            ),
            SceneBeat(
                scene_id="scene_02",
                title="The 5% Rule Math",
                scene_role="mechanism",
                focus_concept="The 5% Rule",
                viewer_question="How does unrecoverable cost work?",
                core_teaching_point="Break down property tax, maintenance, and interest costs.",
                key_evidence=["Stat 1"],
            ),
            SceneBeat(
                scene_id="scene_03",
                title="Relocation Agility",
                scene_role="resolution",
                focus_concept="Geographic Mobility",
                viewer_question="What is the long term payoff?",
                core_teaching_point="Explain the salary gains from being able to easily move.",
                key_evidence=["Concept 2"],
            ),
        ],
    )
    result = NarrativePlanValidator().validate(plan)
    assert result.status == "valid"
    assert not result.errors
