
# YTcreate V2 — Universal Video System Audit

Date: 2026-09-26  
Scope: forensic audit only; no source-code changes, redesign, or commit performed.

## 1. Executive Summary

The current composition pipeline is running end to end, but it is not yet fact-locked at the point where composition data is filled. The persisted VisualIntent artifact and CompositionBeat lineage are present and inspectable in all four audited runs. They are not the primary failure.

The first material divergence occurs later:

Narration → VisualIntent with qualitative or partial facts → CompositionDataFiller forced to populate a quantitative schema → unsupported values reach the render spec → renderer presents them as authoritative visuals.

The strongest evidence is in the current CompositionDataFiller contract and its prompt. The implementation rejects placeholder strings, but it does not verify that numbers and factual values in composition data came from the source VisualIntent. The prompt simultaneously requires quantitative fields to be populated and permits “scenario context” and derived enrichment. That combination creates pressure to invent plausible-looking values when the intent is qualitative.

Across the three requested renders, a conservative numeric-token comparison found composition output values that were not present in the source VisualIntent for:

- 9 of 35 beats in the ₹1 Crore render: 25.7%.
- 15 of 33 beats in the ₹10 Lakh render: 45.5%.
- 14 of 32 beats in the ₹10,000/month render: 43.8%.

This is an undercount. It catches numeric tokens only; it does not catch invented qualitative labels, derived categories, or values written as words. The supplemental fourth render shows the same problem, including a fabricated prior rate and fabricated savings velocity.

The second major problem is pacing. VisualIntent produces a pacing budget, but it is advisory. Timeline assembly derives durations from voice timestamps and proportional fallbacks, then only logs warnings for long beats. The result is a set of 28–35 beats per video with average beat lengths of 6.3–8.5 seconds and maximum beats of 11–20 seconds. Several compositions therefore have enough time to be read, but many others are too short or too long for their information density.

The third problem is visual variety and progression. Relationship type currently maps almost directly to a composition template. There is no evidence-aware distinction between factual and conceptual visual modes, no novelty/reuse cost, and no narrative-level choreography layer. The renderer is mostly faithfully executing a weak beat and data plan: dark cards, repeated curves, generic paperwork B-roll, and static or slowly animated panels.

Priority order:

1. Enforce a source-fact lock at composition-data filling and validation.
2. Allow compositions to represent conceptual claims without inventing quantitative endpoints.
3. Make fallback/default paths explicit, observable, and non-authoritative.
4. Make pacing and beat boundaries enforceable rather than advisory.
5. Add evidence-aware composition selection, reuse controls, and narrative choreography.

The report does not recommend removing the persisted VisualIntent or the existing composition architecture. Those are the correct seams for the next fixes.

## 2. Videos Audited

The three /mnt/data paths referenced by the brief were not available in this workspace. Exact matching project/run media files were found in the repository media store and audited instead. A fourth current integrated render was included as supplemental evidence because it uses the same composition architecture and exposes additional failure modes.

| Scope | Project / title | Run | Render file | Duration |
|---|---|---|---|---:|
| Requested 1 | project_0d883688ce0e455f9ca0fec87fa81657 — “Why Your First ₹1 Crore Is Mostly About Time, Not Income” | run_d676fd6ba5e5428fbf64ac3dcc233c27 | /Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_0d883688ce0e455f9ca0fec87fa81657/runs/run_d676fd6ba5e5428fbf64ac3dcc233c27/scene_project_0d883688ce0e455f9ca0fec87fa81657.mp4 | 222.10s |
| Requested 2 | project_5f506a3b863a4d88883421f647154b59 — “Why Your First ₹10 Lakh Feels Impossible — Then Compounding Changes Everything” | run_619a84312d3049288813fd54ed936cc3 | /Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_5f506a3b863a4d88883421f647154b59/runs/run_619a84312d3049288813fd54ed936cc3/scene_project_5f506a3b863a4d88883421f647154b59.mp4 | 244.93s |
| Requested 3 | project_c0fcd75676584494b591d2ceb0059123 — “Why ₹10,000 a Month Can Beat a Bigger Salary — If You Start Early” | run_b083014813ab406ead26a645913da192 | /Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_c0fcd75676584494b591d2ceb0059123/runs/run_b083014813ab406ead26a645913da192/scene_project_c0fcd75676584494b591d2ceb0059123.mp4 | 209.64s |
| Supplemental | project_ccc8dc462a064d2482c18eebec3fdf7f — “The 50–30–20 Rule Is Probably Wrong for You” | run_85d832b84a6d49c99bb8095640b49496 | /Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_ccc8dc462a064d2482c18eebec3fdf7f/runs/run_85d832b84a6d49c99bb8095640b49496/scene_project_ccc8dc462a064d2482c18eebec3fdf7f.mp4 | 239.19s |

All four runs use visual_mode=composition, contain a persisted visual_intent artifact, contain a composition plan, and have a render_spec and video artifact. The database still reports these runs as running at the render stage even though the video artifact exists. That is an operational inconsistency, not the primary visual-quality cause.

### Artifact integrity and lineage

The artifact store contains the expected artifacts for each run: request, research packet, narrative plan, hook, VisualIntent, script visual strategy, review result, voice track, render spec, and video.

| Run | VisualIntent sequences | VisualIntents | Provenance records | CompositionBeats | All beats linked to source intent |
|---|---:|---:|---:|---:|---|
| run_d676... | 8 | 35 | 35 | 35 | Yes |
| run_619... | 9 | 33 | 33 | 33 | Yes |
| run_b083... | 9 | 32 | 32 | 32 | Yes |
| run_85d... | 9 | 28 | 28 | 28 | Yes |

This confirms that the persisted intent contract is functioning at the artifact/lineage level. The failure is that later stages do not revalidate every factual value against that source intent.

## 3. Quantitative Comparison

The following measurements are exact metadata measurements from the render specs and persisted artifacts. >6s, >8s, and >10s count beats whose timeline duration exceeds that threshold. B-roll runtime is calculated from the timeline spans of BrollCaption beats. The word count is the render-spec narration word count; voice-track counts are slightly different because the artifacts use different text/timestamp representations.

| Render | Duration | Render words | Beats | Avg / median beat | Min / max beat | >6s / >8s / >10s | B-roll beats | B-roll runtime | Composition transitions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ₹1 Crore | 222.1s | 712 | 35 | 6.35 / 5.87s | 2.73 / 10.97s | 17 / 10 / 2 | 19 (54.3%) | 46.3% | 23 |
| ₹10 Lakh | 244.9s | 723 | 33 | 7.42 / 7.33s | 1.20 / 19.53s | 22 / 14 / 8 | 13 (39.4%) | 36.8% | 27 |
| ₹10,000/month | 209.6s | 630 | 32 | 6.55 / 6.10s | 2.70 / 18.33s | 17 / 6 / 2 | 11 (34.4%) | 29.8% | 21 |
| Supplemental 50–30–20 | 239.2s | 687 | 28 | 8.54 / 7.12s | 3.17 / 19.97s | 21 / 12 / 7 | 13 (46.4%) | 44.0% | not used as a primary comparison |

The render-spec composition distributions are:

- ₹1 Crore: 19 BrollCaption, 6 GrowthTrajectory, 4 CauseEffect, 3 MetricHero, 1 SplitComparison, 1 CalculationStory, and 1 TrajectoryDivergence.
- ₹10 Lakh: 13 BrollCaption, 6 CauseEffect, 6 GrowthTrajectory, 3 SplitComparison, 2 MetricHero, 2 AccumulationDecomposition, and 1 CalculationStory.
- ₹10,000/month: 11 BrollCaption, 10 GrowthTrajectory, 8 SplitComparison, 2 CauseEffect, and 1 MetricHero.
- Supplemental 50–30–20: 13 BrollCaption, 5 CauseEffect, 3 CashFlowWaterfall, 2 MetricHero, and one each of CalculationStory, TimeDecay, MultiFactorPressure, SplitComparison, and TrajectoryDivergence.

These counts show that the system is not merely failing in one composition. The same contract problem affects growth, comparison, cause/effect, time decay, waterfall, accumulation, multi-factor pressure, and divergence components whenever their schema requests facts absent from the source intent.

## 4. Visual Quality Analysis

The audited renders were inspected using scene-level midpoint contacts across the full sequence, together with render-spec timing and component data. The following are visual observations; they are qualitative and should be treated as design judgments rather than measured facts.

### What works

- The output has a consistent 1920×1080, 30fps presentation.
- The composition system is actually being used end to end in these runs.
- Numeric cards and growth curves are legible when the beat provides enough time and the values are supported.
- Composition-specific internal animation exists: curves draw, arrows/cards appear, and metric values animate.
- The persisted intent and beat lineage gives the system a usable audit trail.

### What fails

The dominant rhythm is:

dark information card → generic B-roll → single chart/card → generic B-roll → dark information card.

The system does not yet build a visual argument across a section. Most beats are isolated component selections. There is little state carried from one beat to the next, little transformation of an object or number, and no consistent introduce → develop → transform → emphasize → resolve progression at the narrative level.

The ₹1 Crore render is particularly statement-heavy. It repeatedly shows hands over financial paperwork, laptops, or office/market footage. Growth scenes often use a similar single upward curve even when the narration is qualitative. Cause/effect scenes often appear as static cards and arrows rather than visibly changing systems.

The ₹10 Lakh render has a better component mix, but it contains an approximately 19.5-second comparison beat and an approximately 1.2-second accumulation beat. The former is visually over-held; the latter is likely too short to read its decomposition. This is an information-density/pacing problem, not simply an animation polish problem.

The ₹10,000/month render has repeated growth and split-comparison patterns. The 18.3-second growth beat is especially long for one visual state. The render communicates the intended subject, but the sequence feels templated because the same visual grammar is reused without a stronger progression.

The supplemental 50–30–20 render makes the failure more visible: repeated paperwork B-roll appears in the opening, several cards are sparse, and the visual system displays unsupported values such as 11.5% → 5.3% and -35% Savings Velocity.

## 5. Data/Composition-Filling Analysis

### The source contract is correct until the filler boundary

script_visual_strategy_handler.py persists the VisualIntent sequence and provenance before planning. It then creates CompositionBeats with the exact artifact ID and idea ID. The current runs confirm that this part is working.

composition_planner_engine.py then takes the persisted path and invokes CompositionDataFillerEngine. The filler receives VisualIntent-derived input, but the current validator only rejects known placeholder strings. It does not prove that every number, label, amount, rate, endpoint, or time horizon appears in the source intent or in an explicitly approved provenance field.

The filler prompt creates the conflict. In backend/app/assets/prompts/composition_data_filler_system.txt, it says that all quantitative fields are mandatory, instructs the model to extract exact metrics from narration or “scenario context,” and encourages active enrichment and derived fields. That is incompatible with a fact-locked VisualIntent contract when the intent is intentionally qualitative or incomplete.

### First-divergence examples

| Beat | Source VisualIntent / narration | Composition output | Diagnosis |
|---|---|---|---|
| ₹1 Crore beat_02_02 | “Compound interest accelerates portfolio growth exponentially over longer time horizons.” No source amounts or endpoints. | ₹1 Lakh → ₹1.47 Crore, 20 Years. | Filler invented a numeric growth example. |
| ₹1 Crore beat_02_05 | 25-year routine builds a substantial corpus; no ending corpus value. | ₹0 → ₹1.5 Crore, 25 years. | The duration survives; the endpoint is fabricated. |
| ₹1 Crore beat_03_03 | Sustained duration reaches a milestone; causal fields are null. | ₹14.7 Lakh outcome plus synthetic causes such as 0x, Standard, and 10+ Years. | Unsupported causal facts and an unsupported outcome. |
| ₹1 Crore beat_06_02 | “Active savings → passive returns”; qualitative only. | ₹0 → ₹1 Crore, 10 years. | Filler converted a conceptual transition into a numeric projection. |
| ₹1 Crore beat_06_04 | Returns outpace salary savings; source values are qualitative outpacing and static. | ₹0 → ₹25 Lakh versus ₹0 → ₹10 Lakh, 10 years. | Unsupported comparison endpoints. |
| ₹10 Lakh beat_01_03 | Small starting balance and strong annual return produce few rupees; no amount/rate. | ₹50,000 × 10% → ₹5,000, 1 year. | Unsupported principal, rate, and timeframe. |
| ₹10 Lakh beat_04_03 | Source contains ₹7.5 lakh principal and first ₹10 lakh milestone, but not a ₹14.7 lakh total or ₹7.2 lakh return stream. | ₹7.5 Lakh + ₹7.2 Lakh = ₹14.7 Lakh. | Partially grounded beat was enriched beyond its source. |
| ₹10 Lakh beat_08_02 | Qualitative critical-mass/compounding claim. | ₹14.7 Lakh, ₹6.0 Lakh contributions, ₹8.7 Lakh returns, 12% CAGR. | Multiple unsupported values. |
| ₹10,000/month beat_02_03 | Extra ten years changes the math. | ₹10,000 → ₹1.47 Crore, 20 years. | Unsupported amount and endpoint. |
| ₹10,000/month beat_07_01 | Historical competitive returns over 10–15-year periods; no return rate. | ₹0 → ₹1.4 Crore, 15 years. | Unsupported endpoint. |
| ₹10,000/month beat_08_02 | Early smaller investments are advantageous; qualitative. | ₹5,000/month → ₹1.4 Crore, 20 years. | Unsupported monthly amount and endpoint. |
| Supplemental beat_01_01 | 50/30/20 allocation; no salary amount. | ₹1,00,000 → ₹50,000/₹30,000/₹20,000. | Filler invented the base salary. |
| Supplemental beat_05_02 | 5.3% and FY2022–23 are present. | 11.5% → 5.3%. | The current value is grounded; the previous value is fabricated. |
| Supplemental beat_05_03 | Rising expenses and stagnant income; qualitative. | -35% Savings Velocity. | Fabricated quantitative metric. |
| Supplemental beat_07_04 | Lower versus higher earner; qualitative divergence. | Numeric-looking time and qualitative endpoints rendered as a trajectory. | The system presents a conceptual comparison as a quantitative-looking path without an explicit conceptual mode. |

### Why this affects every composition

The issue is not specific to CauseEffect. Each composition schema declares required fields. A qualitative VisualIntent can therefore be routed to:

- GrowthTrajectory and receive invented start/end values.
- SplitComparison and receive invented amounts for both sides.
- TimeDecay and receive an invented baseline or default decline profile.
- CashFlowWaterfall and receive invented starting/final totals or steps.
- AccumulationDecomposition and receive invented contributions/returns.
- MultiFactorPressure and receive invented percentages.
- TrajectoryDivergence and receive numeric-looking paths from qualitative labels.
- CauseEffect and receive synthetic causes/outcomes even when causal is null.

The universal rule should therefore be: a composition may only render a factual value if that value is explicitly present in the approved source contract for that beat. If required data is absent, the planner must select a conceptual variant, request a different composition, or reject the beat. It must not fill the field with a plausible value.

## 6. Composition Selection Analysis

composition_selector.py is primarily a direct relationship-to-template map. For example, growth routes to GrowthTrajectory, comparison routes to SplitComparison, cause_effect routes to CauseEffect, and statement/definition/quote routes to BrollCaption.

This is a useful first routing layer, but it is not an evidence-aware selector. It answers “which template matches the relationship label?” It does not answer:

- Are the required fields present?
- Is the claim factual, conceptual, or illustrative?
- Is a numeric representation authorized?
- Has this composition already been overused nearby?
- Can the beat be represented with the available evidence without filler?
- Does the previous beat already use the same visual grammar?

The current direct mapping explains why a CauseEffect component can be selected while VisualIntent.causal is null. It also explains why a qualitative growth claim becomes a numeric growth chart. The relationship type is being used as a semantic category and a rendering instruction at the same time, without a separate evidence-sufficiency decision.

A future selector should preserve the relationship type but add an evidence profile, such as factual_numeric, factual_categorical, conceptual, or unsupported_for_visualization. That is a Step 2 design direction, not an implementation performed in this audit.

## 7. Fallback Analysis

There are multiple fallback layers, and they are not all visible in the final artifact:

1. composition_resolver.py falls back to Typography when a composition is unknown or its data is invalid. This can produce a successful render while hiding a composition/data failure.
2. TimeDecay.tsx has preset/default profiles when data is missing, including default percentage/value displays. Those defaults are visually authoritative unless the output is explicitly marked illustrative.
3. GrowthTrajectory.tsx supplies labels such as Starting Point and Target Corpus when labels are absent. This is less dangerous than numeric defaults but can make an under-specified beat appear complete.
4. TrajectoryDivergence.tsx can derive path geometry from direction/tone and use a balanced separation when endpoints are qualitative. That can be valid for a conceptual visual, but the schema does not clearly distinguish conceptual from factual mode.
5. TimelineBuilder uses proportional splitting when trigger-word boundaries do not resolve cleanly. This keeps the timeline renderable but can weaken semantic alignment.

The audited render specs do not show used_fallback=true on the B-roll beats, so the high B-roll count is not simply an execution fallback. It is largely the planner intentionally selecting BrollCaption for statement-like intents. However, the resolver/default paths remain a P0/P1 reliability risk because they can turn invalid or incomplete data into a successful-looking video.

A fallback should be an explicit state in the artifact and render spec, with a reason and an allowed visual mode. It should never silently become a factual value.

## 8. B-roll Analysis

B-roll is not inherently wrong. It is appropriate when the intent is atmospheric, human, contextual, or intentionally illustrative. The current problem is that it is also the default destination for many statement-like intents that lack a planned visual abstraction.

Exact B-roll measurements:

- ₹1 Crore: 19 of 35 beats, 54.3% of beats and 46.3% of runtime.
- ₹10 Lakh: 13 of 33 beats, 39.4% of beats and 36.8% of runtime.
- ₹10,000/month: 11 of 32 beats, 34.4% of beats and 29.8% of runtime.
- Supplemental: 13 of 28 beats, 46.4% of beats and 44.0% of runtime.

Repeated asset-query evidence:

- ₹1 Crore: person reviewing bank statement laptop appears 5 times; person reviewing investment growth laptop 3 times; person reviewing investment portfolio laptop 2 times. There are only 12 unique queries for 19 B-roll beats.
- ₹10 Lakh: person reviewing bank statement laptop appears 7 times and person reviewing investment portfolio laptop 3 times. There are only 5 unique queries for 13 B-roll beats.
- ₹10,000/month: 11 B-roll beats use 9 unique queries; young professional checking investment app and person reviewing bank statement laptop each appear twice.
- Supplemental: 13 B-roll beats use 6 unique queries; person reviewing bank statement laptop appears 7 times.

All audited B-roll beats had relationship_type=statement except one definition beat in the ₹10 Lakh render, and the resolver did not mark them as used fallbacks. This points to planner behavior and missing visual alternatives, not merely an asset-resolution bug.

## 9. Pacing Analysis

visual_intent_engine.py calculates a pacing budget from words and target words-per-second. Its prompt also recommends beat durations and beat counts. In practice, those targets are advisory and are frequently missed.

The 5-minute style runs are roughly 620–723 render words and 28–35 beats. The intent budgets often call for more beats than are actually produced. The largest under-segmentation is in the supplemental render: several body sections have 2–4 beats against target ranges of 5–8.

timeline_builder.py derives actual scene timing from voice timestamps and uses proportional splits when trigger words are unavailable. It defines a maximum recommended beat duration of 6 seconds, but the current behavior logs a warning instead of enforcing, splitting, or requiring an intentional long-beat justification.

Observed consequences:

- ₹10 Lakh contains a 19.53-second SplitComparison beat and a 1.20-second AccumulationDecomposition beat.
- ₹10,000/month contains an 18.33-second GrowthTrajectory beat.
- Supplemental contains beats of 19.97 seconds and 19.50 seconds.
- The ₹1 Crore render has 10 beats over 8 seconds despite a generally shorter median.

These are not automatically defects: a long beat can be correct for a deliberate visual argument. The defect is that there is no evidence in the artifact that the long duration was intentional, and the same system permits very short, overloaded beats.

The timing contract should eventually include an information-density budget: words, required fields, animation phases, and minimum readable duration. A beat should not be accepted solely because audio spans exist.

## 10. Choreography Analysis

Choreography exists inside individual components, but not as a narrative-level system.

The composition assembly path resolves a sequence of beats and VideoAssembly.tsx renders them as Series.Sequence entries. There is no shared section state or choreography planner that knows whether a visual fact was introduced, transformed, emphasized, and resolved.

Current component-level examples:

- Growth curves draw and then emphasize an endpoint.
- Cause/effect cards and arrows appear with local animation.
- Metric cards animate values.

Missing narrative-level behavior:

- Reuse of the same object, axis, ledger, or character across beats.
- Explicit handoff from a prior beat’s output to the next beat’s input.
- State transformation rather than repeated reintroduction.
- Controlled escalation and release across a section.
- A visual resolution beat after a comparison or causal chain.

This is why the output can be technically animated yet still feel like a sequence of unrelated templates. The renderer is not the first divergence; it is exposing the absence of a higher-level visual plan.

## 11. Repetition Analysis

Repetition is measurable at the component and asset-query level, and visually evident in the scene contacts.

### Component repetition

- ₹1 Crore has a maximum consecutive run of 7 BrollCaption beats.
- ₹10 Lakh has a maximum consecutive run of 3 identical components, but still repeats BrollCaption, GrowthTrajectory, and CauseEffect across sections.
- ₹10,000/month has 10 GrowthTrajectory and 8 SplitComparison beats out of 32.
- Supplemental has 13 BrollCaption beats out of 28.

### Asset repetition

The same paperwork and laptop queries recur across runs and within runs. This is not explained by renderer reuse alone; the planner and asset resolver are repeatedly requesting semantically similar generic footage.

### Root cause of repetition

There is no visible novelty cost or local reuse policy in composition selection. The selector optimizes for relationship-template fit, while the asset layer optimizes for query resolution. Neither stage has a strong penalty for:

- same component as the previous beat;
- same component too often in a section;
- same asset query or visual motif;
- same chart geometry for different claims;
- same visual mode across a complete argument.

## 12. Root-Cause Prioritization

### P0 — Fact-lock failure at composition filling

CompositionDataFiller rejects placeholders but does not verify source membership for factual values. The prompt requires complete quantitative data and allows derived enrichment. This is the first divergence for the fabricated values.

### P0 — Schema pressure converts qualitative intent into fake quantitative visuals

Many composition schemas require numeric endpoints or complete step values. The system has no explicit conceptual variant for a qualitative claim. The filler is therefore encouraged to invent data instead of refusing or selecting a conceptual treatment.

### P0/P1 — Silent fallback/default paths

Typography fallback and component defaults can make an invalid beat render successfully. This reduces operational visibility and can present defaults as facts.

### P1 — Relationship mapping is not evidence-aware

The relationship label selects a composition, but factual sufficiency, conceptual mode, novelty, and prior visual history are not part of the decision.

### P1 — Pacing targets are advisory

VisualIntent pacing budgets are not enforced by planning or timeline assembly. Long beats are warned about but not corrected or explicitly justified.

### P1 — No narrative-level choreography

The current system sequences independent components rather than planning a visual argument across a section.

### P1/P2 — Statement-heavy B-roll default

Many statement intents are treated as legitimate B-roll beats. This is not a fallback flag problem; it is a missing visual abstraction problem.

### P2 — No repetition/novelty policy

Component and asset reuse are not penalized or controlled.

### P2 — Semantic boundary fallback

Proportional timing splits can create boundaries that do not align with intent or trigger-word semantics.

### P2 — Artifact identifiers are run/idea-scoped

The lineage is inspectable, but intent IDs such as intent_01 repeat across ideas. The composite artifact ID plus idea ID currently prevents ambiguity; globally unique intent IDs would make cross-run analysis simpler later.

### P2 — Run state is not finalized

The database remains at running/render after a video artifact exists. This affects observability and downstream orchestration, but not the visual content directly.

## 13. Root-Cause Table

| Priority | Symptom | First divergence | Why it persists into the render | Evidence |
|---|---|---|---|---|
| P0 | Unsupported amounts, rates, and endpoints appear in charts/cards | CompositionDataFiller and filler prompt | Render spec accepts schema-valid data; renderer displays it | 25.7–45.5% of audited beats have output numeric tokens absent from source intent |
| P0 | Qualitative claims become numeric growth/comparison visuals | Composition schema requires quantitative fields; no conceptual mode | Filler uses plausible examples to satisfy required fields | ₹1 Crore qualitative growth → ₹1 Lakh to ₹1.47 Crore; ₹10,000/month qualitative claim → numeric corpus |
| P0/P1 | Invalid/incomplete data can still render | Resolver/component defaults | Fallback is not always visible in final artifact | Typography fallback; TimeDecay default profiles; derived divergence paths |
| P1 | CauseEffect selected with no causal payload | Direct relationship map and weak selection guard | Filler synthesizes causes/outcomes | ₹1 Crore beat_03_03 has causal=null but CauseEffect data |
| P1 | Beats are too long or too short | TimelineBuilder timing fallback and warning-only max | Render uses audio spans regardless of visual information density | 1.2s to 19.97s observed beat range |
| P1 | Video feels like templates rather than a visual argument | No narrative choreography layer | Series renders independent beat components | Repeated card/B-roll/curve rhythm in scene contacts |
| P1/P2 | Generic B-roll dominates some sections | Statement intents lack planned abstraction | BrollCaption is a valid direct mapping, not marked as fallback | 34.4–54.3% of beats are B-roll |
| P2 | Same charts and footage recur | No novelty/reuse policy | Selector and asset resolver optimize locally | Repeated growth/split components and repeated paperwork queries |
| P2 | Semantic beat boundaries drift | Trigger-word resolution falls back to proportional splitting | Timeline remains renderable but excerpt alignment weakens | TimelineBuilder proportional fallback paths |

## 14. Universal System Model

The current system behaves approximately as follows:

Narration  
↓  
VisualIntent  
- relationship type  
- excerpt  
- viewer understanding  
- partial facts / provenance  
↓ persisted artifact  
CompositionBeat  
- source intent artifact reference  
- selected composition  
↓  
CompositionDataFiller  
- schema pressure  
- “active enrichment”  
- placeholder rejection only  
↓  
Composition data  
- may contain unsupported values  
↓  
CompositionResolver / component defaults  
- may hide invalid or missing data  
↓  
RenderSpec  
↓  
Remotion renderer

The desired universal contract is:

Narration  
↓  
VisualIntentSequence  
- exact excerpt  
- relationship type  
- factual values only when present  
- conceptual/factual evidence mode  
- provenance for every factual value  
↓ persisted artifact  
CompositionBeat  
- exact source intent artifact reference  
- selected composition family  
- evidence requirements  
↓  
Evidence-aware composition selection  
- validate required facts  
- choose factual or conceptual variant  
- apply reuse/novelty constraints  
↓  
Composition input validation  
- every factual value must be source-backed  
- no implicit defaults for factual fields  
- reject unsupported/missing facts  
↓  
RenderSpec  
- explicit fallback/illustrative flags if any  
- timing budget and intentional long-beat reason  
↓  
Renderer  
- render only the authorized visual model

Universal rule:

> A composition is allowed to display a factual value only when that value is explicitly present in the approved source intent/provenance for the beat, or is an explicitly declared deterministic transformation whose inputs are all source-backed. Missing facts must remain missing. The system must choose a conceptual treatment, request more evidence, or reject the beat; it must not fabricate a placeholder or plausible example.

This rule applies to every composition family, not only cause/effect.

## 15. Dependency / Change Impact Analysis

### Highest-impact dependency chain

VisualIntent schema → persisted artifact → CompositionBeat → composition selector → data filler → composition schema validation → render-spec builder → resolver/defaults → renderer

A fact-lock change at the filler boundary will affect every composition whose schema requires numeric or categorical fields. That is desirable, but it will expose under-specified intents that currently render only because the filler enriches them.

### Expected impact by module

| Module | Impact of a correct Step 2 fix | Risk |
|---|---|---|
| VisualIntent engine/schema | May need explicit evidence mode and per-value provenance | Medium; preserve existing intent artifact compatibility |
| Composition planner/selector | Must consider evidence sufficiency and conceptual variants | High; affects all composition routing |
| CompositionDataFiller | Must stop inventing and reject or emit conceptual data | Very high; expected to reveal current unsupported beats |
| Composition registry/schemas | May need factual and conceptual variants or optional fields | High; avoid weakening validation globally |
| TimelineBuilder | May need enforceable information-density/timing rules | Medium |
| CompositionResolver | Must stop silently hiding invalid factual composition data | High for observability |
| Remotion components | Should render explicit conceptual/illustrative modes | Medium; renderer change should follow contract change |
| AssetResolver/B-roll | Should receive visual-purpose and reuse constraints | Medium |
| Artifact store/UI | Should expose fact provenance and fallback reasons | Medium; important for debugging |
| Existing legacy system | Keep intact during transition | Low if composition path remains separately gated |

Do not solve this by deleting the legacy system or by changing the renderer first. The data contract must become authoritative before visual polish can be evaluated reliably.

## 16. Recommended Order of Investigation/Fixes

1. Add a source-fact audit at the CompositionDataFiller boundary. For every output field, record whether it is copied, deterministically derived from approved inputs, conceptual, or rejected. Reject unsupported factual values.
2. Remove the prompt instruction that treats all quantitative fields as mandatory when the source intent does not contain the facts. Remove unrestricted active enrichment.
3. Define an explicit conceptual visual mode for every composition family that needs one. A conceptual mode must not display invented numeric endpoints.
4. Make composition schemas distinguish required factual fields from optional presentation fields. Missing factual data should be a selection input, not a value to fill.
5. Make resolver/component fallback explicit in artifacts and render specs. Defaults must be tagged as non-factual or disabled for factual compositions.
6. Add cross-stage tests for every composition family: source intent → beat → filled input → render spec. Test copied values, deterministic derivations, missing values, and unsupported values.
7. Enforce beat information-density and timing budgets. Require an intentional reason for long beats and split or reject beats that cannot be read.
8. Add evidence-aware selection and a novelty/reuse policy after fact-lock behavior is stable.
9. Add narrative-level choreography planning after beat semantics and data are trustworthy.
10. Improve asset query diversity and visual-purpose mapping after the planner can distinguish atmospheric B-roll from explanatory visualization.

## 17. What NOT to Change Yet

- Do not remove the persisted VisualIntent artifact or CompositionBeat source references. They are the correct audit seam and are working.
- Do not redesign the entire composition registry before the fact-lock contract is tested.
- Do not tune micro-animation, colors, or typography as the primary fix; they cannot correct unsupported facts or weak beat selection.
- Do not make the renderer responsible for determining whether a number is true. That decision belongs upstream in the source/evidence contract.
- Do not treat all B-roll as a renderer failure. The current B-roll mix is primarily a planner/visual-abstraction issue.
- Do not remove the legacy architecture yet. Keep it available while the composition path is made authoritative and observable.
- Do not make cause/effect a special case. The same source-fact rule must apply uniformly to growth, comparison, waterfall, time decay, accumulation, multi-factor pressure, divergence, metric, and calculation compositions.

## 18. Evidence Appendix

### A. Code locations inspected

- backend/app/stage_handlers/script_visual_strategy_handler.py: persists VisualIntent and provenance, then creates CompositionBeats with source references.
- backend/engines/composition_planner_engine.py: persisted composition path and filler invocation.
- backend/engines/composition_data_filler_engine.py: current placeholder-only grounding check and schema validation boundary.
- backend/app/assets/prompts/composition_data_filler_system.txt: mandatory quantitative fields, scenario-context extraction, and active-enrichment instructions.
- backend/engines/composition_selector.py: direct relationship-to-composition routing.
- backend/registries/composition_registry.py: composition schemas and required fields.
- backend/engines/video_assembly/timeline_builder.py: audio-derived timing, trigger-word matching, proportional fallback, and warning-only long-beat threshold.
- backend/engines/video_assembly/composition_resolver.py: invalid composition/data fallback behavior.
- backend/engines/visual_intent_engine.py: advisory pacing budget and VisualIntent prompt constraints.
- backend/engines/video_assembly/render_spec_builder.py: render-spec duration and scene timing.
- backend/engines/video_assembly/composition_assembly_engine.py: composition-mode assembly and legacy compatibility branch.
- renderer/remotion/src/compositions/TimeDecay.tsx: default decline profiles when data is absent.
- renderer/remotion/src/compositions/GrowthTrajectory.tsx: default labels and numeric trajectory presentation.
- renderer/remotion/src/compositions/TrajectoryDivergence.tsx: qualitative path derivation and divergence rendering.
- renderer/remotion/src/VideoAssembly.tsx: scene sequence rendering without narrative-level choreography state.

### B. Artifact/runtime evidence

For each audited run, the artifact store contained valid request, research, narrative, VisualIntent, strategy, review, voice, render-spec, and video artifacts. The composition plan contained one beat per VisualIntent in all four runs, and every beat referenced its source intent artifact.

The evidence therefore supports this conclusion:

- VisualIntent persistence: working.
- CompositionBeat source lineage: working.
- Factual preservation through composition filling: not working.
- Composition selection based on evidence sufficiency: not working.
- Timing enforcement: not working; timing is advisory/warning-only.
- Narrative-level choreography: not present as a planning layer.
- Legacy removal: not performed and not recommended at this stage.

### C. Measurement caveats

- The /mnt/data copies named in the brief were absent; the report uses exact matching media found in the repository’s project/run media store.
- Beat counts, durations, component distributions, B-roll runtime, and composition transitions are exact artifact/render-spec measurements.
- Numeric-token fabrication percentages are conservative heuristics. They detect numeric tokens present in composition output but absent from recursively inspected source VisualIntent text; they do not detect every semantic fabrication.
- Visual-quality, repetition, and choreography findings are engineering judgments based on full scene coverage through artifact timing and scene midpoint contact inspection. They are not automated perceptual scores.
- Semantic transition quality is not directly encoded in the current artifacts. Where discussed, it is an interpretation of the relationship/component sequence, not a claimed ground-truth metric.

### D. Audit change boundary

No source files, prompts, schemas, renderers, tests, database records, or legacy components were modified during this audit. No commit was created. The only intended new file is this report.

