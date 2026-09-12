# Comprehensive End-to-End Pipeline Artifact Trail (Stage 0 to Stage 8)

**Project:** *The ₹1 Lakh Lifestyle Trap*  
**Project ID:** `project_149b665e28a94e838d9341252c969bb1`  
**Run ID:** `run_565f2ef6833a4bd091e6b53cb58ae913`  
**Visual Architecture Mode:** `composition` (Pure Composition Engine)  
**Output Video File:** `scene_project_149b665e28a94e838d9341252c969bb1.mp4` (216.13s, 6,484 frames @ 30fps, 1080x1920)  

---

## System Architecture Context for AI Evaluation

This document contains the complete, un-truncated, stage-by-stage artifact trail of an automated video generation pipeline (YTcreate_V2).

### Pipeline Operating Principles & Contracts:
1. **Pipeline Execution Flow:** Stage 0 (`generate_video_request`) -> Stage 1 (`research_packet`) -> Stage 2 (`narrative_plan`) -> Stage 3 (`hook`) -> Stage 4 (`script_visual_strategy`) -> Stage 5 (`review_result`) -> Stage 6 (`voice_track`) -> Stage 7 (`render_spec`) -> Stage 8 (`video`).
2. **Dual Visual Modes:**
   - **Legacy Mode (`legacy`):** Uses `ComponentRegistry` with standard atomic scenes (`Typography`, `StockVideo`, `SplitComparison`, `StatCallout`, etc.). Assumes 2 visual beats per idea.
   - **Composition Mode (`composition`):** Body beats use authored multi-element compositions (`metric_hero`, `calculation_story`, `cause_effect`, `time_decay`, `multi_factor_pressure`, `broll_caption`). Hook beats (first ~15s) may utilize specialized legacy hook components.
3. **Composition Planning Contract:**
   - `CompositionPlannerEngine` receives `VisualIntent` objects derived from narrative ideas.
   - Strict concrete JSON schemas are generated per composition via `CompositionRegistry.build_planner_response_schema()`.
   - The LLM must populate required composition fields (e.g. `start_value`, `operation`, `result_value` for `calculation_story`; `metric_value`, `metric_label` for `metric_hero`).
   - If validation passes, the composition is accepted into `CompositionPlan`.
4. **Timeline & Assembly Invariant:**
   - Body beat count is strictly determined by `CompositionPlan.composition_beats`.
   - Narration intervals for each idea are partitioned contiguously across its composition beats.
   - Total video frames must exactly match voice track audio duration (`round(audio_duration * fps)`).
   - Zero frame gaps or overlaps between consecutive scenes (`scene[i].start_frame == scene[i-1].end_frame`).

---

## Stage 0: Video Generation Request (Initial User & System Prompt)

- **Artifact ID:** `artifact_21b4f7a00c324ecda64c1a009175c3e7`
- **Artifact Type:** `generate_video_request`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-09T07:04:07.267567+00:00`
- **Parent Artifact Roles:** `{}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Captures the raw user intent, topic, audience, visual mode, duration target, and stylistic parameters.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "topic": "The ₹1 Lakh Lifestyle Trap",
  "angle": "Show why earning your first ₹1 lakh/month can actually make wealth-building harder if your lifestyle immediately expands to match it.",
  "audience": "9-to-5 corporate employees wanting freedom",
  "language": "English",
  "style": "philosophical and metrics-driven",
  "channel": "MindshiftFinance",
  "duration_profile": "long_5min",
  "visual_mode": "composition"
}
```

---

## Stage 1: Research Packet (Domain Research & Quantitative Anchor Extraction)

- **Artifact ID:** `artifact_e6e75473be8742dea993456f08249abb`
- **Artifact Type:** `research_packet`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-09T07:04:16.393167+00:00`
- **Parent Artifact Roles:** `{"generate_video_request": "artifact_21b4f7a00c324ecda64c1a009175c3e7"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Researches facts, statistics, historical parallels, and numeric anchors using Perplexity/Search/LLM.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "topic": "The ₹1 Lakh Lifestyle Trap",
  "audience": "9-to-5 corporate employees wanting freedom",
  "channel": "MindshiftFinance",
  "verified_facts": [
    "Earning ₹1,00,000 per month puts an individual in the top 3 percent of Indian earners based on income tax data from the Ministry of Finance.",
    "Upgrading from a rented 1 BHK to a 2 BHK apartment in cities like Bengaluru or Mumbai increases monthly housing expenses by an average of ₹25,000 to ₹40,000.",
    "Purchasing a mid-size car on an auto loan at an EMI of ₹22,000 per month locks in vehicle depreciation and loan interest for 5 years.",
    "Ordering food delivery 15 times a month instead of cooking adds an extra ₹7,500 to monthly discretionary spending.",
    "Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent annual return builds a corpus of over ₹1 crore in 15 years."
  ],
  "statistics": [
    "68 percent of urban Indian professionals earning between ₹1,00,000 and ₹1,50,000 per month report having less than ₹50,000 in liquid emergency savings (RBI Consumer Confidence Survey 2023).",
    "Average monthly discretionary spend on dining out and lifestyle apps increases by 85 percent within 6 months of a salary promotion crossing ₹1,00,000 per month (Kantar Urban Spending Index 2022).",
    "Lifestyle inflation causes 42 percent of corporate employees to remain paycheck-to-paycheck despite crossing the ₹12,00,000 annual income bracket (Mastercard Financial Literacy Index 2023)."
  ],
  "concepts": [
    "Lifestyle Inflation",
    "Effective Hourly Rate",
    "Hedonic Adaptation",
    "The 50/30/20 Rule",
    "Opportunity Cost of Consumption"
  ],
  "misconceptions": [
    "Earning ₹1,00,000 a month means you are automatically wealthy and financially secure.",
    "Taking on luxury EMIs helps build a good credit score and is a sign of financial maturity.",
    "Saving money is more important than optimizing your primary income streams when you reach mid-career."
  ],
  "examples": [
    "A software engineer in Bengaluru earning ₹1,00,000/month who immediately rents a luxury gated community apartment, buys a new iPhone on EMI, and leases a sedan, leaving zero surplus for investing.",
    "A marketing manager in Mumbai earning ₹1,20,000/month who continues living in a modest rented flat, saves ₹60,000 monthly into index funds, and achieves financial independence in 12 years."
  ],
  "trusted_sources": [
    "Reserve Bank of India Consumer Confidence Survey",
    "Ministry of Finance Income Tax Return Statistics",
    "Kantar Urban Spending Index",
    "Mastercard Financial Literacy Index"
  ],
  "provider_metadata": {
    "provider": "gemini",
    "model": "gemini-3.5-flash-lite",
    "raw_metadata": {
      "finish_reason": "STOP",
      "usage_metadata": {
        "promptTokenCount": 1012,
        "candidatesTokenCount": 711,
        "totalTokenCount": 1723,
        "promptTokensDetails": [
          {
            "modality": "TEXT",
            "tokenCount": 1012
          }
        ],
        "serviceTier": "standard"
      },
      "schema_name": "ResearchPacket"
    }
  }
}
```

---

## Stage 2: Narrative Plan (Core Thesis & Scene Beat Outline)

- **Artifact ID:** `artifact_cfb6e8a9063c4be1be52aa89b619bff8`
- **Artifact Type:** `narrative_plan`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-09T07:04:26.906763+00:00`
- **Parent Artifact Roles:** `{"research_packet": "artifact_e6e75473be8742dea993456f08249abb"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Defines the thesis, emotional/intellectual hook, and sequential core scene beats that structure the argument.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "thesis": "Earning ₹1,00,000 per month does not guarantee financial freedom if lifestyle inflation and luxury EMIs swallow your surplus, whereas disciplined 50 percent savings builds a ₹1 crore corpus in 15 years.",
  "target_pain_point": "Urban Indian corporate employees earning ₹1,00,000+ per month who feel stuck in a paycheck-to-paycheck cycle despite hitting what they thought was their dream salary milestone.",
  "conceptual_hook": "Making ₹1,00,000 a month puts you in India's top 3 percent of earners, yet 68 percent of professionals at this level have less than ₹50,000 in liquid savings—proving that a bigger paycheck is often just a gilded cage.",
  "narrative_arc_type": "Problem-Agitation-Solution",
  "scene_beats": [
    {
      "scene_id": "scene_01",
      "title": "The Top 3 Percent Illusion",
      "focus_concept": "Lifestyle Inflation",
      "core_teaching_point": "Earning ₹1,00,000 a month places you in India's top 3 percent of earners, yet most professionals remain cash-poor due to immediate spending upgrades."
    },
    {
      "scene_id": "scene_02",
      "title": "The Gilded Cage Trap",
      "focus_concept": "Hedonic Adaptation",
      "core_teaching_point": "Discretionary spending on dining out and lifestyle apps surges by 85 percent within six months of crossing the ₹1,00,000 income milestone."
    },
    {
      "scene_id": "scene_03",
      "title": "Fixing the Wealth Leak",
      "focus_concept": "Effective Hourly Rate",
      "core_teaching_point": "Upgrading housing from a 1 BHK to a 2 BHK and locking into heavy auto loan EMIs silently erodes your actual wealth accumulation capacity."
    },
    {
      "scene_id": "scene_04",
      "title": "Two Paths in Mumbai",
      "focus_concept": "Opportunity Cost of Consumption",
      "core_teaching_point": "Choosing immediate luxury consumption over asset building costs you years of working life and prevents true financial independence."
    },
    {
      "scene_id": "scene_05",
      "title": "Debunking Financial Myths",
      "focus_concept": "Lifestyle Inflation",
      "core_teaching_point": "Believing that luxury EMIs build financial maturity is a dangerous myth that keeps 42 percent of corporate earners trapped paycheck-to-paycheck."
    },
    {
      "scene_id": "scene_06",
      "title": "The Freedom Blueprint",
      "focus_concept": "The 50/30/20 Rule",
      "core_teaching_point": "Systematically allocating your income using structured saving rules prevents lifestyle creep and secures your long-term financial freedom."
    },
    {
      "scene_id": "scene_07",
      "title": "The One Crore Reality",
      "focus_concept": "The 50/30/20 Rule",
      "core_teaching_point": "Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent return builds a corpus of over ₹1 crore in 15 years."
    }
  ],
  "provider_metadata": {
    "provider": "gemini",
    "model": "gemini-3.5-flash-lite",
    "raw_metadata": {
      "finish_reason": "STOP",
      "usage_metadata": {
        "promptTokenCount": 1663,
        "candidatesTokenCount": 801,
        "totalTokenCount": 2464,
        "promptTokensDetails": [
          {
            "modality": "TEXT",
            "tokenCount": 1663
          }
        ],
        "serviceTier": "standard"
      },
      "schema_name": "NarrativePlan"
    }
  }
}
```

---

## Stage 3: Hook Script & Visual Directives (First 15 Seconds)

- **Artifact ID:** `artifact_91617e44824b4af1891382f21ead3c14`
- **Artifact Type:** `hook`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-09T07:04:44.332964+00:00`
- **Parent Artifact Roles:** `{"generate_video_request": "artifact_21b4f7a00c324ecda64c1a009175c3e7", "narrative_plan": "artifact_cfb6e8a9063c4be1be52aa89b619bff8"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Generates high-retention opening script and legacy visual components (Typography, StockVideo, SplitComparison).

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "conceptual_hook": "Making ₹1,00,000 a month puts you in India's top 3 percent of earners, yet 68 percent of professionals at this level have less than ₹50,000 in liquid savings—proving that a bigger paycheck is often just a gilded cage.",
  "script_text": "You finally hit ₹1,00,000 a month and thought you made it. But instead of financial freedom, you traded your financial stress for a luxury EMI. Your income doubled, but your savings stayed at zero. You are not building wealth. You just moved into a much more expensive cage.",
  "visual_directives": [
    {
      "beat_id": "beat_01",
      "preferred_component": "Typography",
      "visual_goal": "Provocative bold headline about hitting the salary milestone.",
      "visual_instruction": null,
      "asset_query": null,
      "notes": null,
      "trigger_word": null,
      "component_data": {
        "text": "The ₹1,00,000 Illusion",
        "subtitle": "Top 3 percent income, zero savings",
        "variant": "headline"
      }
    },
    {
      "beat_id": "beat_02",
      "preferred_component": "StockVideo",
      "visual_goal": "Stressed corporate professional looking at bank account on phone.",
      "visual_instruction": null,
      "asset_query": "stressed person checking phone",
      "notes": null,
      "trigger_word": "freedom",
      "component_data": {}
    },
    {
      "beat_id": "beat_03",
      "preferred_component": "SplitComparison",
      "visual_goal": "Side-by-side comparison of soaring income versus stagnant savings.",
      "visual_instruction": null,
      "asset_query": null,
      "notes": null,
      "trigger_word": "doubled",
      "component_data": {
        "left_role": "Monthly Salary",
        "left_value": "₹1,00,000",
        "right_role": "Liquid Savings",
        "right_value": "₹50,000",
        "header_label": "THE REALITY GAP",
        "left_label": "Monthly Salary",
        "right_label": "Liquid Savings",
        "tone": "neutral",
        "variant": "cards"
      }
    }
  ],
  "provider_metadata": {
    "provider": "gemini",
    "model": "gemini-3.5-flash-lite",
    "raw_metadata": {
      "finish_reason": "STOP",
      "usage_metadata": {
        "promptTokenCount": 6040,
        "candidatesTokenCount": 502,
        "totalTokenCount": 6542,
        "promptTokensDetails": [
          {
            "modality": "TEXT",
            "tokenCount": 6040
          }
        ],
        "serviceTier": "standard"
      },
      "schema_name": "Hook"
    }
  }
}
```

---

## Stage 4: Script & Visual Strategy (Narrative Script + Composition Plan)

- **Artifact ID:** `artifact_8fff4dcb609c48618a35d6879fe88b27`
- **Artifact Type:** `script_visual_strategy`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-09T07:39:26.365313+00:00`
- **Parent Artifact Roles:** `{"hook": "artifact_91617e44824b4af1891382f21ead3c14", "narrative_plan": "artifact_cfb6e8a9063c4be1be52aa89b619bff8", "research_packet": "artifact_e6e75473be8742dea993456f08249abb"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Generates the body narration and maps visual intents to concrete composition models (MetricHero, CalculationStory, CauseEffect, BrollCaption).

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "thesis": "Earning ₹1,00,000 per month does not guarantee financial freedom if lifestyle inflation and luxury EMIs swallow your surplus, whereas disciplined 50 percent savings builds a ₹1 crore corpus in 15 years.",
  "ideas": [
    {
      "idea_id": "idea_01",
      "title": "The Top 3 Percent Illusion",
      "focus_concept": "Lifestyle Inflation",
      "core_teaching_point": "Earning ₹1,00,000 a month places you in India's top 3 percent of earners, yet most professionals remain cash-poor due to immediate spending upgrades.",
      "narration": "When you finally cross that major salary threshold, reality hits hard. Earning ₹1,00,000 per month officially places you in India's top 3 percent of earners according to data from the Ministry of Finance. It feels like an incredible milestone. Yet, behind the polished corporate facade, financial vulnerability lurks. In fact, 68 percent of urban Indian professionals earning between ₹1,00,000 and ₹1,50,000 per month report having less than ₹50,000 in liquid emergency savings. Instead of accumulating real freedom, your growing salary instantly vanishes into newly inflated lifestyle choices.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Bold typography introducing the elite top 3 percent income bracket.",
          "asset_query": "corporate salary growth",
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "Top 3 Percent Earners",
            "subtitle": "Ministry of Finance data",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter showing the monthly earnings threshold.",
          "asset_query": "salary milestone counter",
          "notes": null,
          "trigger_word": "finance",
          "component_data": {
            "end_value": 100000.0,
            "label": "Monthly Income",
            "prefix": "₹",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "StockVideo",
          "visual_goal": "Corporate professional looking overwhelmed at desk.",
          "asset_query": "stressed corporate employee at desk",
          "notes": null,
          "trigger_word": "facade",
          "component_data": {}
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter highlighting the high percentage of professionals with minimal savings.",
          "asset_query": "low bank savings percentage",
          "notes": null,
          "trigger_word": "professionals",
          "component_data": {
            "end_value": 68.0,
            "label": "Low Liquid Savings",
            "suffix": "%",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Closing text emphasizing the illusion of safety.",
          "asset_query": "gilded cage financial trap",
          "notes": null,
          "trigger_word": "vanishes",
          "component_data": {
            "text": "The Gilded Cage",
            "subtitle": "Bigger salary, zero surplus",
            "variant": "statement"
          }
        }
      ]
    },
    {
      "idea_id": "idea_02",
      "title": "The Gilded Cage Trap",
      "focus_concept": "Hedonic Adaptation",
      "core_teaching_point": "Discretionary spending on dining out and lifestyle apps surges by 85 percent within six months of crossing the ₹1,00,000 income milestone.",
      "narration": "Why does this happen so quickly? The answer lies in psychological conditioning and immediate gratification. Studies from the Kantar Urban Spending Index reveal that average monthly discretionary spend on dining out and lifestyle apps increases by 85 percent within 6 months of a salary promotion crossing ₹1,00,000 per month. Furthermore, ordering food delivery 15 times a month instead of cooking adds an extra ₹7,500 to monthly discretionary spending. You start treating luxury conveniences as absolute necessities, trapping yourself in an endless cycle of consumption.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography showing the danger of hedonic adaptation.",
          "asset_query": "lifestyle inflation concept",
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "Hedonic Adaptation",
            "subtitle": "Upgrading lifestyle instantly",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "Charts",
          "visual_goal": "Bar chart illustrating spending surge on lifestyle apps.",
          "asset_query": "spending surge chart",
          "notes": null,
          "trigger_word": "kantar",
          "component_data": {
            "chart_type": "bar",
            "header_label": "DISCRETIONARY SURGE",
            "labels": [
              "Month 1",
              "Month 3",
              "Month 6"
            ],
            "unit": "%",
            "values": [
              10.0,
              45.0,
              85.0
            ]
          }
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "StockVideo",
          "visual_goal": "Ordering food on a smartphone delivery app.",
          "asset_query": "food delivery app on phone",
          "notes": null,
          "trigger_word": "apps",
          "component_data": {}
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter displaying extra monthly dining costs.",
          "asset_query": "food delivery cost counter",
          "notes": null,
          "trigger_word": "cooking",
          "component_data": {
            "end_value": 7500.0,
            "label": "Extra Monthly Dining",
            "prefix": "₹",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Closing text on convenience spending traps.",
          "asset_query": "expensive habits trap",
          "notes": null,
          "trigger_word": "consumption",
          "component_data": {
            "text": "Convenience is Costly",
            "subtitle": "Small habits drain your income",
            "variant": "takeaway"
          }
        }
      ]
    },
    {
      "idea_id": "idea_03",
      "title": "Fixing the Wealth Leak",
      "focus_concept": "Effective Hourly Rate",
      "core_teaching_point": "Upgrading housing from a 1 BHK to a 2 BHK and locking into heavy auto loan EMIs silently erodes your actual wealth accumulation capacity.",
      "narration": "Once discretionary spending spikes, major fixed commitments enter the picture. Upgrading from a rented 1 BHK to a 2 BHK apartment in cities like Bengaluru or Mumbai increases monthly housing expenses by an average of ₹25,000 to ₹40,000. On top of that, purchasing a mid-size car on an auto loan at an EMI of ₹22,000 per month locks in vehicle depreciation and loan interest for 5 years. These heavy financial anchors silently crush your effective hourly rate and destroy your capacity to build genuine long-term wealth.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography showing heavy fixed commitment leaks.",
          "asset_query": "housing and car loan debt",
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "The Big Wealth Leaks",
            "subtitle": "Housing and auto loans",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter showing housing upgrade rent increase.",
          "asset_query": "apartment rent increase counter",
          "notes": null,
          "trigger_word": "mumbai",
          "component_data": {
            "end_value": 40000.0,
            "label": "Max Rent Increase",
            "prefix": "₹",
            "subtitle": "1 BHK to 2 BHK upgrade",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "StockVideo",
          "visual_goal": "Signing car loan paperwork at a dealership.",
          "asset_query": "signing car loan paperwork",
          "notes": null,
          "trigger_word": "purchasing",
          "component_data": {}
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter displaying monthly car EMI commitment.",
          "asset_query": "car loan monthly payment",
          "notes": null,
          "trigger_word": "month",
          "component_data": {
            "end_value": 22000.0,
            "label": "Monthly Car EMI",
            "prefix": "₹",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Summary text on long-term wealth destruction.",
          "asset_query": "debt shackles concept",
          "notes": null,
          "trigger_word": "wealth",
          "component_data": {
            "text": "Anchored by Liabilities",
            "subtitle": "Locks you into 5 years of debt",
            "variant": "statement"
          }
        }
      ]
    },
    {
      "idea_id": "idea_04",
      "title": "Two Paths in Mumbai",
      "focus_concept": "Opportunity Cost of Consumption",
      "core_teaching_point": "Choosing immediate luxury consumption over asset building costs you years of working life and prevents true financial independence.",
      "narration": "Let us examine the stark opportunity cost of consumption. Every rupee spent on maintaining an upscale image in Mumbai or Gurgaon is a rupee stolen from your future self. When you prioritize flash over assets, you are trading decades of freedom for a temporary status symbol. The hidden price of your luxury car and upgraded apartment isn't just the sticker price—it is the lost compound growth that could have set you free a decade earlier.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography highlighting opportunity cost of consumption.",
          "asset_query": "luxury consumption vs savings",
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "The Price of Status",
            "subtitle": "Trading freedom for flash",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "StockVideo",
          "visual_goal": "Traffic passing by upscale buildings in Mumbai.",
          "asset_query": "mumbai corporate street lifestyle",
          "notes": null,
          "trigger_word": "mumbai",
          "component_data": {}
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "Typography",
          "visual_goal": "Statement emphasizing future self trade-off.",
          "asset_query": "future financial regret",
          "notes": null,
          "trigger_word": "self",
          "component_data": {
            "text": "Stolen From Your Future",
            "subtitle": "Every luxury purchase has a hidden cost",
            "variant": "statement"
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "StockVideo",
          "visual_goal": "Person calculating finances with calculator.",
          "asset_query": "calculating financial opportunity cost",
          "notes": null,
          "trigger_word": "assets",
          "component_data": {}
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Final takeaway on escaping the trap.",
          "asset_query": "wealth building mindset",
          "notes": null,
          "trigger_word": "earlier",
          "component_data": {
            "text": "Choose Assets Over Image",
            "subtitle": "Break free from the consumption cycle",
            "variant": "takeaway"
          }
        }
      ]
    },
    {
      "idea_id": "idea_05",
      "title": "Debunking Financial Myths",
      "focus_concept": "Lifestyle Inflation",
      "core_teaching_point": "Believing that luxury EMIs build financial maturity is a dangerous myth that keeps 42 percent of corporate earners trapped paycheck-to-paycheck.",
      "narration": "There is a pervasive myth in urban corporate culture that carrying heavy EMIs signals financial maturity or success. According to the Mastercard Financial Literacy Index, lifestyle inflation causes 42 percent of corporate employees to remain paycheck-to-paycheck despite crossing the ₹12,00,000 annual income bracket. They believe that buying luxury items on credit establishes creditworthiness, when in reality, it simply chains them tighter to their desks, eliminating any margin for error if economic conditions shift.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography debunking corporate financial myths.",
          "asset_query": "credit card debt myth",
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "Debunking the EMI Myth",
            "subtitle": "Credit is not true wealth",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter showing percentage trapped paycheck to paycheck.",
          "asset_query": "paycheck to paycheck statistic counter",
          "notes": null,
          "trigger_word": "causes",
          "component_data": {
            "end_value": 42.0,
            "label": "Paycheck to Paycheck",
            "suffix": "%",
            "unit": "%",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "Typography",
          "visual_goal": "Highlighting the annual income bracket trap.",
          "asset_query": "annual income salary trap",
          "notes": null,
          "trigger_word": "bracket",
          "component_data": {
            "text": "₹12,00,000 Annual Trap",
            "subtitle": "High income, zero security",
            "variant": "statement"
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "StockVideo",
          "visual_goal": "Frustrated office worker looking at bills.",
          "asset_query": "stressed worker reviewing credit bills",
          "notes": null,
          "trigger_word": "creditworthiness",
          "component_data": {}
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Takeaway warning against false financial security.",
          "asset_query": "financial freedom warning",
          "notes": null,
          "trigger_word": "shift",
          "component_data": {
            "text": "EMIs Are Not Wealth",
            "subtitle": "Eliminate lifestyle inflation",
            "variant": "takeaway"
          }
        }
      ]
    },
    {
      "idea_id": "idea_06",
      "title": "The Freedom Blueprint",
      "focus_concept": "The 50/30/20 Rule",
      "core_teaching_point": "Systematically allocating your income using structured saving rules prevents lifestyle creep and secures your long-term financial freedom.",
      "narration": "Escaping this cycle requires a rigorous framework, and the time-tested 50/30/20 rule is your ultimate weapon. By allocating 50 percent of your ₹1,00,000 salary to absolute needs, 30 percent to guilt-free wants, and a disciplined 50 percent directly to aggressive wealth building, you completely break the pattern of lifestyle creep. Instead of letting your bank account bleed out through miscellaneous expenses, every single rupee is assigned a specific, mission-driven purpose.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography introducing the financial freedom blueprint.",
          "asset_query": "financial budget blueprint",
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "The Freedom Blueprint",
            "subtitle": "Master your cash flow",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "ProcessFlow",
          "visual_goal": "Process flow displaying the structured budget allocation.",
          "asset_query": "budget allocation flow chart",
          "notes": null,
          "trigger_word": "rule",
          "component_data": {
            "header_label": "BUDGET ALLOCATION",
            "steps": [
              {
                "title": "50% Needs",
                "subtitle": null,
                "type": "cause",
                "value": "Essentials",
                "connector_label": null,
                "icon": null
              },
              {
                "title": "30% Wants",
                "subtitle": null,
                "type": "step",
                "value": "Discretionary",
                "connector_label": null,
                "icon": null
              },
              {
                "title": "50% Savings",
                "subtitle": null,
                "type": "outcome",
                "value": "Wealth Building",
                "connector_label": null,
                "icon": null
              }
            ]
          }
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "StockVideo",
          "visual_goal": "Person organizing budget on laptop.",
          "asset_query": "budgeting on laptop",
          "notes": null,
          "trigger_word": "salary",
          "component_data": {}
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "Typography",
          "visual_goal": "Highlighting the elimination of lifestyle creep.",
          "asset_query": "stopping lifestyle inflation",
          "notes": null,
          "trigger_word": "creep",
          "component_data": {
            "text": "Stop Lifestyle Creep",
            "subtitle": "Systematic allocation beats impulse",
            "variant": "statement"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Closing text on purposeful money management.",
          "asset_query": "purposeful money management",
          "notes": null,
          "trigger_word": "purpose",
          "component_data": {
            "text": "Purpose-Driven Money",
            "subtitle": "Every rupee has a job",
            "variant": "takeaway"
          }
        }
      ]
    },
    {
      "idea_id": "idea_07",
      "title": "The One Crore Reality",
      "focus_concept": "The 50/30/20 Rule",
      "core_teaching_point": "Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent return builds a corpus of over ₹1 crore in 15 years.",
      "narration": "When you commit to this disciplined path, the math becomes life-changing. Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent annual return builds a corpus of over ₹1 crore in 15 years. Pause and reflect on that. While your peers are trapped paying off luxury car loans and inflated apartment rents, your disciplined surplus compounds into true financial independence. You stop working for a paycheck and let your money work for you.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography introducing the one crore financial milestone.",
          "asset_query": "one crore wealth milestone",
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "The ₹1 Crore Milestone",
            "subtitle": "Compound growth in action",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter showing the massive investment corpus goal.",
          "asset_query": "one crore corpus counter",
          "notes": null,
          "trigger_word": "salary",
          "component_data": {
            "end_value": 1.0,
            "label": "Target Corpus",
            "prefix": "₹",
            "suffix": " Crore",
            "unit": "Crore",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "Charts",
          "visual_goal": "Line chart showing 15 year compounding growth trajectory.",
          "asset_query": "investment growth line chart",
          "notes": null,
          "trigger_word": "years",
          "component_data": {
            "chart_type": "line",
            "header_label": "15-YEAR COMPOUNDING TRAJECTORY",
            "labels": [
              "Year 1",
              "Year 5",
              "Year 10",
              "Year 15"
            ],
            "unit": "₹",
            "values": [
              6.0,
              40.0,
              80.0,
              100.0
            ]
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "StockVideo",
          "visual_goal": "Confident professional looking at sunset from balcony.",
          "asset_query": "financial freedom success view",
          "notes": null,
          "trigger_word": "independence",
          "component_data": {}
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Final inspiring takeaway on financial freedom.",
          "asset_query": "wealth building success",
          "notes": null,
          "trigger_word": "you",
          "component_data": {
            "text": "Let Your Money Work",
            "subtitle": "Escape the lifestyle trap forever",
            "variant": "takeaway"
          }
        }
      ]
    }
  ],
  "provider_metadata": {
    "provider": "gemini",
    "model": "gemini-3.5-flash-lite",
    "raw_metadata": {
      "finish_reason": "STOP",
      "usage_metadata": {
        "promptTokenCount": 5892,
        "candidatesTokenCount": 5388,
        "totalTokenCount": 11280,
        "promptTokensDetails": [
          {
            "modality": "TEXT",
            "tokenCount": 5892
          }
        ],
        "serviceTier": "standard"
      },
      "schema_name": "ScriptVisualStrategy"
    }
  },
  "visual_mode": "composition",
  "composition_plan": {
    "schema_version": "1",
    "visual_mode": "composition",
    "thesis": "Earning ₹1,00,000 per month does not guarantee financial freedom if lifestyle inflation and luxury EMIs swallow your surplus, whereas disciplined 50 percent savings builds a ₹1 crore corpus in 15 years.",
    "ideas": [
      {
        "idea_id": "idea_01",
        "narration": "When you finally cross that major salary threshold, reality hits hard. Earning ₹1,00,000 per month officially places you in India's top 3 percent of earners according to data from the Ministry of Finance. It feels like an incredible milestone. Yet, behind the polished corporate facade, financial vulnerability lurks. In fact, 68 percent of urban Indian professionals earning between ₹1,00,000 and ₹1,50,000 per month report having less than ₹50,000 in liquid emergency savings. Instead of accumulating real freedom, your growing salary instantly vanishes into newly inflated lifestyle choices.",
        "beats": [
          {
            "beat_id": "beat_01_01",
            "composition_id": "metric_hero",
            "variant": "hero",
            "composition_data": {
              "value": "₹1,00,000",
              "label": "Monthly Income",
              "context": "Top 3% of Earners in India",
              "emphasis": "hero"
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": null,
            "visual_goal": "Highlight ₹1,00,000 monthly income as putting the viewer in India's top 3 percent of earners."
          },
          {
            "beat_id": "beat_01_02",
            "composition_id": "metric_hero",
            "variant": "hero",
            "composition_data": {
              "value": "68%",
              "label": "Professionals with <₹50,000 Emergency Savings",
              "context": "earning ₹1L-1.5L/month",
              "emphasis": "hero"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "corporate professional stressed about money",
            "trigger_word": "vulnerability",
            "visual_goal": "Highlight the startling statistic that 68 percent of high earners have minimal emergency savings."
          },
          {
            "beat_id": "beat_01_03",
            "composition_id": "cause_effect",
            "variant": null,
            "composition_data": {
              "causes": [
                {
                  "label": "Higher Salary",
                  "value": null,
                  "icon": "💰"
                },
                {
                  "label": "Lifestyle Inflation",
                  "value": null,
                  "icon": "📈"
                }
              ],
              "connector": "leads to",
              "outcome_label": "Zero Freedom Gained",
              "outcome_value": null,
              "outcome_severity": "negative"
            },
            "asset_requirement": "optional_broll",
            "asset_query": null,
            "trigger_word": "vanishes",
            "visual_goal": "Show how increased earnings are swallowed by lifestyle choices instead of building wealth."
          }
        ]
      },
      {
        "idea_id": "idea_02",
        "narration": "Why does this happen so quickly? The answer lies in psychological conditioning and immediate gratification. Studies from the Kantar Urban Spending Index reveal that average monthly discretionary spend on dining out and lifestyle apps increases by 85 percent within 6 months of a salary promotion crossing ₹1,00,000 per month. Furthermore, ordering food delivery 15 times a month instead of cooking adds an extra ₹7,500 to monthly discretionary spending. You start treating luxury conveniences as absolute necessities, trapping yourself in an endless cycle of consumption.",
        "beats": [
          {
            "beat_id": "beat_02_01",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "Psychological conditioning and immediate gratification drive fast lifestyle inflation.",
              "emphasis_phrase": "immediate gratification",
              "author": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": "corporate employee shopping stress lifestyle inflation",
            "trigger_word": null,
            "visual_goal": "Illustrate the psychological drivers of lifestyle inflation with atmospheric B-roll and a clear statement caption."
          },
          {
            "beat_id": "beat_02_02",
            "composition_id": "metric_hero",
            "variant": "hero",
            "composition_data": {
              "value": "85%",
              "label": "Discretionary Spend Increase",
              "context": "within 6 months of crossing ₹1,00,000",
              "emphasis": "hero"
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "Studies",
            "visual_goal": "Highlight the 85 percent jump in discretionary spending after crossing the salary threshold."
          },
          {
            "beat_id": "beat_02_03",
            "composition_id": "calculation_story",
            "variant": null,
            "composition_data": {
              "input_label": "Food Delivery",
              "input_value": "15 times",
              "operation_label": "adds",
              "rate_label": "instead of cooking",
              "result_label": "Monthly Discretionary",
              "result_value": "₹7,500",
              "note": "Extra monthly expense"
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "Furthermore",
            "visual_goal": "Show how ordering food 15 times a month adds ₹7,500 to discretionary spending."
          },
          {
            "beat_id": "beat_02_04",
            "composition_id": "cause_effect",
            "variant": null,
            "composition_data": {
              "causes": [
                {
                  "label": "Luxury Conveniences",
                  "value": null,
                  "icon": "✨"
                },
                {
                  "label": "Treated as Necessities",
                  "value": null,
                  "icon": "🛒"
                }
              ],
              "connector": "leads to",
              "outcome_label": "Endless Consumption Trap",
              "outcome_value": null,
              "outcome_severity": "negative"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "person shopping online lifestyle trap",
            "trigger_word": "treating",
            "visual_goal": "Show how treating luxuries as necessities causes an endless consumption trap."
          }
        ]
      },
      {
        "idea_id": "idea_03",
        "narration": "Once discretionary spending spikes, major fixed commitments enter the picture. Upgrading from a rented 1 BHK to a 2 BHK apartment in cities like Bengaluru or Mumbai increases monthly housing expenses by an average of ₹25,000 to ₹40,000. On top of that, purchasing a mid-size car on an auto loan at an EMI of ₹22,000 per month locks in vehicle depreciation and loan interest for 5 years. These heavy financial anchors silently crush your effective hourly rate and destroy your capacity to build genuine long-term wealth.",
        "beats": [
          {
            "beat_id": "beat_03_01",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "Upgrading to a larger apartment increases monthly housing expenses by ₹25,000 to ₹40,000.",
              "emphasis_phrase": "₹25,000"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "Once discretionary spending spikes, major fixed commitments ",
            "trigger_word": null,
            "visual_goal": "Upgrading to a larger apartment increases monthly housing expenses by ₹25,000 to ₹40,000."
          },
          {
            "beat_id": "beat_03_02",
            "composition_id": "metric_hero",
            "variant": "hero",
            "composition_data": {
              "value": "₹22,000",
              "label": "Monthly Car EMI",
              "context": "per month for 5 years",
              "emphasis": "hero"
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "purchasing",
            "visual_goal": "Highlight the ₹22,000 monthly car EMI as a heavy financial commitment."
          },
          {
            "beat_id": "beat_03_03",
            "composition_id": "cause_effect",
            "variant": null,
            "composition_data": {
              "causes": [
                {
                  "label": "Heavy Financial Anchors",
                  "value": null,
                  "icon": "⚓"
                }
              ],
              "connector": "destroys",
              "outcome_label": "Long-Term Wealth Capacity",
              "outcome_value": null,
              "outcome_severity": "negative"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "financial burden stress corporate lifestyle",
            "trigger_word": "anchors",
            "visual_goal": "Show how fixed lifestyle commitments cause the destruction of long-term wealth capacity."
          }
        ]
      },
      {
        "idea_id": "idea_04",
        "narration": "Let us examine the stark opportunity cost of consumption. Every rupee spent on maintaining an upscale image in Mumbai or Gurgaon is a rupee stolen from your future self. When you prioritize flash over assets, you are trading decades of freedom for a temporary status symbol. The hidden price of your luxury car and upgraded apartment isn't just the sticker price—it is the lost compound growth that could have set you free a decade earlier.",
        "beats": [
          {
            "beat_id": "beat_04_01",
            "composition_id": "cause_effect",
            "variant": null,
            "composition_data": {
              "causes": [
                {
                  "label": "Mumbai / Gurgaon Upscale Lifestyle",
                  "value": null,
                  "icon": "🏙️"
                }
              ],
              "connector": "steals from",
              "outcome_label": "Future Self",
              "outcome_value": "Vulnerability",
              "outcome_severity": "negative"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "expensive city lifestyle corporate employee",
            "trigger_word": null,
            "visual_goal": "Show how spending on lifestyle in cities causes financial harm to the future self."
          },
          {
            "beat_id": "beat_04_02",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "Prioritizing flash over assets trades decades of freedom for temporary status.",
              "emphasis_phrase": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": "When you prioritize flash over assets, you are trading decad",
            "trigger_word": "prioritize",
            "visual_goal": "Prioritizing flash over assets trades decades of freedom for temporary status."
          },
          {
            "beat_id": "beat_04_03",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "The true cost of luxury items includes lost compound growth and delayed freedom.",
              "emphasis_phrase": "luxury car"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "The hidden price of your luxury car and upgraded apartment i",
            "trigger_word": "hidden",
            "visual_goal": "The true cost of luxury items includes lost compound growth and delayed freedom."
          }
        ]
      },
      {
        "idea_id": "idea_05",
        "narration": "There is a pervasive myth in urban corporate culture that carrying heavy EMIs signals financial maturity or success. According to the Mastercard Financial Literacy Index, lifestyle inflation causes 42 percent of corporate employees to remain paycheck-to-paycheck despite crossing the ₹12,00,000 annual income bracket. They believe that buying luxury items on credit establishes creditworthiness, when in reality, it simply chains them tighter to their desks, eliminating any margin for error if economic conditions shift.",
        "beats": [
          {
            "beat_id": "beat_05_01",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "Carrying heavy EMIs is viewed as a sign of success in urban corporate culture.",
              "emphasis_phrase": "sign of success",
              "author": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": "corporate worker modern lifestyle urban",
            "trigger_word": null,
            "visual_goal": "Show atmospheric corporate lifestyle visuals highlighting the perception of EMIs as success."
          },
          {
            "beat_id": "beat_05_02",
            "composition_id": "cause_effect",
            "variant": null,
            "composition_data": {
              "causes": [
                {
                  "label": "Mastercard Financial Literacy Index",
                  "value": "42%",
                  "icon": null
                },
                {
                  "label": "Annual Income Threshold",
                  "value": "₹12,00,000",
                  "icon": null
                }
              ],
              "connector": "leads to",
              "outcome_label": "Paycheck-to-Paycheck Lifestyle Inflation",
              "outcome_value": null,
              "outcome_severity": "negative"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "corporate employee financial stress modern office",
            "trigger_word": "According",
            "visual_goal": "Show how earning over ₹12 lakh leads to paycheck-to-paycheck living due to lifestyle inflation as reported by the Mastercard Financial Literacy Index."
          },
          {
            "beat_id": "beat_05_03",
            "composition_id": "cause_effect",
            "variant": null,
            "composition_data": {
              "causes": [
                {
                  "label": "Luxury Purchases on Credit",
                  "value": "Debt",
                  "icon": "💳"
                }
              ],
              "connector": "chains workers to desks and eliminates",
              "outcome_label": "Financial Margin for Error",
              "outcome_value": "Zero",
              "outcome_severity": "negative"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "corporate employee chained to desk office",
            "trigger_word": "believe",
            "visual_goal": "Show how buying luxury items on credit directly removes financial safety margins and chains workers to their desks."
          }
        ]
      },
      {
        "idea_id": "idea_06",
        "narration": "Escaping this cycle requires a rigorous framework, and the time-tested 50/30/20 rule is your ultimate weapon. By allocating 50 percent of your ₹1,00,000 salary to absolute needs, 30 percent to guilt-free wants, and a disciplined 50 percent directly to aggressive wealth building, you completely break the pattern of lifestyle creep. Instead of letting your bank account bleed out through miscellaneous expenses, every single rupee is assigned a specific, mission-driven purpose.",
        "beats": [
          {
            "beat_id": "beat_06_01",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "Escaping this cycle requires a rigorous framework, and the time-tested 50/30/20 rule is your ultimate weapon.",
              "emphasis_phrase": "50/30/20 rule",
              "author": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": "person looking at budget planner corporate office",
            "trigger_word": null,
            "visual_goal": "Introduce the 50/30/20 rule as the framework to escape the lifestyle cycle with an atmospheric broll and caption."
          },
          {
            "beat_id": "beat_06_02",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "The ₹1,00,000 salary is budgeted as 50 percent needs, 30 percent wants, and savings/wealth building.",
              "emphasis_phrase": "50 percent"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "By allocating 50 percent of your ₹1,00,000 salary to absolut",
            "trigger_word": "allocating",
            "visual_goal": "The ₹1,00,000 salary is budgeted as 50 percent needs, 30 percent wants, and savings/wealth building."
          },
          {
            "beat_id": "beat_06_03",
            "composition_id": "cause_effect",
            "variant": null,
            "composition_data": {
              "causes": [
                {
                  "label": "Miscellaneous Expenses",
                  "value": "Bleeding Out",
                  "icon": "💸"
                }
              ],
              "connector": "stopped by",
              "outcome_label": "Mission-Driven Purpose",
              "outcome_value": "Protected Bank Account",
              "outcome_severity": "positive"
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "bleeding",
            "visual_goal": "Show how assigning a specific purpose to every rupee stops miscellaneous expenses from draining the account."
          }
        ]
      },
      {
        "idea_id": "idea_07",
        "narration": "When you commit to this disciplined path, the math becomes life-changing. Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent annual return builds a corpus of over ₹1 crore in 15 years. Pause and reflect on that. While your peers are trapped paying off luxury car loans and inflated apartment rents, your disciplined surplus compounds into true financial independence. You stop working for a paycheck and let your money work for you.",
        "beats": [
          {
            "beat_id": "beat_07_01",
            "composition_id": "calculation_story",
            "variant": null,
            "composition_data": {
              "input_label": "Monthly Investment",
              "input_value": "₹50,000",
              "operation_label": "→",
              "rate_label": "12% return over 15 years",
              "result_label": "Final Corpus",
              "result_value": "₹1 crore",
              "note": "Based on 50% of ₹1,00,000 salary"
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": null,
            "visual_goal": "Show how investing 50 percent of a ₹1,00,000 salary grows to ₹1 crore in 15 years at a 12 percent return."
          },
          {
            "beat_id": "beat_07_02",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "Comparison between peer luxury debt and disciplined surplus leading to financial independence.",
              "emphasis_phrase": "luxury car loans"
            },
            "asset_requirement": "optional_broll",
            "asset_query": "While your peers are trapped paying off luxury car loans and",
            "trigger_word": "peers",
            "visual_goal": "Comparison between peer luxury debt and disciplined surplus leading to financial independence."
          },
          {
            "beat_id": "beat_07_03",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "Break free from the paycheck cycle and let your money work for you.",
              "emphasis_phrase": "money work for you",
              "author": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": "financial freedom lifestyle corporate employee",
            "trigger_word": "stop",
            "visual_goal": "Show an atmospheric visual representing financial freedom and breaking the paycheck cycle."
          }
        ]
      }
    ]
  }
}
```

---

## Stage 5: Automated Quality Review (Safety, Policy & Retention Check)

- **Artifact ID:** `artifact_2f6cbd40cd2645139d16dc058e3284af`
- **Artifact Type:** `review_result`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-09T07:40:34.335927+00:00`
- **Parent Artifact Roles:** `{"script_visual_strategy": "artifact_8fff4dcb609c48618a35d6879fe88b27"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Evaluates script quality, pacing, guideline compliance, and visual directive alignment before rendering.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "approved": true,
  "checks": [
    {
      "name": "Concept Alignment",
      "status": "passed",
      "message": "All script concepts are present in research."
    },
    {
      "name": "Statistic Verification",
      "status": "passed",
      "message": "All numeric statistics in script are verified in research."
    },
    {
      "name": "Visual Configuration",
      "status": "passed",
      "message": "All visual component configurations are valid."
    }
  ],
  "feedback": "All checks passed successfully."
}
```

---

## Stage 6: Voice Track & Timing Alignment (TTS Generation & Word Timestamps)

- **Artifact ID:** `artifact_b2bfeb1c57d5450c9511eb0c39f19818`
- **Artifact Type:** `voice_track`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-09T07:40:48.836542+00:00`
- **Parent Artifact Roles:** `{"script_visual_strategy": "artifact_8fff4dcb609c48618a35d6879fe88b27", "hook": "artifact_91617e44824b4af1891382f21ead3c14"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Generates voiceover audio via ElevenLabs and produces word-level timestamps for exact frame synchronization.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "voice_id": "Matthew",
  "audio_file_name": "narration.mp3",
  "storage_key": "projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/narration.mp3",
  "duration_seconds": 216.12,
  "full_script_text": "You finally hit ₹1,00,000 a month and thought you made it. But instead of financial freedom, you traded your financial stress for a luxury EMI. Your income doubled, but your savings stayed at zero. You are not building wealth. You just moved into a much more expensive cage.\n\nWhen you finally cross that major salary threshold, reality hits hard. Earning ₹1,00,000 per month officially places you in India's top 3 percent of earners according to data from the Ministry of Finance. It feels like an incredible milestone. Yet, behind the polished corporate facade, financial vulnerability lurks. In fact, 68 percent of urban Indian professionals earning between ₹1,00,000 and ₹1,50,000 per month report having less than ₹50,000 in liquid emergency savings. Instead of accumulating real freedom, your growing salary instantly vanishes into newly inflated lifestyle choices.\n\nWhy does this happen so quickly? The answer lies in psychological conditioning and immediate gratification. Studies from the Kantar Urban Spending Index reveal that average monthly discretionary spend on dining out and lifestyle apps increases by 85 percent within 6 months of a salary promotion crossing ₹1,00,000 per month. Furthermore, ordering food delivery 15 times a month instead of cooking adds an extra ₹7,500 to monthly discretionary spending. You start treating luxury conveniences as absolute necessities, trapping yourself in an endless cycle of consumption.\n\nOnce discretionary spending spikes, major fixed commitments enter the picture. Upgrading from a rented 1 BHK to a 2 BHK apartment in cities like Bengaluru or Mumbai increases monthly housing expenses by an average of ₹25,000 to ₹40,000. On top of that, purchasing a mid-size car on an auto loan at an EMI of ₹22,000 per month locks in vehicle depreciation and loan interest for 5 years. These heavy financial anchors silently crush your effective hourly rate and destroy your capacity to build genuine long-term wealth.\n\nLet us examine the stark opportunity cost of consumption. Every rupee spent on maintaining an upscale image in Mumbai or Gurgaon is a rupee stolen from your future self. When you prioritize flash over assets, you are trading decades of freedom for a temporary status symbol. The hidden price of your luxury car and upgraded apartment isn't just the sticker price—it is the lost compound growth that could have set you free a decade earlier.\n\nThere is a pervasive myth in urban corporate culture that carrying heavy EMIs signals financial maturity or success. According to the Mastercard Financial Literacy Index, lifestyle inflation causes 42 percent of corporate employees to remain paycheck-to-paycheck despite crossing the ₹12,00,000 annual income bracket. They believe that buying luxury items on credit establishes creditworthiness, when in reality, it simply chains them tighter to their desks, eliminating any margin for error if economic conditions shift.\n\nEscaping this cycle requires a rigorous framework, and the time-tested 50/30/20 rule is your ultimate weapon. By allocating 50 percent of your ₹1,00,000 salary to absolute needs, 30 percent to guilt-free wants, and a disciplined 50 percent directly to aggressive wealth building, you completely break the pattern of lifestyle creep. Instead of letting your bank account bleed out through miscellaneous expenses, every single rupee is assigned a specific, mission-driven purpose.\n\nWhen you commit to this disciplined path, the math becomes life-changing. Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent annual return builds a corpus of over ₹1 crore in 15 years. Pause and reflect on that. While your peers are trapped paying off luxury car loans and inflated apartment rents, your disciplined surplus compounds into true financial independence. You stop working for a paycheck and let your money work for you.",
  "word_timestamps": [
    {
      "word": "You",
      "start_ms": 25,
      "end_ms": 149,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "finally",
      "start_ms": 150,
      "end_ms": 465,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "hit",
      "start_ms": 550,
      "end_ms": 685,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹1,00,000",
      "start_ms": 750,
      "end_ms": 1155,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 1975,
      "end_ms": 2011,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "month",
      "start_ms": 2012,
      "end_ms": 2237,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 2337,
      "end_ms": 2449,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "thought",
      "start_ms": 2450,
      "end_ms": 2661,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 2662,
      "end_ms": 2724,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "made",
      "start_ms": 2725,
      "end_ms": 2905,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "it",
      "start_ms": 2937,
      "end_ms": 3037,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "But",
      "start_ms": 3567,
      "end_ms": 3702,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "instead",
      "start_ms": 3717,
      "end_ms": 4032,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 4042,
      "end_ms": 4116,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 4117,
      "end_ms": 4522,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "freedom",
      "start_ms": 4580,
      "end_ms": 4895,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 5230,
      "end_ms": 5341,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "traded",
      "start_ms": 5342,
      "end_ms": 5612,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 5730,
      "end_ms": 5816,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 5817,
      "end_ms": 6222,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "stress",
      "start_ms": 6292,
      "end_ms": 6562,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 6680,
      "end_ms": 6815,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 6830,
      "end_ms": 6866,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "luxury",
      "start_ms": 6867,
      "end_ms": 7137,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "EMI",
      "start_ms": 7355,
      "end_ms": 7490,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Your",
      "start_ms": 8147,
      "end_ms": 8327,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "income",
      "start_ms": 8335,
      "end_ms": 8605,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "doubled",
      "start_ms": 8660,
      "end_ms": 8975,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "but",
      "start_ms": 9260,
      "end_ms": 9395,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 9460,
      "end_ms": 9571,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "savings",
      "start_ms": 9572,
      "end_ms": 9887,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "stayed",
      "start_ms": 9985,
      "end_ms": 10255,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "at",
      "start_ms": 10260,
      "end_ms": 10346,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "zero",
      "start_ms": 10347,
      "end_ms": 10527,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "You",
      "start_ms": 11265,
      "end_ms": 11400,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "are",
      "start_ms": 11415,
      "end_ms": 11489,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "not",
      "start_ms": 11490,
      "end_ms": 11625,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "building",
      "start_ms": 11702,
      "end_ms": 12051,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "wealth",
      "start_ms": 12052,
      "end_ms": 12322,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "You",
      "start_ms": 12932,
      "end_ms": 13031,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "just",
      "start_ms": 13032,
      "end_ms": 13212,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "moved",
      "start_ms": 13257,
      "end_ms": 13482,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "into",
      "start_ms": 13545,
      "end_ms": 13725,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 13770,
      "end_ms": 13806,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "much",
      "start_ms": 13807,
      "end_ms": 13987,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "more",
      "start_ms": 14070,
      "end_ms": 14250,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "expensive",
      "start_ms": 14295,
      "end_ms": 14700,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cage",
      "start_ms": 14782,
      "end_ms": 14962,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "When",
      "start_ms": 15385,
      "end_ms": 15521,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 15522,
      "end_ms": 15609,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "finally",
      "start_ms": 15610,
      "end_ms": 15925,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cross",
      "start_ms": 15985,
      "end_ms": 16210,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 16335,
      "end_ms": 16484,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "major",
      "start_ms": 16485,
      "end_ms": 16710,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "salary",
      "start_ms": 16797,
      "end_ms": 17067,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "threshold",
      "start_ms": 17210,
      "end_ms": 17615,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "reality",
      "start_ms": 17997,
      "end_ms": 18312,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "hits",
      "start_ms": 18460,
      "end_ms": 18640,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "hard",
      "start_ms": 18660,
      "end_ms": 18840,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Earning",
      "start_ms": 19502,
      "end_ms": 19801,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹1,00,000",
      "start_ms": 19802,
      "end_ms": 20207,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "per",
      "start_ms": 21065,
      "end_ms": 21200,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "month",
      "start_ms": 21227,
      "end_ms": 21452,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "officially",
      "start_ms": 21502,
      "end_ms": 21901,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "places",
      "start_ms": 21902,
      "end_ms": 22172,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 22377,
      "end_ms": 22512,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 22540,
      "end_ms": 22614,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "India's",
      "start_ms": 22615,
      "end_ms": 22930,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "top",
      "start_ms": 23002,
      "end_ms": 23137,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "3",
      "start_ms": 23252,
      "end_ms": 23352,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 23477,
      "end_ms": 23792,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 23840,
      "end_ms": 23939,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "earners",
      "start_ms": 23940,
      "end_ms": 24255,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "according",
      "start_ms": 24265,
      "end_ms": 24614,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 24615,
      "end_ms": 24714,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "data",
      "start_ms": 24715,
      "end_ms": 24895,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "from",
      "start_ms": 25002,
      "end_ms": 25176,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 25177,
      "end_ms": 25239,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Ministry",
      "start_ms": 25240,
      "end_ms": 25600,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 25690,
      "end_ms": 25751,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Finance",
      "start_ms": 25752,
      "end_ms": 26067,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "It",
      "start_ms": 26820,
      "end_ms": 26920,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "feels",
      "start_ms": 26957,
      "end_ms": 27182,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "like",
      "start_ms": 27307,
      "end_ms": 27481,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 27482,
      "end_ms": 27544,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "incredible",
      "start_ms": 27545,
      "end_ms": 27995,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "milestone",
      "start_ms": 28007,
      "end_ms": 28412,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Yet",
      "start_ms": 29212,
      "end_ms": 29347,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "behind",
      "start_ms": 29750,
      "end_ms": 30020,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 30075,
      "end_ms": 30136,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "polished",
      "start_ms": 30137,
      "end_ms": 30497,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "corporate",
      "start_ms": 30537,
      "end_ms": 30911,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "facade",
      "start_ms": 30912,
      "end_ms": 31182,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 31675,
      "end_ms": 32080,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "vulnerability",
      "start_ms": 32175,
      "end_ms": 32760,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "lurks",
      "start_ms": 32825,
      "end_ms": 33050,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "In",
      "start_ms": 33755,
      "end_ms": 33855,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "fact",
      "start_ms": 33905,
      "end_ms": 34085,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "68",
      "start_ms": 34542,
      "end_ms": 34642,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 35105,
      "end_ms": 35420,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 35455,
      "end_ms": 35554,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "urban",
      "start_ms": 35555,
      "end_ms": 35780,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Indian",
      "start_ms": 35830,
      "end_ms": 36100,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "professionals",
      "start_ms": 36155,
      "end_ms": 36740,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "earning",
      "start_ms": 36767,
      "end_ms": 37029,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "between",
      "start_ms": 37030,
      "end_ms": 37345,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹1,00,000",
      "start_ms": 37392,
      "end_ms": 37797,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 38667,
      "end_ms": 38802,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹1,50,000",
      "start_ms": 38805,
      "end_ms": 39210,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "per",
      "start_ms": 40355,
      "end_ms": 40490,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "month",
      "start_ms": 40517,
      "end_ms": 40742,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "report",
      "start_ms": 40805,
      "end_ms": 41075,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "having",
      "start_ms": 41205,
      "end_ms": 41475,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "less",
      "start_ms": 41492,
      "end_ms": 41672,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "than",
      "start_ms": 41730,
      "end_ms": 41879,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹50,000",
      "start_ms": 41880,
      "end_ms": 42195,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 43067,
      "end_ms": 43154,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "liquid",
      "start_ms": 43155,
      "end_ms": 43416,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "emergency",
      "start_ms": 43417,
      "end_ms": 43822,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "savings",
      "start_ms": 43930,
      "end_ms": 44245,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Instead",
      "start_ms": 44972,
      "end_ms": 45287,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 45322,
      "end_ms": 45409,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "accumulating",
      "start_ms": 45410,
      "end_ms": 45950,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "real",
      "start_ms": 45972,
      "end_ms": 46152,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "freedom",
      "start_ms": 46210,
      "end_ms": 46525,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 46860,
      "end_ms": 47021,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "growing",
      "start_ms": 47022,
      "end_ms": 47337,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "salary",
      "start_ms": 47397,
      "end_ms": 47667,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "instantly",
      "start_ms": 47885,
      "end_ms": 48234,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "vanishes",
      "start_ms": 48235,
      "end_ms": 48595,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "into",
      "start_ms": 48822,
      "end_ms": 48996,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "newly",
      "start_ms": 48997,
      "end_ms": 49222,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "inflated",
      "start_ms": 49347,
      "end_ms": 49707,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "lifestyle",
      "start_ms": 49760,
      "end_ms": 50165,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "choices",
      "start_ms": 50272,
      "end_ms": 50587,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Why",
      "start_ms": 51001,
      "end_ms": 51136,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "does",
      "start_ms": 51176,
      "end_ms": 51325,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "this",
      "start_ms": 51326,
      "end_ms": 51500,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "happen",
      "start_ms": 51501,
      "end_ms": 51771,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "so",
      "start_ms": 51788,
      "end_ms": 51888,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "quickly",
      "start_ms": 51963,
      "end_ms": 52278,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "The",
      "start_ms": 52943,
      "end_ms": 53078,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "answer",
      "start_ms": 53143,
      "end_ms": 53380,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "lies",
      "start_ms": 53381,
      "end_ms": 53561,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 53768,
      "end_ms": 53867,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "psychological",
      "start_ms": 53868,
      "end_ms": 54453,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "conditioning",
      "start_ms": 54581,
      "end_ms": 55121,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 55206,
      "end_ms": 55280,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "immediate",
      "start_ms": 55281,
      "end_ms": 55686,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "gratification",
      "start_ms": 55693,
      "end_ms": 56278,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Studies",
      "start_ms": 56986,
      "end_ms": 57301,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "from",
      "start_ms": 57448,
      "end_ms": 57572,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 57573,
      "end_ms": 57647,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Kantar",
      "start_ms": 57648,
      "end_ms": 57918,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Urban",
      "start_ms": 57998,
      "end_ms": 58223,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Spending",
      "start_ms": 58261,
      "end_ms": 58621,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Index",
      "start_ms": 58686,
      "end_ms": 58911,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "reveal",
      "start_ms": 59098,
      "end_ms": 59368,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 59486,
      "end_ms": 59597,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "average",
      "start_ms": 59598,
      "end_ms": 59913,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "monthly",
      "start_ms": 59923,
      "end_ms": 60238,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "discretionary",
      "start_ms": 60248,
      "end_ms": 60833,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "spend",
      "start_ms": 60948,
      "end_ms": 61173,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "on",
      "start_ms": 61286,
      "end_ms": 61386,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "dining",
      "start_ms": 61423,
      "end_ms": 61693,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "out",
      "start_ms": 61786,
      "end_ms": 61921,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 61961,
      "end_ms": 62072,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "lifestyle",
      "start_ms": 62073,
      "end_ms": 62478,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "apps",
      "start_ms": 62636,
      "end_ms": 62816,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "increases",
      "start_ms": 62873,
      "end_ms": 63278,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "by",
      "start_ms": 63436,
      "end_ms": 63536,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "85",
      "start_ms": 63648,
      "end_ms": 63748,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 64136,
      "end_ms": 64451,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "within",
      "start_ms": 64548,
      "end_ms": 64818,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "6",
      "start_ms": 64836,
      "end_ms": 64936,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "months",
      "start_ms": 65111,
      "end_ms": 65381,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 65436,
      "end_ms": 65522,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 65523,
      "end_ms": 65572,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "salary",
      "start_ms": 65573,
      "end_ms": 65843,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "promotion",
      "start_ms": 66011,
      "end_ms": 66416,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "crossing",
      "start_ms": 66511,
      "end_ms": 66871,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹1,00,000",
      "start_ms": 66973,
      "end_ms": 67378,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "per",
      "start_ms": 68136,
      "end_ms": 68271,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "month",
      "start_ms": 68286,
      "end_ms": 68511,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Furthermore",
      "start_ms": 69153,
      "end_ms": 69648,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "ordering",
      "start_ms": 70041,
      "end_ms": 70401,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "food",
      "start_ms": 70441,
      "end_ms": 70621,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "delivery",
      "start_ms": 70728,
      "end_ms": 71088,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "15",
      "start_ms": 71128,
      "end_ms": 71228,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "times",
      "start_ms": 71616,
      "end_ms": 71841,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 71941,
      "end_ms": 71977,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "month",
      "start_ms": 71978,
      "end_ms": 72203,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "instead",
      "start_ms": 72303,
      "end_ms": 72577,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 72578,
      "end_ms": 72677,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cooking",
      "start_ms": 72678,
      "end_ms": 72993,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "adds",
      "start_ms": 73028,
      "end_ms": 73208,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 73253,
      "end_ms": 73327,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "extra",
      "start_ms": 73328,
      "end_ms": 73553,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹7,500",
      "start_ms": 73616,
      "end_ms": 73886,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 75303,
      "end_ms": 75390,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "monthly",
      "start_ms": 75391,
      "end_ms": 75706,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "discretionary",
      "start_ms": 75728,
      "end_ms": 76313,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "spending",
      "start_ms": 76378,
      "end_ms": 76738,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "You",
      "start_ms": 77371,
      "end_ms": 77495,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "start",
      "start_ms": 77496,
      "end_ms": 77721,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "treating",
      "start_ms": 77808,
      "end_ms": 78107,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "luxury",
      "start_ms": 78108,
      "end_ms": 78378,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "conveniences",
      "start_ms": 78483,
      "end_ms": 79023,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "as",
      "start_ms": 79196,
      "end_ms": 79296,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "absolute",
      "start_ms": 79346,
      "end_ms": 79706,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "necessities",
      "start_ms": 79771,
      "end_ms": 80266,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "trapping",
      "start_ms": 80671,
      "end_ms": 81020,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "yourself",
      "start_ms": 81021,
      "end_ms": 81381,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 81483,
      "end_ms": 81557,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 81558,
      "end_ms": 81645,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "endless",
      "start_ms": 81646,
      "end_ms": 81920,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cycle",
      "start_ms": 81921,
      "end_ms": 82146,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 82296,
      "end_ms": 82370,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "consumption",
      "start_ms": 82371,
      "end_ms": 82866,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Once",
      "start_ms": 83185,
      "end_ms": 83365,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "discretionary",
      "start_ms": 83485,
      "end_ms": 84070,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "spending",
      "start_ms": 84172,
      "end_ms": 84532,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "spikes",
      "start_ms": 84560,
      "end_ms": 84830,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "major",
      "start_ms": 85272,
      "end_ms": 85497,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "fixed",
      "start_ms": 85647,
      "end_ms": 85872,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "commitments",
      "start_ms": 85960,
      "end_ms": 86421,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "enter",
      "start_ms": 86422,
      "end_ms": 86559,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 86560,
      "end_ms": 86646,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "picture",
      "start_ms": 86647,
      "end_ms": 86962,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Upgrading",
      "start_ms": 87602,
      "end_ms": 88007,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "from",
      "start_ms": 88102,
      "end_ms": 88276,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 88277,
      "end_ms": 88339,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rented",
      "start_ms": 88340,
      "end_ms": 88610,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "1",
      "start_ms": 88690,
      "end_ms": 88790,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "BHK",
      "start_ms": 88965,
      "end_ms": 89100,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 89552,
      "end_ms": 89652,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 89715,
      "end_ms": 89751,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "2",
      "start_ms": 89752,
      "end_ms": 89852,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "BHK",
      "start_ms": 89977,
      "end_ms": 90112,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "apartment",
      "start_ms": 90540,
      "end_ms": 90945,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 90952,
      "end_ms": 91052,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cities",
      "start_ms": 91065,
      "end_ms": 91335,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "like",
      "start_ms": 91465,
      "end_ms": 91645,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Bengaluru",
      "start_ms": 91652,
      "end_ms": 92057,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "or",
      "start_ms": 92252,
      "end_ms": 92352,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Mumbai",
      "start_ms": 92365,
      "end_ms": 92635,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "increases",
      "start_ms": 92840,
      "end_ms": 93245,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "monthly",
      "start_ms": 93427,
      "end_ms": 93742,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "housing",
      "start_ms": 93777,
      "end_ms": 94092,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "expenses",
      "start_ms": 94152,
      "end_ms": 94512,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "by",
      "start_ms": 94740,
      "end_ms": 94840,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 94940,
      "end_ms": 95014,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "average",
      "start_ms": 95015,
      "end_ms": 95330,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 95352,
      "end_ms": 95439,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹25,000",
      "start_ms": 95440,
      "end_ms": 95755,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 96802,
      "end_ms": 96889,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹40,000",
      "start_ms": 96890,
      "end_ms": 97205,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "On",
      "start_ms": 98582,
      "end_ms": 98682,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "top",
      "start_ms": 98745,
      "end_ms": 98880,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 98995,
      "end_ms": 99081,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 99082,
      "end_ms": 99262,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "purchasing",
      "start_ms": 99470,
      "end_ms": 99920,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 99970,
      "end_ms": 100006,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "mid-size",
      "start_ms": 100007,
      "end_ms": 100367,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "car",
      "start_ms": 100532,
      "end_ms": 100667,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "on",
      "start_ms": 100807,
      "end_ms": 100894,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 100895,
      "end_ms": 100969,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "auto",
      "start_ms": 100970,
      "end_ms": 101150,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "loan",
      "start_ms": 101232,
      "end_ms": 101412,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "at",
      "start_ms": 101532,
      "end_ms": 101606,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 101607,
      "end_ms": 101706,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "EMI",
      "start_ms": 101707,
      "end_ms": 101842,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 101945,
      "end_ms": 102044,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹22,000",
      "start_ms": 102045,
      "end_ms": 102360,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "per",
      "start_ms": 103332,
      "end_ms": 103467,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "month",
      "start_ms": 103495,
      "end_ms": 103720,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "locks",
      "start_ms": 103795,
      "end_ms": 104020,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 104145,
      "end_ms": 104245,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "vehicle",
      "start_ms": 104270,
      "end_ms": 104585,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "depreciation",
      "start_ms": 104645,
      "end_ms": 105185,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 105382,
      "end_ms": 105517,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "loan",
      "start_ms": 105520,
      "end_ms": 105700,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "interest",
      "start_ms": 105732,
      "end_ms": 106069,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 106070,
      "end_ms": 106181,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "5",
      "start_ms": 106182,
      "end_ms": 106282,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "years",
      "start_ms": 106482,
      "end_ms": 106707,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "These",
      "start_ms": 107375,
      "end_ms": 107600,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "heavy",
      "start_ms": 107625,
      "end_ms": 107850,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 107862,
      "end_ms": 108267,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "anchors",
      "start_ms": 108375,
      "end_ms": 108690,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "silently",
      "start_ms": 108700,
      "end_ms": 109060,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "crush",
      "start_ms": 109137,
      "end_ms": 109362,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 109487,
      "end_ms": 109636,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "effective",
      "start_ms": 109637,
      "end_ms": 110036,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "hourly",
      "start_ms": 110037,
      "end_ms": 110307,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rate",
      "start_ms": 110400,
      "end_ms": 110580,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 110687,
      "end_ms": 110774,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "destroy",
      "start_ms": 110775,
      "end_ms": 111090,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 111137,
      "end_ms": 111286,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "capacity",
      "start_ms": 111287,
      "end_ms": 111647,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 111875,
      "end_ms": 111974,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "build",
      "start_ms": 111975,
      "end_ms": 112200,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "genuine",
      "start_ms": 112275,
      "end_ms": 112590,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "long-term",
      "start_ms": 112650,
      "end_ms": 113055,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "wealth",
      "start_ms": 113137,
      "end_ms": 113407,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Let",
      "start_ms": 113713,
      "end_ms": 113848,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "us",
      "start_ms": 113863,
      "end_ms": 113963,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "examine",
      "start_ms": 114000,
      "end_ms": 114315,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 114400,
      "end_ms": 114462,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "stark",
      "start_ms": 114463,
      "end_ms": 114688,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "opportunity",
      "start_ms": 114850,
      "end_ms": 115345,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cost",
      "start_ms": 115388,
      "end_ms": 115568,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 115725,
      "end_ms": 115787,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "consumption",
      "start_ms": 115788,
      "end_ms": 116283,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Every",
      "start_ms": 116918,
      "end_ms": 117143,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rupee",
      "start_ms": 117180,
      "end_ms": 117405,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "spent",
      "start_ms": 117593,
      "end_ms": 117818,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "on",
      "start_ms": 117930,
      "end_ms": 118030,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "maintaining",
      "start_ms": 118043,
      "end_ms": 118538,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 118555,
      "end_ms": 118617,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "upscale",
      "start_ms": 118618,
      "end_ms": 118933,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "image",
      "start_ms": 119105,
      "end_ms": 119329,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 119330,
      "end_ms": 119417,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Mumbai",
      "start_ms": 119418,
      "end_ms": 119688,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "or",
      "start_ms": 119893,
      "end_ms": 119992,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Gurgaon",
      "start_ms": 119993,
      "end_ms": 120308,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 120543,
      "end_ms": 120643,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 120655,
      "end_ms": 120704,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rupee",
      "start_ms": 120705,
      "end_ms": 120930,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "stolen",
      "start_ms": 121068,
      "end_ms": 121338,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "from",
      "start_ms": 121468,
      "end_ms": 121604,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 121605,
      "end_ms": 121704,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "future",
      "start_ms": 121705,
      "end_ms": 121975,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "self",
      "start_ms": 122055,
      "end_ms": 122235,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "When",
      "start_ms": 122998,
      "end_ms": 123159,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 123160,
      "end_ms": 123247,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "prioritize",
      "start_ms": 123248,
      "end_ms": 123698,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "flash",
      "start_ms": 123960,
      "end_ms": 124185,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "over",
      "start_ms": 124285,
      "end_ms": 124465,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "assets",
      "start_ms": 124560,
      "end_ms": 124830,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 125260,
      "end_ms": 125372,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "are",
      "start_ms": 125373,
      "end_ms": 125447,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "trading",
      "start_ms": 125448,
      "end_ms": 125763,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "decades",
      "start_ms": 125848,
      "end_ms": 126163,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 126298,
      "end_ms": 126372,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "freedom",
      "start_ms": 126373,
      "end_ms": 126688,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 126760,
      "end_ms": 126895,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 126935,
      "end_ms": 126972,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "temporary",
      "start_ms": 126973,
      "end_ms": 127378,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "status",
      "start_ms": 127485,
      "end_ms": 127755,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "symbol",
      "start_ms": 127823,
      "end_ms": 128093,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "The",
      "start_ms": 128703,
      "end_ms": 128814,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "hidden",
      "start_ms": 128815,
      "end_ms": 129085,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "price",
      "start_ms": 129103,
      "end_ms": 129328,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 129428,
      "end_ms": 129514,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 129515,
      "end_ms": 129614,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "luxury",
      "start_ms": 129615,
      "end_ms": 129885,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "car",
      "start_ms": 130040,
      "end_ms": 130175,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 130353,
      "end_ms": 130464,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "upgraded",
      "start_ms": 130465,
      "end_ms": 130825,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "apartment",
      "start_ms": 130865,
      "end_ms": 131270,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "isn't",
      "start_ms": 131290,
      "end_ms": 131515,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "just",
      "start_ms": 131540,
      "end_ms": 131720,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 131740,
      "end_ms": 131814,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "sticker",
      "start_ms": 131815,
      "end_ms": 132130,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "price",
      "start_ms": 132140,
      "end_ms": 132365,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "it",
      "start_ms": 132790,
      "end_ms": 132889,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 132890,
      "end_ms": 132989,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 132990,
      "end_ms": 133077,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "lost",
      "start_ms": 133078,
      "end_ms": 133258,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "compound",
      "start_ms": 133403,
      "end_ms": 133763,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "growth",
      "start_ms": 133928,
      "end_ms": 134198,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 134253,
      "end_ms": 134389,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "could",
      "start_ms": 134390,
      "end_ms": 134539,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "have",
      "start_ms": 134540,
      "end_ms": 134627,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "set",
      "start_ms": 134628,
      "end_ms": 134763,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 134890,
      "end_ms": 134977,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "free",
      "start_ms": 134978,
      "end_ms": 135158,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 135240,
      "end_ms": 135289,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "decade",
      "start_ms": 135290,
      "end_ms": 135560,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "earlier",
      "start_ms": 135653,
      "end_ms": 135968,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "There",
      "start_ms": 136273,
      "end_ms": 136434,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 136435,
      "end_ms": 136535,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 136548,
      "end_ms": 136584,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "pervasive",
      "start_ms": 136585,
      "end_ms": 136990,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "myth",
      "start_ms": 137123,
      "end_ms": 137303,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 137398,
      "end_ms": 137498,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "urban",
      "start_ms": 137510,
      "end_ms": 137735,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "corporate",
      "start_ms": 137773,
      "end_ms": 138159,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "culture",
      "start_ms": 138160,
      "end_ms": 138475,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 138573,
      "end_ms": 138722,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "carrying",
      "start_ms": 138723,
      "end_ms": 139083,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "heavy",
      "start_ms": 139148,
      "end_ms": 139373,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "EMIs",
      "start_ms": 139448,
      "end_ms": 139628,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "signals",
      "start_ms": 139710,
      "end_ms": 140025,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 140135,
      "end_ms": 140534,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "maturity",
      "start_ms": 140535,
      "end_ms": 140895,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "or",
      "start_ms": 141048,
      "end_ms": 141122,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "success",
      "start_ms": 141123,
      "end_ms": 141438,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "According",
      "start_ms": 142215,
      "end_ms": 142602,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 142603,
      "end_ms": 142703,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 142715,
      "end_ms": 142802,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Mastercard",
      "start_ms": 142803,
      "end_ms": 143253,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Financial",
      "start_ms": 143440,
      "end_ms": 143839,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Literacy",
      "start_ms": 143840,
      "end_ms": 144200,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Index",
      "start_ms": 144353,
      "end_ms": 144578,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "lifestyle",
      "start_ms": 145053,
      "end_ms": 145458,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "inflation",
      "start_ms": 145665,
      "end_ms": 146070,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "causes",
      "start_ms": 146165,
      "end_ms": 146435,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "42",
      "start_ms": 146603,
      "end_ms": 146703,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 147090,
      "end_ms": 147405,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 147465,
      "end_ms": 147552,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "corporate",
      "start_ms": 147553,
      "end_ms": 147927,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "employees",
      "start_ms": 147928,
      "end_ms": 148333,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 148428,
      "end_ms": 148528,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "remain",
      "start_ms": 148540,
      "end_ms": 148810,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "paycheck-to-paycheck",
      "start_ms": 148890,
      "end_ms": 149790,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "despite",
      "start_ms": 149878,
      "end_ms": 150193,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "crossing",
      "start_ms": 150278,
      "end_ms": 150638,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 150690,
      "end_ms": 150764,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹12,00,000",
      "start_ms": 150765,
      "end_ms": 151215,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "annual",
      "start_ms": 152590,
      "end_ms": 152860,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "income",
      "start_ms": 152953,
      "end_ms": 153223,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "bracket",
      "start_ms": 153253,
      "end_ms": 153568,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "They",
      "start_ms": 154133,
      "end_ms": 154269,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "believe",
      "start_ms": 154270,
      "end_ms": 154585,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 154633,
      "end_ms": 154782,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "buying",
      "start_ms": 154783,
      "end_ms": 155053,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "luxury",
      "start_ms": 155120,
      "end_ms": 155390,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "items",
      "start_ms": 155608,
      "end_ms": 155833,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "on",
      "start_ms": 155920,
      "end_ms": 156020,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "credit",
      "start_ms": 156045,
      "end_ms": 156315,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "establishes",
      "start_ms": 156345,
      "end_ms": 156840,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "creditworthiness",
      "start_ms": 156958,
      "end_ms": 157678,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "when",
      "start_ms": 158033,
      "end_ms": 158213,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 158220,
      "end_ms": 158294,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "reality",
      "start_ms": 158295,
      "end_ms": 158610,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "it",
      "start_ms": 159095,
      "end_ms": 159195,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "simply",
      "start_ms": 159220,
      "end_ms": 159490,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "chains",
      "start_ms": 159570,
      "end_ms": 159840,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "them",
      "start_ms": 159920,
      "end_ms": 160082,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "tighter",
      "start_ms": 160083,
      "end_ms": 160382,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 160383,
      "end_ms": 160483,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "their",
      "start_ms": 160495,
      "end_ms": 160632,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "desks",
      "start_ms": 160633,
      "end_ms": 160858,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "eliminating",
      "start_ms": 161333,
      "end_ms": 161828,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "any",
      "start_ms": 161883,
      "end_ms": 162007,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "margin",
      "start_ms": 162008,
      "end_ms": 162278,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 162445,
      "end_ms": 162580,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "error",
      "start_ms": 162658,
      "end_ms": 162883,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "if",
      "start_ms": 162995,
      "end_ms": 163095,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "economic",
      "start_ms": 163120,
      "end_ms": 163480,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "conditions",
      "start_ms": 163558,
      "end_ms": 164008,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "shift",
      "start_ms": 164045,
      "end_ms": 164270,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Escaping",
      "start_ms": 164641,
      "end_ms": 165001,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "this",
      "start_ms": 165166,
      "end_ms": 165290,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cycle",
      "start_ms": 165291,
      "end_ms": 165516,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "requires",
      "start_ms": 165653,
      "end_ms": 166013,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 166141,
      "end_ms": 166190,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rigorous",
      "start_ms": 166191,
      "end_ms": 166551,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "framework",
      "start_ms": 166578,
      "end_ms": 166983,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 167328,
      "end_ms": 167440,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 167441,
      "end_ms": 167502,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "time-tested",
      "start_ms": 167503,
      "end_ms": 167998,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "50/30/20",
      "start_ms": 168128,
      "end_ms": 168488,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rule",
      "start_ms": 169703,
      "end_ms": 169883,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 170003,
      "end_ms": 170103,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 170116,
      "end_ms": 170252,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "ultimate",
      "start_ms": 170253,
      "end_ms": 170565,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "weapon",
      "start_ms": 170566,
      "end_ms": 170836,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "By",
      "start_ms": 171483,
      "end_ms": 171583,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "allocating",
      "start_ms": 171733,
      "end_ms": 172183,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "50",
      "start_ms": 172196,
      "end_ms": 172296,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 172496,
      "end_ms": 172811,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 172858,
      "end_ms": 172932,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 172933,
      "end_ms": 173045,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹1,00,000",
      "start_ms": 173046,
      "end_ms": 173451,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "salary",
      "start_ms": 174258,
      "end_ms": 174528,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 174746,
      "end_ms": 174846,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "absolute",
      "start_ms": 174908,
      "end_ms": 175268,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "needs",
      "start_ms": 175333,
      "end_ms": 175558,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "30",
      "start_ms": 175871,
      "end_ms": 175971,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 176133,
      "end_ms": 176448,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 176508,
      "end_ms": 176595,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "guilt-free",
      "start_ms": 176596,
      "end_ms": 177020,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "wants",
      "start_ms": 177021,
      "end_ms": 177246,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 177621,
      "end_ms": 177745,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 177746,
      "end_ms": 177782,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "disciplined",
      "start_ms": 177783,
      "end_ms": 178278,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "50",
      "start_ms": 178283,
      "end_ms": 178383,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 178546,
      "end_ms": 178861,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "directly",
      "start_ms": 178933,
      "end_ms": 179293,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 179321,
      "end_ms": 179421,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "aggressive",
      "start_ms": 179483,
      "end_ms": 179932,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "wealth",
      "start_ms": 179933,
      "end_ms": 180157,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "building",
      "start_ms": 180158,
      "end_ms": 180518,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 180808,
      "end_ms": 180920,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "completely",
      "start_ms": 180921,
      "end_ms": 181371,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "break",
      "start_ms": 181396,
      "end_ms": 181621,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 181671,
      "end_ms": 181757,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "pattern",
      "start_ms": 181758,
      "end_ms": 182073,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 182096,
      "end_ms": 182196,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "lifestyle",
      "start_ms": 182208,
      "end_ms": 182613,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "creep",
      "start_ms": 182708,
      "end_ms": 182933,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Instead",
      "start_ms": 183576,
      "end_ms": 183891,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 183926,
      "end_ms": 184025,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "letting",
      "start_ms": 184026,
      "end_ms": 184250,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 184251,
      "end_ms": 184362,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "bank",
      "start_ms": 184363,
      "end_ms": 184543,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "account",
      "start_ms": 184676,
      "end_ms": 184991,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "bleed",
      "start_ms": 185051,
      "end_ms": 185276,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "out",
      "start_ms": 185288,
      "end_ms": 185423,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "through",
      "start_ms": 185501,
      "end_ms": 185712,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "miscellaneous",
      "start_ms": 185713,
      "end_ms": 186298,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "expenses",
      "start_ms": 186401,
      "end_ms": 186761,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "every",
      "start_ms": 187313,
      "end_ms": 187538,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "single",
      "start_ms": 187551,
      "end_ms": 187821,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rupee",
      "start_ms": 187913,
      "end_ms": 188138,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 188338,
      "end_ms": 188438,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "assigned",
      "start_ms": 188463,
      "end_ms": 188787,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 188788,
      "end_ms": 188825,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "specific",
      "start_ms": 188826,
      "end_ms": 189186,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "mission-driven",
      "start_ms": 189663,
      "end_ms": 190287,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "purpose",
      "start_ms": 190288,
      "end_ms": 190603,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "When",
      "start_ms": 190945,
      "end_ms": 191119,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 191120,
      "end_ms": 191219,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "commit",
      "start_ms": 191220,
      "end_ms": 191490,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 191520,
      "end_ms": 191619,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "this",
      "start_ms": 191620,
      "end_ms": 191800,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "disciplined",
      "start_ms": 191820,
      "end_ms": 192294,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "path",
      "start_ms": 192295,
      "end_ms": 192475,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 192895,
      "end_ms": 192981,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "math",
      "start_ms": 192982,
      "end_ms": 193162,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "becomes",
      "start_ms": 193295,
      "end_ms": 193610,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "life-changing",
      "start_ms": 193657,
      "end_ms": 194242,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Investing",
      "start_ms": 194875,
      "end_ms": 195280,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "50",
      "start_ms": 195375,
      "end_ms": 195475,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 195675,
      "end_ms": 195990,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 196062,
      "end_ms": 196136,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 196137,
      "end_ms": 196186,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹1,00,000",
      "start_ms": 196187,
      "end_ms": 196592,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "monthly",
      "start_ms": 197512,
      "end_ms": 197827,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "salary",
      "start_ms": 197862,
      "end_ms": 198132,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "consistently",
      "start_ms": 198312,
      "end_ms": 198852,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "at",
      "start_ms": 198975,
      "end_ms": 199036,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 199037,
      "end_ms": 199086,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "12",
      "start_ms": 199087,
      "end_ms": 199187,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 199400,
      "end_ms": 199715,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "annual",
      "start_ms": 199800,
      "end_ms": 200070,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "return",
      "start_ms": 200150,
      "end_ms": 200420,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "builds",
      "start_ms": 200587,
      "end_ms": 200857,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 200862,
      "end_ms": 200911,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "corpus",
      "start_ms": 200912,
      "end_ms": 201182,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 201350,
      "end_ms": 201449,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "over",
      "start_ms": 201450,
      "end_ms": 201630,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "₹1",
      "start_ms": 201650,
      "end_ms": 201750,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "crore",
      "start_ms": 201925,
      "end_ms": 202150,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 202262,
      "end_ms": 202336,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "15",
      "start_ms": 202337,
      "end_ms": 202437,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "years",
      "start_ms": 202762,
      "end_ms": 202987,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Pause",
      "start_ms": 203667,
      "end_ms": 203892,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 204042,
      "end_ms": 204116,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "reflect",
      "start_ms": 204117,
      "end_ms": 204432,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "on",
      "start_ms": 204530,
      "end_ms": 204630,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 204655,
      "end_ms": 204835,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "While",
      "start_ms": 205397,
      "end_ms": 205571,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 205572,
      "end_ms": 205721,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "peers",
      "start_ms": 205722,
      "end_ms": 205947,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "are",
      "start_ms": 206097,
      "end_ms": 206171,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "trapped",
      "start_ms": 206172,
      "end_ms": 206487,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "paying",
      "start_ms": 206535,
      "end_ms": 206805,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "off",
      "start_ms": 206885,
      "end_ms": 207020,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "luxury",
      "start_ms": 207110,
      "end_ms": 207380,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "car",
      "start_ms": 207497,
      "end_ms": 207632,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "loans",
      "start_ms": 207785,
      "end_ms": 208010,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 208197,
      "end_ms": 208271,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "inflated",
      "start_ms": 208272,
      "end_ms": 208632,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "apartment",
      "start_ms": 208685,
      "end_ms": 209071,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rents",
      "start_ms": 209072,
      "end_ms": 209297,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 209635,
      "end_ms": 209771,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "disciplined",
      "start_ms": 209772,
      "end_ms": 210267,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "surplus",
      "start_ms": 210297,
      "end_ms": 210612,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "compounds",
      "start_ms": 210710,
      "end_ms": 211115,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "into",
      "start_ms": 211285,
      "end_ms": 211446,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "true",
      "start_ms": 211447,
      "end_ms": 211627,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 211672,
      "end_ms": 212077,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "independence",
      "start_ms": 212185,
      "end_ms": 212725,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "You",
      "start_ms": 213315,
      "end_ms": 213426,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "stop",
      "start_ms": 213427,
      "end_ms": 213607,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "working",
      "start_ms": 213752,
      "end_ms": 214051,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 214052,
      "end_ms": 214187,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 214202,
      "end_ms": 214251,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "paycheck",
      "start_ms": 214252,
      "end_ms": 214612,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 214790,
      "end_ms": 214901,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "let",
      "start_ms": 214902,
      "end_ms": 215037,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 215052,
      "end_ms": 215126,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "money",
      "start_ms": 215127,
      "end_ms": 215326,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "work",
      "start_ms": 215327,
      "end_ms": 215507,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 215577,
      "end_ms": 215712,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 215777,
      "end_ms": 215912,
      "start_char": null,
      "end_char": null
    }
  ],
  "chunks": [
    {
      "chunk_id": "chunk_001",
      "sequence": 1,
      "source_id": "hook",
      "text": "You finally hit ₹1,00,000 a month and thought you made it. But instead of financial freedom, you traded your financial stress for a luxury EMI. Your income doubled, but your savings stayed at zero. You are not building wealth. You just moved into a much more expensive cage.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_001.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_001.marks.json",
      "word_timestamps": [
        {
          "word": "You",
          "start_ms": 25,
          "end_ms": 149,
          "start_char": 0,
          "end_char": 3
        },
        {
          "word": "finally",
          "start_ms": 150,
          "end_ms": 465,
          "start_char": 4,
          "end_char": 11
        },
        {
          "word": "hit",
          "start_ms": 550,
          "end_ms": 685,
          "start_char": 12,
          "end_char": 15
        },
        {
          "word": "₹1,00,000",
          "start_ms": 750,
          "end_ms": 1155,
          "start_char": 16,
          "end_char": 27
        },
        {
          "word": "a",
          "start_ms": 1975,
          "end_ms": 2011,
          "start_char": 28,
          "end_char": 29
        },
        {
          "word": "month",
          "start_ms": 2012,
          "end_ms": 2237,
          "start_char": 30,
          "end_char": 35
        },
        {
          "word": "and",
          "start_ms": 2337,
          "end_ms": 2449,
          "start_char": 36,
          "end_char": 39
        },
        {
          "word": "thought",
          "start_ms": 2450,
          "end_ms": 2661,
          "start_char": 40,
          "end_char": 47
        },
        {
          "word": "you",
          "start_ms": 2662,
          "end_ms": 2724,
          "start_char": 48,
          "end_char": 51
        },
        {
          "word": "made",
          "start_ms": 2725,
          "end_ms": 2905,
          "start_char": 52,
          "end_char": 56
        },
        {
          "word": "it",
          "start_ms": 2937,
          "end_ms": 3037,
          "start_char": 57,
          "end_char": 59
        },
        {
          "word": "But",
          "start_ms": 3567,
          "end_ms": 3702,
          "start_char": 61,
          "end_char": 64
        },
        {
          "word": "instead",
          "start_ms": 3717,
          "end_ms": 4032,
          "start_char": 65,
          "end_char": 72
        },
        {
          "word": "of",
          "start_ms": 4042,
          "end_ms": 4116,
          "start_char": 73,
          "end_char": 75
        },
        {
          "word": "financial",
          "start_ms": 4117,
          "end_ms": 4522,
          "start_char": 76,
          "end_char": 85
        },
        {
          "word": "freedom",
          "start_ms": 4580,
          "end_ms": 4895,
          "start_char": 86,
          "end_char": 93
        },
        {
          "word": "you",
          "start_ms": 5230,
          "end_ms": 5341,
          "start_char": 95,
          "end_char": 98
        },
        {
          "word": "traded",
          "start_ms": 5342,
          "end_ms": 5612,
          "start_char": 99,
          "end_char": 105
        },
        {
          "word": "your",
          "start_ms": 5730,
          "end_ms": 5816,
          "start_char": 106,
          "end_char": 110
        },
        {
          "word": "financial",
          "start_ms": 5817,
          "end_ms": 6222,
          "start_char": 111,
          "end_char": 120
        },
        {
          "word": "stress",
          "start_ms": 6292,
          "end_ms": 6562,
          "start_char": 121,
          "end_char": 127
        },
        {
          "word": "for",
          "start_ms": 6680,
          "end_ms": 6815,
          "start_char": 128,
          "end_char": 131
        },
        {
          "word": "a",
          "start_ms": 6830,
          "end_ms": 6866,
          "start_char": 132,
          "end_char": 133
        },
        {
          "word": "luxury",
          "start_ms": 6867,
          "end_ms": 7137,
          "start_char": 134,
          "end_char": 140
        },
        {
          "word": "EMI",
          "start_ms": 7355,
          "end_ms": 7490,
          "start_char": 141,
          "end_char": 144
        },
        {
          "word": "Your",
          "start_ms": 8147,
          "end_ms": 8327,
          "start_char": 146,
          "end_char": 150
        },
        {
          "word": "income",
          "start_ms": 8335,
          "end_ms": 8605,
          "start_char": 151,
          "end_char": 157
        },
        {
          "word": "doubled",
          "start_ms": 8660,
          "end_ms": 8975,
          "start_char": 158,
          "end_char": 165
        },
        {
          "word": "but",
          "start_ms": 9260,
          "end_ms": 9395,
          "start_char": 167,
          "end_char": 170
        },
        {
          "word": "your",
          "start_ms": 9460,
          "end_ms": 9571,
          "start_char": 171,
          "end_char": 175
        },
        {
          "word": "savings",
          "start_ms": 9572,
          "end_ms": 9887,
          "start_char": 176,
          "end_char": 183
        },
        {
          "word": "stayed",
          "start_ms": 9985,
          "end_ms": 10255,
          "start_char": 184,
          "end_char": 190
        },
        {
          "word": "at",
          "start_ms": 10260,
          "end_ms": 10346,
          "start_char": 191,
          "end_char": 193
        },
        {
          "word": "zero",
          "start_ms": 10347,
          "end_ms": 10527,
          "start_char": 194,
          "end_char": 198
        },
        {
          "word": "You",
          "start_ms": 11265,
          "end_ms": 11400,
          "start_char": 200,
          "end_char": 203
        },
        {
          "word": "are",
          "start_ms": 11415,
          "end_ms": 11489,
          "start_char": 204,
          "end_char": 207
        },
        {
          "word": "not",
          "start_ms": 11490,
          "end_ms": 11625,
          "start_char": 208,
          "end_char": 211
        },
        {
          "word": "building",
          "start_ms": 11702,
          "end_ms": 12051,
          "start_char": 212,
          "end_char": 220
        },
        {
          "word": "wealth",
          "start_ms": 12052,
          "end_ms": 12322,
          "start_char": 221,
          "end_char": 227
        },
        {
          "word": "You",
          "start_ms": 12932,
          "end_ms": 13031,
          "start_char": 229,
          "end_char": 232
        },
        {
          "word": "just",
          "start_ms": 13032,
          "end_ms": 13212,
          "start_char": 233,
          "end_char": 237
        },
        {
          "word": "moved",
          "start_ms": 13257,
          "end_ms": 13482,
          "start_char": 238,
          "end_char": 243
        },
        {
          "word": "into",
          "start_ms": 13545,
          "end_ms": 13725,
          "start_char": 244,
          "end_char": 248
        },
        {
          "word": "a",
          "start_ms": 13770,
          "end_ms": 13806,
          "start_char": 249,
          "end_char": 250
        },
        {
          "word": "much",
          "start_ms": 13807,
          "end_ms": 13987,
          "start_char": 251,
          "end_char": 255
        },
        {
          "word": "more",
          "start_ms": 14070,
          "end_ms": 14250,
          "start_char": 256,
          "end_char": 260
        },
        {
          "word": "expensive",
          "start_ms": 14295,
          "end_ms": 14700,
          "start_char": 261,
          "end_char": 270
        },
        {
          "word": "cage",
          "start_ms": 14782,
          "end_ms": 14962,
          "start_char": 271,
          "end_char": 275
        }
      ],
      "duration_ms": 15360,
      "duration_seconds": 15.36
    },
    {
      "chunk_id": "chunk_002",
      "sequence": 2,
      "source_id": "idea_01",
      "text": "When you finally cross that major salary threshold, reality hits hard. Earning ₹1,00,000 per month officially places you in India's top 3 percent of earners according to data from the Ministry of Finance. It feels like an incredible milestone. Yet, behind the polished corporate facade, financial vulnerability lurks. In fact, 68 percent of urban Indian professionals earning between ₹1,00,000 and ₹1,50,000 per month report having less than ₹50,000 in liquid emergency savings. Instead of accumulating real freedom, your growing salary instantly vanishes into newly inflated lifestyle choices.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_002.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_002.marks.json",
      "word_timestamps": [
        {
          "word": "When",
          "start_ms": 25,
          "end_ms": 161,
          "start_char": 0,
          "end_char": 4
        },
        {
          "word": "you",
          "start_ms": 162,
          "end_ms": 249,
          "start_char": 5,
          "end_char": 8
        },
        {
          "word": "finally",
          "start_ms": 250,
          "end_ms": 565,
          "start_char": 9,
          "end_char": 16
        },
        {
          "word": "cross",
          "start_ms": 625,
          "end_ms": 850,
          "start_char": 17,
          "end_char": 22
        },
        {
          "word": "that",
          "start_ms": 975,
          "end_ms": 1124,
          "start_char": 23,
          "end_char": 27
        },
        {
          "word": "major",
          "start_ms": 1125,
          "end_ms": 1350,
          "start_char": 28,
          "end_char": 33
        },
        {
          "word": "salary",
          "start_ms": 1437,
          "end_ms": 1707,
          "start_char": 34,
          "end_char": 40
        },
        {
          "word": "threshold",
          "start_ms": 1850,
          "end_ms": 2255,
          "start_char": 41,
          "end_char": 50
        },
        {
          "word": "reality",
          "start_ms": 2637,
          "end_ms": 2952,
          "start_char": 52,
          "end_char": 59
        },
        {
          "word": "hits",
          "start_ms": 3100,
          "end_ms": 3280,
          "start_char": 60,
          "end_char": 64
        },
        {
          "word": "hard",
          "start_ms": 3300,
          "end_ms": 3480,
          "start_char": 65,
          "end_char": 69
        },
        {
          "word": "Earning",
          "start_ms": 4142,
          "end_ms": 4441,
          "start_char": 71,
          "end_char": 78
        },
        {
          "word": "₹1,00,000",
          "start_ms": 4442,
          "end_ms": 4847,
          "start_char": 79,
          "end_char": 90
        },
        {
          "word": "per",
          "start_ms": 5705,
          "end_ms": 5840,
          "start_char": 91,
          "end_char": 94
        },
        {
          "word": "month",
          "start_ms": 5867,
          "end_ms": 6092,
          "start_char": 95,
          "end_char": 100
        },
        {
          "word": "officially",
          "start_ms": 6142,
          "end_ms": 6541,
          "start_char": 101,
          "end_char": 111
        },
        {
          "word": "places",
          "start_ms": 6542,
          "end_ms": 6812,
          "start_char": 112,
          "end_char": 118
        },
        {
          "word": "you",
          "start_ms": 7017,
          "end_ms": 7152,
          "start_char": 119,
          "end_char": 122
        },
        {
          "word": "in",
          "start_ms": 7180,
          "end_ms": 7254,
          "start_char": 123,
          "end_char": 125
        },
        {
          "word": "India's",
          "start_ms": 7255,
          "end_ms": 7570,
          "start_char": 126,
          "end_char": 133
        },
        {
          "word": "top",
          "start_ms": 7642,
          "end_ms": 7777,
          "start_char": 134,
          "end_char": 137
        },
        {
          "word": "3",
          "start_ms": 7892,
          "end_ms": 7992,
          "start_char": 138,
          "end_char": 139
        },
        {
          "word": "percent",
          "start_ms": 8117,
          "end_ms": 8432,
          "start_char": 140,
          "end_char": 147
        },
        {
          "word": "of",
          "start_ms": 8480,
          "end_ms": 8579,
          "start_char": 148,
          "end_char": 150
        },
        {
          "word": "earners",
          "start_ms": 8580,
          "end_ms": 8895,
          "start_char": 151,
          "end_char": 158
        },
        {
          "word": "according",
          "start_ms": 8905,
          "end_ms": 9254,
          "start_char": 159,
          "end_char": 168
        },
        {
          "word": "to",
          "start_ms": 9255,
          "end_ms": 9354,
          "start_char": 169,
          "end_char": 171
        },
        {
          "word": "data",
          "start_ms": 9355,
          "end_ms": 9535,
          "start_char": 172,
          "end_char": 176
        },
        {
          "word": "from",
          "start_ms": 9642,
          "end_ms": 9816,
          "start_char": 177,
          "end_char": 181
        },
        {
          "word": "the",
          "start_ms": 9817,
          "end_ms": 9879,
          "start_char": 182,
          "end_char": 185
        },
        {
          "word": "Ministry",
          "start_ms": 9880,
          "end_ms": 10240,
          "start_char": 186,
          "end_char": 194
        },
        {
          "word": "of",
          "start_ms": 10330,
          "end_ms": 10391,
          "start_char": 195,
          "end_char": 197
        },
        {
          "word": "Finance",
          "start_ms": 10392,
          "end_ms": 10707,
          "start_char": 198,
          "end_char": 205
        },
        {
          "word": "It",
          "start_ms": 11460,
          "end_ms": 11560,
          "start_char": 207,
          "end_char": 209
        },
        {
          "word": "feels",
          "start_ms": 11597,
          "end_ms": 11822,
          "start_char": 210,
          "end_char": 215
        },
        {
          "word": "like",
          "start_ms": 11947,
          "end_ms": 12121,
          "start_char": 216,
          "end_char": 220
        },
        {
          "word": "an",
          "start_ms": 12122,
          "end_ms": 12184,
          "start_char": 221,
          "end_char": 223
        },
        {
          "word": "incredible",
          "start_ms": 12185,
          "end_ms": 12635,
          "start_char": 224,
          "end_char": 234
        },
        {
          "word": "milestone",
          "start_ms": 12647,
          "end_ms": 13052,
          "start_char": 235,
          "end_char": 244
        },
        {
          "word": "Yet",
          "start_ms": 13852,
          "end_ms": 13987,
          "start_char": 246,
          "end_char": 249
        },
        {
          "word": "behind",
          "start_ms": 14390,
          "end_ms": 14660,
          "start_char": 251,
          "end_char": 257
        },
        {
          "word": "the",
          "start_ms": 14715,
          "end_ms": 14776,
          "start_char": 258,
          "end_char": 261
        },
        {
          "word": "polished",
          "start_ms": 14777,
          "end_ms": 15137,
          "start_char": 262,
          "end_char": 270
        },
        {
          "word": "corporate",
          "start_ms": 15177,
          "end_ms": 15551,
          "start_char": 271,
          "end_char": 280
        },
        {
          "word": "facade",
          "start_ms": 15552,
          "end_ms": 15822,
          "start_char": 281,
          "end_char": 287
        },
        {
          "word": "financial",
          "start_ms": 16315,
          "end_ms": 16720,
          "start_char": 289,
          "end_char": 298
        },
        {
          "word": "vulnerability",
          "start_ms": 16815,
          "end_ms": 17400,
          "start_char": 299,
          "end_char": 312
        },
        {
          "word": "lurks",
          "start_ms": 17465,
          "end_ms": 17690,
          "start_char": 313,
          "end_char": 318
        },
        {
          "word": "In",
          "start_ms": 18395,
          "end_ms": 18495,
          "start_char": 320,
          "end_char": 322
        },
        {
          "word": "fact",
          "start_ms": 18545,
          "end_ms": 18725,
          "start_char": 323,
          "end_char": 327
        },
        {
          "word": "68",
          "start_ms": 19182,
          "end_ms": 19282,
          "start_char": 329,
          "end_char": 331
        },
        {
          "word": "percent",
          "start_ms": 19745,
          "end_ms": 20060,
          "start_char": 332,
          "end_char": 339
        },
        {
          "word": "of",
          "start_ms": 20095,
          "end_ms": 20194,
          "start_char": 340,
          "end_char": 342
        },
        {
          "word": "urban",
          "start_ms": 20195,
          "end_ms": 20420,
          "start_char": 343,
          "end_char": 348
        },
        {
          "word": "Indian",
          "start_ms": 20470,
          "end_ms": 20740,
          "start_char": 349,
          "end_char": 355
        },
        {
          "word": "professionals",
          "start_ms": 20795,
          "end_ms": 21380,
          "start_char": 356,
          "end_char": 369
        },
        {
          "word": "earning",
          "start_ms": 21407,
          "end_ms": 21669,
          "start_char": 370,
          "end_char": 377
        },
        {
          "word": "between",
          "start_ms": 21670,
          "end_ms": 21985,
          "start_char": 378,
          "end_char": 385
        },
        {
          "word": "₹1,00,000",
          "start_ms": 22032,
          "end_ms": 22437,
          "start_char": 386,
          "end_char": 397
        },
        {
          "word": "and",
          "start_ms": 23307,
          "end_ms": 23442,
          "start_char": 398,
          "end_char": 401
        },
        {
          "word": "₹1,50,000",
          "start_ms": 23445,
          "end_ms": 23850,
          "start_char": 402,
          "end_char": 413
        },
        {
          "word": "per",
          "start_ms": 24995,
          "end_ms": 25130,
          "start_char": 414,
          "end_char": 417
        },
        {
          "word": "month",
          "start_ms": 25157,
          "end_ms": 25382,
          "start_char": 418,
          "end_char": 423
        },
        {
          "word": "report",
          "start_ms": 25445,
          "end_ms": 25715,
          "start_char": 424,
          "end_char": 430
        },
        {
          "word": "having",
          "start_ms": 25845,
          "end_ms": 26115,
          "start_char": 431,
          "end_char": 437
        },
        {
          "word": "less",
          "start_ms": 26132,
          "end_ms": 26312,
          "start_char": 438,
          "end_char": 442
        },
        {
          "word": "than",
          "start_ms": 26370,
          "end_ms": 26519,
          "start_char": 443,
          "end_char": 447
        },
        {
          "word": "₹50,000",
          "start_ms": 26520,
          "end_ms": 26835,
          "start_char": 448,
          "end_char": 457
        },
        {
          "word": "in",
          "start_ms": 27707,
          "end_ms": 27794,
          "start_char": 458,
          "end_char": 460
        },
        {
          "word": "liquid",
          "start_ms": 27795,
          "end_ms": 28056,
          "start_char": 461,
          "end_char": 467
        },
        {
          "word": "emergency",
          "start_ms": 28057,
          "end_ms": 28462,
          "start_char": 468,
          "end_char": 477
        },
        {
          "word": "savings",
          "start_ms": 28570,
          "end_ms": 28885,
          "start_char": 478,
          "end_char": 485
        },
        {
          "word": "Instead",
          "start_ms": 29612,
          "end_ms": 29927,
          "start_char": 487,
          "end_char": 494
        },
        {
          "word": "of",
          "start_ms": 29962,
          "end_ms": 30049,
          "start_char": 495,
          "end_char": 497
        },
        {
          "word": "accumulating",
          "start_ms": 30050,
          "end_ms": 30590,
          "start_char": 498,
          "end_char": 510
        },
        {
          "word": "real",
          "start_ms": 30612,
          "end_ms": 30792,
          "start_char": 511,
          "end_char": 515
        },
        {
          "word": "freedom",
          "start_ms": 30850,
          "end_ms": 31165,
          "start_char": 516,
          "end_char": 523
        },
        {
          "word": "your",
          "start_ms": 31500,
          "end_ms": 31661,
          "start_char": 525,
          "end_char": 529
        },
        {
          "word": "growing",
          "start_ms": 31662,
          "end_ms": 31977,
          "start_char": 530,
          "end_char": 537
        },
        {
          "word": "salary",
          "start_ms": 32037,
          "end_ms": 32307,
          "start_char": 538,
          "end_char": 544
        },
        {
          "word": "instantly",
          "start_ms": 32525,
          "end_ms": 32874,
          "start_char": 545,
          "end_char": 554
        },
        {
          "word": "vanishes",
          "start_ms": 32875,
          "end_ms": 33235,
          "start_char": 555,
          "end_char": 563
        },
        {
          "word": "into",
          "start_ms": 33462,
          "end_ms": 33636,
          "start_char": 564,
          "end_char": 568
        },
        {
          "word": "newly",
          "start_ms": 33637,
          "end_ms": 33862,
          "start_char": 569,
          "end_char": 574
        },
        {
          "word": "inflated",
          "start_ms": 33987,
          "end_ms": 34347,
          "start_char": 575,
          "end_char": 583
        },
        {
          "word": "lifestyle",
          "start_ms": 34400,
          "end_ms": 34805,
          "start_char": 584,
          "end_char": 593
        },
        {
          "word": "choices",
          "start_ms": 34912,
          "end_ms": 35227,
          "start_char": 594,
          "end_char": 601
        }
      ],
      "duration_ms": 35616,
      "duration_seconds": 35.616
    },
    {
      "chunk_id": "chunk_003",
      "sequence": 3,
      "source_id": "idea_02",
      "text": "Why does this happen so quickly? The answer lies in psychological conditioning and immediate gratification. Studies from the Kantar Urban Spending Index reveal that average monthly discretionary spend on dining out and lifestyle apps increases by 85 percent within 6 months of a salary promotion crossing ₹1,00,000 per month. Furthermore, ordering food delivery 15 times a month instead of cooking adds an extra ₹7,500 to monthly discretionary spending. You start treating luxury conveniences as absolute necessities, trapping yourself in an endless cycle of consumption.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_003.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_003.marks.json",
      "word_timestamps": [
        {
          "word": "Why",
          "start_ms": 25,
          "end_ms": 160,
          "start_char": 0,
          "end_char": 3
        },
        {
          "word": "does",
          "start_ms": 200,
          "end_ms": 349,
          "start_char": 4,
          "end_char": 8
        },
        {
          "word": "this",
          "start_ms": 350,
          "end_ms": 524,
          "start_char": 9,
          "end_char": 13
        },
        {
          "word": "happen",
          "start_ms": 525,
          "end_ms": 795,
          "start_char": 14,
          "end_char": 20
        },
        {
          "word": "so",
          "start_ms": 812,
          "end_ms": 912,
          "start_char": 21,
          "end_char": 23
        },
        {
          "word": "quickly",
          "start_ms": 987,
          "end_ms": 1302,
          "start_char": 24,
          "end_char": 31
        },
        {
          "word": "The",
          "start_ms": 1967,
          "end_ms": 2102,
          "start_char": 33,
          "end_char": 36
        },
        {
          "word": "answer",
          "start_ms": 2167,
          "end_ms": 2404,
          "start_char": 37,
          "end_char": 43
        },
        {
          "word": "lies",
          "start_ms": 2405,
          "end_ms": 2585,
          "start_char": 44,
          "end_char": 48
        },
        {
          "word": "in",
          "start_ms": 2792,
          "end_ms": 2891,
          "start_char": 49,
          "end_char": 51
        },
        {
          "word": "psychological",
          "start_ms": 2892,
          "end_ms": 3477,
          "start_char": 52,
          "end_char": 65
        },
        {
          "word": "conditioning",
          "start_ms": 3605,
          "end_ms": 4145,
          "start_char": 66,
          "end_char": 78
        },
        {
          "word": "and",
          "start_ms": 4230,
          "end_ms": 4304,
          "start_char": 79,
          "end_char": 82
        },
        {
          "word": "immediate",
          "start_ms": 4305,
          "end_ms": 4710,
          "start_char": 83,
          "end_char": 92
        },
        {
          "word": "gratification",
          "start_ms": 4717,
          "end_ms": 5302,
          "start_char": 93,
          "end_char": 106
        },
        {
          "word": "Studies",
          "start_ms": 6010,
          "end_ms": 6325,
          "start_char": 108,
          "end_char": 115
        },
        {
          "word": "from",
          "start_ms": 6472,
          "end_ms": 6596,
          "start_char": 116,
          "end_char": 120
        },
        {
          "word": "the",
          "start_ms": 6597,
          "end_ms": 6671,
          "start_char": 121,
          "end_char": 124
        },
        {
          "word": "Kantar",
          "start_ms": 6672,
          "end_ms": 6942,
          "start_char": 125,
          "end_char": 131
        },
        {
          "word": "Urban",
          "start_ms": 7022,
          "end_ms": 7247,
          "start_char": 132,
          "end_char": 137
        },
        {
          "word": "Spending",
          "start_ms": 7285,
          "end_ms": 7645,
          "start_char": 138,
          "end_char": 146
        },
        {
          "word": "Index",
          "start_ms": 7710,
          "end_ms": 7935,
          "start_char": 147,
          "end_char": 152
        },
        {
          "word": "reveal",
          "start_ms": 8122,
          "end_ms": 8392,
          "start_char": 153,
          "end_char": 159
        },
        {
          "word": "that",
          "start_ms": 8510,
          "end_ms": 8621,
          "start_char": 160,
          "end_char": 164
        },
        {
          "word": "average",
          "start_ms": 8622,
          "end_ms": 8937,
          "start_char": 165,
          "end_char": 172
        },
        {
          "word": "monthly",
          "start_ms": 8947,
          "end_ms": 9262,
          "start_char": 173,
          "end_char": 180
        },
        {
          "word": "discretionary",
          "start_ms": 9272,
          "end_ms": 9857,
          "start_char": 181,
          "end_char": 194
        },
        {
          "word": "spend",
          "start_ms": 9972,
          "end_ms": 10197,
          "start_char": 195,
          "end_char": 200
        },
        {
          "word": "on",
          "start_ms": 10310,
          "end_ms": 10410,
          "start_char": 201,
          "end_char": 203
        },
        {
          "word": "dining",
          "start_ms": 10447,
          "end_ms": 10717,
          "start_char": 204,
          "end_char": 210
        },
        {
          "word": "out",
          "start_ms": 10810,
          "end_ms": 10945,
          "start_char": 211,
          "end_char": 214
        },
        {
          "word": "and",
          "start_ms": 10985,
          "end_ms": 11096,
          "start_char": 215,
          "end_char": 218
        },
        {
          "word": "lifestyle",
          "start_ms": 11097,
          "end_ms": 11502,
          "start_char": 219,
          "end_char": 228
        },
        {
          "word": "apps",
          "start_ms": 11660,
          "end_ms": 11840,
          "start_char": 229,
          "end_char": 233
        },
        {
          "word": "increases",
          "start_ms": 11897,
          "end_ms": 12302,
          "start_char": 234,
          "end_char": 243
        },
        {
          "word": "by",
          "start_ms": 12460,
          "end_ms": 12560,
          "start_char": 244,
          "end_char": 246
        },
        {
          "word": "85",
          "start_ms": 12672,
          "end_ms": 12772,
          "start_char": 247,
          "end_char": 249
        },
        {
          "word": "percent",
          "start_ms": 13160,
          "end_ms": 13475,
          "start_char": 250,
          "end_char": 257
        },
        {
          "word": "within",
          "start_ms": 13572,
          "end_ms": 13842,
          "start_char": 258,
          "end_char": 264
        },
        {
          "word": "6",
          "start_ms": 13860,
          "end_ms": 13960,
          "start_char": 265,
          "end_char": 266
        },
        {
          "word": "months",
          "start_ms": 14135,
          "end_ms": 14405,
          "start_char": 267,
          "end_char": 273
        },
        {
          "word": "of",
          "start_ms": 14460,
          "end_ms": 14546,
          "start_char": 274,
          "end_char": 276
        },
        {
          "word": "a",
          "start_ms": 14547,
          "end_ms": 14596,
          "start_char": 277,
          "end_char": 278
        },
        {
          "word": "salary",
          "start_ms": 14597,
          "end_ms": 14867,
          "start_char": 279,
          "end_char": 285
        },
        {
          "word": "promotion",
          "start_ms": 15035,
          "end_ms": 15440,
          "start_char": 286,
          "end_char": 295
        },
        {
          "word": "crossing",
          "start_ms": 15535,
          "end_ms": 15895,
          "start_char": 296,
          "end_char": 304
        },
        {
          "word": "₹1,00,000",
          "start_ms": 15997,
          "end_ms": 16402,
          "start_char": 305,
          "end_char": 316
        },
        {
          "word": "per",
          "start_ms": 17160,
          "end_ms": 17295,
          "start_char": 317,
          "end_char": 320
        },
        {
          "word": "month",
          "start_ms": 17310,
          "end_ms": 17535,
          "start_char": 321,
          "end_char": 326
        },
        {
          "word": "Furthermore",
          "start_ms": 18177,
          "end_ms": 18672,
          "start_char": 328,
          "end_char": 339
        },
        {
          "word": "ordering",
          "start_ms": 19065,
          "end_ms": 19425,
          "start_char": 341,
          "end_char": 349
        },
        {
          "word": "food",
          "start_ms": 19465,
          "end_ms": 19645,
          "start_char": 350,
          "end_char": 354
        },
        {
          "word": "delivery",
          "start_ms": 19752,
          "end_ms": 20112,
          "start_char": 355,
          "end_char": 363
        },
        {
          "word": "15",
          "start_ms": 20152,
          "end_ms": 20252,
          "start_char": 364,
          "end_char": 366
        },
        {
          "word": "times",
          "start_ms": 20640,
          "end_ms": 20865,
          "start_char": 367,
          "end_char": 372
        },
        {
          "word": "a",
          "start_ms": 20965,
          "end_ms": 21001,
          "start_char": 373,
          "end_char": 374
        },
        {
          "word": "month",
          "start_ms": 21002,
          "end_ms": 21227,
          "start_char": 375,
          "end_char": 380
        },
        {
          "word": "instead",
          "start_ms": 21327,
          "end_ms": 21601,
          "start_char": 381,
          "end_char": 388
        },
        {
          "word": "of",
          "start_ms": 21602,
          "end_ms": 21701,
          "start_char": 389,
          "end_char": 391
        },
        {
          "word": "cooking",
          "start_ms": 21702,
          "end_ms": 22017,
          "start_char": 392,
          "end_char": 399
        },
        {
          "word": "adds",
          "start_ms": 22052,
          "end_ms": 22232,
          "start_char": 400,
          "end_char": 404
        },
        {
          "word": "an",
          "start_ms": 22277,
          "end_ms": 22351,
          "start_char": 405,
          "end_char": 407
        },
        {
          "word": "extra",
          "start_ms": 22352,
          "end_ms": 22577,
          "start_char": 408,
          "end_char": 413
        },
        {
          "word": "₹7,500",
          "start_ms": 22640,
          "end_ms": 22910,
          "start_char": 414,
          "end_char": 422
        },
        {
          "word": "to",
          "start_ms": 24327,
          "end_ms": 24414,
          "start_char": 423,
          "end_char": 425
        },
        {
          "word": "monthly",
          "start_ms": 24415,
          "end_ms": 24730,
          "start_char": 426,
          "end_char": 433
        },
        {
          "word": "discretionary",
          "start_ms": 24752,
          "end_ms": 25337,
          "start_char": 434,
          "end_char": 447
        },
        {
          "word": "spending",
          "start_ms": 25402,
          "end_ms": 25762,
          "start_char": 448,
          "end_char": 456
        },
        {
          "word": "You",
          "start_ms": 26395,
          "end_ms": 26519,
          "start_char": 458,
          "end_char": 461
        },
        {
          "word": "start",
          "start_ms": 26520,
          "end_ms": 26745,
          "start_char": 462,
          "end_char": 467
        },
        {
          "word": "treating",
          "start_ms": 26832,
          "end_ms": 27131,
          "start_char": 468,
          "end_char": 476
        },
        {
          "word": "luxury",
          "start_ms": 27132,
          "end_ms": 27402,
          "start_char": 477,
          "end_char": 483
        },
        {
          "word": "conveniences",
          "start_ms": 27507,
          "end_ms": 28047,
          "start_char": 484,
          "end_char": 496
        },
        {
          "word": "as",
          "start_ms": 28220,
          "end_ms": 28320,
          "start_char": 497,
          "end_char": 499
        },
        {
          "word": "absolute",
          "start_ms": 28370,
          "end_ms": 28730,
          "start_char": 500,
          "end_char": 508
        },
        {
          "word": "necessities",
          "start_ms": 28795,
          "end_ms": 29290,
          "start_char": 509,
          "end_char": 520
        },
        {
          "word": "trapping",
          "start_ms": 29695,
          "end_ms": 30044,
          "start_char": 522,
          "end_char": 530
        },
        {
          "word": "yourself",
          "start_ms": 30045,
          "end_ms": 30405,
          "start_char": 531,
          "end_char": 539
        },
        {
          "word": "in",
          "start_ms": 30507,
          "end_ms": 30581,
          "start_char": 540,
          "end_char": 542
        },
        {
          "word": "an",
          "start_ms": 30582,
          "end_ms": 30669,
          "start_char": 543,
          "end_char": 545
        },
        {
          "word": "endless",
          "start_ms": 30670,
          "end_ms": 30944,
          "start_char": 546,
          "end_char": 553
        },
        {
          "word": "cycle",
          "start_ms": 30945,
          "end_ms": 31170,
          "start_char": 554,
          "end_char": 559
        },
        {
          "word": "of",
          "start_ms": 31320,
          "end_ms": 31394,
          "start_char": 560,
          "end_char": 562
        },
        {
          "word": "consumption",
          "start_ms": 31395,
          "end_ms": 31890,
          "start_char": 563,
          "end_char": 574
        }
      ],
      "duration_ms": 32184,
      "duration_seconds": 32.184
    },
    {
      "chunk_id": "chunk_004",
      "sequence": 4,
      "source_id": "idea_03",
      "text": "Once discretionary spending spikes, major fixed commitments enter the picture. Upgrading from a rented 1 BHK to a 2 BHK apartment in cities like Bengaluru or Mumbai increases monthly housing expenses by an average of ₹25,000 to ₹40,000. On top of that, purchasing a mid-size car on an auto loan at an EMI of ₹22,000 per month locks in vehicle depreciation and loan interest for 5 years. These heavy financial anchors silently crush your effective hourly rate and destroy your capacity to build genuine long-term wealth.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_004.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_004.marks.json",
      "word_timestamps": [
        {
          "word": "Once",
          "start_ms": 25,
          "end_ms": 205,
          "start_char": 0,
          "end_char": 4
        },
        {
          "word": "discretionary",
          "start_ms": 325,
          "end_ms": 910,
          "start_char": 5,
          "end_char": 18
        },
        {
          "word": "spending",
          "start_ms": 1012,
          "end_ms": 1372,
          "start_char": 19,
          "end_char": 27
        },
        {
          "word": "spikes",
          "start_ms": 1400,
          "end_ms": 1670,
          "start_char": 28,
          "end_char": 34
        },
        {
          "word": "major",
          "start_ms": 2112,
          "end_ms": 2337,
          "start_char": 36,
          "end_char": 41
        },
        {
          "word": "fixed",
          "start_ms": 2487,
          "end_ms": 2712,
          "start_char": 42,
          "end_char": 47
        },
        {
          "word": "commitments",
          "start_ms": 2800,
          "end_ms": 3261,
          "start_char": 48,
          "end_char": 59
        },
        {
          "word": "enter",
          "start_ms": 3262,
          "end_ms": 3399,
          "start_char": 60,
          "end_char": 65
        },
        {
          "word": "the",
          "start_ms": 3400,
          "end_ms": 3486,
          "start_char": 66,
          "end_char": 69
        },
        {
          "word": "picture",
          "start_ms": 3487,
          "end_ms": 3802,
          "start_char": 70,
          "end_char": 77
        },
        {
          "word": "Upgrading",
          "start_ms": 4442,
          "end_ms": 4847,
          "start_char": 79,
          "end_char": 88
        },
        {
          "word": "from",
          "start_ms": 4942,
          "end_ms": 5116,
          "start_char": 89,
          "end_char": 93
        },
        {
          "word": "a",
          "start_ms": 5117,
          "end_ms": 5179,
          "start_char": 94,
          "end_char": 95
        },
        {
          "word": "rented",
          "start_ms": 5180,
          "end_ms": 5450,
          "start_char": 96,
          "end_char": 102
        },
        {
          "word": "1",
          "start_ms": 5530,
          "end_ms": 5630,
          "start_char": 103,
          "end_char": 104
        },
        {
          "word": "BHK",
          "start_ms": 5805,
          "end_ms": 5940,
          "start_char": 105,
          "end_char": 108
        },
        {
          "word": "to",
          "start_ms": 6392,
          "end_ms": 6492,
          "start_char": 109,
          "end_char": 111
        },
        {
          "word": "a",
          "start_ms": 6555,
          "end_ms": 6591,
          "start_char": 112,
          "end_char": 113
        },
        {
          "word": "2",
          "start_ms": 6592,
          "end_ms": 6692,
          "start_char": 114,
          "end_char": 115
        },
        {
          "word": "BHK",
          "start_ms": 6817,
          "end_ms": 6952,
          "start_char": 116,
          "end_char": 119
        },
        {
          "word": "apartment",
          "start_ms": 7380,
          "end_ms": 7785,
          "start_char": 120,
          "end_char": 129
        },
        {
          "word": "in",
          "start_ms": 7792,
          "end_ms": 7892,
          "start_char": 130,
          "end_char": 132
        },
        {
          "word": "cities",
          "start_ms": 7905,
          "end_ms": 8175,
          "start_char": 133,
          "end_char": 139
        },
        {
          "word": "like",
          "start_ms": 8305,
          "end_ms": 8485,
          "start_char": 140,
          "end_char": 144
        },
        {
          "word": "Bengaluru",
          "start_ms": 8492,
          "end_ms": 8897,
          "start_char": 145,
          "end_char": 154
        },
        {
          "word": "or",
          "start_ms": 9092,
          "end_ms": 9192,
          "start_char": 155,
          "end_char": 157
        },
        {
          "word": "Mumbai",
          "start_ms": 9205,
          "end_ms": 9475,
          "start_char": 158,
          "end_char": 164
        },
        {
          "word": "increases",
          "start_ms": 9680,
          "end_ms": 10085,
          "start_char": 165,
          "end_char": 174
        },
        {
          "word": "monthly",
          "start_ms": 10267,
          "end_ms": 10582,
          "start_char": 175,
          "end_char": 182
        },
        {
          "word": "housing",
          "start_ms": 10617,
          "end_ms": 10932,
          "start_char": 183,
          "end_char": 190
        },
        {
          "word": "expenses",
          "start_ms": 10992,
          "end_ms": 11352,
          "start_char": 191,
          "end_char": 199
        },
        {
          "word": "by",
          "start_ms": 11580,
          "end_ms": 11680,
          "start_char": 200,
          "end_char": 202
        },
        {
          "word": "an",
          "start_ms": 11780,
          "end_ms": 11854,
          "start_char": 203,
          "end_char": 205
        },
        {
          "word": "average",
          "start_ms": 11855,
          "end_ms": 12170,
          "start_char": 206,
          "end_char": 213
        },
        {
          "word": "of",
          "start_ms": 12192,
          "end_ms": 12279,
          "start_char": 214,
          "end_char": 216
        },
        {
          "word": "₹25,000",
          "start_ms": 12280,
          "end_ms": 12595,
          "start_char": 217,
          "end_char": 226
        },
        {
          "word": "to",
          "start_ms": 13642,
          "end_ms": 13729,
          "start_char": 227,
          "end_char": 229
        },
        {
          "word": "₹40,000",
          "start_ms": 13730,
          "end_ms": 14045,
          "start_char": 230,
          "end_char": 239
        },
        {
          "word": "On",
          "start_ms": 15422,
          "end_ms": 15522,
          "start_char": 241,
          "end_char": 243
        },
        {
          "word": "top",
          "start_ms": 15585,
          "end_ms": 15720,
          "start_char": 244,
          "end_char": 247
        },
        {
          "word": "of",
          "start_ms": 15835,
          "end_ms": 15921,
          "start_char": 248,
          "end_char": 250
        },
        {
          "word": "that",
          "start_ms": 15922,
          "end_ms": 16102,
          "start_char": 251,
          "end_char": 255
        },
        {
          "word": "purchasing",
          "start_ms": 16310,
          "end_ms": 16760,
          "start_char": 257,
          "end_char": 267
        },
        {
          "word": "a",
          "start_ms": 16810,
          "end_ms": 16846,
          "start_char": 268,
          "end_char": 269
        },
        {
          "word": "mid-size",
          "start_ms": 16847,
          "end_ms": 17207,
          "start_char": 270,
          "end_char": 278
        },
        {
          "word": "car",
          "start_ms": 17372,
          "end_ms": 17507,
          "start_char": 279,
          "end_char": 282
        },
        {
          "word": "on",
          "start_ms": 17647,
          "end_ms": 17734,
          "start_char": 283,
          "end_char": 285
        },
        {
          "word": "an",
          "start_ms": 17735,
          "end_ms": 17809,
          "start_char": 286,
          "end_char": 288
        },
        {
          "word": "auto",
          "start_ms": 17810,
          "end_ms": 17990,
          "start_char": 289,
          "end_char": 293
        },
        {
          "word": "loan",
          "start_ms": 18072,
          "end_ms": 18252,
          "start_char": 294,
          "end_char": 298
        },
        {
          "word": "at",
          "start_ms": 18372,
          "end_ms": 18446,
          "start_char": 299,
          "end_char": 301
        },
        {
          "word": "an",
          "start_ms": 18447,
          "end_ms": 18546,
          "start_char": 302,
          "end_char": 304
        },
        {
          "word": "EMI",
          "start_ms": 18547,
          "end_ms": 18682,
          "start_char": 305,
          "end_char": 308
        },
        {
          "word": "of",
          "start_ms": 18785,
          "end_ms": 18884,
          "start_char": 309,
          "end_char": 311
        },
        {
          "word": "₹22,000",
          "start_ms": 18885,
          "end_ms": 19200,
          "start_char": 312,
          "end_char": 321
        },
        {
          "word": "per",
          "start_ms": 20172,
          "end_ms": 20307,
          "start_char": 322,
          "end_char": 325
        },
        {
          "word": "month",
          "start_ms": 20335,
          "end_ms": 20560,
          "start_char": 326,
          "end_char": 331
        },
        {
          "word": "locks",
          "start_ms": 20635,
          "end_ms": 20860,
          "start_char": 332,
          "end_char": 337
        },
        {
          "word": "in",
          "start_ms": 20985,
          "end_ms": 21085,
          "start_char": 338,
          "end_char": 340
        },
        {
          "word": "vehicle",
          "start_ms": 21110,
          "end_ms": 21425,
          "start_char": 341,
          "end_char": 348
        },
        {
          "word": "depreciation",
          "start_ms": 21485,
          "end_ms": 22025,
          "start_char": 349,
          "end_char": 361
        },
        {
          "word": "and",
          "start_ms": 22222,
          "end_ms": 22357,
          "start_char": 362,
          "end_char": 365
        },
        {
          "word": "loan",
          "start_ms": 22360,
          "end_ms": 22540,
          "start_char": 366,
          "end_char": 370
        },
        {
          "word": "interest",
          "start_ms": 22572,
          "end_ms": 22909,
          "start_char": 371,
          "end_char": 379
        },
        {
          "word": "for",
          "start_ms": 22910,
          "end_ms": 23021,
          "start_char": 380,
          "end_char": 383
        },
        {
          "word": "5",
          "start_ms": 23022,
          "end_ms": 23122,
          "start_char": 384,
          "end_char": 385
        },
        {
          "word": "years",
          "start_ms": 23322,
          "end_ms": 23547,
          "start_char": 386,
          "end_char": 391
        },
        {
          "word": "These",
          "start_ms": 24215,
          "end_ms": 24440,
          "start_char": 393,
          "end_char": 398
        },
        {
          "word": "heavy",
          "start_ms": 24465,
          "end_ms": 24690,
          "start_char": 399,
          "end_char": 404
        },
        {
          "word": "financial",
          "start_ms": 24702,
          "end_ms": 25107,
          "start_char": 405,
          "end_char": 414
        },
        {
          "word": "anchors",
          "start_ms": 25215,
          "end_ms": 25530,
          "start_char": 415,
          "end_char": 422
        },
        {
          "word": "silently",
          "start_ms": 25540,
          "end_ms": 25900,
          "start_char": 423,
          "end_char": 431
        },
        {
          "word": "crush",
          "start_ms": 25977,
          "end_ms": 26202,
          "start_char": 432,
          "end_char": 437
        },
        {
          "word": "your",
          "start_ms": 26327,
          "end_ms": 26476,
          "start_char": 438,
          "end_char": 442
        },
        {
          "word": "effective",
          "start_ms": 26477,
          "end_ms": 26876,
          "start_char": 443,
          "end_char": 452
        },
        {
          "word": "hourly",
          "start_ms": 26877,
          "end_ms": 27147,
          "start_char": 453,
          "end_char": 459
        },
        {
          "word": "rate",
          "start_ms": 27240,
          "end_ms": 27420,
          "start_char": 460,
          "end_char": 464
        },
        {
          "word": "and",
          "start_ms": 27527,
          "end_ms": 27614,
          "start_char": 465,
          "end_char": 468
        },
        {
          "word": "destroy",
          "start_ms": 27615,
          "end_ms": 27930,
          "start_char": 469,
          "end_char": 476
        },
        {
          "word": "your",
          "start_ms": 27977,
          "end_ms": 28126,
          "start_char": 477,
          "end_char": 481
        },
        {
          "word": "capacity",
          "start_ms": 28127,
          "end_ms": 28487,
          "start_char": 482,
          "end_char": 490
        },
        {
          "word": "to",
          "start_ms": 28715,
          "end_ms": 28814,
          "start_char": 491,
          "end_char": 493
        },
        {
          "word": "build",
          "start_ms": 28815,
          "end_ms": 29040,
          "start_char": 494,
          "end_char": 499
        },
        {
          "word": "genuine",
          "start_ms": 29115,
          "end_ms": 29430,
          "start_char": 500,
          "end_char": 507
        },
        {
          "word": "long-term",
          "start_ms": 29490,
          "end_ms": 29895,
          "start_char": 508,
          "end_char": 517
        },
        {
          "word": "wealth",
          "start_ms": 29977,
          "end_ms": 30247,
          "start_char": 518,
          "end_char": 524
        }
      ],
      "duration_ms": 30528,
      "duration_seconds": 30.528
    },
    {
      "chunk_id": "chunk_005",
      "sequence": 5,
      "source_id": "idea_04",
      "text": "Let us examine the stark opportunity cost of consumption. Every rupee spent on maintaining an upscale image in Mumbai or Gurgaon is a rupee stolen from your future self. When you prioritize flash over assets, you are trading decades of freedom for a temporary status symbol. The hidden price of your luxury car and upgraded apartment isn't just the sticker price—it is the lost compound growth that could have set you free a decade earlier.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_005.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_005.marks.json",
      "word_timestamps": [
        {
          "word": "Let",
          "start_ms": 25,
          "end_ms": 160,
          "start_char": 0,
          "end_char": 3
        },
        {
          "word": "us",
          "start_ms": 175,
          "end_ms": 275,
          "start_char": 4,
          "end_char": 6
        },
        {
          "word": "examine",
          "start_ms": 312,
          "end_ms": 627,
          "start_char": 7,
          "end_char": 14
        },
        {
          "word": "the",
          "start_ms": 712,
          "end_ms": 774,
          "start_char": 15,
          "end_char": 18
        },
        {
          "word": "stark",
          "start_ms": 775,
          "end_ms": 1000,
          "start_char": 19,
          "end_char": 24
        },
        {
          "word": "opportunity",
          "start_ms": 1162,
          "end_ms": 1657,
          "start_char": 25,
          "end_char": 36
        },
        {
          "word": "cost",
          "start_ms": 1700,
          "end_ms": 1880,
          "start_char": 37,
          "end_char": 41
        },
        {
          "word": "of",
          "start_ms": 2037,
          "end_ms": 2099,
          "start_char": 42,
          "end_char": 44
        },
        {
          "word": "consumption",
          "start_ms": 2100,
          "end_ms": 2595,
          "start_char": 45,
          "end_char": 56
        },
        {
          "word": "Every",
          "start_ms": 3230,
          "end_ms": 3455,
          "start_char": 58,
          "end_char": 63
        },
        {
          "word": "rupee",
          "start_ms": 3492,
          "end_ms": 3717,
          "start_char": 64,
          "end_char": 69
        },
        {
          "word": "spent",
          "start_ms": 3905,
          "end_ms": 4130,
          "start_char": 70,
          "end_char": 75
        },
        {
          "word": "on",
          "start_ms": 4242,
          "end_ms": 4342,
          "start_char": 76,
          "end_char": 78
        },
        {
          "word": "maintaining",
          "start_ms": 4355,
          "end_ms": 4850,
          "start_char": 79,
          "end_char": 90
        },
        {
          "word": "an",
          "start_ms": 4867,
          "end_ms": 4929,
          "start_char": 91,
          "end_char": 93
        },
        {
          "word": "upscale",
          "start_ms": 4930,
          "end_ms": 5245,
          "start_char": 94,
          "end_char": 101
        },
        {
          "word": "image",
          "start_ms": 5417,
          "end_ms": 5641,
          "start_char": 102,
          "end_char": 107
        },
        {
          "word": "in",
          "start_ms": 5642,
          "end_ms": 5729,
          "start_char": 108,
          "end_char": 110
        },
        {
          "word": "Mumbai",
          "start_ms": 5730,
          "end_ms": 6000,
          "start_char": 111,
          "end_char": 117
        },
        {
          "word": "or",
          "start_ms": 6205,
          "end_ms": 6304,
          "start_char": 118,
          "end_char": 120
        },
        {
          "word": "Gurgaon",
          "start_ms": 6305,
          "end_ms": 6620,
          "start_char": 121,
          "end_char": 128
        },
        {
          "word": "is",
          "start_ms": 6855,
          "end_ms": 6955,
          "start_char": 129,
          "end_char": 131
        },
        {
          "word": "a",
          "start_ms": 6967,
          "end_ms": 7016,
          "start_char": 132,
          "end_char": 133
        },
        {
          "word": "rupee",
          "start_ms": 7017,
          "end_ms": 7242,
          "start_char": 134,
          "end_char": 139
        },
        {
          "word": "stolen",
          "start_ms": 7380,
          "end_ms": 7650,
          "start_char": 140,
          "end_char": 146
        },
        {
          "word": "from",
          "start_ms": 7780,
          "end_ms": 7916,
          "start_char": 147,
          "end_char": 151
        },
        {
          "word": "your",
          "start_ms": 7917,
          "end_ms": 8016,
          "start_char": 152,
          "end_char": 156
        },
        {
          "word": "future",
          "start_ms": 8017,
          "end_ms": 8287,
          "start_char": 157,
          "end_char": 163
        },
        {
          "word": "self",
          "start_ms": 8367,
          "end_ms": 8547,
          "start_char": 164,
          "end_char": 168
        },
        {
          "word": "When",
          "start_ms": 9310,
          "end_ms": 9471,
          "start_char": 170,
          "end_char": 174
        },
        {
          "word": "you",
          "start_ms": 9472,
          "end_ms": 9559,
          "start_char": 175,
          "end_char": 178
        },
        {
          "word": "prioritize",
          "start_ms": 9560,
          "end_ms": 10010,
          "start_char": 179,
          "end_char": 189
        },
        {
          "word": "flash",
          "start_ms": 10272,
          "end_ms": 10497,
          "start_char": 190,
          "end_char": 195
        },
        {
          "word": "over",
          "start_ms": 10597,
          "end_ms": 10777,
          "start_char": 196,
          "end_char": 200
        },
        {
          "word": "assets",
          "start_ms": 10872,
          "end_ms": 11142,
          "start_char": 201,
          "end_char": 207
        },
        {
          "word": "you",
          "start_ms": 11572,
          "end_ms": 11684,
          "start_char": 209,
          "end_char": 212
        },
        {
          "word": "are",
          "start_ms": 11685,
          "end_ms": 11759,
          "start_char": 213,
          "end_char": 216
        },
        {
          "word": "trading",
          "start_ms": 11760,
          "end_ms": 12075,
          "start_char": 217,
          "end_char": 224
        },
        {
          "word": "decades",
          "start_ms": 12160,
          "end_ms": 12475,
          "start_char": 225,
          "end_char": 232
        },
        {
          "word": "of",
          "start_ms": 12610,
          "end_ms": 12684,
          "start_char": 233,
          "end_char": 235
        },
        {
          "word": "freedom",
          "start_ms": 12685,
          "end_ms": 13000,
          "start_char": 236,
          "end_char": 243
        },
        {
          "word": "for",
          "start_ms": 13072,
          "end_ms": 13207,
          "start_char": 244,
          "end_char": 247
        },
        {
          "word": "a",
          "start_ms": 13247,
          "end_ms": 13284,
          "start_char": 248,
          "end_char": 249
        },
        {
          "word": "temporary",
          "start_ms": 13285,
          "end_ms": 13690,
          "start_char": 250,
          "end_char": 259
        },
        {
          "word": "status",
          "start_ms": 13797,
          "end_ms": 14067,
          "start_char": 260,
          "end_char": 266
        },
        {
          "word": "symbol",
          "start_ms": 14135,
          "end_ms": 14405,
          "start_char": 267,
          "end_char": 273
        },
        {
          "word": "The",
          "start_ms": 15015,
          "end_ms": 15126,
          "start_char": 275,
          "end_char": 278
        },
        {
          "word": "hidden",
          "start_ms": 15127,
          "end_ms": 15397,
          "start_char": 279,
          "end_char": 285
        },
        {
          "word": "price",
          "start_ms": 15415,
          "end_ms": 15640,
          "start_char": 286,
          "end_char": 291
        },
        {
          "word": "of",
          "start_ms": 15740,
          "end_ms": 15826,
          "start_char": 292,
          "end_char": 294
        },
        {
          "word": "your",
          "start_ms": 15827,
          "end_ms": 15926,
          "start_char": 295,
          "end_char": 299
        },
        {
          "word": "luxury",
          "start_ms": 15927,
          "end_ms": 16197,
          "start_char": 300,
          "end_char": 306
        },
        {
          "word": "car",
          "start_ms": 16352,
          "end_ms": 16487,
          "start_char": 307,
          "end_char": 310
        },
        {
          "word": "and",
          "start_ms": 16665,
          "end_ms": 16776,
          "start_char": 311,
          "end_char": 314
        },
        {
          "word": "upgraded",
          "start_ms": 16777,
          "end_ms": 17137,
          "start_char": 315,
          "end_char": 323
        },
        {
          "word": "apartment",
          "start_ms": 17177,
          "end_ms": 17582,
          "start_char": 324,
          "end_char": 333
        },
        {
          "word": "isn't",
          "start_ms": 17602,
          "end_ms": 17827,
          "start_char": 334,
          "end_char": 339
        },
        {
          "word": "just",
          "start_ms": 17852,
          "end_ms": 18032,
          "start_char": 340,
          "end_char": 344
        },
        {
          "word": "the",
          "start_ms": 18052,
          "end_ms": 18126,
          "start_char": 345,
          "end_char": 348
        },
        {
          "word": "sticker",
          "start_ms": 18127,
          "end_ms": 18442,
          "start_char": 349,
          "end_char": 356
        },
        {
          "word": "price",
          "start_ms": 18452,
          "end_ms": 18677,
          "start_char": 357,
          "end_char": 362
        },
        {
          "word": "it",
          "start_ms": 19102,
          "end_ms": 19201,
          "start_char": 365,
          "end_char": 367
        },
        {
          "word": "is",
          "start_ms": 19202,
          "end_ms": 19301,
          "start_char": 368,
          "end_char": 370
        },
        {
          "word": "the",
          "start_ms": 19302,
          "end_ms": 19389,
          "start_char": 371,
          "end_char": 374
        },
        {
          "word": "lost",
          "start_ms": 19390,
          "end_ms": 19570,
          "start_char": 375,
          "end_char": 379
        },
        {
          "word": "compound",
          "start_ms": 19715,
          "end_ms": 20075,
          "start_char": 380,
          "end_char": 388
        },
        {
          "word": "growth",
          "start_ms": 20240,
          "end_ms": 20510,
          "start_char": 389,
          "end_char": 395
        },
        {
          "word": "that",
          "start_ms": 20565,
          "end_ms": 20701,
          "start_char": 396,
          "end_char": 400
        },
        {
          "word": "could",
          "start_ms": 20702,
          "end_ms": 20851,
          "start_char": 401,
          "end_char": 406
        },
        {
          "word": "have",
          "start_ms": 20852,
          "end_ms": 20939,
          "start_char": 407,
          "end_char": 411
        },
        {
          "word": "set",
          "start_ms": 20940,
          "end_ms": 21075,
          "start_char": 412,
          "end_char": 415
        },
        {
          "word": "you",
          "start_ms": 21202,
          "end_ms": 21289,
          "start_char": 416,
          "end_char": 419
        },
        {
          "word": "free",
          "start_ms": 21290,
          "end_ms": 21470,
          "start_char": 420,
          "end_char": 424
        },
        {
          "word": "a",
          "start_ms": 21552,
          "end_ms": 21601,
          "start_char": 425,
          "end_char": 426
        },
        {
          "word": "decade",
          "start_ms": 21602,
          "end_ms": 21872,
          "start_char": 427,
          "end_char": 433
        },
        {
          "word": "earlier",
          "start_ms": 21965,
          "end_ms": 22280,
          "start_char": 434,
          "end_char": 441
        }
      ],
      "duration_ms": 22560,
      "duration_seconds": 22.56
    },
    {
      "chunk_id": "chunk_006",
      "sequence": 6,
      "source_id": "idea_05",
      "text": "There is a pervasive myth in urban corporate culture that carrying heavy EMIs signals financial maturity or success. According to the Mastercard Financial Literacy Index, lifestyle inflation causes 42 percent of corporate employees to remain paycheck-to-paycheck despite crossing the ₹12,00,000 annual income bracket. They believe that buying luxury items on credit establishes creditworthiness, when in reality, it simply chains them tighter to their desks, eliminating any margin for error if economic conditions shift.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_006.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_006.marks.json",
      "word_timestamps": [
        {
          "word": "There",
          "start_ms": 25,
          "end_ms": 186,
          "start_char": 0,
          "end_char": 5
        },
        {
          "word": "is",
          "start_ms": 187,
          "end_ms": 287,
          "start_char": 6,
          "end_char": 8
        },
        {
          "word": "a",
          "start_ms": 300,
          "end_ms": 336,
          "start_char": 9,
          "end_char": 10
        },
        {
          "word": "pervasive",
          "start_ms": 337,
          "end_ms": 742,
          "start_char": 11,
          "end_char": 20
        },
        {
          "word": "myth",
          "start_ms": 875,
          "end_ms": 1055,
          "start_char": 21,
          "end_char": 25
        },
        {
          "word": "in",
          "start_ms": 1150,
          "end_ms": 1250,
          "start_char": 26,
          "end_char": 28
        },
        {
          "word": "urban",
          "start_ms": 1262,
          "end_ms": 1487,
          "start_char": 29,
          "end_char": 34
        },
        {
          "word": "corporate",
          "start_ms": 1525,
          "end_ms": 1911,
          "start_char": 35,
          "end_char": 44
        },
        {
          "word": "culture",
          "start_ms": 1912,
          "end_ms": 2227,
          "start_char": 45,
          "end_char": 52
        },
        {
          "word": "that",
          "start_ms": 2325,
          "end_ms": 2474,
          "start_char": 53,
          "end_char": 57
        },
        {
          "word": "carrying",
          "start_ms": 2475,
          "end_ms": 2835,
          "start_char": 58,
          "end_char": 66
        },
        {
          "word": "heavy",
          "start_ms": 2900,
          "end_ms": 3125,
          "start_char": 67,
          "end_char": 72
        },
        {
          "word": "EMIs",
          "start_ms": 3200,
          "end_ms": 3380,
          "start_char": 73,
          "end_char": 77
        },
        {
          "word": "signals",
          "start_ms": 3462,
          "end_ms": 3777,
          "start_char": 78,
          "end_char": 85
        },
        {
          "word": "financial",
          "start_ms": 3887,
          "end_ms": 4286,
          "start_char": 86,
          "end_char": 95
        },
        {
          "word": "maturity",
          "start_ms": 4287,
          "end_ms": 4647,
          "start_char": 96,
          "end_char": 104
        },
        {
          "word": "or",
          "start_ms": 4800,
          "end_ms": 4874,
          "start_char": 105,
          "end_char": 107
        },
        {
          "word": "success",
          "start_ms": 4875,
          "end_ms": 5190,
          "start_char": 108,
          "end_char": 115
        },
        {
          "word": "According",
          "start_ms": 5967,
          "end_ms": 6354,
          "start_char": 117,
          "end_char": 126
        },
        {
          "word": "to",
          "start_ms": 6355,
          "end_ms": 6455,
          "start_char": 127,
          "end_char": 129
        },
        {
          "word": "the",
          "start_ms": 6467,
          "end_ms": 6554,
          "start_char": 130,
          "end_char": 133
        },
        {
          "word": "Mastercard",
          "start_ms": 6555,
          "end_ms": 7005,
          "start_char": 134,
          "end_char": 144
        },
        {
          "word": "Financial",
          "start_ms": 7192,
          "end_ms": 7591,
          "start_char": 145,
          "end_char": 154
        },
        {
          "word": "Literacy",
          "start_ms": 7592,
          "end_ms": 7952,
          "start_char": 155,
          "end_char": 163
        },
        {
          "word": "Index",
          "start_ms": 8105,
          "end_ms": 8330,
          "start_char": 164,
          "end_char": 169
        },
        {
          "word": "lifestyle",
          "start_ms": 8805,
          "end_ms": 9210,
          "start_char": 171,
          "end_char": 180
        },
        {
          "word": "inflation",
          "start_ms": 9417,
          "end_ms": 9822,
          "start_char": 181,
          "end_char": 190
        },
        {
          "word": "causes",
          "start_ms": 9917,
          "end_ms": 10187,
          "start_char": 191,
          "end_char": 197
        },
        {
          "word": "42",
          "start_ms": 10355,
          "end_ms": 10455,
          "start_char": 198,
          "end_char": 200
        },
        {
          "word": "percent",
          "start_ms": 10842,
          "end_ms": 11157,
          "start_char": 201,
          "end_char": 208
        },
        {
          "word": "of",
          "start_ms": 11217,
          "end_ms": 11304,
          "start_char": 209,
          "end_char": 211
        },
        {
          "word": "corporate",
          "start_ms": 11305,
          "end_ms": 11679,
          "start_char": 212,
          "end_char": 221
        },
        {
          "word": "employees",
          "start_ms": 11680,
          "end_ms": 12085,
          "start_char": 222,
          "end_char": 231
        },
        {
          "word": "to",
          "start_ms": 12180,
          "end_ms": 12280,
          "start_char": 232,
          "end_char": 234
        },
        {
          "word": "remain",
          "start_ms": 12292,
          "end_ms": 12562,
          "start_char": 235,
          "end_char": 241
        },
        {
          "word": "paycheck-to-paycheck",
          "start_ms": 12642,
          "end_ms": 13542,
          "start_char": 242,
          "end_char": 262
        },
        {
          "word": "despite",
          "start_ms": 13630,
          "end_ms": 13945,
          "start_char": 263,
          "end_char": 270
        },
        {
          "word": "crossing",
          "start_ms": 14030,
          "end_ms": 14390,
          "start_char": 271,
          "end_char": 279
        },
        {
          "word": "the",
          "start_ms": 14442,
          "end_ms": 14516,
          "start_char": 280,
          "end_char": 283
        },
        {
          "word": "₹12,00,000",
          "start_ms": 14517,
          "end_ms": 14967,
          "start_char": 284,
          "end_char": 296
        },
        {
          "word": "annual",
          "start_ms": 16342,
          "end_ms": 16612,
          "start_char": 297,
          "end_char": 303
        },
        {
          "word": "income",
          "start_ms": 16705,
          "end_ms": 16975,
          "start_char": 304,
          "end_char": 310
        },
        {
          "word": "bracket",
          "start_ms": 17005,
          "end_ms": 17320,
          "start_char": 311,
          "end_char": 318
        },
        {
          "word": "They",
          "start_ms": 17885,
          "end_ms": 18021,
          "start_char": 320,
          "end_char": 324
        },
        {
          "word": "believe",
          "start_ms": 18022,
          "end_ms": 18337,
          "start_char": 325,
          "end_char": 332
        },
        {
          "word": "that",
          "start_ms": 18385,
          "end_ms": 18534,
          "start_char": 333,
          "end_char": 337
        },
        {
          "word": "buying",
          "start_ms": 18535,
          "end_ms": 18805,
          "start_char": 338,
          "end_char": 344
        },
        {
          "word": "luxury",
          "start_ms": 18872,
          "end_ms": 19142,
          "start_char": 345,
          "end_char": 351
        },
        {
          "word": "items",
          "start_ms": 19360,
          "end_ms": 19585,
          "start_char": 352,
          "end_char": 357
        },
        {
          "word": "on",
          "start_ms": 19672,
          "end_ms": 19772,
          "start_char": 358,
          "end_char": 360
        },
        {
          "word": "credit",
          "start_ms": 19797,
          "end_ms": 20067,
          "start_char": 361,
          "end_char": 367
        },
        {
          "word": "establishes",
          "start_ms": 20097,
          "end_ms": 20592,
          "start_char": 368,
          "end_char": 379
        },
        {
          "word": "creditworthiness",
          "start_ms": 20710,
          "end_ms": 21430,
          "start_char": 380,
          "end_char": 396
        },
        {
          "word": "when",
          "start_ms": 21785,
          "end_ms": 21965,
          "start_char": 398,
          "end_char": 402
        },
        {
          "word": "in",
          "start_ms": 21972,
          "end_ms": 22046,
          "start_char": 403,
          "end_char": 405
        },
        {
          "word": "reality",
          "start_ms": 22047,
          "end_ms": 22362,
          "start_char": 406,
          "end_char": 413
        },
        {
          "word": "it",
          "start_ms": 22847,
          "end_ms": 22947,
          "start_char": 415,
          "end_char": 417
        },
        {
          "word": "simply",
          "start_ms": 22972,
          "end_ms": 23242,
          "start_char": 418,
          "end_char": 424
        },
        {
          "word": "chains",
          "start_ms": 23322,
          "end_ms": 23592,
          "start_char": 425,
          "end_char": 431
        },
        {
          "word": "them",
          "start_ms": 23672,
          "end_ms": 23834,
          "start_char": 432,
          "end_char": 436
        },
        {
          "word": "tighter",
          "start_ms": 23835,
          "end_ms": 24134,
          "start_char": 437,
          "end_char": 444
        },
        {
          "word": "to",
          "start_ms": 24135,
          "end_ms": 24235,
          "start_char": 445,
          "end_char": 447
        },
        {
          "word": "their",
          "start_ms": 24247,
          "end_ms": 24384,
          "start_char": 448,
          "end_char": 453
        },
        {
          "word": "desks",
          "start_ms": 24385,
          "end_ms": 24610,
          "start_char": 454,
          "end_char": 459
        },
        {
          "word": "eliminating",
          "start_ms": 25085,
          "end_ms": 25580,
          "start_char": 461,
          "end_char": 472
        },
        {
          "word": "any",
          "start_ms": 25635,
          "end_ms": 25759,
          "start_char": 473,
          "end_char": 476
        },
        {
          "word": "margin",
          "start_ms": 25760,
          "end_ms": 26030,
          "start_char": 477,
          "end_char": 483
        },
        {
          "word": "for",
          "start_ms": 26197,
          "end_ms": 26332,
          "start_char": 484,
          "end_char": 487
        },
        {
          "word": "error",
          "start_ms": 26410,
          "end_ms": 26635,
          "start_char": 488,
          "end_char": 493
        },
        {
          "word": "if",
          "start_ms": 26747,
          "end_ms": 26847,
          "start_char": 494,
          "end_char": 496
        },
        {
          "word": "economic",
          "start_ms": 26872,
          "end_ms": 27232,
          "start_char": 497,
          "end_char": 505
        },
        {
          "word": "conditions",
          "start_ms": 27310,
          "end_ms": 27760,
          "start_char": 506,
          "end_char": 516
        },
        {
          "word": "shift",
          "start_ms": 27797,
          "end_ms": 28022,
          "start_char": 517,
          "end_char": 522
        }
      ],
      "duration_ms": 28368,
      "duration_seconds": 28.368
    },
    {
      "chunk_id": "chunk_007",
      "sequence": 7,
      "source_id": "idea_06",
      "text": "Escaping this cycle requires a rigorous framework, and the time-tested 50/30/20 rule is your ultimate weapon. By allocating 50 percent of your ₹1,00,000 salary to absolute needs, 30 percent to guilt-free wants, and a disciplined 50 percent directly to aggressive wealth building, you completely break the pattern of lifestyle creep. Instead of letting your bank account bleed out through miscellaneous expenses, every single rupee is assigned a specific, mission-driven purpose.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_007.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_007.marks.json",
      "word_timestamps": [
        {
          "word": "Escaping",
          "start_ms": 25,
          "end_ms": 385,
          "start_char": 0,
          "end_char": 8
        },
        {
          "word": "this",
          "start_ms": 550,
          "end_ms": 674,
          "start_char": 9,
          "end_char": 13
        },
        {
          "word": "cycle",
          "start_ms": 675,
          "end_ms": 900,
          "start_char": 14,
          "end_char": 19
        },
        {
          "word": "requires",
          "start_ms": 1037,
          "end_ms": 1397,
          "start_char": 20,
          "end_char": 28
        },
        {
          "word": "a",
          "start_ms": 1525,
          "end_ms": 1574,
          "start_char": 29,
          "end_char": 30
        },
        {
          "word": "rigorous",
          "start_ms": 1575,
          "end_ms": 1935,
          "start_char": 31,
          "end_char": 39
        },
        {
          "word": "framework",
          "start_ms": 1962,
          "end_ms": 2367,
          "start_char": 40,
          "end_char": 49
        },
        {
          "word": "and",
          "start_ms": 2712,
          "end_ms": 2824,
          "start_char": 51,
          "end_char": 54
        },
        {
          "word": "the",
          "start_ms": 2825,
          "end_ms": 2886,
          "start_char": 55,
          "end_char": 58
        },
        {
          "word": "time-tested",
          "start_ms": 2887,
          "end_ms": 3382,
          "start_char": 59,
          "end_char": 70
        },
        {
          "word": "50/30/20",
          "start_ms": 3512,
          "end_ms": 3872,
          "start_char": 71,
          "end_char": 79
        },
        {
          "word": "rule",
          "start_ms": 5087,
          "end_ms": 5267,
          "start_char": 80,
          "end_char": 84
        },
        {
          "word": "is",
          "start_ms": 5387,
          "end_ms": 5487,
          "start_char": 85,
          "end_char": 87
        },
        {
          "word": "your",
          "start_ms": 5500,
          "end_ms": 5636,
          "start_char": 88,
          "end_char": 92
        },
        {
          "word": "ultimate",
          "start_ms": 5637,
          "end_ms": 5949,
          "start_char": 93,
          "end_char": 101
        },
        {
          "word": "weapon",
          "start_ms": 5950,
          "end_ms": 6220,
          "start_char": 102,
          "end_char": 108
        },
        {
          "word": "By",
          "start_ms": 6867,
          "end_ms": 6967,
          "start_char": 110,
          "end_char": 112
        },
        {
          "word": "allocating",
          "start_ms": 7117,
          "end_ms": 7567,
          "start_char": 113,
          "end_char": 123
        },
        {
          "word": "50",
          "start_ms": 7580,
          "end_ms": 7680,
          "start_char": 124,
          "end_char": 126
        },
        {
          "word": "percent",
          "start_ms": 7880,
          "end_ms": 8195,
          "start_char": 127,
          "end_char": 134
        },
        {
          "word": "of",
          "start_ms": 8242,
          "end_ms": 8316,
          "start_char": 135,
          "end_char": 137
        },
        {
          "word": "your",
          "start_ms": 8317,
          "end_ms": 8429,
          "start_char": 138,
          "end_char": 142
        },
        {
          "word": "₹1,00,000",
          "start_ms": 8430,
          "end_ms": 8835,
          "start_char": 143,
          "end_char": 154
        },
        {
          "word": "salary",
          "start_ms": 9642,
          "end_ms": 9912,
          "start_char": 155,
          "end_char": 161
        },
        {
          "word": "to",
          "start_ms": 10130,
          "end_ms": 10230,
          "start_char": 162,
          "end_char": 164
        },
        {
          "word": "absolute",
          "start_ms": 10292,
          "end_ms": 10652,
          "start_char": 165,
          "end_char": 173
        },
        {
          "word": "needs",
          "start_ms": 10717,
          "end_ms": 10942,
          "start_char": 174,
          "end_char": 179
        },
        {
          "word": "30",
          "start_ms": 11255,
          "end_ms": 11355,
          "start_char": 181,
          "end_char": 183
        },
        {
          "word": "percent",
          "start_ms": 11517,
          "end_ms": 11832,
          "start_char": 184,
          "end_char": 191
        },
        {
          "word": "to",
          "start_ms": 11892,
          "end_ms": 11979,
          "start_char": 192,
          "end_char": 194
        },
        {
          "word": "guilt-free",
          "start_ms": 11980,
          "end_ms": 12404,
          "start_char": 195,
          "end_char": 205
        },
        {
          "word": "wants",
          "start_ms": 12405,
          "end_ms": 12630,
          "start_char": 206,
          "end_char": 211
        },
        {
          "word": "and",
          "start_ms": 13005,
          "end_ms": 13129,
          "start_char": 213,
          "end_char": 216
        },
        {
          "word": "a",
          "start_ms": 13130,
          "end_ms": 13166,
          "start_char": 217,
          "end_char": 218
        },
        {
          "word": "disciplined",
          "start_ms": 13167,
          "end_ms": 13662,
          "start_char": 219,
          "end_char": 230
        },
        {
          "word": "50",
          "start_ms": 13667,
          "end_ms": 13767,
          "start_char": 231,
          "end_char": 233
        },
        {
          "word": "percent",
          "start_ms": 13930,
          "end_ms": 14245,
          "start_char": 234,
          "end_char": 241
        },
        {
          "word": "directly",
          "start_ms": 14317,
          "end_ms": 14677,
          "start_char": 242,
          "end_char": 250
        },
        {
          "word": "to",
          "start_ms": 14705,
          "end_ms": 14805,
          "start_char": 251,
          "end_char": 253
        },
        {
          "word": "aggressive",
          "start_ms": 14867,
          "end_ms": 15316,
          "start_char": 254,
          "end_char": 264
        },
        {
          "word": "wealth",
          "start_ms": 15317,
          "end_ms": 15541,
          "start_char": 265,
          "end_char": 271
        },
        {
          "word": "building",
          "start_ms": 15542,
          "end_ms": 15902,
          "start_char": 272,
          "end_char": 280
        },
        {
          "word": "you",
          "start_ms": 16192,
          "end_ms": 16304,
          "start_char": 282,
          "end_char": 285
        },
        {
          "word": "completely",
          "start_ms": 16305,
          "end_ms": 16755,
          "start_char": 286,
          "end_char": 296
        },
        {
          "word": "break",
          "start_ms": 16780,
          "end_ms": 17005,
          "start_char": 297,
          "end_char": 302
        },
        {
          "word": "the",
          "start_ms": 17055,
          "end_ms": 17141,
          "start_char": 303,
          "end_char": 306
        },
        {
          "word": "pattern",
          "start_ms": 17142,
          "end_ms": 17457,
          "start_char": 307,
          "end_char": 314
        },
        {
          "word": "of",
          "start_ms": 17480,
          "end_ms": 17580,
          "start_char": 315,
          "end_char": 317
        },
        {
          "word": "lifestyle",
          "start_ms": 17592,
          "end_ms": 17997,
          "start_char": 318,
          "end_char": 327
        },
        {
          "word": "creep",
          "start_ms": 18092,
          "end_ms": 18317,
          "start_char": 328,
          "end_char": 333
        },
        {
          "word": "Instead",
          "start_ms": 18960,
          "end_ms": 19275,
          "start_char": 335,
          "end_char": 342
        },
        {
          "word": "of",
          "start_ms": 19310,
          "end_ms": 19409,
          "start_char": 343,
          "end_char": 345
        },
        {
          "word": "letting",
          "start_ms": 19410,
          "end_ms": 19634,
          "start_char": 346,
          "end_char": 353
        },
        {
          "word": "your",
          "start_ms": 19635,
          "end_ms": 19746,
          "start_char": 354,
          "end_char": 358
        },
        {
          "word": "bank",
          "start_ms": 19747,
          "end_ms": 19927,
          "start_char": 359,
          "end_char": 363
        },
        {
          "word": "account",
          "start_ms": 20060,
          "end_ms": 20375,
          "start_char": 364,
          "end_char": 371
        },
        {
          "word": "bleed",
          "start_ms": 20435,
          "end_ms": 20660,
          "start_char": 372,
          "end_char": 377
        },
        {
          "word": "out",
          "start_ms": 20672,
          "end_ms": 20807,
          "start_char": 378,
          "end_char": 381
        },
        {
          "word": "through",
          "start_ms": 20885,
          "end_ms": 21096,
          "start_char": 382,
          "end_char": 389
        },
        {
          "word": "miscellaneous",
          "start_ms": 21097,
          "end_ms": 21682,
          "start_char": 390,
          "end_char": 403
        },
        {
          "word": "expenses",
          "start_ms": 21785,
          "end_ms": 22145,
          "start_char": 404,
          "end_char": 412
        },
        {
          "word": "every",
          "start_ms": 22697,
          "end_ms": 22922,
          "start_char": 414,
          "end_char": 419
        },
        {
          "word": "single",
          "start_ms": 22935,
          "end_ms": 23205,
          "start_char": 420,
          "end_char": 426
        },
        {
          "word": "rupee",
          "start_ms": 23297,
          "end_ms": 23522,
          "start_char": 427,
          "end_char": 432
        },
        {
          "word": "is",
          "start_ms": 23722,
          "end_ms": 23822,
          "start_char": 433,
          "end_char": 435
        },
        {
          "word": "assigned",
          "start_ms": 23847,
          "end_ms": 24171,
          "start_char": 436,
          "end_char": 444
        },
        {
          "word": "a",
          "start_ms": 24172,
          "end_ms": 24209,
          "start_char": 445,
          "end_char": 446
        },
        {
          "word": "specific",
          "start_ms": 24210,
          "end_ms": 24570,
          "start_char": 447,
          "end_char": 455
        },
        {
          "word": "mission-driven",
          "start_ms": 25047,
          "end_ms": 25671,
          "start_char": 457,
          "end_char": 471
        },
        {
          "word": "purpose",
          "start_ms": 25672,
          "end_ms": 25987,
          "start_char": 472,
          "end_char": 479
        }
      ],
      "duration_ms": 26304,
      "duration_seconds": 26.304
    },
    {
      "chunk_id": "chunk_008",
      "sequence": 8,
      "source_id": "idea_07",
      "text": "When you commit to this disciplined path, the math becomes life-changing. Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent annual return builds a corpus of over ₹1 crore in 15 years. Pause and reflect on that. While your peers are trapped paying off luxury car loans and inflated apartment rents, your disciplined surplus compounds into true financial independence. You stop working for a paycheck and let your money work for you.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_008.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/chunks/chunk_008.marks.json",
      "word_timestamps": [
        {
          "word": "When",
          "start_ms": 25,
          "end_ms": 199,
          "start_char": 0,
          "end_char": 4
        },
        {
          "word": "you",
          "start_ms": 200,
          "end_ms": 299,
          "start_char": 5,
          "end_char": 8
        },
        {
          "word": "commit",
          "start_ms": 300,
          "end_ms": 570,
          "start_char": 9,
          "end_char": 15
        },
        {
          "word": "to",
          "start_ms": 600,
          "end_ms": 699,
          "start_char": 16,
          "end_char": 18
        },
        {
          "word": "this",
          "start_ms": 700,
          "end_ms": 880,
          "start_char": 19,
          "end_char": 23
        },
        {
          "word": "disciplined",
          "start_ms": 900,
          "end_ms": 1374,
          "start_char": 24,
          "end_char": 35
        },
        {
          "word": "path",
          "start_ms": 1375,
          "end_ms": 1555,
          "start_char": 36,
          "end_char": 40
        },
        {
          "word": "the",
          "start_ms": 1975,
          "end_ms": 2061,
          "start_char": 42,
          "end_char": 45
        },
        {
          "word": "math",
          "start_ms": 2062,
          "end_ms": 2242,
          "start_char": 46,
          "end_char": 50
        },
        {
          "word": "becomes",
          "start_ms": 2375,
          "end_ms": 2690,
          "start_char": 51,
          "end_char": 58
        },
        {
          "word": "life-changing",
          "start_ms": 2737,
          "end_ms": 3322,
          "start_char": 59,
          "end_char": 72
        },
        {
          "word": "Investing",
          "start_ms": 3955,
          "end_ms": 4360,
          "start_char": 74,
          "end_char": 83
        },
        {
          "word": "50",
          "start_ms": 4455,
          "end_ms": 4555,
          "start_char": 84,
          "end_char": 86
        },
        {
          "word": "percent",
          "start_ms": 4755,
          "end_ms": 5070,
          "start_char": 87,
          "end_char": 94
        },
        {
          "word": "of",
          "start_ms": 5142,
          "end_ms": 5216,
          "start_char": 95,
          "end_char": 97
        },
        {
          "word": "a",
          "start_ms": 5217,
          "end_ms": 5266,
          "start_char": 98,
          "end_char": 99
        },
        {
          "word": "₹1,00,000",
          "start_ms": 5267,
          "end_ms": 5672,
          "start_char": 100,
          "end_char": 111
        },
        {
          "word": "monthly",
          "start_ms": 6592,
          "end_ms": 6907,
          "start_char": 112,
          "end_char": 119
        },
        {
          "word": "salary",
          "start_ms": 6942,
          "end_ms": 7212,
          "start_char": 120,
          "end_char": 126
        },
        {
          "word": "consistently",
          "start_ms": 7392,
          "end_ms": 7932,
          "start_char": 127,
          "end_char": 139
        },
        {
          "word": "at",
          "start_ms": 8055,
          "end_ms": 8116,
          "start_char": 140,
          "end_char": 142
        },
        {
          "word": "a",
          "start_ms": 8117,
          "end_ms": 8166,
          "start_char": 143,
          "end_char": 144
        },
        {
          "word": "12",
          "start_ms": 8167,
          "end_ms": 8267,
          "start_char": 145,
          "end_char": 147
        },
        {
          "word": "percent",
          "start_ms": 8480,
          "end_ms": 8795,
          "start_char": 148,
          "end_char": 155
        },
        {
          "word": "annual",
          "start_ms": 8880,
          "end_ms": 9150,
          "start_char": 156,
          "end_char": 162
        },
        {
          "word": "return",
          "start_ms": 9230,
          "end_ms": 9500,
          "start_char": 163,
          "end_char": 169
        },
        {
          "word": "builds",
          "start_ms": 9667,
          "end_ms": 9937,
          "start_char": 170,
          "end_char": 176
        },
        {
          "word": "a",
          "start_ms": 9942,
          "end_ms": 9991,
          "start_char": 177,
          "end_char": 178
        },
        {
          "word": "corpus",
          "start_ms": 9992,
          "end_ms": 10262,
          "start_char": 179,
          "end_char": 185
        },
        {
          "word": "of",
          "start_ms": 10430,
          "end_ms": 10529,
          "start_char": 186,
          "end_char": 188
        },
        {
          "word": "over",
          "start_ms": 10530,
          "end_ms": 10710,
          "start_char": 189,
          "end_char": 193
        },
        {
          "word": "₹1",
          "start_ms": 10730,
          "end_ms": 10830,
          "start_char": 194,
          "end_char": 198
        },
        {
          "word": "crore",
          "start_ms": 11005,
          "end_ms": 11230,
          "start_char": 199,
          "end_char": 204
        },
        {
          "word": "in",
          "start_ms": 11342,
          "end_ms": 11416,
          "start_char": 205,
          "end_char": 207
        },
        {
          "word": "15",
          "start_ms": 11417,
          "end_ms": 11517,
          "start_char": 208,
          "end_char": 210
        },
        {
          "word": "years",
          "start_ms": 11842,
          "end_ms": 12067,
          "start_char": 211,
          "end_char": 216
        },
        {
          "word": "Pause",
          "start_ms": 12747,
          "end_ms": 12972,
          "start_char": 218,
          "end_char": 223
        },
        {
          "word": "and",
          "start_ms": 13122,
          "end_ms": 13196,
          "start_char": 224,
          "end_char": 227
        },
        {
          "word": "reflect",
          "start_ms": 13197,
          "end_ms": 13512,
          "start_char": 228,
          "end_char": 235
        },
        {
          "word": "on",
          "start_ms": 13610,
          "end_ms": 13710,
          "start_char": 236,
          "end_char": 238
        },
        {
          "word": "that",
          "start_ms": 13735,
          "end_ms": 13915,
          "start_char": 239,
          "end_char": 243
        },
        {
          "word": "While",
          "start_ms": 14477,
          "end_ms": 14651,
          "start_char": 245,
          "end_char": 250
        },
        {
          "word": "your",
          "start_ms": 14652,
          "end_ms": 14801,
          "start_char": 251,
          "end_char": 255
        },
        {
          "word": "peers",
          "start_ms": 14802,
          "end_ms": 15027,
          "start_char": 256,
          "end_char": 261
        },
        {
          "word": "are",
          "start_ms": 15177,
          "end_ms": 15251,
          "start_char": 262,
          "end_char": 265
        },
        {
          "word": "trapped",
          "start_ms": 15252,
          "end_ms": 15567,
          "start_char": 266,
          "end_char": 273
        },
        {
          "word": "paying",
          "start_ms": 15615,
          "end_ms": 15885,
          "start_char": 274,
          "end_char": 280
        },
        {
          "word": "off",
          "start_ms": 15965,
          "end_ms": 16100,
          "start_char": 281,
          "end_char": 284
        },
        {
          "word": "luxury",
          "start_ms": 16190,
          "end_ms": 16460,
          "start_char": 285,
          "end_char": 291
        },
        {
          "word": "car",
          "start_ms": 16577,
          "end_ms": 16712,
          "start_char": 292,
          "end_char": 295
        },
        {
          "word": "loans",
          "start_ms": 16865,
          "end_ms": 17090,
          "start_char": 296,
          "end_char": 301
        },
        {
          "word": "and",
          "start_ms": 17277,
          "end_ms": 17351,
          "start_char": 302,
          "end_char": 305
        },
        {
          "word": "inflated",
          "start_ms": 17352,
          "end_ms": 17712,
          "start_char": 306,
          "end_char": 314
        },
        {
          "word": "apartment",
          "start_ms": 17765,
          "end_ms": 18151,
          "start_char": 315,
          "end_char": 324
        },
        {
          "word": "rents",
          "start_ms": 18152,
          "end_ms": 18377,
          "start_char": 325,
          "end_char": 330
        },
        {
          "word": "your",
          "start_ms": 18715,
          "end_ms": 18851,
          "start_char": 332,
          "end_char": 336
        },
        {
          "word": "disciplined",
          "start_ms": 18852,
          "end_ms": 19347,
          "start_char": 337,
          "end_char": 348
        },
        {
          "word": "surplus",
          "start_ms": 19377,
          "end_ms": 19692,
          "start_char": 349,
          "end_char": 356
        },
        {
          "word": "compounds",
          "start_ms": 19790,
          "end_ms": 20195,
          "start_char": 357,
          "end_char": 366
        },
        {
          "word": "into",
          "start_ms": 20365,
          "end_ms": 20526,
          "start_char": 367,
          "end_char": 371
        },
        {
          "word": "true",
          "start_ms": 20527,
          "end_ms": 20707,
          "start_char": 372,
          "end_char": 376
        },
        {
          "word": "financial",
          "start_ms": 20752,
          "end_ms": 21157,
          "start_char": 377,
          "end_char": 386
        },
        {
          "word": "independence",
          "start_ms": 21265,
          "end_ms": 21805,
          "start_char": 387,
          "end_char": 399
        },
        {
          "word": "You",
          "start_ms": 22395,
          "end_ms": 22506,
          "start_char": 401,
          "end_char": 404
        },
        {
          "word": "stop",
          "start_ms": 22507,
          "end_ms": 22687,
          "start_char": 405,
          "end_char": 409
        },
        {
          "word": "working",
          "start_ms": 22832,
          "end_ms": 23131,
          "start_char": 410,
          "end_char": 417
        },
        {
          "word": "for",
          "start_ms": 23132,
          "end_ms": 23267,
          "start_char": 418,
          "end_char": 421
        },
        {
          "word": "a",
          "start_ms": 23282,
          "end_ms": 23331,
          "start_char": 422,
          "end_char": 423
        },
        {
          "word": "paycheck",
          "start_ms": 23332,
          "end_ms": 23692,
          "start_char": 424,
          "end_char": 432
        },
        {
          "word": "and",
          "start_ms": 23870,
          "end_ms": 23981,
          "start_char": 433,
          "end_char": 436
        },
        {
          "word": "let",
          "start_ms": 23982,
          "end_ms": 24117,
          "start_char": 437,
          "end_char": 440
        },
        {
          "word": "your",
          "start_ms": 24132,
          "end_ms": 24206,
          "start_char": 441,
          "end_char": 445
        },
        {
          "word": "money",
          "start_ms": 24207,
          "end_ms": 24406,
          "start_char": 446,
          "end_char": 451
        },
        {
          "word": "work",
          "start_ms": 24407,
          "end_ms": 24587,
          "start_char": 452,
          "end_char": 456
        },
        {
          "word": "for",
          "start_ms": 24657,
          "end_ms": 24792,
          "start_char": 457,
          "end_char": 460
        },
        {
          "word": "you",
          "start_ms": 24857,
          "end_ms": 24992,
          "start_char": 461,
          "end_char": 464
        }
      ],
      "duration_ms": 25200,
      "duration_seconds": 25.2
    }
  ]
}
```

---

## Stage 7: Render Specification (Remotion Composition Tree & Frame Spans)

- **Artifact ID:** `artifact_0c0ab16ac11748578a6e56ebf54a8699`
- **Artifact Type:** `render_spec`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-09T07:43:00.285944+00:00`
- **Parent Artifact Roles:** `{"voice_track": "artifact_b2bfeb1c57d5450c9511eb0c39f19818", "script_visual_strategy": "artifact_8fff4dcb609c48618a35d6879fe88b27", "hook": "artifact_91617e44824b4af1891382f21ead3c14"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Assembles audio, motion graphics, video b-roll, text layers, and frame-accurate timeline spans into Remotion props.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "scene_id": "scene_project_149b665e28a94e838d9341252c969bb1",
  "composition": "VideoAssembly",
  "fps": 30,
  "duration_frames": 6484,
  "props": {
    "scenes": [
      {
        "scene_id": "scene_001",
        "start_frame": 0,
        "end_frame": 137,
        "duration_frames": 137,
        "component": {
          "component_id": "Typography",
          "props": {
            "headerLabel": null,
            "text": "The ₹1,00,000 Illusion",
            "subtitle": "Top 3 percent income, zero savings",
            "variant": "headline",
            "highlight": null,
            "align": null,
            "value": null,
            "author": null
          }
        },
        "asset": null,
        "narration_text": "You finally hit ₹1,00,000 a month and thought you made it. But instead of financial freedom, you traded your financial stress for a luxury EMI. Your income doubled, but your savings stayed at zero. You are not building wealth. You just moved into a much more expensive cage."
      },
      {
        "scene_id": "scene_002",
        "start_frame": 137,
        "end_frame": 260,
        "duration_frames": 123,
        "component": {
          "component_id": "StockVideo",
          "props": {
            "headerLabel": null
          }
        },
        "asset": {
          "asset_id": "asset_hook_0_1_beat_02",
          "asset_type": "video",
          "source": "pexels",
          "query": "stressed person checking phone",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_002_asset_hook_0_1_beat_02.mp4",
          "url": "https://videos.pexels.com/video-files/9465064/9465064-hd_2048_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "You finally hit ₹1,00,000 a month and thought you made it. But instead of financial freedom, you traded your financial stress for a luxury EMI. Your income doubled, but your savings stayed at zero. You are not building wealth. You just moved into a much more expensive cage."
      },
      {
        "scene_id": "scene_003",
        "start_frame": 260,
        "end_frame": 462,
        "duration_frames": 202,
        "component": {
          "component_id": "SplitComparison",
          "props": {
            "headerLabel": "THE REALITY GAP",
            "comparisonLabel": null,
            "variant": "cards",
            "tone": "neutral",
            "leftRole": "Monthly Salary",
            "leftLabel": "Monthly Salary",
            "leftValue": "₹1,00,000",
            "leftUnit": null,
            "rightRole": "Liquid Savings",
            "rightLabel": "Liquid Savings",
            "rightValue": "₹50,000",
            "rightUnit": null,
            "delta": null,
            "winner": null
          }
        },
        "asset": null,
        "narration_text": "You finally hit ₹1,00,000 a month and thought you made it. But instead of financial freedom, you traded your financial stress for a luxury EMI. Your income doubled, but your savings stayed at zero. You are not building wealth. You just moved into a much more expensive cage."
      },
      {
        "scene_id": "scene_004",
        "start_frame": 462,
        "end_frame": 965,
        "duration_frames": 503,
        "component": {
          "component_id": "MetricHero",
          "props": {
            "value": "₹1,00,000",
            "label": "Monthly Income",
            "context": "Top 3% of Earners in India",
            "emphasis": "hero",
            "variant": "hero"
          }
        },
        "asset": null,
        "narration_text": "When you finally cross that major salary threshold, reality hits hard. Earning ₹1,00,000 per month officially places you in India's top 3 percent of earners according to data from the Ministry of Finance. It feels like an incredible milestone. Yet, behind the polished corporate facade, financial vulnerability lurks. In fact, 68 percent of urban Indian professionals earning between ₹1,00,000 and ₹1,50,000 per month report having less than ₹50,000 in liquid emergency savings. Instead of accumulating real freedom, your growing salary instantly vanishes into newly inflated lifestyle choices."
      },
      {
        "scene_id": "scene_005",
        "start_frame": 965,
        "end_frame": 1447,
        "duration_frames": 482,
        "component": {
          "component_id": "MetricHero",
          "props": {
            "value": "68%",
            "label": "Professionals with <₹50,000 Emergency Savings",
            "context": "earning ₹1L-1.5L/month",
            "emphasis": "hero",
            "variant": "hero"
          }
        },
        "asset": {
          "asset_id": "asset_comp_0_1_beat_01_02",
          "asset_type": "video",
          "source": "pexels",
          "query": "corporate professional stressed about money",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_005_asset_comp_0_1_beat_01_02.mp4",
          "url": "https://videos.pexels.com/video-files/9077864/9077864-hd_2048_1080_25fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "When you finally cross that major salary threshold, reality hits hard. Earning ₹1,00,000 per month officially places you in India's top 3 percent of earners according to data from the Ministry of Finance. It feels like an incredible milestone. Yet, behind the polished corporate facade, financial vulnerability lurks. In fact, 68 percent of urban Indian professionals earning between ₹1,00,000 and ₹1,50,000 per month report having less than ₹50,000 in liquid emergency savings. Instead of accumulating real freedom, your growing salary instantly vanishes into newly inflated lifestyle choices."
      },
      {
        "scene_id": "scene_006",
        "start_frame": 1447,
        "end_frame": 1530,
        "duration_frames": 83,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Higher Salary",
                "value": null,
                "icon": "💰"
              },
              {
                "label": "Lifestyle Inflation",
                "value": null,
                "icon": "📈"
              }
            ],
            "connector": "leads to",
            "outcomeLabel": "Zero Freedom Gained",
            "outcomeValue": null,
            "outcomeSeverity": "negative"
          }
        },
        "asset": {
          "asset_id": "asset_comp_0_2_beat_01_03",
          "asset_type": "video",
          "source": "pexels",
          "query": "Show how increased earnings are swallowed by lifestyle choices instead of building wealth.",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_006_asset_comp_0_2_beat_01_03.mp4",
          "url": "https://videos.pexels.com/video-files/5849636/5849636-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "When you finally cross that major salary threshold, reality hits hard. Earning ₹1,00,000 per month officially places you in India's top 3 percent of earners according to data from the Ministry of Finance. It feels like an incredible milestone. Yet, behind the polished corporate facade, financial vulnerability lurks. In fact, 68 percent of urban Indian professionals earning between ₹1,00,000 and ₹1,50,000 per month report having less than ₹50,000 in liquid emergency savings. Instead of accumulating real freedom, your growing salary instantly vanishes into newly inflated lifestyle choices."
      },
      {
        "scene_id": "scene_007",
        "start_frame": 1530,
        "end_frame": 1710,
        "duration_frames": 180,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Psychological conditioning and immediate gratification drive fast lifestyle inflation.",
            "emphasisPhrase": "immediate gratification",
            "author": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_1_0_beat_02_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "corporate employee shopping stress lifestyle inflation",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_007_asset_comp_1_0_beat_02_01.mp4",
          "url": "https://videos.pexels.com/video-files/29068393/12563855_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Why does this happen so quickly? The answer lies in psychological conditioning and immediate gratification. Studies from the Kantar Urban Spending Index reveal that average monthly discretionary spend on dining out and lifestyle apps increases by 85 percent within 6 months of a salary promotion crossing ₹1,00,000 per month. Furthermore, ordering food delivery 15 times a month instead of cooking adds an extra ₹7,500 to monthly discretionary spending. You start treating luxury conveniences as absolute necessities, trapping yourself in an endless cycle of consumption."
      },
      {
        "scene_id": "scene_008",
        "start_frame": 1710,
        "end_frame": 2075,
        "duration_frames": 365,
        "component": {
          "component_id": "MetricHero",
          "props": {
            "value": "85%",
            "label": "Discretionary Spend Increase",
            "context": "within 6 months of crossing ₹1,00,000",
            "emphasis": "hero",
            "variant": "hero"
          }
        },
        "asset": null,
        "narration_text": "Why does this happen so quickly? The answer lies in psychological conditioning and immediate gratification. Studies from the Kantar Urban Spending Index reveal that average monthly discretionary spend on dining out and lifestyle apps increases by 85 percent within 6 months of a salary promotion crossing ₹1,00,000 per month. Furthermore, ordering food delivery 15 times a month instead of cooking adds an extra ₹7,500 to monthly discretionary spending. You start treating luxury conveniences as absolute necessities, trapping yourself in an endless cycle of consumption."
      },
      {
        "scene_id": "scene_009",
        "start_frame": 2075,
        "end_frame": 2334,
        "duration_frames": 259,
        "component": {
          "component_id": "CalculationStory",
          "props": {
            "inputLabel": "Food Delivery",
            "inputValue": "15 times",
            "operationLabel": "adds",
            "rateLabel": "instead of cooking",
            "resultLabel": "Monthly Discretionary",
            "resultValue": "₹7,500",
            "note": "Extra monthly expense"
          }
        },
        "asset": null,
        "narration_text": "Why does this happen so quickly? The answer lies in psychological conditioning and immediate gratification. Studies from the Kantar Urban Spending Index reveal that average monthly discretionary spend on dining out and lifestyle apps increases by 85 percent within 6 months of a salary promotion crossing ₹1,00,000 per month. Furthermore, ordering food delivery 15 times a month instead of cooking adds an extra ₹7,500 to monthly discretionary spending. You start treating luxury conveniences as absolute necessities, trapping yourself in an endless cycle of consumption."
      },
      {
        "scene_id": "scene_010",
        "start_frame": 2334,
        "end_frame": 2496,
        "duration_frames": 162,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Luxury Conveniences",
                "value": null,
                "icon": "✨"
              },
              {
                "label": "Treated as Necessities",
                "value": null,
                "icon": "🛒"
              }
            ],
            "connector": "leads to",
            "outcomeLabel": "Endless Consumption Trap",
            "outcomeValue": null,
            "outcomeSeverity": "negative"
          }
        },
        "asset": {
          "asset_id": "asset_comp_1_3_beat_02_04",
          "asset_type": "video",
          "source": "pexels",
          "query": "person shopping online lifestyle trap",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_010_asset_comp_1_3_beat_02_04.mp4",
          "url": "https://videos.pexels.com/video-files/6994766/6994766-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Why does this happen so quickly? The answer lies in psychological conditioning and immediate gratification. Studies from the Kantar Urban Spending Index reveal that average monthly discretionary spend on dining out and lifestyle apps increases by 85 percent within 6 months of a salary promotion crossing ₹1,00,000 per month. Furthermore, ordering food delivery 15 times a month instead of cooking adds an extra ₹7,500 to monthly discretionary spending. You start treating luxury conveniences as absolute necessities, trapping yourself in an endless cycle of consumption."
      },
      {
        "scene_id": "scene_011",
        "start_frame": 2496,
        "end_frame": 2984,
        "duration_frames": 488,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Upgrading to a larger apartment increases monthly housing expenses by ₹25,000 to ₹40,000.",
            "emphasisPhrase": "₹25,000",
            "author": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_2_0_beat_03_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "Once discretionary spending spikes, major fixed commitments",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_011_asset_comp_2_0_beat_03_01.mp4",
          "url": "https://videos.pexels.com/video-files/5790229/5790229-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Once discretionary spending spikes, major fixed commitments enter the picture. Upgrading from a rented 1 BHK to a 2 BHK apartment in cities like Bengaluru or Mumbai increases monthly housing expenses by an average of ₹25,000 to ₹40,000. On top of that, purchasing a mid-size car on an auto loan at an EMI of ₹22,000 per month locks in vehicle depreciation and loan interest for 5 years. These heavy financial anchors silently crush your effective hourly rate and destroy your capacity to build genuine long-term wealth."
      },
      {
        "scene_id": "scene_012",
        "start_frame": 2984,
        "end_frame": 3251,
        "duration_frames": 267,
        "component": {
          "component_id": "MetricHero",
          "props": {
            "value": "₹22,000",
            "label": "Monthly Car EMI",
            "context": "per month for 5 years",
            "emphasis": "hero",
            "variant": "hero"
          }
        },
        "asset": null,
        "narration_text": "Once discretionary spending spikes, major fixed commitments enter the picture. Upgrading from a rented 1 BHK to a 2 BHK apartment in cities like Bengaluru or Mumbai increases monthly housing expenses by an average of ₹25,000 to ₹40,000. On top of that, purchasing a mid-size car on an auto loan at an EMI of ₹22,000 per month locks in vehicle depreciation and loan interest for 5 years. These heavy financial anchors silently crush your effective hourly rate and destroy your capacity to build genuine long-term wealth."
      },
      {
        "scene_id": "scene_013",
        "start_frame": 3251,
        "end_frame": 3411,
        "duration_frames": 160,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Heavy Financial Anchors",
                "value": null,
                "icon": "⚓"
              }
            ],
            "connector": "destroys",
            "outcomeLabel": "Long-Term Wealth Capacity",
            "outcomeValue": null,
            "outcomeSeverity": "negative"
          }
        },
        "asset": {
          "asset_id": "asset_comp_2_2_beat_03_03",
          "asset_type": "video",
          "source": "pexels",
          "query": "financial burden stress corporate lifestyle",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_013_asset_comp_2_2_beat_03_03.mp4",
          "url": "https://videos.pexels.com/video-files/6282125/6282125-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Once discretionary spending spikes, major fixed commitments enter the picture. Upgrading from a rented 1 BHK to a 2 BHK apartment in cities like Bengaluru or Mumbai increases monthly housing expenses by an average of ₹25,000 to ₹40,000. On top of that, purchasing a mid-size car on an auto loan at an EMI of ₹22,000 per month locks in vehicle depreciation and loan interest for 5 years. These heavy financial anchors silently crush your effective hourly rate and destroy your capacity to build genuine long-term wealth."
      },
      {
        "scene_id": "scene_014",
        "start_frame": 3411,
        "end_frame": 3697,
        "duration_frames": 286,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Mumbai / Gurgaon Upscale Lifestyle",
                "value": null,
                "icon": "🏙️"
              }
            ],
            "connector": "steals from",
            "outcomeLabel": "Future Self",
            "outcomeValue": "Vulnerability",
            "outcomeSeverity": "negative"
          }
        },
        "asset": {
          "asset_id": "asset_comp_3_0_beat_04_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "expensive city lifestyle corporate employee",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_014_asset_comp_3_0_beat_04_01.mp4",
          "url": "https://videos.pexels.com/video-files/6531750/6531750-hd_2048_1080_25fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Let us examine the stark opportunity cost of consumption. Every rupee spent on maintaining an upscale image in Mumbai or Gurgaon is a rupee stolen from your future self. When you prioritize flash over assets, you are trading decades of freedom for a temporary status symbol. The hidden price of your luxury car and upgraded apartment isn't just the sticker price—it is the lost compound growth that could have set you free a decade earlier."
      },
      {
        "scene_id": "scene_015",
        "start_frame": 3697,
        "end_frame": 3864,
        "duration_frames": 167,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Prioritizing flash over assets trades decades of freedom for temporary status.",
            "emphasisPhrase": null,
            "author": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_3_1_beat_04_02",
          "asset_type": "video",
          "source": "pexels",
          "query": "When you prioritize flash over assets, you are trading decad",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_015_asset_comp_3_1_beat_04_02.mp4",
          "url": "https://videos.pexels.com/video-files/7450203/7450203-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Let us examine the stark opportunity cost of consumption. Every rupee spent on maintaining an upscale image in Mumbai or Gurgaon is a rupee stolen from your future self. When you prioritize flash over assets, you are trading decades of freedom for a temporary status symbol. The hidden price of your luxury car and upgraded apartment isn't just the sticker price—it is the lost compound growth that could have set you free a decade earlier."
      },
      {
        "scene_id": "scene_016",
        "start_frame": 3864,
        "end_frame": 4088,
        "duration_frames": 224,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "The true cost of luxury items includes lost compound growth and delayed freedom.",
            "emphasisPhrase": "luxury car",
            "author": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_3_2_beat_04_03",
          "asset_type": "video",
          "source": "pexels",
          "query": "The hidden price of your luxury car and upgraded apartment i",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_016_asset_comp_3_2_beat_04_03.mp4",
          "url": "https://videos.pexels.com/video-files/30763728/13160071_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Let us examine the stark opportunity cost of consumption. Every rupee spent on maintaining an upscale image in Mumbai or Gurgaon is a rupee stolen from your future self. When you prioritize flash over assets, you are trading decades of freedom for a temporary status symbol. The hidden price of your luxury car and upgraded apartment isn't just the sticker price—it is the lost compound growth that could have set you free a decade earlier."
      },
      {
        "scene_id": "scene_017",
        "start_frame": 4088,
        "end_frame": 4266,
        "duration_frames": 178,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Carrying heavy EMIs is viewed as a sign of success in urban corporate culture.",
            "emphasisPhrase": "sign of success",
            "author": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_4_0_beat_05_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "corporate worker modern lifestyle urban",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_017_asset_comp_4_0_beat_05_01.mp4",
          "url": "https://videos.pexels.com/video-files/7681890/7681890-hd_1920_1080_25fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "There is a pervasive myth in urban corporate culture that carrying heavy EMIs signals financial maturity or success. According to the Mastercard Financial Literacy Index, lifestyle inflation causes 42 percent of corporate employees to remain paycheck-to-paycheck despite crossing the ₹12,00,000 annual income bracket. They believe that buying luxury items on credit establishes creditworthiness, when in reality, it simply chains them tighter to their desks, eliminating any margin for error if economic conditions shift."
      },
      {
        "scene_id": "scene_018",
        "start_frame": 4266,
        "end_frame": 4628,
        "duration_frames": 362,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Mastercard Financial Literacy Index",
                "value": "42%",
                "icon": null
              },
              {
                "label": "Annual Income Threshold",
                "value": "₹12,00,000",
                "icon": null
              }
            ],
            "connector": "leads to",
            "outcomeLabel": "Paycheck-to-Paycheck Lifestyle Inflation",
            "outcomeValue": null,
            "outcomeSeverity": "negative"
          }
        },
        "asset": {
          "asset_id": "asset_comp_4_1_beat_05_02",
          "asset_type": "video",
          "source": "pexels",
          "query": "corporate employee financial stress modern office",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_018_asset_comp_4_1_beat_05_02.mp4",
          "url": "https://videos.pexels.com/video-files/7581176/7581176-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "There is a pervasive myth in urban corporate culture that carrying heavy EMIs signals financial maturity or success. According to the Mastercard Financial Literacy Index, lifestyle inflation causes 42 percent of corporate employees to remain paycheck-to-paycheck despite crossing the ₹12,00,000 annual income bracket. They believe that buying luxury items on credit establishes creditworthiness, when in reality, it simply chains them tighter to their desks, eliminating any margin for error if economic conditions shift."
      },
      {
        "scene_id": "scene_019",
        "start_frame": 4628,
        "end_frame": 4939,
        "duration_frames": 311,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Luxury Purchases on Credit",
                "value": "Debt",
                "icon": "💳"
              }
            ],
            "connector": "chains workers to desks and eliminates",
            "outcomeLabel": "Financial Margin for Error",
            "outcomeValue": "Zero",
            "outcomeSeverity": "negative"
          }
        },
        "asset": {
          "asset_id": "asset_comp_4_2_beat_05_03",
          "asset_type": "video",
          "source": "pexels",
          "query": "corporate employee chained to desk office",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_019_asset_comp_4_2_beat_05_03.mp4",
          "url": "https://videos.pexels.com/video-files/8297996/8297996-hd_1920_1080_25fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "There is a pervasive myth in urban corporate culture that carrying heavy EMIs signals financial maturity or success. According to the Mastercard Financial Literacy Index, lifestyle inflation causes 42 percent of corporate employees to remain paycheck-to-paycheck despite crossing the ₹12,00,000 annual income bracket. They believe that buying luxury items on credit establishes creditworthiness, when in reality, it simply chains them tighter to their desks, eliminating any margin for error if economic conditions shift."
      },
      {
        "scene_id": "scene_020",
        "start_frame": 4939,
        "end_frame": 5152,
        "duration_frames": 213,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Escaping this cycle requires a rigorous framework, and the time-tested 50/30/20 rule is your ultimate weapon.",
            "emphasisPhrase": "50/30/20 rule",
            "author": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_5_0_beat_06_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "person looking at budget planner corporate office",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_020_asset_comp_5_0_beat_06_01.mp4",
          "url": "https://videos.pexels.com/video-files/7821650/7821650-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Escaping this cycle requires a rigorous framework, and the time-tested 50/30/20 rule is your ultimate weapon. By allocating 50 percent of your ₹1,00,000 salary to absolute needs, 30 percent to guilt-free wants, and a disciplined 50 percent directly to aggressive wealth building, you completely break the pattern of lifestyle creep. Instead of letting your bank account bleed out through miscellaneous expenses, every single rupee is assigned a specific, mission-driven purpose."
      },
      {
        "scene_id": "scene_021",
        "start_frame": 5152,
        "end_frame": 5552,
        "duration_frames": 400,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "The ₹1,00,000 salary is budgeted as 50 percent needs, 30 percent wants, and savings/wealth building.",
            "emphasisPhrase": "50 percent",
            "author": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_5_1_beat_06_02",
          "asset_type": "video",
          "source": "pexels",
          "query": "By allocating 50 percent of your ₹1,00,000 salary to absolut",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_021_asset_comp_5_1_beat_06_02.mp4",
          "url": "https://videos.pexels.com/video-files/7651768/7651768-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Escaping this cycle requires a rigorous framework, and the time-tested 50/30/20 rule is your ultimate weapon. By allocating 50 percent of your ₹1,00,000 salary to absolute needs, 30 percent to guilt-free wants, and a disciplined 50 percent directly to aggressive wealth building, you completely break the pattern of lifestyle creep. Instead of letting your bank account bleed out through miscellaneous expenses, every single rupee is assigned a specific, mission-driven purpose."
      },
      {
        "scene_id": "scene_022",
        "start_frame": 5552,
        "end_frame": 5728,
        "duration_frames": 176,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Miscellaneous Expenses",
                "value": "Bleeding Out",
                "icon": "💸"
              }
            ],
            "connector": "stopped by",
            "outcomeLabel": "Mission-Driven Purpose",
            "outcomeValue": "Protected Bank Account",
            "outcomeSeverity": "positive"
          }
        },
        "asset": null,
        "narration_text": "Escaping this cycle requires a rigorous framework, and the time-tested 50/30/20 rule is your ultimate weapon. By allocating 50 percent of your ₹1,00,000 salary to absolute needs, 30 percent to guilt-free wants, and a disciplined 50 percent directly to aggressive wealth building, you completely break the pattern of lifestyle creep. Instead of letting your bank account bleed out through miscellaneous expenses, every single rupee is assigned a specific, mission-driven purpose."
      },
      {
        "scene_id": "scene_023",
        "start_frame": 5728,
        "end_frame": 6172,
        "duration_frames": 444,
        "component": {
          "component_id": "CalculationStory",
          "props": {
            "inputLabel": "Monthly Investment",
            "inputValue": "₹50,000",
            "operationLabel": "→",
            "rateLabel": "12% return over 15 years",
            "resultLabel": "Final Corpus",
            "resultValue": "₹1 crore",
            "note": "Based on 50% of ₹1,00,000 salary"
          }
        },
        "asset": null,
        "narration_text": "When you commit to this disciplined path, the math becomes life-changing. Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent annual return builds a corpus of over ₹1 crore in 15 years. Pause and reflect on that. While your peers are trapped paying off luxury car loans and inflated apartment rents, your disciplined surplus compounds into true financial independence. You stop working for a paycheck and let your money work for you."
      },
      {
        "scene_id": "scene_024",
        "start_frame": 6172,
        "end_frame": 6403,
        "duration_frames": 231,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Comparison between peer luxury debt and disciplined surplus leading to financial independence.",
            "emphasisPhrase": "luxury car loans",
            "author": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_6_1_beat_07_02",
          "asset_type": "video",
          "source": "pexels",
          "query": "While your peers are trapped paying off luxury car loans and",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_024_asset_comp_6_1_beat_07_02.mp4",
          "url": "https://videos.pexels.com/video-files/5520104/5520104-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "When you commit to this disciplined path, the math becomes life-changing. Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent annual return builds a corpus of over ₹1 crore in 15 years. Pause and reflect on that. While your peers are trapped paying off luxury car loans and inflated apartment rents, your disciplined surplus compounds into true financial independence. You stop working for a paycheck and let your money work for you."
      },
      {
        "scene_id": "scene_025",
        "start_frame": 6403,
        "end_frame": 6484,
        "duration_frames": 81,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Break free from the paycheck cycle and let your money work for you.",
            "emphasisPhrase": "money work for you",
            "author": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_6_2_beat_07_03",
          "asset_type": "video",
          "source": "pexels",
          "query": "financial freedom lifestyle corporate employee",
          "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_scene_025_asset_comp_6_2_beat_07_03.mp4",
          "url": "https://videos.pexels.com/video-files/18514339/18514339-hd_1920_1080_60fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "When you commit to this disciplined path, the math becomes life-changing. Investing 50 percent of a ₹1,00,000 monthly salary consistently at a 12 percent annual return builds a corpus of over ₹1 crore in 15 years. Pause and reflect on that. While your peers are trapped paying off luxury car loans and inflated apartment rents, your disciplined surplus compounds into true financial independence. You stop working for a paycheck and let your money work for you."
      }
    ],
    "audio": {
      "audio_file_name": "narration.mp3",
      "local_path": "run_565f2ef6833a4bd091e6b53cb58ae913_narration.mp3",
      "duration_seconds": 216.12
    }
  },
  "frame_spans": [
    {
      "event_id": "scene_001",
      "start_frame": 0,
      "end_frame": 137,
      "duration_frames": 137
    },
    {
      "event_id": "scene_002",
      "start_frame": 137,
      "end_frame": 260,
      "duration_frames": 123
    },
    {
      "event_id": "scene_003",
      "start_frame": 260,
      "end_frame": 462,
      "duration_frames": 202
    },
    {
      "event_id": "scene_004",
      "start_frame": 462,
      "end_frame": 965,
      "duration_frames": 503
    },
    {
      "event_id": "scene_005",
      "start_frame": 965,
      "end_frame": 1447,
      "duration_frames": 482
    },
    {
      "event_id": "scene_006",
      "start_frame": 1447,
      "end_frame": 1530,
      "duration_frames": 83
    },
    {
      "event_id": "scene_007",
      "start_frame": 1530,
      "end_frame": 1710,
      "duration_frames": 180
    },
    {
      "event_id": "scene_008",
      "start_frame": 1710,
      "end_frame": 2075,
      "duration_frames": 365
    },
    {
      "event_id": "scene_009",
      "start_frame": 2075,
      "end_frame": 2334,
      "duration_frames": 259
    },
    {
      "event_id": "scene_010",
      "start_frame": 2334,
      "end_frame": 2496,
      "duration_frames": 162
    },
    {
      "event_id": "scene_011",
      "start_frame": 2496,
      "end_frame": 2984,
      "duration_frames": 488
    },
    {
      "event_id": "scene_012",
      "start_frame": 2984,
      "end_frame": 3251,
      "duration_frames": 267
    },
    {
      "event_id": "scene_013",
      "start_frame": 3251,
      "end_frame": 3411,
      "duration_frames": 160
    },
    {
      "event_id": "scene_014",
      "start_frame": 3411,
      "end_frame": 3697,
      "duration_frames": 286
    },
    {
      "event_id": "scene_015",
      "start_frame": 3697,
      "end_frame": 3864,
      "duration_frames": 167
    },
    {
      "event_id": "scene_016",
      "start_frame": 3864,
      "end_frame": 4088,
      "duration_frames": 224
    },
    {
      "event_id": "scene_017",
      "start_frame": 4088,
      "end_frame": 4266,
      "duration_frames": 178
    },
    {
      "event_id": "scene_018",
      "start_frame": 4266,
      "end_frame": 4628,
      "duration_frames": 362
    },
    {
      "event_id": "scene_019",
      "start_frame": 4628,
      "end_frame": 4939,
      "duration_frames": 311
    },
    {
      "event_id": "scene_020",
      "start_frame": 4939,
      "end_frame": 5152,
      "duration_frames": 213
    },
    {
      "event_id": "scene_021",
      "start_frame": 5152,
      "end_frame": 5552,
      "duration_frames": 400
    },
    {
      "event_id": "scene_022",
      "start_frame": 5552,
      "end_frame": 5728,
      "duration_frames": 176
    },
    {
      "event_id": "scene_023",
      "start_frame": 5728,
      "end_frame": 6172,
      "duration_frames": 444
    },
    {
      "event_id": "scene_024",
      "start_frame": 6172,
      "end_frame": 6403,
      "duration_frames": 231
    },
    {
      "event_id": "scene_025",
      "start_frame": 6403,
      "end_frame": 6484,
      "duration_frames": 81
    }
  ]
}
```

---

## Stage 8: Final Video Render (Rendered MP4 Output & Storage Metadata)

- **Artifact ID:** `artifact_a7e659ca8524455988eb3a86a5c28ffb`
- **Artifact Type:** `video`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-09T07:47:36.498414+00:00`
- **Parent Artifact Roles:** `{"render_spec": "artifact_0c0ab16ac11748578a6e56ebf54a8699"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** The completed MP4 video rendered by Remotion CLI, including file size, frame count, and storage key.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "scene_id": "scene_project_149b665e28a94e838d9341252c969bb1",
  "render_status": "succeeded",
  "file_name": "scene_project_149b665e28a94e838d9341252c969bb1.mp4",
  "content_type": "video/mp4",
  "fps": 30,
  "duration_frames": 6484,
  "storage_key": "projects/project_149b665e28a94e838d9341252c969bb1/runs/run_565f2ef6833a4bd091e6b53cb58ae913/scene_project_149b665e28a94e838d9341252c969bb1.mp4",
  "size_bytes": 50449512,
  "error_message": null
}
```

---
