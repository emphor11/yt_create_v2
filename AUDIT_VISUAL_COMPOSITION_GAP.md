# YTCreate V2 — Visual Composition Gap Audit

## Scope and evidence

This audit uses the six most recent runs that are both `completed` and have a succeeded `video` artifact in `backend/.data/ytcreate_v2.db`:

1. The First ₹10 Lakh Changes Everything — `run_cf2517b8b55740b994e71bf01edfc32b`
2. How ₹10,000/Month Can Change Your Financial Life — `run_0dcb645b5fc741e1a2249e6e0535cb36`
3. The ₹30,000 EMI Trap: How Your ‘Dream Car’ Can Delay Your Financial Freedom — `run_b065ea545b824dd49f4a3e52d22db3cd`
4. Why ₹10 Lakh in Your Bank Account Is NOT ₹10 Lakh in Wealth — `run_2edef7df90ca4d04b755f3f3e64a1e2b`
5. You’re Saving Money Every Month… And Still Getting Poorer — `run_73a45e7446be47acbdd971412ed60c9e`
6. Your ₹20,000 EMI Isn’t Really ₹20,000 — `run_5a8bdbc3d61f49f3aab5a3f346f05b4b`

The runs contain 185 final scenes and 185 planned beats in total. I inspected their research, narrative, script/visual strategy, composition plans, RenderSpecs, final MP4s, and extracted frame samples. The final videos are stored under `backend/.data/media/projects/.../runs/...`.

The current checkout also contains uncommitted GrowthTrajectory work. That work is treated as current architecture, but not as production evidence: none of the six audited production RenderSpecs uses `GrowthTrajectory`. No production code was modified by this audit.

## 1. Executive Summary

YTCreate V2 has a real semantic composition pipeline, not merely a collection of animations. The active catalog already renders metrics, scalar calculations, causes, multi-factor pressure, comparisons, processes, and decline/erosion with a consistent visual system. Those components are generally legible and visually coherent in the inspected frames.

The main bottleneck is a semantic middle layer that is still too narrow for finance explanations. The six videos repeatedly teach relationships that are neither a single number nor a static A-versus-B comparison: money moving through a budget, two financial paths separating over time, principal versus interest changing across a loan, and contributions versus returns composing a final corpus. When those relationships are missing, the system falls back to B-roll or forces the idea into CauseEffect, TimeDecay, ComparisonSplit, or CalculationStory.

B-roll is overrepresented, but not all of it is a problem. Across the six RenderSpecs, 650.6 seconds of 1,419.4 seconds are `BrollCaption` scenes, approximately 45.8% of total runtime. Asset-backed media appears for approximately 52.4% of runtime because a small number of non-B-roll compositions also carry an asset in some runs. B-roll is appropriate for hooks, emotional context, human situations, and atmospheric transitions. It is semantically weak when the narration teaches a trajectory, a cumulative allocation, or a financial mechanism.

The strongest hard evidence is six `no_suitable_composition` fallbacks: three upward-growth beats, one conceptual comparison, one multi-year loan calculation, and one first-year depreciation beat. One additional fallback is an external Gemini 503, which is not a composition gap. The upward-growth gap is now partially addressed by the uncommitted `growth_trajectory` work. The other gaps remain.

The most important opportunity is not to eliminate B-roll. It is to add a small set of structural primitives and make semantic lineage observable. The recommended roadmap is six new semantic grammars plus two existing-composition upgrades. Building eight new React components immediately would create composition sprawl.

## 2. Current Composition Inventory

The active catalog is defined in [composition_registry.py](/Users/dakshyadav/Documents/YTcreate_V2/backend/registries/composition_registry.py:740). Relationship types are closed in [visual_intent.py](/Users/dakshyadav/Documents/YTcreate_V2/backend/domain/visual_intent.py:27).

| Composition | Relationship | Actual usage in six videos | Strength | Weakness | Status |
|---|---|---:|---|---|---|
| `broll_caption` / BrollCaption | `broll`, `statement`, `quote`, `definition` | Dominant; 83 planned idea beats plus fallback beats; 650.6 rendered seconds | Strong cinematic/context fallback; good for human situations and claims | Does not preserve structured relationships; stock query may be semantically adjacent rather than explanatory | Active and reachable |
| `cause_effect` / CauseEffect | `cause_effect` | 37 idea beats; all six videos use it | Clear one-to-three-cause convergence; good visual hierarchy | Semantically overloaded for accumulation, allocation, and opportunity cost; does not show quantity moving | Active and reachable |
| `comparison_split` / SplitComparison | `comparison` | 11 idea beats; used in four of six videos | Clear static A/B and before/after contrast | Static cards cannot show two paths evolving or a changing gap | Active and reachable |
| `metric_hero` / MetricHero | `metric` | 11 idea beats; used in four of six videos | Excellent emphasis for a single number | Often holds a scalar where the narration explains a relationship or threshold | Active and reachable |
| `calculation_story` / CalculationStory | `calculation` | 6 idea beats in the six plans | Good input → operator → result grammar for exact scalar arithmetic | Schema is not a loan schedule, range, or period-by-period decomposition | Active and reachable |
| `time_decay` / TimeDecay | `decline`, legacy `trend` | 12 idea beats; used in five videos | Strong visual for purchasing-power erosion and depreciation | Can be incorrectly used for slow growth/opportunity cost; planner historically rejected one valid single-period depreciation case | Active and reachable; `trend` support is guarded |
| `process_flow` / ProcessFlow | `process` | 6 idea beats; used in five videos | Good ordered steps and operational procedures | A linear path cannot naturally show a loop, branching decision, or resource transfer | Active and reachable |
| `multi_factor_pressure` / MultiFactorPressure | `multi_factor` | 2 idea beats in the car-loan video | Good simultaneous-pressure treatment | Shows convergence, not cumulative cost or balance movement | Active and reachable |
| `ranked_list` / RankedList | `ranking` | 0 in audited plans | Schema and renderer exist for ordered items | No evidence of current planner use in the sampled production set | Registered but unobserved |
| `growth_trajectory` / GrowthTrajectory | `growth` | 0 in audited production RenderSpecs | Current checkout adds the right upward-trajectory grammar with linear/accelerating/compound variants | Not yet production-proven; current data extraction needs benchmark validation | Present in uncommitted worktree; not yet evidenced |

### Legacy versus active reachability

The legacy `ComponentRegistry` still exposes direct components such as `Typography`, `Charts`, `Timeline`, `KPIGrid`, `ProgressiveList`, `RankedList`, `DataTable`, `BeforeAfter`, `QuoteCallout`, `NumberCounter`, `IconAnimation`, `StockImage`, and `StockVideo`. They remain renderer/legacy-pipeline reachable through `ComponentResolver` and `VideoAssembly`, but the current composition planner is closed over the catalog above. They should not be treated as missing semantic compositions merely because they are not selected.

Two test families refer to `cash_flow_waterfall` and `trajectory_divergence`, but neither ID is registered in the current catalog. The tests therefore skip at import time. They are design intent, not active production capabilities.

## 3. Five/Six Video Overview

Percentages below distinguish `BrollCaption` runtime from any scene carrying an asset.

| Video | Duration | Scenes | Main composition mix | BrollCaption runtime | Asset-backed runtime | Fallbacks | Major visual weakness |
|---|---:|---:|---|---:|---:|---:|---|
| The First ₹10 Lakh Changes Everything | 271.2s | 38 | Broll 23, CauseEffect 8, SplitComparison 4, ProcessFlow 2, TimeDecay 1 | 59.7% | 59.7% | 4; 3 semantic growth, 1 provider error | Linear accumulation, compounding transition, and milestone progression are explained through stock/cards rather than a trajectory |
| How ₹10,000/Month Can Change Your Financial Life | 256.3s | 33 | Broll 18, CauseEffect 6, CalculationStory 3, MetricHero 3, TimeDecay 2, ProcessFlow 1 | 48.9% | 48.9% | 1 conceptual comparison | SIP progression and opportunity cost are split across B-roll, decay, and scalar calculations |
| The ₹30,000 EMI Trap | 223.6s | 31 | Broll 16, CauseEffect 6, SplitComparison 3, MultiFactor 2, TimeDecay 2, ProcessFlow 1, MetricHero 1 | 52.2% | 52.2% | 2; loan range and first-year depreciation | 19.4s of B-roll carries a multi-year loan/range explanation; ownership costs are not accumulated into a visible total |
| Why ₹10 Lakh in Your Bank Account Is NOT ₹10 Lakh in Wealth | 217.2s | 26 | Broll 13, CauseEffect 6, TimeDecay 3, SplitComparison 2, MetricHero 2 | 44.7% | 65.6% | 0 | Strong causal/decay treatment, but nominal versus real wealth is repeatedly static or stock-based instead of two evolving paths |
| You’re Saving Money Every Month… And Still Getting Poorer | 233.2s | 31 | Broll 10, MetricHero 6, CauseEffect 7, TimeDecay 5, SplitComparison 2, ProcessFlow 1 | 24.9% | 34.1% | 0 | The video has the best structured-visual ratio, but real purchasing power and nominal savings still appear as static comparison/decay rather than a paired trajectory |
| Your ₹20,000 EMI Isn’t Really ₹20,000 | 217.9s | 26 | Broll 12, CalculationStory 3, CauseEffect 6, MetricHero 3, ProcessFlow 1, TimeDecay 1 | 42.1% | 54.2% | 0 | Scalar calculations communicate headline values, but not principal/interest schedule behavior or the accumulating opportunity cost |

## 4. Scene-Level Failure Analysis

These are representative beats, not a claim that every B-roll scene is wrong.

| Video / scene | Narration meaning | Intent and current representation | Problem | Root cause | Better visual grammar |
|---|---|---|---|---|---|
| First ₹10 Lakh, `scene_015` / `beat_03_03`, 96.9–102.2s | Early growth is strictly linear; monthly savings add predictable increments | `trend` → BrollCaption; explicit `no_suitable_composition` | Viewer sees a person/calculator, not a steadily accumulating balance | `ROOT_CAUSE_COMPOSITION_MISSING` in the audited run; current worktree’s GrowthTrajectory is the appropriate remedy | Linear growth trajectory with monthly contribution cadence and first-milestone marker |
| First ₹10 Lakh, `scene_027` / `beat_06_01`, 177.0–187.4s | Later capital blocks take fewer months as returns become larger | `trend` → BrollCaption; explicit fallback | This is accelerating growth, not atmosphere | `ROOT_CAUSE_COMPOSITION_MISSING` in the audited run; also old taxonomy lag | Accelerating/compound GrowthTrajectory; show the changing slope |
| First ₹10 Lakh, `scene_038` / `beat_08_04`, 262.8–271.2s | Wealth snowball changes struggle into mathematical progression | `trend` → BrollCaption; explicit fallback | A stock shot cannot show the transition from labor-funded to self-funded growth | `ROOT_CAUSE_COMPOSITION_MISSING` in the audited run; current `growth` relationship should be used | Growth trajectory with a regime-change annotation |
| First ₹10 Lakh, `scene_012`, 70.8–79.1s | Conservative vehicles grow slowly and extend the time to the milestone | `decline` → TimeDecay | A slow accumulation is rendered as erosion/decay; the viewer may infer loss instead of delay | `ROOT_CAUSE_VISUAL_INTENT_CLASSIFICATION` | Growth or scenario timing treatment; do not use a decline curve unless value actually falls |
| First ₹10 Lakh, `scene_032` / `beat_07_02`, 215.8–225.4s | Capital is allocated across small-cap, mid-cap, and flexi-cap funds | `process` → ProcessFlow | The scene implies sequence, while the narration describes allocation across a portfolio | `ROOT_CAUSE_COMPOSITION_MISSING`; a process-flow extension would not show part-to-whole allocation | Portfolio allocation / part-to-whole composition with verified weights when available |
| ₹10,000/Month, `scene_003` / `beat_hook_03`, 7.8–14.3s | Waiting for a larger salary is contrasted with starting at ₹10,000 today | `comparison` → BrollCaption; explicit fallback | The current schema could express a string-valued contrast, but the intent did not provide paired subjects/values cleanly | `ROOT_CAUSE_VISUAL_INTENT_CLASSIFICATION` / `ROOT_CAUSE_DATA_MODEL`; not a new composition | Normalize as comparison with `₹50,000` versus `₹10,000`, or use a short decision/tradeoff variant |
| ₹10,000/Month, `scene_007` / `beat_01_04`, 34.8–43.9s | Waiting loses the benefit of early market exposure | `decline` → TimeDecay | Opportunity cost is not the same as one value eroding | `ROOT_CAUSE_VISUAL_INTENT_CLASSIFICATION` | Diverging time paths or an opportunity-cost comparison |
| ₹30,000 EMI, `scene_009` / `beat_02_01`, 42.6–62.0s | 3–7 years and 7.5–11.5% interest push total cash outflow above the sticker price | `calculation` → BrollCaption; explicit fallback | A 19.4s stock segment carries a financial range and cumulative obligation | `ROOT_CAUSE_COMPOSITION_SCHEMA_TOO_RESTRICTIVE` for the scalar CalculationStory; a schedule/range grammar is missing | Debt amortization or cost-stack treatment with ranges preserved, not fabricated point estimates |
| ₹30,000 EMI, `scene_015` / `beat_04_01`, 100.3–113.3s | Vehicle loses 15–20% in the first year | `decline` → BrollCaption; explicit fallback | Current TimeDecayData already permits a single-period drop and optional percentage; the planner rejected a case the schema can represent | `ROOT_CAUSE_PLANNER_SELECTION` with a prompt/schema contract mismatch | Use TimeDecay `single_period_drop` after fixing planner selection; no new component required |
| ₹30,000 EMI, `scene_010` / `beat_02_02`, 62.0–72.6s | Loan payment, interest, and term create combined pressure | `multi_factor` → MultiFactorPressure | The graphic shows converging pressure but not how each item adds to the total outflow | `ROOT_CAUSE_COMPOSITION_MISSING` for cumulative balance movement | Cash-flow waterfall or cost-stack composition |
| Bank Account, `scene_008` / `beat_02_01`, 40.5–61.1s | Savings interest is lower than the broader return/inflation context | `comparison` → SplitComparison, 20.6s | Long static side-by-side cards cannot show the rate gap widening over time | `ROOT_CAUSE_COMPOSITION_MISSING` | Two-path trajectory with a visible gap and time horizon |
| Bank Account, `scene_020` / `beat_06_02`, 164.4–172.4s | ₹10 lakh left in savings loses purchasing power over five years | `decline` → TimeDecay | TimeDecay explains one falling real value but not the counterfactual productive-asset path | `ROOT_CAUSE_COMPOSITION_MISSING` | TrajectoryDivergence; retain TimeDecay for the single-path version |
| Saving Money, `scene_013` / `beat_03_03`, 89.9–99.4s | Nominal savings and real outcomes differ | `comparison` → SplitComparison | The viewer gets two labels, not the evolution of nominal balance versus purchasing power | `ROOT_CAUSE_COMPOSITION_MISSING` | Real-versus-nominal paired trajectory |
| ₹20,000 EMI, `scene_017` / `beat_05_02`, 127.3–138.9s | A ₹5 crore home loan produces over ₹5.4 crore of interest over 20 years | `calculation` → CalculationStory | The stored `input_value` is `₹5,000`, while the narration/visual goal says ₹5 crore. This is a factual data mismatch, not a composition gap | `ROOT_CAUSE_CONTENT_QUALITY` / `ROOT_CAUSE_DATA_MODEL` | Correct the authoritative fact and add a validation that source values survive merge; then use amortization for the schedule |
| ₹20,000 EMI, `scene_020` and `scene_022`, 157.5–168.8s and 176.7–184.8s | Fees/interest add to purchase cost; prepayment changes tenure from 20 to 11 years | `calculation` → CalculationStory | Scalar input/result cards hide the period-by-period principal/interest and tenure transformation | `ROOT_CAUSE_COMPOSITION_MISSING` | DebtAmortizationSchedule with a deterministic summary mode |

## 5. Cross-Video Semantic Gap Matrix

| Semantic pattern | Videos affected | Evidence frequency | Current representation | B-roll/fallback | New composition or upgrade |
|---|---|---:|---|---|---|
| Single quantity growing, accelerating, or crossing a milestone | First ₹10 Lakh; ₹10,000/Month; also savings/wealth narratives | 3 explicit fallbacks plus several statement/comparison beats | BrollCaption, CauseEffect, ComparisonSplit | 3 explicit growth fallbacks | `GrowthTrajectory` is already in the worktree; validate and route `growth` instead of `trend` |
| Two financial paths diverging over time | First ₹10 Lakh; Bank Account; Saving Money; ₹30,000 EMI; ₹20,000 EMI | Repeated across at least 4 videos | Static SplitComparison, isolated TimeDecay, CauseEffect | Some stock; no explicit fallback required because the wrong available grammar is selected | New `trajectory_divergence` |
| Income or principal reduced by sequential outflows | First ₹10 Lakh; ₹30,000 EMI; ₹20,000 EMI; savings/wealth topics | At least 3 direct finance mechanisms | ProcessFlow, MultiFactorPressure, CauseEffect, scalar CalculationStory | One explicit loan-range fallback; several B-roll explanations | New `cash_flow_waterfall` |
| Principal, interest, fees, and tenure changing over a loan | ₹30,000 EMI and ₹20,000 EMI | 2 videos, multiple beats | CalculationStory, MetricHero, TimeDecay | One explicit loan-range fallback; B-roll for long loan explanation | New `debt_amortization_schedule` |
| Contributions versus investment returns composing final wealth | First ₹10 Lakh; ₹10,000/Month; Saving Money | 3 videos | CauseEffect, ComparisonSplit, CalculationStory, TimeDecay | Several stock/card treatments | New `accumulation_decomposition`, or a carefully scoped extension to GrowthTrajectory |
| Portfolio allocation as parts of a whole | First ₹10 Lakh; Saving Money | 2 videos, one direct allocation scene | ProcessFlow and generic B-roll | One direct B-roll statement plus a sequential flow | New `portfolio_allocation`; keep weights optional and factual |
| Ranges and uncertainty in rates/terms | ₹30,000 EMI directly; likely reusable in loan/investment videos | 1 explicit audited case | BrollCaption because CalculationStory wants an exact input/result | One explicit fallback | Conditional `scenario_range_band`; implement only after more production evidence |
| Feedback loop / self-reinforcing mechanism | First ₹10 Lakh; compound-investing beats; loan prepayment cycle | 2–3 narrative instances | ProcessFlow or CauseEffect | Usually structured, but linearized | Upgrade ProcessFlow with a loop variant before creating a new component |
| Generic human context, emotion, or environment | All six | Frequent | BrollCaption | Intentional | Keep as B-roll; no new composition |

## 6. Candidate Composition Pool

The following pool was generated before filtering. Scores are qualitative 1–5 indicators, not a claim of predicted performance.

| Candidate | Semantic relationship | Evidence | Reuse | Overlap risk | Complexity | Decision |
|---|---|---|---:|---:|---:|---|
| Trajectory Divergence | Two quantities evolve over the same horizon and separate | 4+ videos | 5 | 2 | High | Final |
| Cash-Flow Waterfall | One balance is transformed by ordered positive/negative adjustments | 3+ videos | 5 | 2 | High | Final |
| Debt Amortization Schedule | Principal, interest, payment, tenure, and prepayment evolve over time | 2 videos; core finance primitive | 5 | 2 | High | Final |
| Accumulation Decomposition | Contributions and returns compose a growing corpus | 3 videos | 5 | 3 | High | Final |
| Portfolio Allocation | A whole is partitioned across asset/risk buckets | 2 videos | 4 | 3 | Medium | Final, medium confidence |
| Scenario Range Band | A value is bounded by rate/term scenarios rather than one point | 1 explicit case | 4 | 3 | High | Conditional final |
| Feedback Loop | An output becomes a future input, such as returns generating returns | 2–3 narrative cases | 4 | 4 | Medium | Solve as ProcessFlow variant first |
| Milestone Ladder | Ordered financial thresholds with changing effort/time | 3 videos | 4 | 4 | Medium | GrowthTrajectory variant, not a new component |
| Ownership Cost Stack | Sticker price plus financing, fuel, maintenance, insurance, depreciation | ₹30,000 EMI strongly; ₹20,000 EMI adjacent | 4 | 2 | Medium | Waterfall variant, not separate |
| Real-versus-Nominal Overlay | Nominal balance and purchasing power on one time axis | Bank Account and Saving Money | 5 | 3 | Medium | TrajectoryDivergence variant |
| Decision Branch | A choice splits into different downstream financial outcomes | One hook and several opportunity-cost statements | 3 | 3 | High | Defer; insufficient direct evidence |
| Ranked Distribution | Ordered expenses/assets by magnitude | No audited beat selected it | 3 | 4 | Medium | Do not prioritize; registered RankedList is enough |
| Rate-Sensitivity Matrix | Multiple rates/terms change a result | One explicit range case | 4 | 3 | High | Defer until more runs show recurrence |
| Debt Paydown Progression | Principal falls while interest share changes | ₹20,000 EMI and ₹30,000 EMI | 5 | 2 | High | Fold into DebtAmortizationSchedule |

## 7. FINAL TOP 8–10 COMPOSITIONS / ROADMAP PRIMITIVES

The evidence supports eight roadmap primitives, but only six of them should initially be new Remotion compositions. The other two are current-composition upgrades. This distinction is important: the target is semantic coverage, not eight new files.

### Composition 1 — Trajectory Divergence

**Proposed `composition_id`:** `trajectory_divergence`  
**Relationship:** `divergence` (new relationship type, distinct from static `comparison`).

**Purpose and evidence:** Show two options or states on the same time axis, such as savings versus inflation, equity SIP versus car purchase, or bank balance versus real purchasing power. Evidence appears in Bank Account `scene_008`/`scene_020`, Saving Money `scene_013`, First ₹10 Lakh `scene_05`/`scene_06`, and the ₹30,000 EMI comparison beats.

**Why current primitives fail:** SplitComparison is static; TimeDecay shows one path; CauseEffect has no time axis. B-roll cannot preserve the gap.

**Viewer understanding:** “These two choices start near the same baseline but create increasingly different outcomes over the stated horizon.”

**Visual grammar:** Shared origin, two animated paths, time axis, end labels, optional gap callout, optional crossing/inflection marker. A nominal-versus-real variant should use the same grammar, not a new component.

**Structured data:** `time_horizon`, `baseline_label`, `path_a`, `path_b`, optional `divergence_gap`, optional explicit rates/end values, and `variant`. Values must come from verified facts; no interpolated endpoints unless the source provides them.

**Variants and boundaries:** `wealth_gap`, `real_vs_nominal`, `opportunity_cost`, `standard`. Do not use for static A/B or for a single declining value. Use GrowthTrajectory for one path.

**Planner mapping:** `divergence -> trajectory_divergence`.

**Value:** Highest cross-video impact and largest replacement of semantically weak static comparisons. Complexity High; maintenance includes schema, deterministic fact merge, duration tests, and path-label collision tests. Expected B-roll reduction is qualitative: it can replace the specific comparison/decay beats that currently need a time axis, not general statement B-roll.

### Composition 2 — Cash-Flow Waterfall

**Proposed `composition_id`:** `cash_flow_waterfall`  
**Relationship:** `waterfall` / ordered resource allocation.

**Purpose and evidence:** Show salary or principal being reduced by tax, debt, rent, living costs, fees, or ownership costs. Evidence is strongest in the ₹30,000 EMI cost explanation, the ₹20,000 EMI cash-flow beats, and First ₹10 Lakh’s salary-funded accumulation.

**Why current primitives fail:** MultiFactorPressure converges factors but does not preserve order or remaining balance. ProcessFlow implies steps but not amounts. CalculationStory shows one transformation.

**Viewer understanding:** “This starting amount is progressively consumed, and the remaining balance is the amount available for the next decision.”

**Visual grammar:** Starting bar/card, signed adjustments entering one at a time, running balance, final surplus/deficit, optional grouped categories. The visual should preserve positive inflows and negative outflows.

**Structured data:** `starting_label`, `starting_value`, `steps[{label,value,direction,subtext,numeric_amount?}]`, optional `final_label`, `final_value`, `header_label`, `variant`. Derive a final numeric balance only when all numeric inputs and signs are explicit; otherwise omit it.

**Variants and boundaries:** `standard`, `detailed`, `compact`, `ownership_cost`. Do not use for a loan schedule or for a pure causal explanation.

**Planner mapping:** `waterfall -> cash_flow_waterfall`; `allocation` may route here only when the whole is being consumed/allocated sequentially.

**Value:** High finance reuse and high B-roll replacement potential for money-movement beats. Complexity High because signed numeric derivation and factual merge must be deterministic.

### Composition 3 — Debt Amortization Schedule

**Proposed `composition_id`:** `debt_amortization_schedule`  
**Relationship:** loan state transition over repeated payments.

**Purpose and evidence:** Explain why early EMI payments contain more interest, how principal falls, what total interest becomes, and how prepayment changes tenure. Evidence is present in both EMI videos; the ₹30,000 case currently falls back on a multi-year range and the ₹20,000 case uses three scalar CalculationStory scenes.

**Why current primitives fail:** CalculationStory can show `20 years -> 11 years`, but not the changing principal/interest split. TimeDecay can imply decline but cannot show two loan components and payment cadence.

**Viewer understanding:** “Each payment is divided between interest and principal; changing the principal changes both the remaining balance and the loan horizon.”

**Visual grammar:** Stacked payment bars or a timeline of payment periods, interest share receding as principal share grows, outstanding balance line, optional prepayment intervention, exact tenure summary.

**Structured data:** verified `principal`, `rate`, `term`, `payment_frequency`, `payment_amount` or authoritative schedule rows, optional `prepayment`, `baseline_term`, `revised_term`, and `total_interest`. Prefer source schedule rows; derive only from a validated formula and explicit inputs.

**Variants and boundaries:** `standard`, `interest_front_loaded`, `prepayment`, `range_summary`. Do not use when only a generic debt warning exists or when the source lacks enough data to compute a schedule.

**Planner mapping:** `amortization -> debt_amortization_schedule`; exact scalar results can remain `calculation -> calculation_story`.

**Value:** High finance specificity and high recurrence in loan/EMI content. Complexity High; correctness and rounding tests are mandatory.

### Composition 4 — Accumulation Decomposition

**Proposed `composition_id`:** `accumulation_decomposition`  
**Relationship:** a growing total composed of contributions plus returns or other verified components.

**Purpose and evidence:** First ₹10 Lakh repeatedly distinguishes salary savings from returns; ₹10,000/Month uses monthly contributions and 12% growth to explain 7- and 15-year corpora; Saving Money contrasts deposits with real outcomes.

**Why current primitives fail:** GrowthTrajectory shows one total path; CalculationStory shows input/result; CauseEffect says returns generate returns but does not show contribution composition.

**Viewer understanding:** “The final corpus is made of these components, and the relative contribution changes over time.”

**Visual grammar:** Stacked area/column or layered trajectory where principal/contributions and returns remain visually distinct, with an optional inflection marker.

**Structured data:** `time_points` or verified milestone rows containing `period`, `contributions`, `returns`, `total`, plus labels and optional `milestone`. Do not synthesize intermediate rows from a headline total unless a deterministic calculation is explicitly authorized.

**Variants and boundaries:** `contributions_vs_returns`, `nominal_vs_real`, `milestone_blocks`. Use TrajectoryDivergence for two competing strategies; use GrowthTrajectory for a single un-decomposed total.

**Planner mapping:** `accumulation_decomposition -> accumulation_decomposition`.

**Value:** High explanatory value across savings, SIP, compounding, and retirement topics. Complexity High because factual subcomponents must reconcile to totals.

### Composition 5 — Portfolio Allocation

**Proposed `composition_id`:** `portfolio_allocation`  
**Relationship:** part-to-whole distribution across financial buckets.

**Purpose and evidence:** First ₹10 Lakh directly describes capital being scaled across small-cap, mid-cap, and flexi-cap funds, but the current ProcessFlow renders them as sequential steps. Saving Money also discusses diversified vehicles.

**Why current primitives fail:** ProcessFlow implies order, and RankedList implies priority; neither communicates that parts sum to a whole or that different buckets carry different roles.

**Viewer understanding:** “This whole portfolio is divided among these buckets, and each bucket has a distinct role or risk level.”

**Visual grammar:** Animated whole-to-parts split, labeled allocation shares when verified, risk/role annotations, and optional rebalance transition.

**Structured data:** `total_label`, optional `total_value`, `allocations[{label,share,value?,role?,risk?}]`, optional `variant`. Shares must be explicit or deterministically derived from explicit values.

**Variants and boundaries:** `allocation_donut`, `allocation_bars`, `rebalance`. Do not use for a sequence of actions or an unquantified list of fund names.

**Planner mapping:** `allocation -> portfolio_allocation` only when the whole-to-parts relationship is explicit.

**Value:** Medium-high; it adds a finance-native grammar absent from the current runs. Complexity Medium-high. Because direct recurrence is lower than trajectory divergence, implement after the first four.

### Composition 6 — Scenario Range Band

**Proposed `composition_id`:** `scenario_range_band`  
**Relationship:** one financial outcome under bounded rates/terms/scenarios.

**Purpose and evidence:** The ₹30,000 EMI beat explicitly contains 3–7 years and 7.5–11.5% interest. Current CalculationStory requires an exact input/result and the planner falls back to B-roll. This is a conditional recommendation: one direct audited case is not enough by itself, but the grammar generalizes to loan rates, inflation assumptions, and return scenarios.

**Why current primitives fail:** A scalar card hides range uncertainty; ComparisonSplit would require inventing arbitrary low/high “winners.”

**Viewer understanding:** “The result is a bounded range because the term/rate assumptions vary; the range is uncertainty, not a precise promise.”

**Visual grammar:** Low/high band or scenario columns, explicit assumption labels, optional midpoint only when source-supported, and no false precision.

**Structured data:** `scenarios[{label,assumptions,result?}]`, or explicit `min`, `max`, `unit`, `horizon`, and `source_context`. At least two source-supported endpoints are required.

**Variants and boundaries:** `rate_range`, `term_range`, `best_base_worst`. Do not use for vague uncertainty without numeric bounds.

**Planner mapping:** `scenario_range -> scenario_range_band`.

**Value:** Medium until more runs confirm recurrence. Complexity High because assumptions and factual ranges must be preserved.

### Composition 7 — GrowthTrajectory Completeness Upgrade

**Current `composition_id`:** `growth_trajectory` (already in the uncommitted checkout).  
**Relationship:** `growth`.

**Purpose:** Close the three explicit upward-growth fallbacks, route old `trend` cases correctly, and support milestone/regime changes. The current schema already has linear, accelerating, compound, and milestone variants.

**Required validation before calling it complete:** production benchmark renders from real VisualIntents, correct mapping of linear versus accelerating versus compound, no fabricated intermediate points, short-duration safety, and a factual check that start/end values survive merge.

**Boundary:** Do not use for two competing paths; use TrajectoryDivergence. Do not use for a generic positive statement.

### Composition 8 — ProcessFlow Feedback-Loop Upgrade

**Current `composition_id`:** `process_flow` with a semantic loop variant; not a new React component unless renderer evidence requires it.  
**Relationship:** `feedback_loop` or `process` with an explicit cycle.

**Purpose:** First ₹10 Lakh describes past savings → returns → future returns, and the EMI video describes breaking a compounding interest cycle. Current ProcessFlow linearizes those loops.

**Required schema change:** allow an explicit `cycle_back_to`/loop closure and distinguish causal feedback from a simple ordered procedure. Only derive the loop when narration states it.

**Boundary:** If the main viewer understanding is quantitative growth, GrowthTrajectory or AccumulationDecomposition remains primary; the loop is a supporting causal grammar.

## 8. Recommended Future Semantic Taxonomy

The taxonomy should describe the thought, not the animation.

| Relationship type | Composition |
|---|---|
| `statement`, `quote`, `definition`, intentional `broll` | `broll_caption` |
| `metric` | `metric_hero` |
| scalar `calculation` | `calculation_story` |
| `cause_effect` | `cause_effect` |
| `multi_factor` | `multi_factor_pressure` |
| static `comparison` | `comparison_split` |
| single upward `growth` | `growth_trajectory` |
| single-path `decline` | `time_decay` |
| ordered operational `process` | `process_flow` |
| `ranking` | `ranked_list` |
| `divergence` | `trajectory_divergence` |
| `waterfall` | `cash_flow_waterfall` |
| `amortization` | `debt_amortization_schedule` |
| `accumulation_decomposition` | `accumulation_decomposition` |
| `allocation` | `portfolio_allocation` |
| `scenario_range` | `scenario_range_band` |
| `feedback_loop` | `process_flow` loop variant initially |

`trend` should stop being a catch-all. The classifier should choose `growth`, `decline`, `divergence`, or `scenario_range` when the semantics support one of them. If none applies, retain `trend` only as an explicit unresolved category that routes to a diagnostic fallback, not silently to B-roll.

## 9. Before vs After Coverage

### Current

- 185 final scenes across six videos.
- 650.6 seconds / 45.8% of total runtime rendered as BrollCaption.
- Approximately 52.4% of runtime carries an asset.
- Six `no_suitable_composition` fallbacks: three upward growth, one conceptual comparison, one loan-range calculation, one first-year depreciation case.
- One additional provider-error fallback.
- Time-based comparisons are split between static cards and one-path decay.
- The RenderSpec stores final component IDs and props, but not the semantic `composition_id`, `relationship_type`, `used_fallback`, or `fallback_reason`.

### Proposed

- Three explicit upward-growth fallbacks can route to the current GrowthTrajectory after production validation.
- The conceptual comparison should be recovered through better intent extraction/normalization, not a new composition.
- The loan-range fallback can route to ScenarioRangeBand or DebtAmortizationSchedule when source data supports it.
- The first-year depreciation fallback should route to the existing TimeDecay single-period variant after fixing planner selection.
- Static comparisons in Bank Account, Saving Money, First ₹10 Lakh, and the EMI videos can become paired trajectories when the narration provides two time-evolving paths.
- Salary/expense/debt explanations can become Waterfall beats; principal/interest explanations can become Amortization beats.
- B-roll should remain for hooks, emotion, people, places, contextual car/office footage, and statements without a structured relationship.

The audit does not justify claiming that a fixed percentage of all B-roll will disappear. It does justify eliminating the documented semantic fallbacks and reducing repeated stock/card treatment for the identified structured beats.

## 10. Architecture Impact

### VisualIntent

The current schema already has rich entities, measurements, temporal context, causal structure, comparison, and visual dynamics. Add new relationship types only for genuinely distinct grammars: `divergence`, `waterfall`, `amortization`, `accumulation_decomposition`, `allocation`, and conditionally `scenario_range`. `growth` is already present in the current worktree.

Persist standalone VisualIntent artifacts in production. The six audited runs do not contain a `visual_intent` artifact type; the semantic trail is embedded indirectly in `script_visual_strategy.composition_plan`. That makes classification-versus-planner diagnosis harder than it should be.

### Composition registry and planner

Register one Pydantic data model per new semantic grammar. Generate the planner catalog from the registry as today. Add explicit boundary examples so `comparison` does not absorb `divergence`, `process` does not absorb `allocation`, and `decline` does not absorb slow growth.

Fix the existing mismatch where TimeDecayData supports `single_period_drop`/`drop_rate` but a production planner fallback claims the case is unsupported. Improve conceptual comparison extraction so a hook with explicit ₹50,000 versus ₹10,000 values does not fall back.

### Candidate factual data and merge

Facts should remain authoritative over LLM presentation. Waterfalls must derive balances only from signed, explicit values. Amortization must use verified schedule rows or validated formula inputs. Accumulation decomposition must reconcile contributions plus returns to total. Ranges must preserve their endpoints and assumptions. No renderer should receive fabricated intermediate values.

### Resolver and RenderSpec

Add resolver branches and snake_case → camelCase mappings for each registered composition. Extend `SceneSpec` or an adjacent lineage object to preserve `composition_id`, `relationship_type`, `used_fallback`, `fallback_reason`, and planner/candidate-data provenance. Today the final RenderSpec records `component_id` but loses the semantic identity that selected it.

### Asset resolver

Keep assets optional for all structured compositions. BrollCaption should remain the only composition that requests stock media by default. Add query-quality and semantic-fit diagnostics, but do not turn stock matching into a substitute for a missing diagram.

### Remotion and duration

Implement the new grammars as data-driven components under the existing VideoAssembly dispatch. Every component needs short, normal, and long duration tests; no hard-coded frame window should be allowed to collapse on short narration. Keep the current dark visual language and reuse existing tokens, but do not duplicate components for cosmetic variants.

### Tests and QA

For each new grammar, add schema acceptance/rejection tests, factual-merge tests, resolver-prop tests, planner routing tests, fallback tests, and rendered frame/snapshot cases. Add cross-composition boundary tests, especially:

- growth versus divergence;
- waterfall versus process;
- amortization versus scalar calculation;
- allocation versus ranking;
- decline versus slow growth;
- scenario range versus comparison.

The local test collection was not executed because this environment has no `pytest` module (`python3 -m pytest` returns `No module named pytest`).

## 11. Implementation Sequence

1. Add semantic lineage and data-quality checks first. Persist VisualIntent/composition metadata, and block or flag mismatches such as the ₹5 crore / `₹5,000` case.
2. Validate the current GrowthTrajectory work against real production-shaped intents and route the three documented growth fallbacks.
3. Fix planner/classifier boundaries for opportunity cost, first-year depreciation, and conceptual comparisons.
4. Implement TrajectoryDivergence. It unlocks the broadest set of repeated weak comparisons.
5. Implement CashFlowWaterfall. It gives salary, EMI, expense, and ownership-cost narratives a real resource grammar.
6. Implement DebtAmortizationSchedule. It is the most finance-specific high-value primitive and must follow the factual rules above.
7. Implement AccumulationDecomposition, then validate reconciliation and transition timing.
8. Implement PortfolioAllocation after more allocation-heavy runs confirm the schema.
9. Add ScenarioRangeBand only if the next production sample continues to contain explicit ranges; otherwise keep it as a planner/data-model extension.
10. Add the ProcessFlow feedback-loop variant and reassess whether a separate component is still justified.

## 12. What NOT To Build

- Do not build a second static comparison component. Extend ComparisonSplit only where presentation fields are missing.
- Do not build a separate “milestone ladder” component before validating GrowthTrajectory’s milestone variant; the audited evidence describes one growth grammar.
- Do not build a separate “ownership cost stack” component if CashFlowWaterfall can represent signed ownership adjustments.
- Do not build a separate real-versus-nominal component; it is a TrajectoryDivergence variant.
- Do not build a generic feedback-loop component before testing a ProcessFlow loop variant.
- Do not prioritize RankedList, DataTable, or a dashboard/grid composition from this sample; the audited runs contain no ranking intent.
- Do not convert every statement into graphics. Emotional claims, human context, hooks, and atmospheric transitions should remain B-roll.
- Do not use a new composition to hide bad factual extraction, provider errors, missing numeric evidence, or script repetition.
- Do not create cosmetic variants as separate composition IDs.

## 13. Final Recommendation

The smallest composition vocabulary that would materially expand the visual language of YTCreate V2 is:

1. Validate and productionize the existing `growth_trajectory`.
2. Add `trajectory_divergence`.
3. Add `cash_flow_waterfall`.
4. Add `debt_amortization_schedule`.
5. Add `accumulation_decomposition`.
6. Add `portfolio_allocation`.
7. Add `scenario_range_band` only after another evidence sample confirms recurring bounded assumptions.
8. Add a `process_flow` feedback-loop variant rather than immediately creating another component.

The first six are the high-confidence semantic expansion. The last two are conditional/upgrade items, not permission to create two more decorative components.

These should be treated as semantic primitives, not decorative UI components.
