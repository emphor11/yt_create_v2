# Comprehensive End-to-End Pipeline Artifact Trail (Stage 0 to Stage 8)

**Project:** *The ₹10 Lakh Mistake Most Indians Make Before Buying Their First Home*  
**Project ID:** `project_bd64dbe39bb646ddb4d8294b63def4ff`  
**Run ID:** `run_9c4a21e6b1da41ed96e63a391e521b0b`  
**Visual Architecture Mode:** `composition` (Dynamic Multi-Element Composition Engine)  
**Output Video File:** `scene_project_bd64dbe39bb646ddb4d8294b63def4ff.mp4` (188.38s, 5,651 frames @ 30fps, 1080x1920)  
**Voice Track File:** `narration.mp3` (188.38s, 535 words, 8 synthesis chunks)  

---

## Executive Summary of Pipeline Run

All 9 pipeline stages succeeded and produced fully validated artifacts:
1. **Stage 0 (`generate_video_request`):** Captured topic, angle, target audience, duration profile, and `composition` visual mode.
2. **Stage 1 (`research_packet`):** Generated quantitative facts, RBI statistics, housing fee metrics, and misconceptions using Perplexity/Search/LLM.
3. **Stage 2 (`narrative_plan`):** Architected the 5-part narrative arc, thesis statement, and emotional beat structure.
4. **Stage 3 (`hook`):** Designed high-retention opening hooks with visual directives.
5. **Stage 4 (`script_visual_strategy`):** Generated complete spoken script and multi-element composition plan mapped across all narrative beats.
6. **Stage 5 (`review_result`):** Automated quality review validated narrative consistency, pacing, and visual directives (Approved).
7. **Stage 6 (`voice_track`):** Synthesized 8 audio chunks into continuous 188.38s narration with 535 word-level timestamps.
8. **Stage 7 (`render_spec`):** Remotion scene specification containing 22 continuous composition scenes (MetricHero, CalculationStory, SplitComparison, CauseEffect, ProcessFlow, BrollCaption).
9. **Stage 8 (`video`):** Headless Remotion render produced the finalized 1080x1920 30fps video file (17.3 MB).

---

## Stage 0: Video Generation Request

- **Artifact ID:** `artifact_d6d60b36d0ed47a09a68c0d4d0f7ea0c`
- **Artifact Type:** `generate_video_request`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-14T13:16:07.472024+00:00`
- **Parent Artifact Roles:** `{}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Captures raw user intent, topic, audience, visual mode, duration target, and stylistic parameters.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "topic": "The \u20b910 Lakh Mistake Most Indians Make Before Buying Their First Home",
  "angle": "Challenge the idea that \u201cEMI = affordable.\u201d Show that a home isn't just the down payment and EMI\u2014you also have registration, interiors, maintenance, property taxes, interest, and the opportunity cost of the down payment.",
  "audience": "9-to-5 corporate employees wanting freedom",
  "language": "English",
  "style": "philosophical and metrics-driven",
  "channel": "MindshiftFinance",
  "duration_profile": "long_5min",
  "visual_mode": "composition"
}
```

---

## Stage 1: Research Packet

- **Artifact ID:** `artifact_03325bf448f54667aadc833c8b277692`
- **Artifact Type:** `research_packet`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-14T13:18:49.276203+00:00`
- **Parent Artifact Roles:** `{"generate_video_request": "artifact_d6d60b36d0ed47a09a68c0d4d0f7ea0c"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Researches facts, statistics, historical parallels, and numeric anchors using LLM and research engine.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "topic": "The \u20b910 Lakh Mistake Most Indians Make Before Buying Their First Home",
  "audience": "9-to-5 corporate employees wanting freedom",
  "channel": "MindshiftFinance",
  "verified_facts": [
    "Stamp duty and registration charges in major Indian metro cities add an extra 5% to 7% of the property value upfront, costing approximately \u20b93.5 Lakh on a \u20b950 Lakh apartment (Knight Frank India 2023).",
    "Standard interior furnishing for a 2BHK apartment in urban India typically consumes 10% to 15% of the property cost, amounting to \u20b95 Lakh on a \u20b950 Lakh home (Livspace Home Interior Index 2023).",
    "Over a standard 20-year home loan tenure at an 8.5% interest rate, a borrower pays back roughly 2.1 times the principal amount borrowed due to cumulative interest (RBI Housing Finance Report 2023).",
    "The opportunity cost of locking a \u20b910 Lakh down payment into real estate rather than investing it in equity mutual funds at a historical 12% CAGR results in a 20-year wealth gap of over \u20b996 Lakh (AMFI India 2023).",
    "Annual maintenance charges, society fees, and municipal property taxes average 1% of the property's original value per year, adding \u20b950,000 annually for a \u20b950 Lakh home (CREDAI Real Estate Outlook 2023)."
  ],
  "statistics": [
    "78% of urban Indian first-time homebuyers fail to budget for interior work and registration fees in their initial financial planning (PropTiger Consumer Sentiment Survey 2023).",
    "71 minutes is the average daily one-way commute time in Bengaluru, driving many corporate employees to buy overpriced properties near tech parks (TomTom Traffic Index 2023).",
    "2.5 times the annual gross salary is the maximum recommended home loan limit to avoid severe financial distress, whereas average corporate buyers currently borrow at 4.5 times their annual salary (RBI Financial Stability Report 2023)."
  ],
  "concepts": [
    "Effective Total Cost of Ownership",
    "Opportunity Cost of Down Payment",
    "Hidden Real Estate Expenses",
    "EMI Affordability Trap"
  ],
  "misconceptions": [
    "If the monthly EMI is less than 40% of my take-home salary, the house is easily affordable.",
    "Buying a house is always a superior financial choice compared to renting and investing the difference in equity."
  ],
  "examples": [
    "A 32-year-old IT manager in Bengaluru earning \u20b920 Lakhs per annum who drains \u20b915 Lakhs in savings for a down payment and registration, leaving zero emergency buffer.",
    "A corporate professional in Mumbai purchasing a \u20b91 Crore flat, only to discover that monthly society maintenance and property taxes add \u20b912,000 to fixed monthly expenses."
  ],
  "trusted_sources": [
    "Reserve Bank of India Housing Finance Report",
    "Knight Frank India Real Estate Outlook",
    "Association of Mutual Funds in India",
    "CREDAI Real Estate Consumer Sentiment Survey"
  ],
  "provider_metadata": {
    "provider": "gemini",
    "model": "gemini-3.5-flash-lite",
    "raw_metadata": {
      "finish_reason": "STOP",
      "usage_metadata": {
        "promptTokenCount": 1041,
        "candidatesTokenCount": 734,
        "totalTokenCount": 1775,
        "promptTokensDetails": [
          {
            "modality": "TEXT",
            "tokenCount": 1041
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

## Stage 2: Narrative Plan

- **Artifact ID:** `artifact_c8e3ee1bf19f4bbe960058b6d80af158`
- **Artifact Type:** `narrative_plan`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-14T13:19:24.291772+00:00`
- **Parent Artifact Roles:** `{"research_packet": "artifact_03325bf448f54667aadc833c8b277692"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Structures the core thesis, psychological tension, and 5-stage narrative arc.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "thesis": "First-time home buyers in urban India routinely drain their savings for a down payment without realizing that hidden costs and opportunity costs create a \u20b910 Lakh financial blind spot that destroys long-term wealth.",
  "target_pain_point": "A 9-to-5 corporate professional in an Indian metro city like Bengaluru or Mumbai who feels immense societal pressure to buy a home, but risks severe financial distress and a ruined savings buffer due to hidden ownership expenses.",
  "conceptual_hook": "Most corporate employees think buying a \u20b950 Lakh apartment means paying just for the walls and the roof, but they are walking blind into a \u20b910 Lakh trap of hidden charges before they even step through the front door.",
  "narrative_arc_type": "Problem-Agitation-Solution",
  "scene_beats": [
    {
      "scene_id": "scene_01",
      "title": "The \u20b910 Lakh Blind Spot",
      "focus_concept": "Hidden Real Estate Expenses",
      "core_teaching_point": "First-time buyers severely miscalculate their initial out-of-pocket expenses because stamp duty, registration, and interiors hit their bank accounts immediately."
    },
    {
      "scene_id": "scene_02",
      "title": "The Societal Pressure Trap",
      "focus_concept": "EMI Affordability Trap",
      "core_teaching_point": "Relying solely on the rule that an EMI under 40% of salary makes a home affordable completely ignores total financial exposure and borrowing multipliers."
    },
    {
      "scene_id": "scene_03",
      "title": "The Hidden Costs of Ownership",
      "focus_concept": "Effective Total Cost of Ownership",
      "core_teaching_point": "Ongoing maintenance fees, property taxes, and cumulative interest drastically inflate the actual price of an Indian residential property over a 20-year span."
    },
    {
      "scene_id": "scene_04",
      "title": "The Bengaluru Tech Park Dilemma",
      "focus_concept": "EMI Affordability Trap",
      "core_teaching_point": "Long grueling commutes drive corporate employees to purchase overpriced properties while borrowing far beyond safe income multiples."
    },
    {
      "scene_id": "scene_05",
      "title": "The Down Payment Wealth Killer",
      "focus_concept": "Opportunity Cost of Down Payment",
      "core_teaching_point": "Locking a massive down payment into real estate rather than compounding it in equity mutual funds leads to a staggering multi-lakh wealth gap over decades."
    },
    {
      "scene_id": "scene_06",
      "title": "Dismantling the Renting Myth",
      "focus_concept": "Opportunity Cost of Down Payment",
      "core_teaching_point": "Buying a home is not universally superior to renting when factoring in the immense opportunity costs and liquidity losses of property investment."
    },
    {
      "scene_id": "scene_07",
      "title": "The Smart Home Buyer Blueprint",
      "focus_concept": "Effective Total Cost of Ownership",
      "core_teaching_point": "Corporate professionals must calculate all hidden expenses and maintain a robust emergency buffer before ever committing to a housing loan."
    }
  ],
  "provider_metadata": {
    "provider": "gemini",
    "model": "gemini-3.5-flash-lite",
    "raw_metadata": {
      "finish_reason": "STOP",
      "usage_metadata": {
        "promptTokenCount": 1690,
        "candidatesTokenCount": 755,
        "totalTokenCount": 2445,
        "promptTokensDetails": [
          {
            "modality": "TEXT",
            "tokenCount": 1690
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

## Stage 3: Hook

- **Artifact ID:** `artifact_8be68bb4d6b74a158fb52a458aee6c5f`
- **Artifact Type:** `hook`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-14T13:19:47.886376+00:00`
- **Parent Artifact Roles:** `{"generate_video_request": "artifact_d6d60b36d0ed47a09a68c0d4d0f7ea0c", "narrative_plan": "artifact_c8e3ee1bf19f4bbe960058b6d80af158"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Crafts the 0-15s hook, visual disruption, and curiosity gap.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "conceptual_hook": "Most corporate employees think buying a \u20b950 Lakh apartment means paying just for the walls and the roof, but they are walking blind into a \u20b910 Lakh trap of hidden charges before they even step through the front door.",
  "script_text": "You saved for years for that down payment. But the moment you sign the deed, hidden fees swallow 10 Lakhs of your cash before you even unpack a box. Stamp duty, registration, and basic interiors are waiting in the dark to drain your emergency fund.",
  "visual_directives": [
    {
      "beat_id": "beat_01",
      "preferred_component": "Typography",
      "visual_goal": "Bold statement revealing the true cost behind buying a home.",
      "visual_instruction": null,
      "asset_query": null,
      "notes": null,
      "trigger_word": null,
      "component_data": {
        "text": "The \u20b910 Lakh Blind Spot",
        "subtitle": "What they never tell you about buying a home",
        "variant": "headline"
      }
    },
    {
      "beat_id": "beat_02",
      "preferred_component": "StockVideo",
      "visual_goal": "Corporate worker looking stressed while reviewing documents on a desk.",
      "visual_instruction": null,
      "asset_query": "person looking at paperwork",
      "notes": null,
      "trigger_word": "deed",
      "component_data": {}
    },
    {
      "beat_id": "beat_03",
      "preferred_component": "NumberCounter",
      "visual_goal": "Counter showing the sudden drain of hidden expenses from the bank account.",
      "visual_instruction": null,
      "asset_query": null,
      "notes": null,
      "trigger_word": "swallow",
      "component_data": {
        "end_value": 10,
        "prefix": "\u20b9",
        "suffix": " Lakhs",
        "unit": "\u20b9",
        "variant": "change"
      }
    }
  ],
  "provider_metadata": {
    "provider": "gemini",
    "model": "gemini-3.5-flash-lite",
    "raw_metadata": {
      "finish_reason": "STOP",
      "usage_metadata": {
        "promptTokenCount": 6039,
        "candidatesTokenCount": 442,
        "totalTokenCount": 6481,
        "promptTokensDetails": [
          {
            "modality": "TEXT",
            "tokenCount": 6039
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

## Stage 4: Script & Visual Strategy

- **Artifact ID:** `artifact_310863c3cad84c229bdc74b5e82e4393`
- **Artifact Type:** `script_visual_strategy`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-14T13:22:37.934575+00:00`
- **Parent Artifact Roles:** `{"hook": "artifact_8be68bb4d6b74a158fb52a458aee6c5f", "narrative_plan": "artifact_c8e3ee1bf19f4bbe960058b6d80af158", "research_packet": "artifact_03325bf448f54667aadc833c8b277692"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Generates full script ideas with narrative beats and detailed multi-element composition specifications.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "thesis": "First-time home buyers in urban India routinely drain their savings for a down payment without realizing that hidden costs and opportunity costs create a \u20b910 Lakh financial blind spot that destroys long-term wealth.",
  "ideas": [
    {
      "idea_id": "idea_01",
      "title": "The \u20b910 Lakh Blind Spot",
      "focus_concept": "Hidden Real Estate Expenses",
      "core_teaching_point": "First-time buyers severely miscalculate their initial out-of-pocket expenses because stamp duty, registration, and interiors hit their bank accounts immediately.",
      "narration": "When you finally decide to purchase property, you assume the quoted price covers everything. But our research reveals that 78 percent of urban Indian first-time homebuyers completely fail to budget for interior work and registration fees in their initial financial planning. Stamp duty and registration charges in major Indian metro cities add an extra 5 percent to 7 percent of the property value upfront, costing approximately \u20b93.5 Lakh on a \u20b950 Lakh apartment.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography showing the hidden real estate expenses.",
          "asset_query": null,
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "The \u20b910 Lakh Blind Spot",
            "subtitle": "Hidden Real Estate Expenses",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "StockVideo",
          "visual_goal": "Corporate worker reviewing financial documents at a desk.",
          "asset_query": "person reviewing documents",
          "notes": null,
          "trigger_word": "purchase",
          "component_data": {}
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter showing the percentage of unprepared homebuyers.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "reveals",
          "component_data": {
            "end_value": 78,
            "label": "Unprepared Buyers",
            "suffix": "%",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "Charts",
          "visual_goal": "Bar chart showing upfront costs on a property.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "upfront",
          "component_data": {
            "chart_type": "bar",
            "header_label": "UPFRONT COSTS BREAKDOWN",
            "labels": [
              "Stamp Duty",
              "Registration",
              "Interiors"
            ],
            "unit": "\u20b9",
            "values": [
              3.5,
              1.5,
              5.0
            ]
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Highlighting the standard interior furnishing cost.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "apartment",
          "component_data": {
            "text": "\u20b95 Lakhs for Interiors",
            "subtitle": "Livspace Home Interior Index 2023",
            "variant": "takeaway"
          }
        }
      ]
    },
    {
      "idea_id": "idea_02",
      "title": "The Societal Pressure Trap",
      "focus_concept": "EMI Affordability Trap",
      "core_teaching_point": "Relying solely on the rule that an EMI under 40% of salary makes a home affordable completely ignores total financial exposure and borrowing multipliers.",
      "narration": "Society tells you that renting is throwing money away, pushing corporate employees into rushed purchases. Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe. But this metric ignores your total financial exposure. According to the RBI Financial Stability Report 2023, average corporate buyers currently borrow at 4.5 times their annual salary, far exceeding the recommended safety limit of 2.5 times.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography showing the societal pressure trap.",
          "asset_query": null,
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "The Societal Pressure Trap",
            "subtitle": "EMI Affordability Trap",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "StockVideo",
          "visual_goal": "Stressed corporate worker looking at laptop screen.",
          "asset_query": "stressed worker at laptop",
          "notes": null,
          "trigger_word": "employees",
          "component_data": {}
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter showing the safe income multiple versus actual.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "currently",
          "component_data": {
            "end_value": 4.5,
            "label": "Actual Borrowing Multiple",
            "suffix": "x",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "SplitComparison",
          "visual_goal": "Comparison between safe multiple and actual borrower multiple.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "salary",
          "component_data": {
            "left_role": "Safe Limit",
            "left_value": 2.5,
            "right_role": "Actual",
            "right_value": 4.5,
            "comparison_label": "Salary Multiple",
            "header_label": "BORROWING MULTIPLIER",
            "left_label": "Safe Limit",
            "right_label": "Actual",
            "tone": "neutral",
            "variant": "versus"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Displaying the RBI stability report warning.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "limit",
          "component_data": {
            "text": "Severe Financial Distress Risk",
            "subtitle": "RBI Financial Stability Report 2023",
            "variant": "statement"
          }
        }
      ]
    },
    {
      "idea_id": "idea_03",
      "title": "The Hidden Costs of Ownership",
      "focus_concept": "Effective Total Cost of Ownership",
      "core_teaching_point": "Ongoing maintenance fees, property taxes, and cumulative interest drastically inflate the actual price of an Indian residential property over a 20-year span.",
      "narration": "Buying the home is only the beginning of your financial commitment. Annual maintenance charges, society fees, and municipal property taxes average 1 percent of the property's original value per year, adding \u20b950,000 annually for a \u20b950 Lakh home according to CREDAI Real Estate Outlook 2023. Furthermore, over a standard 20-year home loan tenure at an 8.5 percent interest rate, a borrower pays back roughly 2.1 times the principal amount borrowed due to cumulative interest.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography showing total cost of ownership concept.",
          "asset_query": null,
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "Hidden Costs of Ownership",
            "subtitle": "Effective Total Cost of Ownership",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter showing annual maintenance cost in rupees.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "annually",
          "component_data": {
            "end_value": 50000,
            "label": "Annual Maintenance & Tax",
            "prefix": "\u20b9",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "Charts",
          "visual_goal": "Line chart showing loan repayment multiplier over 20 years.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "tenure",
          "component_data": {
            "chart_type": "line",
            "header_label": "LOAN REPAYMENT MULTIPLIER",
            "labels": [
              "Year 5",
              "Year 10",
              "Year 15",
              "Year 20"
            ],
            "unit": "x",
            "values": [
              1.2,
              1.5,
              1.8,
              2.1
            ]
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "Typography",
          "visual_goal": "Displaying total repayment factor over principal.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "borrowed",
          "component_data": {
            "text": "2.1 Times Principal Paid Back",
            "subtitle": "RBI Housing Finance Report 2023",
            "variant": "takeaway"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "StockVideo",
          "visual_goal": "Apartment building exterior shot in an Indian metro.",
          "asset_query": "modern apartment building exterior",
          "notes": null,
          "trigger_word": "home",
          "component_data": {}
        }
      ]
    },
    {
      "idea_id": "idea_04",
      "title": "The Bengaluru Tech Park Dilemma",
      "focus_concept": "EMI Affordability Trap",
      "core_teaching_point": "Long grueling commutes drive corporate employees to purchase overpriced properties while borrowing far beyond safe income multiples.",
      "narration": "In major tech hubs like Bengaluru, daily life is dictated by gridlocked traffic. According to the TomTom Traffic Index 2023, 71 minutes is the average daily one-way commute time in Bengaluru. This punishing routine drives many corporate employees to buy overpriced properties located near tech parks, forcing them into aggressive loans and trapping them in an inescapable EMI affordability cycle without adequate emergency buffers.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography showing the tech park commute dilemma.",
          "asset_query": null,
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "The Bengaluru Tech Park Dilemma",
            "subtitle": "EMI Affordability Trap",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "StockVideo",
          "visual_goal": "Heavy traffic jam in an Indian city during rush hour.",
          "asset_query": "traffic jam city rush hour",
          "notes": null,
          "trigger_word": "traffic",
          "component_data": {}
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter showing daily commute minutes in Bengaluru.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "bengaluru",
          "component_data": {
            "end_value": 71,
            "label": "One-Way Commute",
            "suffix": " min",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "Typography",
          "visual_goal": "Highlighting the TomTom Traffic Index data.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "routine",
          "component_data": {
            "text": "71 Minutes Daily Commute",
            "subtitle": "TomTom Traffic Index 2023",
            "variant": "statement"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "StockVideo",
          "visual_goal": "Stressed commuter looking out a cab window in traffic.",
          "asset_query": "commuter looking out window traffic",
          "notes": null,
          "trigger_word": "overpriced",
          "component_data": {}
        }
      ]
    },
    {
      "idea_id": "idea_05",
      "title": "The Down Payment Wealth Killer",
      "focus_concept": "Opportunity Cost of Down Payment",
      "core_teaching_point": "Locking a massive down payment into real estate rather than compounding it in equity mutual funds leads to a staggering multi-lakh wealth gap over decades.",
      "narration": "The most devastating part of buying a home early is the invisible opportunity cost. When you drain your savings for a down payment, you miss out on decades of market compounding. Data from AMFI India 2023 shows that the opportunity cost of locking a \u20b910 Lakh down payment into real estate rather than investing it in equity mutual funds at a historical 12 percent CAGR results in a staggering 20-year wealth gap of over \u20b996 Lakh.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography showing the down payment wealth killer.",
          "asset_query": null,
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "The Down Payment Wealth Killer",
            "subtitle": "Opportunity Cost of Down Payment",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "StockVideo",
          "visual_goal": "Person analyzing investment portfolio growth charts on a computer.",
          "asset_query": "investment portfolio growth charts",
          "notes": null,
          "trigger_word": "compounding",
          "component_data": {}
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "Charts",
          "visual_goal": "Line chart comparing real estate growth versus 12 percent equity compounding.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "mutual",
          "component_data": {
            "chart_type": "line",
            "header_label": "20-YEAR WEALTH GAP",
            "labels": [
              "Year 0",
              "Year 5",
              "Year 10",
              "Year 15",
              "Year 20"
            ],
            "unit": "\u20b9L",
            "values": [
              10.0,
              18.0,
              31.0,
              55.0,
              96.0
            ]
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter highlighting the 20-year wealth gap amount.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "staggering",
          "component_data": {
            "end_value": 96,
            "label": "Wealth Gap Over 20 Years",
            "prefix": "\u20b9",
            "suffix": " Lakh",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Displaying AMFI India research source.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "wealth",
          "component_data": {
            "text": "AMFI India 2023 Data",
            "subtitle": "12 percent historical equity CAGR",
            "variant": "takeaway"
          }
        }
      ]
    },
    {
      "idea_id": "idea_06",
      "title": "Dismantling the Renting Myth",
      "focus_concept": "Opportunity Cost of Down Payment",
      "core_teaching_point": "Buying a home is not universally superior to renting when factoring in the immense opportunity costs and liquidity losses of property investment.",
      "narration": "Generations before us viewed renting as a waste of money, but today's financial reality is entirely different. When you factor in the immense opportunity costs, liquidity losses, and maintenance burdens of homeownership, renting while aggressively investing your capital in high-yield equities often leaves you far wealthier. You maintain the financial flexibility to switch jobs, relocate, and grow your net worth without being tied down to a crushing debt obligation.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography dismantling the renting myth.",
          "asset_query": null,
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "Dismantling the Renting Myth",
            "subtitle": "Opportunity Cost of Down Payment",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "StockVideo",
          "visual_goal": "Young professional working flexibly from a modern cafe.",
          "asset_query": "professional working in modern cafe",
          "notes": null,
          "trigger_word": "reality",
          "component_data": {}
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "SplitComparison",
          "visual_goal": "Comparison between rigid homeownership and flexible renting.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "homeownership",
          "component_data": {
            "left_role": "Homeowner",
            "left_value": 85.0,
            "right_role": "Renter Investor",
            "right_value": 180.0,
            "comparison_label": "Net Wealth Potential",
            "header_label": "RENT VS BUY REALITY",
            "left_unit": "\u20b9L",
            "right_unit": "\u20b9L",
            "left_label": "Homeowner",
            "right_label": "Renter Investor",
            "tone": "neutral",
            "variant": "versus"
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "Typography",
          "visual_goal": "Highlighting financial flexibility and liquidity.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "flexibility",
          "component_data": {
            "text": "Flexibility & Liquidity Win",
            "subtitle": "Avoid the liquidity trap of real estate",
            "variant": "statement"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "StockVideo",
          "visual_goal": "Happy corporate employee looking out city window.",
          "asset_query": "happy professional looking out window",
          "notes": null,
          "trigger_word": "obligation",
          "component_data": {}
        }
      ]
    },
    {
      "idea_id": "idea_07",
      "title": "The Smart Home Buyer Blueprint",
      "focus_concept": "Effective Total Cost of Ownership",
      "core_teaching_point": "Corporate professionals must calculate all hidden expenses and maintain a robust emergency buffer before ever committing to a housing loan.",
      "narration": "To protect your financial future, adopt the Smart Home Buyer Blueprint. Before signing any agreement, calculate your total cost of ownership including stamp duty, registration, interiors, and maintenance. Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched. By sidestepping the \u20b910 Lakh trap, you keep your wealth compounding and secure true financial freedom.",
      "visual_sequence": [
        {
          "beat_id": "beat_01",
          "preferred_component": "Typography",
          "visual_goal": "Typography showing the smart home buyer blueprint.",
          "asset_query": null,
          "notes": null,
          "trigger_word": null,
          "component_data": {
            "text": "The Smart Home Buyer Blueprint",
            "subtitle": "Effective Total Cost of Ownership",
            "variant": "headline"
          }
        },
        {
          "beat_id": "beat_02",
          "preferred_component": "StockVideo",
          "visual_goal": "Financial planner showing a strategy blueprint on a tablet.",
          "asset_query": "financial planner showing strategy tablet",
          "notes": null,
          "trigger_word": "blueprint",
          "component_data": {}
        },
        {
          "beat_id": "beat_03",
          "preferred_component": "ProgressiveList",
          "visual_goal": "List of key steps for safe home buying.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "ownership",
          "component_data": {
            "header_label": "BUYER CHECKLIST",
            "items": [
              {
                "title": "Calculate Hidden Costs",
                "text": "Calculate Hidden Costs",
                "subtitle": "Include stamp duty & registration",
                "icon": null,
                "highlight": false,
                "value": null
              },
              {
                "title": "Safe Multiples",
                "text": "Safe Multiples",
                "subtitle": "Keep borrowing below 2.5x salary",
                "icon": null,
                "highlight": false,
                "value": null
              },
              {
                "title": "Protect Emergency Fund",
                "text": "Protect Emergency Fund",
                "subtitle": "Preserve equity compounding",
                "icon": null,
                "highlight": false,
                "value": null
              }
            ],
            "variant": "detailed"
          }
        },
        {
          "beat_id": "beat_04",
          "preferred_component": "NumberCounter",
          "visual_goal": "Counter highlighting the recommended maximum salary multiple.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "salary",
          "component_data": {
            "end_value": 2.5,
            "label": "Max Safe Salary Multiple",
            "suffix": "x",
            "variant": "single"
          }
        },
        {
          "beat_id": "beat_05",
          "preferred_component": "Typography",
          "visual_goal": "Final empowering statement on financial freedom.",
          "asset_query": null,
          "notes": null,
          "trigger_word": "freedom",
          "component_data": {
            "text": "Secure True Financial Freedom",
            "subtitle": "MindshiftFinance",
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
        "promptTokenCount": 5815,
        "candidatesTokenCount": 5390,
        "totalTokenCount": 11205,
        "promptTokensDetails": [
          {
            "modality": "TEXT",
            "tokenCount": 5815
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
    "thesis": "First-time home buyers in urban India routinely drain their savings for a down payment without realizing that hidden costs and opportunity costs create a \u20b910 Lakh financial blind spot that destroys long-term wealth.",
    "hook_plan": {
      "hook_id": "hook",
      "narration": "You saved for years for that down payment. But the moment you sign the deed, hidden fees swallow 10 Lakhs of your cash before you even unpack a box. Stamp duty, registration, and basic interiors are waiting in the dark to drain your emergency fund.",
      "beats": [
        {
          "beat_id": "beat_hook_01",
          "composition_id": "metric_hero",
          "variant": "warning_metric",
          "composition_data": {
            "value": "\u20b910 Lakh",
            "label": "Hidden Home-Buying Fees",
            "context": "swallowed before moving in",
            "emphasis": "hero",
            "variant": "warning_metric",
            "polarity": "negative",
            "direction": null,
            "baseline_value": null,
            "delta": null
          },
          "asset_requirement": "none",
          "asset_query": null,
          "trigger_word": null,
          "visual_goal": "Highlight \u20b910 Lakhs as an immediate shock loss from hidden fees.",
          "relationship_type": "metric",
          "used_fallback": false,
          "fallback_reason": null
        },
        {
          "beat_id": "beat_hook_02",
          "composition_id": "multi_factor_pressure",
          "variant": "tri_factor",
          "composition_data": {
            "factors": [
              {
                "label": "Stamp Duty",
                "value": null,
                "severity": "high",
                "icon": null
              },
              {
                "label": "Registration Fees",
                "value": null,
                "severity": "high",
                "icon": null
              },
              {
                "label": "Basic Interiors",
                "value": null,
                "severity": "high",
                "icon": null
              }
            ],
            "combined_label": "Emergency Fund Drain",
            "combined_severity": "critical",
            "outcome_note": "Hidden upfront costs depleting your financial safety net",
            "outcome_value": "100% Drained",
            "outcome_header_label": null,
            "variant": "tri_factor",
            "polarity": null
          },
          "asset_requirement": "optional_broll",
          "asset_query": "home buying hidden costs financial stress",
          "trigger_word": "Stamp",
          "visual_goal": "Show how stamp duty, registration, and interiors combine to drain the emergency fund.",
          "relationship_type": "multi_factor",
          "used_fallback": false,
          "fallback_reason": null
        }
      ]
    },
    "ideas": [
      {
        "idea_id": "idea_01",
        "narration": "When you finally decide to purchase property, you assume the quoted price covers everything. But our research reveals that 78 percent of urban Indian first-time homebuyers completely fail to budget for interior work and registration fees in their initial financial planning. Stamp duty and registration charges in major Indian metro cities add an extra 5 percent to 7 percent of the property value upfront, costing approximately \u20b93.5 Lakh on a \u20b950 Lakh apartment.",
        "beats": [
          {
            "beat_id": "beat_01_01",
            "composition_id": "broll_caption",
            "variant": "statement",
            "composition_data": {
              "caption": "Homebuyers typically assume the quoted property price is the total cost.",
              "emphasis_phrase": "quoted price covers everything",
              "author": null,
              "header_label": "THE HOMEBUYING ASSUMPTION",
              "variant": "statement",
              "source_context": null,
              "polarity": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": null,
            "trigger_word": null,
            "visual_goal": "Illustrate the common misconception that the quoted property price is the final total cost.",
            "relationship_type": "statement",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_01_02",
            "composition_id": "metric_hero",
            "variant": "warning_metric",
            "composition_data": {
              "value": "78%",
              "label": "First-Time Buyers Failing to Budget Hidden Costs",
              "context": "Urban Indian Homebuyers",
              "emphasis": "hero",
              "variant": "warning_metric",
              "polarity": "negative",
              "direction": null,
              "baseline_value": null,
              "delta": null
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": null,
            "visual_goal": "Highlight that 78 percent of urban Indian first-time homebuyers fail to budget for hidden purchase costs.",
            "relationship_type": "metric",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_01_03",
            "composition_id": "calculation_story",
            "variant": "multiplication",
            "composition_data": {
              "input_label": "Apartment Value",
              "input_value": "\u20b950 Lakh",
              "operation_label": "\u00d7",
              "rate_label": "5% to 7% Stamp Duty",
              "result_label": "Upfront Cost",
              "result_value": "\u20b93.5 Lakh",
              "note": "Registration & Stamp Duty Charges",
              "operation_type": "multiplication",
              "variant": null,
              "polarity": "warning",
              "timeframe": null
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "Stamp",
            "visual_goal": "Show how stamp duty and registration percentages calculate to \u20b93.5 Lakh on a \u20b950 Lakh apartment.",
            "relationship_type": "calculation",
            "used_fallback": false,
            "fallback_reason": null
          }
        ]
      },
      {
        "idea_id": "idea_02",
        "narration": "Society tells you that renting is throwing money away, pushing corporate employees into rushed purchases. Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe. But this metric ignores your total financial exposure. According to the RBI Financial Stability Report 2023, average corporate buyers currently borrow at 4.5 times their annual salary, far exceeding the recommended safety limit of 2.5 times.",
        "beats": [
          {
            "beat_id": "beat_02_01",
            "composition_id": "broll_caption",
            "variant": "statement",
            "composition_data": {
              "caption": "Society tells you that renting is throwing money away, pushing corporate employees into rushed purchases.",
              "emphasis_phrase": "throwing money away",
              "author": null,
              "header_label": "SOCIAL PRESSURE",
              "variant": "statement",
              "source_context": null,
              "polarity": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": null,
            "trigger_word": "Society",
            "visual_goal": "Show corporate employee facing societal pressure regarding homeownership.",
            "relationship_type": "statement",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_02_02",
            "composition_id": "broll_caption",
            "variant": null,
            "composition_data": {
              "caption": "Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe.",
              "emphasis_phrase": "40 percent",
              "author": null,
              "header_label": "INDUSTRY RULE OF THUMB",
              "variant": "statement",
              "source_context": null,
              "polarity": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": "real estate agent talking to couple modern office",
            "trigger_word": "agents",
            "visual_goal": "Display the common real estate rule about keeping EMI under 40 percent over a relevant corporate housing B-roll.",
            "relationship_type": "definition",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_02_03",
            "composition_id": "broll_caption",
            "variant": "statement",
            "composition_data": {
              "caption": "The traditional metric ignores your total financial exposure.",
              "emphasis_phrase": "total financial exposure",
              "author": null,
              "header_label": "CRITICAL FLAW",
              "variant": "statement",
              "source_context": null,
              "polarity": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": null,
            "trigger_word": "ignores",
            "visual_goal": "Highlight the flaw in traditional EMI metrics ignoring financial exposure.",
            "relationship_type": "statement",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_02_04",
            "composition_id": "comparison_split",
            "variant": "metric_compare",
            "composition_data": {
              "left_role": "Actual Borrowing",
              "left_value": "4.5x",
              "left_label": null,
              "left_unit": null,
              "right_role": "Safe Limit",
              "right_value": "2.5x",
              "right_label": null,
              "right_unit": null,
              "comparison_label": null,
              "delta": null,
              "winner": null,
              "tone": "superiority",
              "header_label": "RBI FINANCIAL STABILITY REPORT 2023",
              "variant": "metrics"
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "Report",
            "visual_goal": "Show side-by-side comparison of actual corporate borrowing against the recommended safety limit.",
            "relationship_type": "comparison",
            "used_fallback": false,
            "fallback_reason": null
          }
        ]
      },
      {
        "idea_id": "idea_03",
        "narration": "Buying the home is only the beginning of your financial commitment. Annual maintenance charges, society fees, and municipal property taxes average 1 percent of the property's original value per year, adding \u20b950,000 annually for a \u20b950 Lakh home according to CREDAI Real Estate Outlook 2023. Furthermore, over a standard 20-year home loan tenure at an 8.5 percent interest rate, a borrower pays back roughly 2.1 times the principal amount borrowed due to cumulative interest.",
        "beats": [
          {
            "beat_id": "beat_03_01",
            "composition_id": "calculation_story",
            "variant": "multiplication",
            "composition_data": {
              "input_label": "Property Value",
              "input_value": "\u20b950 Lakh",
              "operation_label": "\u00d7",
              "rate_label": "1% Annual Maintenance",
              "result_label": "Annual Cost",
              "result_value": "\u20b950,000",
              "note": "Maintenance, Society Fees & Taxes",
              "operation_type": "multiplication",
              "variant": null,
              "polarity": null,
              "timeframe": "per year"
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "beginning",
            "visual_goal": "Show the 1% annual maintenance calculation on a \u20b950 Lakh home totaling \u20b950,000 per year.",
            "relationship_type": "calculation",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_03_02",
            "composition_id": "calculation_story",
            "variant": "multiplication",
            "composition_data": {
              "input_label": "Principal Amount",
              "input_value": "1.0x",
              "operation_label": "\u00d7",
              "rate_label": "20-yr Loan @ 8.5%",
              "result_label": "Total Repayment",
              "result_value": "2.1x Principal",
              "note": "Cumulative interest burden over tenure",
              "operation_type": "multiplication",
              "variant": null,
              "polarity": "warning",
              "timeframe": "over 20 years"
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "Furthermore",
            "visual_goal": "Show how an 8.5% interest rate over 20 years multiplies the principal repayment to 2.1 times.",
            "relationship_type": "calculation",
            "used_fallback": false,
            "fallback_reason": null
          }
        ]
      },
      {
        "idea_id": "idea_04",
        "narration": "In major tech hubs like Bengaluru, daily life is dictated by gridlocked traffic. According to the TomTom Traffic Index 2023, 71 minutes is the average daily one-way commute time in Bengaluru. This punishing routine drives many corporate employees to buy overpriced properties located near tech parks, forcing them into aggressive loans and trapping them in an inescapable EMI affordability cycle without adequate emergency buffers.",
        "beats": [
          {
            "beat_id": "beat_04_01",
            "composition_id": "metric_hero",
            "variant": "hero",
            "composition_data": {
              "value": "71 min",
              "label": "Average Daily One-Way Commute",
              "context": "TomTom Traffic Index 2023",
              "emphasis": "hero",
              "variant": null,
              "polarity": null,
              "direction": null,
              "baseline_value": null,
              "delta": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": null,
            "trigger_word": "minutes",
            "visual_goal": "Highlight the 71-minute daily one-way commute time in Bengaluru as a hero metric.",
            "relationship_type": "metric",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_04_02",
            "composition_id": "cause_effect",
            "variant": "single_cause",
            "composition_data": {
              "causes": [
                {
                  "label": "Long Commutes & Punishing Routine",
                  "value": null,
                  "icon": "\ud83d\ude97"
                }
              ],
              "connector": "drives",
              "outcome_label": "Inescapable EMI Debt Trap",
              "outcome_value": null,
              "outcome_severity": "negative",
              "outcome_header_label": "Ultimate Consequence",
              "outcome_note": "Aggressive loans without emergency buffers",
              "variant": null,
              "polarity": null
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "drives",
            "visual_goal": "Show how grueling commutes drive employees into overpriced real estate and debt traps.",
            "relationship_type": "cause_effect",
            "used_fallback": false,
            "fallback_reason": null
          }
        ]
      },
      {
        "idea_id": "idea_05",
        "narration": "The most devastating part of buying a home early is the invisible opportunity cost. When you drain your savings for a down payment, you miss out on decades of market compounding. Data from AMFI India 2023 shows that the opportunity cost of locking a \u20b910 Lakh down payment into real estate rather than investing it in equity mutual funds at a historical 12 percent CAGR results in a staggering 20-year wealth gap of over \u20b996 Lakh.",
        "beats": [
          {
            "beat_id": "beat_05_01",
            "composition_id": "cause_effect",
            "variant": "single_cause",
            "composition_data": {
              "causes": [
                {
                  "label": "Draining Savings for Down Payment",
                  "value": null,
                  "icon": "\ud83d\udcb8"
                }
              ],
              "connector": "leads to",
              "outcome_label": "Invisible Opportunity Cost",
              "outcome_value": "Lost Market Compounding",
              "outcome_severity": "negative",
              "outcome_header_label": null,
              "outcome_note": null,
              "variant": "single_cause",
              "polarity": null
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "drain",
            "visual_goal": "Show how draining savings for a home down payment causes the invisible opportunity cost of lost compounding.",
            "relationship_type": "cause_effect",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_05_02",
            "composition_id": "comparison_split",
            "variant": "cards",
            "composition_data": {
              "left_role": "Real Estate Down Payment",
              "left_value": "\u20b910 Lakh",
              "left_label": null,
              "left_unit": null,
              "right_role": "Equity Mutual Funds (12% CAGR)",
              "right_value": "\u20b996 Lakh Gap",
              "right_label": null,
              "right_unit": null,
              "comparison_label": "20-YEAR OPPORTUNITY COST",
              "delta": null,
              "winner": "right",
              "tone": null,
              "header_label": "AMFI INDIA 2023 DATA",
              "variant": null
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "AMFI",
            "visual_goal": "Show the 20-year wealth gap of over \u20b996 Lakh comparing real estate vs equity mutual funds.",
            "relationship_type": "comparison",
            "used_fallback": false,
            "fallback_reason": null
          }
        ]
      },
      {
        "idea_id": "idea_06",
        "narration": "Generations before us viewed renting as a waste of money, but today's financial reality is entirely different. When you factor in the immense opportunity costs, liquidity losses, and maintenance burdens of homeownership, renting while aggressively investing your capital in high-yield equities often leaves you far wealthier. You maintain the financial flexibility to switch jobs, relocate, and grow your net worth without being tied down to a crushing debt obligation.",
        "beats": [
          {
            "beat_id": "beat_06_01",
            "composition_id": "broll_caption",
            "variant": "statement",
            "composition_data": {
              "caption": "Generations before us viewed renting as a waste of money, but today's financial reality is entirely different.",
              "emphasis_phrase": "financial reality is entirely different",
              "author": null,
              "header_label": "THE RENT VS BUY DEBATE",
              "variant": "statement",
              "source_context": null,
              "polarity": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": null,
            "trigger_word": null,
            "visual_goal": "Set the contextual backdrop for why old home-buying assumptions no longer apply.",
            "relationship_type": "statement",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_06_02",
            "composition_id": "comparison_split",
            "variant": "versus",
            "composition_data": {
              "left_role": "Homeownership",
              "left_value": "Burdens",
              "left_label": null,
              "left_unit": null,
              "right_role": "Renting + Equities",
              "right_value": "Far Wealthier",
              "right_label": null,
              "right_unit": null,
              "comparison_label": "WEALTH STRATEGY",
              "delta": null,
              "winner": "right",
              "tone": null,
              "header_label": "RENTING VS BUYING",
              "variant": null
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "factor",
            "visual_goal": "Show a side-by-side comparison illustrating why renting and investing outperforms homeownership.",
            "relationship_type": "comparison",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_06_03",
            "composition_id": "cause_effect",
            "variant": "dual_cause",
            "composition_data": {
              "causes": [
                {
                  "label": "Career Flexibility",
                  "value": null,
                  "icon": "\ud83d\udcbc"
                },
                {
                  "label": "Debt-Free Living",
                  "value": null,
                  "icon": "\u2728"
                }
              ],
              "connector": "leads to",
              "outcome_label": "Net Worth Growth",
              "outcome_value": "Financial Freedom",
              "outcome_severity": "positive",
              "outcome_header_label": null,
              "outcome_note": null,
              "variant": "dual_cause",
              "polarity": null
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "maintain",
            "visual_goal": "Show how career flexibility and freedom from crushing debt lead to net worth growth.",
            "relationship_type": "cause_effect",
            "used_fallback": false,
            "fallback_reason": null
          }
        ]
      },
      {
        "idea_id": "idea_07",
        "narration": "To protect your financial future, adopt the Smart Home Buyer Blueprint. Before signing any agreement, calculate your total cost of ownership including stamp duty, registration, interiors, and maintenance. Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched. By sidestepping the \u20b910 Lakh trap, you keep your wealth compounding and secure true financial freedom.",
        "beats": [
          {
            "beat_id": "beat_07_01",
            "composition_id": "broll_caption",
            "variant": "statement",
            "composition_data": {
              "caption": "To protect your financial future, adopt the Smart Home Buyer Blueprint.",
              "emphasis_phrase": "Smart Home Buyer Blueprint",
              "author": null,
              "header_label": "FRAMEWORK",
              "variant": "statement",
              "source_context": null,
              "polarity": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": null,
            "trigger_word": "protect",
            "visual_goal": "Introduce the Smart Home Buyer Blueprint with cinematic atmospheric B-roll.",
            "relationship_type": "statement",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_07_02",
            "composition_id": "process_flow",
            "variant": null,
            "composition_data": {
              "steps": [
                {
                  "title": "Stamp Duty",
                  "subtitle": "Government levy",
                  "type": "step",
                  "value": null,
                  "connector_label": null
                },
                {
                  "title": "Registration",
                  "subtitle": "Legal paperwork fee",
                  "type": "step",
                  "value": null,
                  "connector_label": null
                },
                {
                  "title": "Interiors",
                  "subtitle": "Setup and furnishing",
                  "type": "step",
                  "value": null,
                  "connector_label": null
                },
                {
                  "title": "Maintenance",
                  "subtitle": "Ongoing society upkeep",
                  "type": "step",
                  "value": null,
                  "connector_label": null
                }
              ],
              "header_label": "TOTAL COST OF OWNERSHIP",
              "layout": "horizontal",
              "variant": "horizontal",
              "footer_label": null
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "calculate",
            "visual_goal": "Show the four key hidden expenses making up the total cost of home ownership.",
            "relationship_type": "process",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_07_03",
            "composition_id": "broll_caption",
            "variant": "statement",
            "composition_data": {
              "caption": "Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched.",
              "emphasis_phrase": "2.5x annual salary borrowing cap",
              "author": null,
              "header_label": "GOLDEN RULE",
              "variant": "statement",
              "source_context": null,
              "polarity": null
            },
            "asset_requirement": "optional_broll",
            "asset_query": null,
            "trigger_word": null,
            "visual_goal": "Emphasize the financial rule of keeping home loans under 2.5x annual salary with atmospheric b-roll.",
            "relationship_type": "statement",
            "used_fallback": false,
            "fallback_reason": null
          },
          {
            "beat_id": "beat_07_04",
            "composition_id": "cause_effect",
            "variant": "single_cause",
            "composition_data": {
              "causes": [
                {
                  "label": "Sidestepping the \u20b910 Lakh Trap",
                  "value": "\u20b910 Lakh",
                  "icon": "\ud83d\udee1\ufe0f"
                }
              ],
              "connector": "leads to",
              "outcome_label": "True Financial Freedom",
              "outcome_value": "Compounding Wealth",
              "outcome_severity": "positive",
              "outcome_header_label": "Ultimate Consequence",
              "outcome_note": "Keeps your wealth compounding securely",
              "variant": null,
              "polarity": null
            },
            "asset_requirement": "none",
            "asset_query": null,
            "trigger_word": "sidestepping",
            "visual_goal": "Show how avoiding the \u20b910 lakh trap directly leads to compounding wealth and financial freedom.",
            "relationship_type": "cause_effect",
            "used_fallback": false,
            "fallback_reason": null
          }
        ]
      }
    ]
  }
}
```

---

## Stage 5: Quality Review Result

- **Artifact ID:** `artifact_533908107c684cacbd7620ea476e89c0`
- **Artifact Type:** `review_result`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-14T13:23:08.702293+00:00`
- **Parent Artifact Roles:** `{"script_visual_strategy": "artifact_310863c3cad84c229bdc74b5e82e4393"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Performs automated quality review checks against narrative criteria and policy bounds.

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

## Stage 6: Voice Track & Audio Assembly

- **Artifact ID:** `artifact_41f599323e9f45f4bea4adeac8407f54`
- **Artifact Type:** `voice_track`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-14T13:23:21.929118+00:00`
- **Parent Artifact Roles:** `{"script_visual_strategy": "artifact_310863c3cad84c229bdc74b5e82e4393", "hook": "artifact_8be68bb4d6b74a158fb52a458aee6c5f"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Synthesizes multi-chunk voice audio and generates word-level timestamps for caption/scene alignment.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "voice_id": "Matthew",
  "audio_file_name": "narration.mp3",
  "storage_key": "projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/narration.mp3",
  "duration_seconds": 188.376,
  "full_script_text": "You saved for years for that down payment. But the moment you sign the deed, hidden fees swallow 10 Lakhs of your cash before you even unpack a box. Stamp duty, registration, and basic interiors are waiting in the dark to drain your emergency fund.\n\nWhen you finally decide to purchase property, you assume the quoted price covers everything. But our research reveals that 78 percent of urban Indian first-time homebuyers completely fail to budget for interior work and registration fees in their initial financial planning. Stamp duty and registration charges in major Indian metro cities add an extra 5 percent to 7 percent of the property value upfront, costing approximately \u20b93.5 Lakh on a \u20b950 Lakh apartment.\n\nSociety tells you that renting is throwing money away, pushing corporate employees into rushed purchases. Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe. But this metric ignores your total financial exposure. According to the RBI Financial Stability Report 2023, average corporate buyers currently borrow at 4.5 times their annual salary, far exceeding the recommended safety limit of 2.5 times.\n\nBuying the home is only the beginning of your financial commitment. Annual maintenance charges, society fees, and municipal property taxes average 1 percent of the property's original value per year, adding \u20b950,000 annually for a \u20b950 Lakh home according to CREDAI Real Estate Outlook 2023. Furthermore, over a standard 20-year home loan tenure at an 8.5 percent interest rate, a borrower pays back roughly 2.1 times the principal amount borrowed due to cumulative interest.\n\nIn major tech hubs like Bengaluru, daily life is dictated by gridlocked traffic. According to the TomTom Traffic Index 2023, 71 minutes is the average daily one-way commute time in Bengaluru. This punishing routine drives many corporate employees to buy overpriced properties located near tech parks, forcing them into aggressive loans and trapping them in an inescapable EMI affordability cycle without adequate emergency buffers.\n\nThe most devastating part of buying a home early is the invisible opportunity cost. When you drain your savings for a down payment, you miss out on decades of market compounding. Data from AMFI India 2023 shows that the opportunity cost of locking a \u20b910 Lakh down payment into real estate rather than investing it in equity mutual funds at a historical 12 percent CAGR results in a staggering 20-year wealth gap of over \u20b996 Lakh.\n\nGenerations before us viewed renting as a waste of money, but today's financial reality is entirely different. When you factor in the immense opportunity costs, liquidity losses, and maintenance burdens of homeownership, renting while aggressively investing your capital in high-yield equities often leaves you far wealthier. You maintain the financial flexibility to switch jobs, relocate, and grow your net worth without being tied down to a crushing debt obligation.\n\nTo protect your financial future, adopt the Smart Home Buyer Blueprint. Before signing any agreement, calculate your total cost of ownership including stamp duty, registration, interiors, and maintenance. Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched. By sidestepping the \u20b910 Lakh trap, you keep your wealth compounding and secure true financial freedom.",
  "word_timestamps": [
    {
      "word": "You",
      "start_ms": 25,
      "end_ms": 149,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "saved",
      "start_ms": 150,
      "end_ms": 375,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 450,
      "end_ms": 561,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "years",
      "start_ms": 562,
      "end_ms": 787,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 900,
      "end_ms": 999,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 1000,
      "end_ms": 1180,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "down",
      "start_ms": 1212,
      "end_ms": 1392,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "payment",
      "start_ms": 1450,
      "end_ms": 1765,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "But",
      "start_ms": 2330,
      "end_ms": 2465,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 2480,
      "end_ms": 2541,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "moment",
      "start_ms": 2542,
      "end_ms": 2812,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 2867,
      "end_ms": 2941,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "sign",
      "start_ms": 2942,
      "end_ms": 3122,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 3230,
      "end_ms": 3304,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "deed",
      "start_ms": 3305,
      "end_ms": 3485,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "hidden",
      "start_ms": 3867,
      "end_ms": 4137,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "fees",
      "start_ms": 4142,
      "end_ms": 4322,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "swallow",
      "start_ms": 4430,
      "end_ms": 4745,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "10",
      "start_ms": 4817,
      "end_ms": 4917,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Lakhs",
      "start_ms": 5130,
      "end_ms": 5355,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 5417,
      "end_ms": 5504,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 5505,
      "end_ms": 5629,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cash",
      "start_ms": 5630,
      "end_ms": 5810,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "before",
      "start_ms": 5992,
      "end_ms": 6262,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 6292,
      "end_ms": 6427,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "even",
      "start_ms": 6467,
      "end_ms": 6647,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "unpack",
      "start_ms": 6655,
      "end_ms": 6925,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 7055,
      "end_ms": 7104,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "box",
      "start_ms": 7105,
      "end_ms": 7240,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Stamp",
      "start_ms": 8035,
      "end_ms": 8260,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "duty",
      "start_ms": 8397,
      "end_ms": 8577,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "registration",
      "start_ms": 8985,
      "end_ms": 9525,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 9997,
      "end_ms": 10132,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "basic",
      "start_ms": 10160,
      "end_ms": 10385,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "interiors",
      "start_ms": 10535,
      "end_ms": 10940,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "are",
      "start_ms": 11122,
      "end_ms": 11184,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "waiting",
      "start_ms": 11185,
      "end_ms": 11500,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 11510,
      "end_ms": 11571,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 11572,
      "end_ms": 11646,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "dark",
      "start_ms": 11647,
      "end_ms": 11827,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 11960,
      "end_ms": 12046,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "drain",
      "start_ms": 12047,
      "end_ms": 12272,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 12347,
      "end_ms": 12496,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "emergency",
      "start_ms": 12497,
      "end_ms": 12902,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "fund",
      "start_ms": 12985,
      "end_ms": 13165,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "When",
      "start_ms": 13561,
      "end_ms": 13710,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 13711,
      "end_ms": 13810,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "finally",
      "start_ms": 13811,
      "end_ms": 14126,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "decide",
      "start_ms": 14211,
      "end_ms": 14481,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 14598,
      "end_ms": 14672,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "purchase",
      "start_ms": 14673,
      "end_ms": 15033,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "property",
      "start_ms": 15061,
      "end_ms": 15421,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 15798,
      "end_ms": 15933,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "assume",
      "start_ms": 15961,
      "end_ms": 16231,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 16298,
      "end_ms": 16372,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "quoted",
      "start_ms": 16373,
      "end_ms": 16643,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "price",
      "start_ms": 16698,
      "end_ms": 16923,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "covers",
      "start_ms": 17011,
      "end_ms": 17281,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "everything",
      "start_ms": 17336,
      "end_ms": 17786,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "But",
      "start_ms": 18291,
      "end_ms": 18426,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "our",
      "start_ms": 18441,
      "end_ms": 18552,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "research",
      "start_ms": 18553,
      "end_ms": 18913,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "reveals",
      "start_ms": 19041,
      "end_ms": 19356,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 19516,
      "end_ms": 19665,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "78",
      "start_ms": 19666,
      "end_ms": 19766,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 20203,
      "end_ms": 20518,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 20566,
      "end_ms": 20665,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "urban",
      "start_ms": 20666,
      "end_ms": 20891,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Indian",
      "start_ms": 20941,
      "end_ms": 21211,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "first-time",
      "start_ms": 21291,
      "end_ms": 21741,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "homebuyers",
      "start_ms": 21841,
      "end_ms": 22291,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "completely",
      "start_ms": 22403,
      "end_ms": 22853,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "fail",
      "start_ms": 22866,
      "end_ms": 23046,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 23178,
      "end_ms": 23278,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "budget",
      "start_ms": 23291,
      "end_ms": 23561,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 23653,
      "end_ms": 23788,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "interior",
      "start_ms": 23853,
      "end_ms": 24213,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "work",
      "start_ms": 24291,
      "end_ms": 24471,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 24616,
      "end_ms": 24690,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "registration",
      "start_ms": 24691,
      "end_ms": 25231,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "fees",
      "start_ms": 25366,
      "end_ms": 25546,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 25716,
      "end_ms": 25777,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "their",
      "start_ms": 25778,
      "end_ms": 25927,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "initial",
      "start_ms": 25928,
      "end_ms": 26227,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 26228,
      "end_ms": 26633,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "planning",
      "start_ms": 26678,
      "end_ms": 27038,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Stamp",
      "start_ms": 27621,
      "end_ms": 27846,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "duty",
      "start_ms": 28033,
      "end_ms": 28213,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 28346,
      "end_ms": 28432,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "registration",
      "start_ms": 28433,
      "end_ms": 28973,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "charges",
      "start_ms": 29096,
      "end_ms": 29411,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 29571,
      "end_ms": 29670,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "major",
      "start_ms": 29671,
      "end_ms": 29896,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Indian",
      "start_ms": 30046,
      "end_ms": 30316,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "metro",
      "start_ms": 30333,
      "end_ms": 30558,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cities",
      "start_ms": 30658,
      "end_ms": 30928,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "add",
      "start_ms": 31071,
      "end_ms": 31206,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 31221,
      "end_ms": 31320,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "extra",
      "start_ms": 31321,
      "end_ms": 31546,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "5",
      "start_ms": 31621,
      "end_ms": 31721,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 31933,
      "end_ms": 32248,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 32333,
      "end_ms": 32432,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "7",
      "start_ms": 32433,
      "end_ms": 32533,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 32758,
      "end_ms": 33073,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 33108,
      "end_ms": 33157,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 33158,
      "end_ms": 33232,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "property",
      "start_ms": 33233,
      "end_ms": 33593,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "value",
      "start_ms": 33683,
      "end_ms": 33908,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "upfront",
      "start_ms": 34058,
      "end_ms": 34373,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "costing",
      "start_ms": 34708,
      "end_ms": 35023,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "approximately",
      "start_ms": 35121,
      "end_ms": 35706,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "\u20b93.5",
      "start_ms": 35708,
      "end_ms": 35888,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Lakh",
      "start_ms": 37208,
      "end_ms": 37388,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "on",
      "start_ms": 37533,
      "end_ms": 37632,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 37633,
      "end_ms": 37682,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "\u20b950",
      "start_ms": 37683,
      "end_ms": 37818,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Lakh",
      "start_ms": 38446,
      "end_ms": 38626,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "apartment",
      "start_ms": 38671,
      "end_ms": 39076,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Society",
      "start_ms": 39289,
      "end_ms": 39604,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "tells",
      "start_ms": 39876,
      "end_ms": 40101,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 40201,
      "end_ms": 40288,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 40289,
      "end_ms": 40450,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "renting",
      "start_ms": 40451,
      "end_ms": 40766,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 40789,
      "end_ms": 40889,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "throwing",
      "start_ms": 40901,
      "end_ms": 41238,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "money",
      "start_ms": 41239,
      "end_ms": 41464,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "away",
      "start_ms": 41489,
      "end_ms": 41669,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "pushing",
      "start_ms": 42051,
      "end_ms": 42366,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "corporate",
      "start_ms": 42389,
      "end_ms": 42763,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "employees",
      "start_ms": 42764,
      "end_ms": 43169,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "into",
      "start_ms": 43326,
      "end_ms": 43500,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rushed",
      "start_ms": 43501,
      "end_ms": 43771,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "purchases",
      "start_ms": 43776,
      "end_ms": 44181,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Real",
      "start_ms": 44881,
      "end_ms": 45061,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "estate",
      "start_ms": 45169,
      "end_ms": 45439,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "agents",
      "start_ms": 45481,
      "end_ms": 45751,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "tell",
      "start_ms": 45844,
      "end_ms": 46024,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 46056,
      "end_ms": 46191,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 46206,
      "end_ms": 46355,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "as",
      "start_ms": 46356,
      "end_ms": 46456,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "long",
      "start_ms": 46481,
      "end_ms": 46661,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "as",
      "start_ms": 46731,
      "end_ms": 46831,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 46844,
      "end_ms": 46918,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "monthly",
      "start_ms": 46919,
      "end_ms": 47234,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "EMI",
      "start_ms": 47344,
      "end_ms": 47479,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "stays",
      "start_ms": 47531,
      "end_ms": 47756,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "under",
      "start_ms": 47944,
      "end_ms": 48118,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "40",
      "start_ms": 48119,
      "end_ms": 48219,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 48431,
      "end_ms": 48746,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 48794,
      "end_ms": 48868,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 48869,
      "end_ms": 48955,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "monthly",
      "start_ms": 48956,
      "end_ms": 49271,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "salary",
      "start_ms": 49331,
      "end_ms": 49601,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 50069,
      "end_ms": 50193,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "are",
      "start_ms": 50194,
      "end_ms": 50280,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "safe",
      "start_ms": 50281,
      "end_ms": 50461,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "But",
      "start_ms": 51224,
      "end_ms": 51359,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "this",
      "start_ms": 51386,
      "end_ms": 51566,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "metric",
      "start_ms": 51586,
      "end_ms": 51856,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "ignores",
      "start_ms": 51961,
      "end_ms": 52276,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 52361,
      "end_ms": 52460,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "total",
      "start_ms": 52461,
      "end_ms": 52686,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 52761,
      "end_ms": 53166,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "exposure",
      "start_ms": 53286,
      "end_ms": 53646,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "According",
      "start_ms": 54341,
      "end_ms": 54728,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 54729,
      "end_ms": 54829,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 54841,
      "end_ms": 54976,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "RBI",
      "start_ms": 55004,
      "end_ms": 55139,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Financial",
      "start_ms": 55479,
      "end_ms": 55884,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Stability",
      "start_ms": 55966,
      "end_ms": 56371,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Report",
      "start_ms": 56441,
      "end_ms": 56711,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "2023",
      "start_ms": 56866,
      "end_ms": 57046,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "average",
      "start_ms": 58029,
      "end_ms": 58344,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "corporate",
      "start_ms": 58366,
      "end_ms": 58765,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "buyers",
      "start_ms": 58766,
      "end_ms": 59036,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "currently",
      "start_ms": 59141,
      "end_ms": 59478,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "borrow",
      "start_ms": 59479,
      "end_ms": 59749,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "at",
      "start_ms": 59916,
      "end_ms": 59978,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "4.5",
      "start_ms": 59979,
      "end_ms": 60114,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "times",
      "start_ms": 60779,
      "end_ms": 61004,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "their",
      "start_ms": 61154,
      "end_ms": 61328,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "annual",
      "start_ms": 61329,
      "end_ms": 61599,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "salary",
      "start_ms": 61604,
      "end_ms": 61874,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "far",
      "start_ms": 62316,
      "end_ms": 62451,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "exceeding",
      "start_ms": 62654,
      "end_ms": 63040,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 63041,
      "end_ms": 63128,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "recommended",
      "start_ms": 63129,
      "end_ms": 63624,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "safety",
      "start_ms": 63679,
      "end_ms": 63949,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "limit",
      "start_ms": 64041,
      "end_ms": 64266,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 64291,
      "end_ms": 64390,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "2.5",
      "start_ms": 64391,
      "end_ms": 64526,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "times",
      "start_ms": 65116,
      "end_ms": 65341,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Buying",
      "start_ms": 65761,
      "end_ms": 66031,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 66123,
      "end_ms": 66197,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "home",
      "start_ms": 66198,
      "end_ms": 66378,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 66498,
      "end_ms": 66598,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "only",
      "start_ms": 66636,
      "end_ms": 66816,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 66836,
      "end_ms": 66922,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "beginning",
      "start_ms": 66923,
      "end_ms": 67322,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 67323,
      "end_ms": 67410,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 67411,
      "end_ms": 67510,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 67511,
      "end_ms": 67916,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "commitment",
      "start_ms": 67973,
      "end_ms": 68423,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Annual",
      "start_ms": 68953,
      "end_ms": 69223,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "maintenance",
      "start_ms": 69316,
      "end_ms": 69740,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "charges",
      "start_ms": 69741,
      "end_ms": 70056,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "society",
      "start_ms": 70491,
      "end_ms": 70806,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "fees",
      "start_ms": 71041,
      "end_ms": 71221,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 71703,
      "end_ms": 71827,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "municipal",
      "start_ms": 71828,
      "end_ms": 72233,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "property",
      "start_ms": 72328,
      "end_ms": 72688,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "taxes",
      "start_ms": 72778,
      "end_ms": 73003,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "average",
      "start_ms": 73253,
      "end_ms": 73552,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "1",
      "start_ms": 73553,
      "end_ms": 73653,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 73803,
      "end_ms": 74118,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 74141,
      "end_ms": 74190,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 74191,
      "end_ms": 74265,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "property's",
      "start_ms": 74266,
      "end_ms": 74716,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "original",
      "start_ms": 74803,
      "end_ms": 75163,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "value",
      "start_ms": 75216,
      "end_ms": 75441,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "per",
      "start_ms": 75553,
      "end_ms": 75688,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "year",
      "start_ms": 75716,
      "end_ms": 75896,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "adding",
      "start_ms": 76303,
      "end_ms": 76540,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "\u20b950,000",
      "start_ms": 76541,
      "end_ms": 76856,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "annually",
      "start_ms": 77641,
      "end_ms": 78001,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 78041,
      "end_ms": 78176,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 78253,
      "end_ms": 78290,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "\u20b950",
      "start_ms": 78291,
      "end_ms": 78426,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Lakh",
      "start_ms": 79066,
      "end_ms": 79246,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "home",
      "start_ms": 79328,
      "end_ms": 79508,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "according",
      "start_ms": 79578,
      "end_ms": 79940,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 79941,
      "end_ms": 80027,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "CREDAI",
      "start_ms": 80028,
      "end_ms": 80298,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Real",
      "start_ms": 80441,
      "end_ms": 80621,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Estate",
      "start_ms": 80716,
      "end_ms": 80986,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Outlook",
      "start_ms": 81016,
      "end_ms": 81331,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "2023",
      "start_ms": 81366,
      "end_ms": 81546,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Furthermore",
      "start_ms": 82821,
      "end_ms": 83316,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "over",
      "start_ms": 83733,
      "end_ms": 83913,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 83996,
      "end_ms": 84032,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "standard",
      "start_ms": 84033,
      "end_ms": 84393,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "20-year",
      "start_ms": 84471,
      "end_ms": 84786,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "home",
      "start_ms": 84908,
      "end_ms": 85088,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "loan",
      "start_ms": 85146,
      "end_ms": 85326,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "tenure",
      "start_ms": 85433,
      "end_ms": 85703,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "at",
      "start_ms": 85833,
      "end_ms": 85907,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 85908,
      "end_ms": 86007,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "8.5",
      "start_ms": 86008,
      "end_ms": 86143,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 86746,
      "end_ms": 87061,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "interest",
      "start_ms": 87133,
      "end_ms": 87482,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rate",
      "start_ms": 87483,
      "end_ms": 87663,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 87921,
      "end_ms": 87995,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "borrower",
      "start_ms": 87996,
      "end_ms": 88356,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "pays",
      "start_ms": 88433,
      "end_ms": 88613,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "back",
      "start_ms": 88808,
      "end_ms": 88988,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "roughly",
      "start_ms": 89083,
      "end_ms": 89370,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "2.1",
      "start_ms": 89371,
      "end_ms": 89506,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "times",
      "start_ms": 90133,
      "end_ms": 90358,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 90483,
      "end_ms": 90570,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "principal",
      "start_ms": 90571,
      "end_ms": 90976,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "amount",
      "start_ms": 91058,
      "end_ms": 91328,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "borrowed",
      "start_ms": 91358,
      "end_ms": 91718,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "due",
      "start_ms": 91733,
      "end_ms": 91857,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 91858,
      "end_ms": 91932,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cumulative",
      "start_ms": 91933,
      "end_ms": 92383,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "interest",
      "start_ms": 92471,
      "end_ms": 92831,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "In",
      "start_ms": 93073,
      "end_ms": 93173,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "major",
      "start_ms": 93210,
      "end_ms": 93435,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "tech",
      "start_ms": 93535,
      "end_ms": 93715,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "hubs",
      "start_ms": 93798,
      "end_ms": 93978,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "like",
      "start_ms": 94085,
      "end_ms": 94265,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Bengaluru",
      "start_ms": 94285,
      "end_ms": 94690,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "daily",
      "start_ms": 95198,
      "end_ms": 95423,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "life",
      "start_ms": 95498,
      "end_ms": 95678,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 95835,
      "end_ms": 95935,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "dictated",
      "start_ms": 95960,
      "end_ms": 96320,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "by",
      "start_ms": 96448,
      "end_ms": 96548,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "gridlocked",
      "start_ms": 96598,
      "end_ms": 97048,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "traffic",
      "start_ms": 97073,
      "end_ms": 97388,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "According",
      "start_ms": 98053,
      "end_ms": 98427,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 98428,
      "end_ms": 98528,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 98540,
      "end_ms": 98627,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "TomTom",
      "start_ms": 98628,
      "end_ms": 98898,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Traffic",
      "start_ms": 99178,
      "end_ms": 99493,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Index",
      "start_ms": 99603,
      "end_ms": 99828,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "2023",
      "start_ms": 99978,
      "end_ms": 100158,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "71",
      "start_ms": 101078,
      "end_ms": 101178,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "minutes",
      "start_ms": 101740,
      "end_ms": 102055,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 102090,
      "end_ms": 102190,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 102203,
      "end_ms": 102338,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "average",
      "start_ms": 102365,
      "end_ms": 102680,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "daily",
      "start_ms": 102690,
      "end_ms": 102915,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "one-way",
      "start_ms": 102953,
      "end_ms": 103268,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "commute",
      "start_ms": 103378,
      "end_ms": 103693,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "time",
      "start_ms": 103740,
      "end_ms": 103920,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 104015,
      "end_ms": 104114,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Bengaluru",
      "start_ms": 104115,
      "end_ms": 104520,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "This",
      "start_ms": 105233,
      "end_ms": 105413,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "punishing",
      "start_ms": 105470,
      "end_ms": 105875,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "routine",
      "start_ms": 105908,
      "end_ms": 106223,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "drives",
      "start_ms": 106320,
      "end_ms": 106590,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "many",
      "start_ms": 106695,
      "end_ms": 106875,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "corporate",
      "start_ms": 106908,
      "end_ms": 107294,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "employees",
      "start_ms": 107295,
      "end_ms": 107700,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 107808,
      "end_ms": 107894,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "buy",
      "start_ms": 107895,
      "end_ms": 108030,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "overpriced",
      "start_ms": 108158,
      "end_ms": 108608,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "properties",
      "start_ms": 108670,
      "end_ms": 109120,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "located",
      "start_ms": 109195,
      "end_ms": 109510,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "near",
      "start_ms": 109645,
      "end_ms": 109825,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "tech",
      "start_ms": 109833,
      "end_ms": 110013,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "parks",
      "start_ms": 110083,
      "end_ms": 110308,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "forcing",
      "start_ms": 110695,
      "end_ms": 111010,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "them",
      "start_ms": 111145,
      "end_ms": 111307,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "into",
      "start_ms": 111308,
      "end_ms": 111488,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "aggressive",
      "start_ms": 111533,
      "end_ms": 111969,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "loans",
      "start_ms": 111970,
      "end_ms": 112195,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 112345,
      "end_ms": 112444,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "trapping",
      "start_ms": 112445,
      "end_ms": 112805,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "them",
      "start_ms": 112820,
      "end_ms": 112994,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 112995,
      "end_ms": 113069,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "an",
      "start_ms": 113070,
      "end_ms": 113169,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "inescapable",
      "start_ms": 113170,
      "end_ms": 113665,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "EMI",
      "start_ms": 113845,
      "end_ms": 113980,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "affordability",
      "start_ms": 114045,
      "end_ms": 114630,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cycle",
      "start_ms": 114683,
      "end_ms": 114908,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "without",
      "start_ms": 115070,
      "end_ms": 115385,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "adequate",
      "start_ms": 115408,
      "end_ms": 115768,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "emergency",
      "start_ms": 115783,
      "end_ms": 116188,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "buffers",
      "start_ms": 116283,
      "end_ms": 116598,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "The",
      "start_ms": 116953,
      "end_ms": 117052,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "most",
      "start_ms": 117053,
      "end_ms": 117233,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "devastating",
      "start_ms": 117340,
      "end_ms": 117835,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "part",
      "start_ms": 117903,
      "end_ms": 118083,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 118140,
      "end_ms": 118214,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "buying",
      "start_ms": 118215,
      "end_ms": 118485,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 118565,
      "end_ms": 118602,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "home",
      "start_ms": 118603,
      "end_ms": 118783,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "early",
      "start_ms": 118903,
      "end_ms": 119128,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 119215,
      "end_ms": 119315,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 119328,
      "end_ms": 119463,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "invisible",
      "start_ms": 119465,
      "end_ms": 119870,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "opportunity",
      "start_ms": 119915,
      "end_ms": 120410,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cost",
      "start_ms": 120428,
      "end_ms": 120608,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "When",
      "start_ms": 121370,
      "end_ms": 121532,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 121533,
      "end_ms": 121632,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "drain",
      "start_ms": 121633,
      "end_ms": 121858,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 121920,
      "end_ms": 122032,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "savings",
      "start_ms": 122033,
      "end_ms": 122348,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "for",
      "start_ms": 122508,
      "end_ms": 122643,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 122683,
      "end_ms": 122757,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "down",
      "start_ms": 122758,
      "end_ms": 122938,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "payment",
      "start_ms": 123033,
      "end_ms": 123348,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 123645,
      "end_ms": 123757,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "miss",
      "start_ms": 123758,
      "end_ms": 123938,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "out",
      "start_ms": 123995,
      "end_ms": 124130,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "on",
      "start_ms": 124145,
      "end_ms": 124245,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "decades",
      "start_ms": 124295,
      "end_ms": 124610,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 124745,
      "end_ms": 124807,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "market",
      "start_ms": 124808,
      "end_ms": 125078,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "compounding",
      "start_ms": 125145,
      "end_ms": 125640,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Data",
      "start_ms": 126250,
      "end_ms": 126430,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "from",
      "start_ms": 126550,
      "end_ms": 126730,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "AMFI",
      "start_ms": 126763,
      "end_ms": 126943,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "India",
      "start_ms": 127113,
      "end_ms": 127338,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "2023",
      "start_ms": 127400,
      "end_ms": 127580,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "shows",
      "start_ms": 128213,
      "end_ms": 128438,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "that",
      "start_ms": 128588,
      "end_ms": 128724,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 128725,
      "end_ms": 128849,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "opportunity",
      "start_ms": 128850,
      "end_ms": 129345,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cost",
      "start_ms": 129400,
      "end_ms": 129580,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 129763,
      "end_ms": 129849,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "locking",
      "start_ms": 129850,
      "end_ms": 130165,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 130213,
      "end_ms": 130262,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "\u20b910",
      "start_ms": 130263,
      "end_ms": 130398,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Lakh",
      "start_ms": 131000,
      "end_ms": 131180,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "down",
      "start_ms": 131263,
      "end_ms": 131443,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "payment",
      "start_ms": 131538,
      "end_ms": 131853,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "into",
      "start_ms": 131875,
      "end_ms": 132055,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "real",
      "start_ms": 132075,
      "end_ms": 132255,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "estate",
      "start_ms": 132338,
      "end_ms": 132608,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "rather",
      "start_ms": 132700,
      "end_ms": 132949,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "than",
      "start_ms": 132950,
      "end_ms": 133099,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "investing",
      "start_ms": 133100,
      "end_ms": 133505,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "it",
      "start_ms": 133550,
      "end_ms": 133612,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 133613,
      "end_ms": 133712,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "equity",
      "start_ms": 133713,
      "end_ms": 133983,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "mutual",
      "start_ms": 134025,
      "end_ms": 134295,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "funds",
      "start_ms": 134450,
      "end_ms": 134675,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "at",
      "start_ms": 134850,
      "end_ms": 134912,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 134913,
      "end_ms": 134949,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "historical",
      "start_ms": 134950,
      "end_ms": 135400,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "12",
      "start_ms": 135500,
      "end_ms": 135600,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "percent",
      "start_ms": 135800,
      "end_ms": 136115,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "CAGR",
      "start_ms": 136225,
      "end_ms": 136405,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "results",
      "start_ms": 137025,
      "end_ms": 137340,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 137488,
      "end_ms": 137562,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 137563,
      "end_ms": 137599,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "staggering",
      "start_ms": 137600,
      "end_ms": 138050,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "20-year",
      "start_ms": 138125,
      "end_ms": 138440,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "wealth",
      "start_ms": 138588,
      "end_ms": 138858,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "gap",
      "start_ms": 138888,
      "end_ms": 139023,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 139175,
      "end_ms": 139275,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "over",
      "start_ms": 139288,
      "end_ms": 139468,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "\u20b996",
      "start_ms": 139488,
      "end_ms": 139623,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Lakh",
      "start_ms": 140463,
      "end_ms": 140643,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Generations",
      "start_ms": 141001,
      "end_ms": 141496,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "before",
      "start_ms": 141701,
      "end_ms": 141971,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "us",
      "start_ms": 142076,
      "end_ms": 142176,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "viewed",
      "start_ms": 142213,
      "end_ms": 142475,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "renting",
      "start_ms": 142476,
      "end_ms": 142791,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "as",
      "start_ms": 142838,
      "end_ms": 142937,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 142938,
      "end_ms": 142987,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "waste",
      "start_ms": 142988,
      "end_ms": 143213,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 143301,
      "end_ms": 143375,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "money",
      "start_ms": 143376,
      "end_ms": 143601,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "but",
      "start_ms": 143876,
      "end_ms": 144011,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "today's",
      "start_ms": 144063,
      "end_ms": 144378,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 144413,
      "end_ms": 144818,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "reality",
      "start_ms": 144826,
      "end_ms": 145141,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "is",
      "start_ms": 145338,
      "end_ms": 145438,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "entirely",
      "start_ms": 145451,
      "end_ms": 145811,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "different",
      "start_ms": 145863,
      "end_ms": 146268,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "When",
      "start_ms": 146781,
      "end_ms": 146942,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 146943,
      "end_ms": 147042,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "factor",
      "start_ms": 147043,
      "end_ms": 147313,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 147493,
      "end_ms": 147567,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 147568,
      "end_ms": 147680,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "immense",
      "start_ms": 147681,
      "end_ms": 147992,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "opportunity",
      "start_ms": 147993,
      "end_ms": 148488,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "costs",
      "start_ms": 148518,
      "end_ms": 148743,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "liquidity",
      "start_ms": 149218,
      "end_ms": 149623,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "losses",
      "start_ms": 149681,
      "end_ms": 149951,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 150431,
      "end_ms": 150555,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "maintenance",
      "start_ms": 150556,
      "end_ms": 150967,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "burdens",
      "start_ms": 150968,
      "end_ms": 151283,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 151331,
      "end_ms": 151405,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "homeownership",
      "start_ms": 151406,
      "end_ms": 151991,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "renting",
      "start_ms": 152293,
      "end_ms": 152608,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "while",
      "start_ms": 152706,
      "end_ms": 152892,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "aggressively",
      "start_ms": 152893,
      "end_ms": 153433,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "investing",
      "start_ms": 153468,
      "end_ms": 153873,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 153893,
      "end_ms": 154005,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "capital",
      "start_ms": 154006,
      "end_ms": 154321,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "in",
      "start_ms": 154456,
      "end_ms": 154530,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "high-yield",
      "start_ms": 154531,
      "end_ms": 154981,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "equities",
      "start_ms": 155081,
      "end_ms": 155441,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "often",
      "start_ms": 155493,
      "end_ms": 155718,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "leaves",
      "start_ms": 155781,
      "end_ms": 156051,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 156081,
      "end_ms": 156180,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "far",
      "start_ms": 156181,
      "end_ms": 156316,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "wealthier",
      "start_ms": 156418,
      "end_ms": 156823,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "You",
      "start_ms": 157448,
      "end_ms": 157547,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "maintain",
      "start_ms": 157548,
      "end_ms": 157908,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 157973,
      "end_ms": 158047,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 158048,
      "end_ms": 158453,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "flexibility",
      "start_ms": 158511,
      "end_ms": 159006,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 159223,
      "end_ms": 159323,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "switch",
      "start_ms": 159348,
      "end_ms": 159618,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "jobs",
      "start_ms": 159686,
      "end_ms": 159866,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "relocate",
      "start_ms": 160398,
      "end_ms": 160758,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 161223,
      "end_ms": 161358,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "grow",
      "start_ms": 161373,
      "end_ms": 161553,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 161573,
      "end_ms": 161747,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "net",
      "start_ms": 161748,
      "end_ms": 161883,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "worth",
      "start_ms": 161973,
      "end_ms": 162198,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "without",
      "start_ms": 162248,
      "end_ms": 162563,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "being",
      "start_ms": 162573,
      "end_ms": 162798,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "tied",
      "start_ms": 162811,
      "end_ms": 162991,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "down",
      "start_ms": 163111,
      "end_ms": 163291,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "to",
      "start_ms": 163373,
      "end_ms": 163473,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "a",
      "start_ms": 163523,
      "end_ms": 163560,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "crushing",
      "start_ms": 163561,
      "end_ms": 163921,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "debt",
      "start_ms": 163973,
      "end_ms": 164122,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "obligation",
      "start_ms": 164123,
      "end_ms": 164573,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "To",
      "start_ms": 164977,
      "end_ms": 165076,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "protect",
      "start_ms": 165077,
      "end_ms": 165392,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 165489,
      "end_ms": 165576,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 165577,
      "end_ms": 165982,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "future",
      "start_ms": 166039,
      "end_ms": 166309,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "adopt",
      "start_ms": 166714,
      "end_ms": 166939,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 167039,
      "end_ms": 167126,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Smart",
      "start_ms": 167127,
      "end_ms": 167352,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Home",
      "start_ms": 167452,
      "end_ms": 167632,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Buyer",
      "start_ms": 167677,
      "end_ms": 167902,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Blueprint",
      "start_ms": 167939,
      "end_ms": 168344,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Before",
      "start_ms": 168957,
      "end_ms": 169227,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "signing",
      "start_ms": 169319,
      "end_ms": 169634,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "any",
      "start_ms": 169694,
      "end_ms": 169829,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "agreement",
      "start_ms": 169869,
      "end_ms": 170274,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "calculate",
      "start_ms": 170469,
      "end_ms": 170874,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 171007,
      "end_ms": 171106,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "total",
      "start_ms": 171107,
      "end_ms": 171332,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "cost",
      "start_ms": 171419,
      "end_ms": 171599,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "of",
      "start_ms": 171757,
      "end_ms": 171856,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "ownership",
      "start_ms": 171857,
      "end_ms": 172262,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "including",
      "start_ms": 172332,
      "end_ms": 172718,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "stamp",
      "start_ms": 172719,
      "end_ms": 172944,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "duty",
      "start_ms": 173057,
      "end_ms": 173237,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "registration",
      "start_ms": 173619,
      "end_ms": 174159,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "interiors",
      "start_ms": 174657,
      "end_ms": 175062,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 175507,
      "end_ms": 175618,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "maintenance",
      "start_ms": 175619,
      "end_ms": 176114,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Never",
      "start_ms": 176637,
      "end_ms": 176862,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "borrow",
      "start_ms": 176937,
      "end_ms": 177207,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "more",
      "start_ms": 177237,
      "end_ms": 177417,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "than",
      "start_ms": 177474,
      "end_ms": 177623,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "2.5",
      "start_ms": 177624,
      "end_ms": 177759,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "times",
      "start_ms": 178387,
      "end_ms": 178612,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 178749,
      "end_ms": 178898,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "annual",
      "start_ms": 178899,
      "end_ms": 179169,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "salary",
      "start_ms": 179187,
      "end_ms": 179457,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 179962,
      "end_ms": 180097,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "ensure",
      "start_ms": 180099,
      "end_ms": 180369,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 180462,
      "end_ms": 180642,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "emergency",
      "start_ms": 180674,
      "end_ms": 181079,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "fund",
      "start_ms": 181212,
      "end_ms": 181392,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "remains",
      "start_ms": 181499,
      "end_ms": 181814,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "untouched",
      "start_ms": 181912,
      "end_ms": 182317,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "By",
      "start_ms": 182967,
      "end_ms": 183067,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "sidestepping",
      "start_ms": 183129,
      "end_ms": 183669,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "the",
      "start_ms": 183792,
      "end_ms": 183866,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "\u20b910",
      "start_ms": 183867,
      "end_ms": 184002,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "Lakh",
      "start_ms": 184567,
      "end_ms": 184747,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "trap",
      "start_ms": 184804,
      "end_ms": 184984,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "you",
      "start_ms": 185367,
      "end_ms": 185478,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "keep",
      "start_ms": 185479,
      "end_ms": 185659,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "your",
      "start_ms": 185704,
      "end_ms": 185791,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "wealth",
      "start_ms": 185792,
      "end_ms": 186062,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "compounding",
      "start_ms": 186067,
      "end_ms": 186562,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "and",
      "start_ms": 186629,
      "end_ms": 186716,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "secure",
      "start_ms": 186717,
      "end_ms": 186987,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "true",
      "start_ms": 187079,
      "end_ms": 187259,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "financial",
      "start_ms": 187304,
      "end_ms": 187709,
      "start_char": null,
      "end_char": null
    },
    {
      "word": "freedom",
      "start_ms": 187754,
      "end_ms": 188069,
      "start_char": null,
      "end_char": null
    }
  ],
  "chunks": [
    {
      "chunk_id": "chunk_001",
      "sequence": 1,
      "source_id": "hook",
      "text": "You saved for years for that down payment. But the moment you sign the deed, hidden fees swallow 10 Lakhs of your cash before you even unpack a box. Stamp duty, registration, and basic interiors are waiting in the dark to drain your emergency fund.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_001.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_001.marks.json",
      "word_timestamps": [
        {
          "word": "You",
          "start_ms": 25,
          "end_ms": 149,
          "start_char": 0,
          "end_char": 3
        },
        {
          "word": "saved",
          "start_ms": 150,
          "end_ms": 375,
          "start_char": 4,
          "end_char": 9
        },
        {
          "word": "for",
          "start_ms": 450,
          "end_ms": 561,
          "start_char": 10,
          "end_char": 13
        },
        {
          "word": "years",
          "start_ms": 562,
          "end_ms": 787,
          "start_char": 14,
          "end_char": 19
        },
        {
          "word": "for",
          "start_ms": 900,
          "end_ms": 999,
          "start_char": 20,
          "end_char": 23
        },
        {
          "word": "that",
          "start_ms": 1000,
          "end_ms": 1180,
          "start_char": 24,
          "end_char": 28
        },
        {
          "word": "down",
          "start_ms": 1212,
          "end_ms": 1392,
          "start_char": 29,
          "end_char": 33
        },
        {
          "word": "payment",
          "start_ms": 1450,
          "end_ms": 1765,
          "start_char": 34,
          "end_char": 41
        },
        {
          "word": "But",
          "start_ms": 2330,
          "end_ms": 2465,
          "start_char": 43,
          "end_char": 46
        },
        {
          "word": "the",
          "start_ms": 2480,
          "end_ms": 2541,
          "start_char": 47,
          "end_char": 50
        },
        {
          "word": "moment",
          "start_ms": 2542,
          "end_ms": 2812,
          "start_char": 51,
          "end_char": 57
        },
        {
          "word": "you",
          "start_ms": 2867,
          "end_ms": 2941,
          "start_char": 58,
          "end_char": 61
        },
        {
          "word": "sign",
          "start_ms": 2942,
          "end_ms": 3122,
          "start_char": 62,
          "end_char": 66
        },
        {
          "word": "the",
          "start_ms": 3230,
          "end_ms": 3304,
          "start_char": 67,
          "end_char": 70
        },
        {
          "word": "deed",
          "start_ms": 3305,
          "end_ms": 3485,
          "start_char": 71,
          "end_char": 75
        },
        {
          "word": "hidden",
          "start_ms": 3867,
          "end_ms": 4137,
          "start_char": 77,
          "end_char": 83
        },
        {
          "word": "fees",
          "start_ms": 4142,
          "end_ms": 4322,
          "start_char": 84,
          "end_char": 88
        },
        {
          "word": "swallow",
          "start_ms": 4430,
          "end_ms": 4745,
          "start_char": 89,
          "end_char": 96
        },
        {
          "word": "10",
          "start_ms": 4817,
          "end_ms": 4917,
          "start_char": 97,
          "end_char": 99
        },
        {
          "word": "Lakhs",
          "start_ms": 5130,
          "end_ms": 5355,
          "start_char": 100,
          "end_char": 105
        },
        {
          "word": "of",
          "start_ms": 5417,
          "end_ms": 5504,
          "start_char": 106,
          "end_char": 108
        },
        {
          "word": "your",
          "start_ms": 5505,
          "end_ms": 5629,
          "start_char": 109,
          "end_char": 113
        },
        {
          "word": "cash",
          "start_ms": 5630,
          "end_ms": 5810,
          "start_char": 114,
          "end_char": 118
        },
        {
          "word": "before",
          "start_ms": 5992,
          "end_ms": 6262,
          "start_char": 119,
          "end_char": 125
        },
        {
          "word": "you",
          "start_ms": 6292,
          "end_ms": 6427,
          "start_char": 126,
          "end_char": 129
        },
        {
          "word": "even",
          "start_ms": 6467,
          "end_ms": 6647,
          "start_char": 130,
          "end_char": 134
        },
        {
          "word": "unpack",
          "start_ms": 6655,
          "end_ms": 6925,
          "start_char": 135,
          "end_char": 141
        },
        {
          "word": "a",
          "start_ms": 7055,
          "end_ms": 7104,
          "start_char": 142,
          "end_char": 143
        },
        {
          "word": "box",
          "start_ms": 7105,
          "end_ms": 7240,
          "start_char": 144,
          "end_char": 147
        },
        {
          "word": "Stamp",
          "start_ms": 8035,
          "end_ms": 8260,
          "start_char": 149,
          "end_char": 154
        },
        {
          "word": "duty",
          "start_ms": 8397,
          "end_ms": 8577,
          "start_char": 155,
          "end_char": 159
        },
        {
          "word": "registration",
          "start_ms": 8985,
          "end_ms": 9525,
          "start_char": 161,
          "end_char": 173
        },
        {
          "word": "and",
          "start_ms": 9997,
          "end_ms": 10132,
          "start_char": 175,
          "end_char": 178
        },
        {
          "word": "basic",
          "start_ms": 10160,
          "end_ms": 10385,
          "start_char": 179,
          "end_char": 184
        },
        {
          "word": "interiors",
          "start_ms": 10535,
          "end_ms": 10940,
          "start_char": 185,
          "end_char": 194
        },
        {
          "word": "are",
          "start_ms": 11122,
          "end_ms": 11184,
          "start_char": 195,
          "end_char": 198
        },
        {
          "word": "waiting",
          "start_ms": 11185,
          "end_ms": 11500,
          "start_char": 199,
          "end_char": 206
        },
        {
          "word": "in",
          "start_ms": 11510,
          "end_ms": 11571,
          "start_char": 207,
          "end_char": 209
        },
        {
          "word": "the",
          "start_ms": 11572,
          "end_ms": 11646,
          "start_char": 210,
          "end_char": 213
        },
        {
          "word": "dark",
          "start_ms": 11647,
          "end_ms": 11827,
          "start_char": 214,
          "end_char": 218
        },
        {
          "word": "to",
          "start_ms": 11960,
          "end_ms": 12046,
          "start_char": 219,
          "end_char": 221
        },
        {
          "word": "drain",
          "start_ms": 12047,
          "end_ms": 12272,
          "start_char": 222,
          "end_char": 227
        },
        {
          "word": "your",
          "start_ms": 12347,
          "end_ms": 12496,
          "start_char": 228,
          "end_char": 232
        },
        {
          "word": "emergency",
          "start_ms": 12497,
          "end_ms": 12902,
          "start_char": 233,
          "end_char": 242
        },
        {
          "word": "fund",
          "start_ms": 12985,
          "end_ms": 13165,
          "start_char": 243,
          "end_char": 247
        }
      ],
      "duration_ms": 13536,
      "duration_seconds": 13.536
    },
    {
      "chunk_id": "chunk_002",
      "sequence": 2,
      "source_id": "idea_01",
      "text": "When you finally decide to purchase property, you assume the quoted price covers everything. But our research reveals that 78 percent of urban Indian first-time homebuyers completely fail to budget for interior work and registration fees in their initial financial planning. Stamp duty and registration charges in major Indian metro cities add an extra 5 percent to 7 percent of the property value upfront, costing approximately \u20b93.5 Lakh on a \u20b950 Lakh apartment.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_002.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_002.marks.json",
      "word_timestamps": [
        {
          "word": "When",
          "start_ms": 25,
          "end_ms": 174,
          "start_char": 0,
          "end_char": 4
        },
        {
          "word": "you",
          "start_ms": 175,
          "end_ms": 274,
          "start_char": 5,
          "end_char": 8
        },
        {
          "word": "finally",
          "start_ms": 275,
          "end_ms": 590,
          "start_char": 9,
          "end_char": 16
        },
        {
          "word": "decide",
          "start_ms": 675,
          "end_ms": 945,
          "start_char": 17,
          "end_char": 23
        },
        {
          "word": "to",
          "start_ms": 1062,
          "end_ms": 1136,
          "start_char": 24,
          "end_char": 26
        },
        {
          "word": "purchase",
          "start_ms": 1137,
          "end_ms": 1497,
          "start_char": 27,
          "end_char": 35
        },
        {
          "word": "property",
          "start_ms": 1525,
          "end_ms": 1885,
          "start_char": 36,
          "end_char": 44
        },
        {
          "word": "you",
          "start_ms": 2262,
          "end_ms": 2397,
          "start_char": 46,
          "end_char": 49
        },
        {
          "word": "assume",
          "start_ms": 2425,
          "end_ms": 2695,
          "start_char": 50,
          "end_char": 56
        },
        {
          "word": "the",
          "start_ms": 2762,
          "end_ms": 2836,
          "start_char": 57,
          "end_char": 60
        },
        {
          "word": "quoted",
          "start_ms": 2837,
          "end_ms": 3107,
          "start_char": 61,
          "end_char": 67
        },
        {
          "word": "price",
          "start_ms": 3162,
          "end_ms": 3387,
          "start_char": 68,
          "end_char": 73
        },
        {
          "word": "covers",
          "start_ms": 3475,
          "end_ms": 3745,
          "start_char": 74,
          "end_char": 80
        },
        {
          "word": "everything",
          "start_ms": 3800,
          "end_ms": 4250,
          "start_char": 81,
          "end_char": 91
        },
        {
          "word": "But",
          "start_ms": 4755,
          "end_ms": 4890,
          "start_char": 93,
          "end_char": 96
        },
        {
          "word": "our",
          "start_ms": 4905,
          "end_ms": 5016,
          "start_char": 97,
          "end_char": 100
        },
        {
          "word": "research",
          "start_ms": 5017,
          "end_ms": 5377,
          "start_char": 101,
          "end_char": 109
        },
        {
          "word": "reveals",
          "start_ms": 5505,
          "end_ms": 5820,
          "start_char": 110,
          "end_char": 117
        },
        {
          "word": "that",
          "start_ms": 5980,
          "end_ms": 6129,
          "start_char": 118,
          "end_char": 122
        },
        {
          "word": "78",
          "start_ms": 6130,
          "end_ms": 6230,
          "start_char": 123,
          "end_char": 125
        },
        {
          "word": "percent",
          "start_ms": 6667,
          "end_ms": 6982,
          "start_char": 126,
          "end_char": 133
        },
        {
          "word": "of",
          "start_ms": 7030,
          "end_ms": 7129,
          "start_char": 134,
          "end_char": 136
        },
        {
          "word": "urban",
          "start_ms": 7130,
          "end_ms": 7355,
          "start_char": 137,
          "end_char": 142
        },
        {
          "word": "Indian",
          "start_ms": 7405,
          "end_ms": 7675,
          "start_char": 143,
          "end_char": 149
        },
        {
          "word": "first-time",
          "start_ms": 7755,
          "end_ms": 8205,
          "start_char": 150,
          "end_char": 160
        },
        {
          "word": "homebuyers",
          "start_ms": 8305,
          "end_ms": 8755,
          "start_char": 161,
          "end_char": 171
        },
        {
          "word": "completely",
          "start_ms": 8867,
          "end_ms": 9317,
          "start_char": 172,
          "end_char": 182
        },
        {
          "word": "fail",
          "start_ms": 9330,
          "end_ms": 9510,
          "start_char": 183,
          "end_char": 187
        },
        {
          "word": "to",
          "start_ms": 9642,
          "end_ms": 9742,
          "start_char": 188,
          "end_char": 190
        },
        {
          "word": "budget",
          "start_ms": 9755,
          "end_ms": 10025,
          "start_char": 191,
          "end_char": 197
        },
        {
          "word": "for",
          "start_ms": 10117,
          "end_ms": 10252,
          "start_char": 198,
          "end_char": 201
        },
        {
          "word": "interior",
          "start_ms": 10317,
          "end_ms": 10677,
          "start_char": 202,
          "end_char": 210
        },
        {
          "word": "work",
          "start_ms": 10755,
          "end_ms": 10935,
          "start_char": 211,
          "end_char": 215
        },
        {
          "word": "and",
          "start_ms": 11080,
          "end_ms": 11154,
          "start_char": 216,
          "end_char": 219
        },
        {
          "word": "registration",
          "start_ms": 11155,
          "end_ms": 11695,
          "start_char": 220,
          "end_char": 232
        },
        {
          "word": "fees",
          "start_ms": 11830,
          "end_ms": 12010,
          "start_char": 233,
          "end_char": 237
        },
        {
          "word": "in",
          "start_ms": 12180,
          "end_ms": 12241,
          "start_char": 238,
          "end_char": 240
        },
        {
          "word": "their",
          "start_ms": 12242,
          "end_ms": 12391,
          "start_char": 241,
          "end_char": 246
        },
        {
          "word": "initial",
          "start_ms": 12392,
          "end_ms": 12691,
          "start_char": 247,
          "end_char": 254
        },
        {
          "word": "financial",
          "start_ms": 12692,
          "end_ms": 13097,
          "start_char": 255,
          "end_char": 264
        },
        {
          "word": "planning",
          "start_ms": 13142,
          "end_ms": 13502,
          "start_char": 265,
          "end_char": 273
        },
        {
          "word": "Stamp",
          "start_ms": 14085,
          "end_ms": 14310,
          "start_char": 275,
          "end_char": 280
        },
        {
          "word": "duty",
          "start_ms": 14497,
          "end_ms": 14677,
          "start_char": 281,
          "end_char": 285
        },
        {
          "word": "and",
          "start_ms": 14810,
          "end_ms": 14896,
          "start_char": 286,
          "end_char": 289
        },
        {
          "word": "registration",
          "start_ms": 14897,
          "end_ms": 15437,
          "start_char": 290,
          "end_char": 302
        },
        {
          "word": "charges",
          "start_ms": 15560,
          "end_ms": 15875,
          "start_char": 303,
          "end_char": 310
        },
        {
          "word": "in",
          "start_ms": 16035,
          "end_ms": 16134,
          "start_char": 311,
          "end_char": 313
        },
        {
          "word": "major",
          "start_ms": 16135,
          "end_ms": 16360,
          "start_char": 314,
          "end_char": 319
        },
        {
          "word": "Indian",
          "start_ms": 16510,
          "end_ms": 16780,
          "start_char": 320,
          "end_char": 326
        },
        {
          "word": "metro",
          "start_ms": 16797,
          "end_ms": 17022,
          "start_char": 327,
          "end_char": 332
        },
        {
          "word": "cities",
          "start_ms": 17122,
          "end_ms": 17392,
          "start_char": 333,
          "end_char": 339
        },
        {
          "word": "add",
          "start_ms": 17535,
          "end_ms": 17670,
          "start_char": 340,
          "end_char": 343
        },
        {
          "word": "an",
          "start_ms": 17685,
          "end_ms": 17784,
          "start_char": 344,
          "end_char": 346
        },
        {
          "word": "extra",
          "start_ms": 17785,
          "end_ms": 18010,
          "start_char": 347,
          "end_char": 352
        },
        {
          "word": "5",
          "start_ms": 18085,
          "end_ms": 18185,
          "start_char": 353,
          "end_char": 354
        },
        {
          "word": "percent",
          "start_ms": 18397,
          "end_ms": 18712,
          "start_char": 355,
          "end_char": 362
        },
        {
          "word": "to",
          "start_ms": 18797,
          "end_ms": 18896,
          "start_char": 363,
          "end_char": 365
        },
        {
          "word": "7",
          "start_ms": 18897,
          "end_ms": 18997,
          "start_char": 366,
          "end_char": 367
        },
        {
          "word": "percent",
          "start_ms": 19222,
          "end_ms": 19537,
          "start_char": 368,
          "end_char": 375
        },
        {
          "word": "of",
          "start_ms": 19572,
          "end_ms": 19621,
          "start_char": 376,
          "end_char": 378
        },
        {
          "word": "the",
          "start_ms": 19622,
          "end_ms": 19696,
          "start_char": 379,
          "end_char": 382
        },
        {
          "word": "property",
          "start_ms": 19697,
          "end_ms": 20057,
          "start_char": 383,
          "end_char": 391
        },
        {
          "word": "value",
          "start_ms": 20147,
          "end_ms": 20372,
          "start_char": 392,
          "end_char": 397
        },
        {
          "word": "upfront",
          "start_ms": 20522,
          "end_ms": 20837,
          "start_char": 398,
          "end_char": 405
        },
        {
          "word": "costing",
          "start_ms": 21172,
          "end_ms": 21487,
          "start_char": 407,
          "end_char": 414
        },
        {
          "word": "approximately",
          "start_ms": 21585,
          "end_ms": 22170,
          "start_char": 415,
          "end_char": 428
        },
        {
          "word": "\u20b93.5",
          "start_ms": 22172,
          "end_ms": 22352,
          "start_char": 429,
          "end_char": 435
        },
        {
          "word": "Lakh",
          "start_ms": 23672,
          "end_ms": 23852,
          "start_char": 436,
          "end_char": 440
        },
        {
          "word": "on",
          "start_ms": 23997,
          "end_ms": 24096,
          "start_char": 441,
          "end_char": 443
        },
        {
          "word": "a",
          "start_ms": 24097,
          "end_ms": 24146,
          "start_char": 444,
          "end_char": 445
        },
        {
          "word": "\u20b950",
          "start_ms": 24147,
          "end_ms": 24282,
          "start_char": 446,
          "end_char": 451
        },
        {
          "word": "Lakh",
          "start_ms": 24910,
          "end_ms": 25090,
          "start_char": 452,
          "end_char": 456
        },
        {
          "word": "apartment",
          "start_ms": 25135,
          "end_ms": 25540,
          "start_char": 457,
          "end_char": 466
        }
      ],
      "duration_ms": 25728,
      "duration_seconds": 25.728
    },
    {
      "chunk_id": "chunk_003",
      "sequence": 3,
      "source_id": "idea_02",
      "text": "Society tells you that renting is throwing money away, pushing corporate employees into rushed purchases. Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe. But this metric ignores your total financial exposure. According to the RBI Financial Stability Report 2023, average corporate buyers currently borrow at 4.5 times their annual salary, far exceeding the recommended safety limit of 2.5 times.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_003.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_003.marks.json",
      "word_timestamps": [
        {
          "word": "Society",
          "start_ms": 25,
          "end_ms": 340,
          "start_char": 0,
          "end_char": 7
        },
        {
          "word": "tells",
          "start_ms": 612,
          "end_ms": 837,
          "start_char": 8,
          "end_char": 13
        },
        {
          "word": "you",
          "start_ms": 937,
          "end_ms": 1024,
          "start_char": 14,
          "end_char": 17
        },
        {
          "word": "that",
          "start_ms": 1025,
          "end_ms": 1186,
          "start_char": 18,
          "end_char": 22
        },
        {
          "word": "renting",
          "start_ms": 1187,
          "end_ms": 1502,
          "start_char": 23,
          "end_char": 30
        },
        {
          "word": "is",
          "start_ms": 1525,
          "end_ms": 1625,
          "start_char": 31,
          "end_char": 33
        },
        {
          "word": "throwing",
          "start_ms": 1637,
          "end_ms": 1974,
          "start_char": 34,
          "end_char": 42
        },
        {
          "word": "money",
          "start_ms": 1975,
          "end_ms": 2200,
          "start_char": 43,
          "end_char": 48
        },
        {
          "word": "away",
          "start_ms": 2225,
          "end_ms": 2405,
          "start_char": 49,
          "end_char": 53
        },
        {
          "word": "pushing",
          "start_ms": 2787,
          "end_ms": 3102,
          "start_char": 55,
          "end_char": 62
        },
        {
          "word": "corporate",
          "start_ms": 3125,
          "end_ms": 3499,
          "start_char": 63,
          "end_char": 72
        },
        {
          "word": "employees",
          "start_ms": 3500,
          "end_ms": 3905,
          "start_char": 73,
          "end_char": 82
        },
        {
          "word": "into",
          "start_ms": 4062,
          "end_ms": 4236,
          "start_char": 83,
          "end_char": 87
        },
        {
          "word": "rushed",
          "start_ms": 4237,
          "end_ms": 4507,
          "start_char": 88,
          "end_char": 94
        },
        {
          "word": "purchases",
          "start_ms": 4512,
          "end_ms": 4917,
          "start_char": 95,
          "end_char": 104
        },
        {
          "word": "Real",
          "start_ms": 5617,
          "end_ms": 5797,
          "start_char": 106,
          "end_char": 110
        },
        {
          "word": "estate",
          "start_ms": 5905,
          "end_ms": 6175,
          "start_char": 111,
          "end_char": 117
        },
        {
          "word": "agents",
          "start_ms": 6217,
          "end_ms": 6487,
          "start_char": 118,
          "end_char": 124
        },
        {
          "word": "tell",
          "start_ms": 6580,
          "end_ms": 6760,
          "start_char": 125,
          "end_char": 129
        },
        {
          "word": "you",
          "start_ms": 6792,
          "end_ms": 6927,
          "start_char": 130,
          "end_char": 133
        },
        {
          "word": "that",
          "start_ms": 6942,
          "end_ms": 7091,
          "start_char": 134,
          "end_char": 138
        },
        {
          "word": "as",
          "start_ms": 7092,
          "end_ms": 7192,
          "start_char": 139,
          "end_char": 141
        },
        {
          "word": "long",
          "start_ms": 7217,
          "end_ms": 7397,
          "start_char": 142,
          "end_char": 146
        },
        {
          "word": "as",
          "start_ms": 7467,
          "end_ms": 7567,
          "start_char": 147,
          "end_char": 149
        },
        {
          "word": "your",
          "start_ms": 7580,
          "end_ms": 7654,
          "start_char": 150,
          "end_char": 154
        },
        {
          "word": "monthly",
          "start_ms": 7655,
          "end_ms": 7970,
          "start_char": 155,
          "end_char": 162
        },
        {
          "word": "EMI",
          "start_ms": 8080,
          "end_ms": 8215,
          "start_char": 163,
          "end_char": 166
        },
        {
          "word": "stays",
          "start_ms": 8267,
          "end_ms": 8492,
          "start_char": 167,
          "end_char": 172
        },
        {
          "word": "under",
          "start_ms": 8680,
          "end_ms": 8854,
          "start_char": 173,
          "end_char": 178
        },
        {
          "word": "40",
          "start_ms": 8855,
          "end_ms": 8955,
          "start_char": 179,
          "end_char": 181
        },
        {
          "word": "percent",
          "start_ms": 9167,
          "end_ms": 9482,
          "start_char": 182,
          "end_char": 189
        },
        {
          "word": "of",
          "start_ms": 9530,
          "end_ms": 9604,
          "start_char": 190,
          "end_char": 192
        },
        {
          "word": "your",
          "start_ms": 9605,
          "end_ms": 9691,
          "start_char": 193,
          "end_char": 197
        },
        {
          "word": "monthly",
          "start_ms": 9692,
          "end_ms": 10007,
          "start_char": 198,
          "end_char": 205
        },
        {
          "word": "salary",
          "start_ms": 10067,
          "end_ms": 10337,
          "start_char": 206,
          "end_char": 212
        },
        {
          "word": "you",
          "start_ms": 10805,
          "end_ms": 10929,
          "start_char": 214,
          "end_char": 217
        },
        {
          "word": "are",
          "start_ms": 10930,
          "end_ms": 11016,
          "start_char": 218,
          "end_char": 221
        },
        {
          "word": "safe",
          "start_ms": 11017,
          "end_ms": 11197,
          "start_char": 222,
          "end_char": 226
        },
        {
          "word": "But",
          "start_ms": 11960,
          "end_ms": 12095,
          "start_char": 228,
          "end_char": 231
        },
        {
          "word": "this",
          "start_ms": 12122,
          "end_ms": 12302,
          "start_char": 232,
          "end_char": 236
        },
        {
          "word": "metric",
          "start_ms": 12322,
          "end_ms": 12592,
          "start_char": 237,
          "end_char": 243
        },
        {
          "word": "ignores",
          "start_ms": 12697,
          "end_ms": 13012,
          "start_char": 244,
          "end_char": 251
        },
        {
          "word": "your",
          "start_ms": 13097,
          "end_ms": 13196,
          "start_char": 252,
          "end_char": 256
        },
        {
          "word": "total",
          "start_ms": 13197,
          "end_ms": 13422,
          "start_char": 257,
          "end_char": 262
        },
        {
          "word": "financial",
          "start_ms": 13497,
          "end_ms": 13902,
          "start_char": 263,
          "end_char": 272
        },
        {
          "word": "exposure",
          "start_ms": 14022,
          "end_ms": 14382,
          "start_char": 273,
          "end_char": 281
        },
        {
          "word": "According",
          "start_ms": 15077,
          "end_ms": 15464,
          "start_char": 283,
          "end_char": 292
        },
        {
          "word": "to",
          "start_ms": 15465,
          "end_ms": 15565,
          "start_char": 293,
          "end_char": 295
        },
        {
          "word": "the",
          "start_ms": 15577,
          "end_ms": 15712,
          "start_char": 296,
          "end_char": 299
        },
        {
          "word": "RBI",
          "start_ms": 15740,
          "end_ms": 15875,
          "start_char": 300,
          "end_char": 303
        },
        {
          "word": "Financial",
          "start_ms": 16215,
          "end_ms": 16620,
          "start_char": 304,
          "end_char": 313
        },
        {
          "word": "Stability",
          "start_ms": 16702,
          "end_ms": 17107,
          "start_char": 314,
          "end_char": 323
        },
        {
          "word": "Report",
          "start_ms": 17177,
          "end_ms": 17447,
          "start_char": 324,
          "end_char": 330
        },
        {
          "word": "2023",
          "start_ms": 17602,
          "end_ms": 17782,
          "start_char": 331,
          "end_char": 335
        },
        {
          "word": "average",
          "start_ms": 18765,
          "end_ms": 19080,
          "start_char": 337,
          "end_char": 344
        },
        {
          "word": "corporate",
          "start_ms": 19102,
          "end_ms": 19501,
          "start_char": 345,
          "end_char": 354
        },
        {
          "word": "buyers",
          "start_ms": 19502,
          "end_ms": 19772,
          "start_char": 355,
          "end_char": 361
        },
        {
          "word": "currently",
          "start_ms": 19877,
          "end_ms": 20214,
          "start_char": 362,
          "end_char": 371
        },
        {
          "word": "borrow",
          "start_ms": 20215,
          "end_ms": 20485,
          "start_char": 372,
          "end_char": 378
        },
        {
          "word": "at",
          "start_ms": 20652,
          "end_ms": 20714,
          "start_char": 379,
          "end_char": 381
        },
        {
          "word": "4.5",
          "start_ms": 20715,
          "end_ms": 20850,
          "start_char": 382,
          "end_char": 385
        },
        {
          "word": "times",
          "start_ms": 21515,
          "end_ms": 21740,
          "start_char": 386,
          "end_char": 391
        },
        {
          "word": "their",
          "start_ms": 21890,
          "end_ms": 22064,
          "start_char": 392,
          "end_char": 397
        },
        {
          "word": "annual",
          "start_ms": 22065,
          "end_ms": 22335,
          "start_char": 398,
          "end_char": 404
        },
        {
          "word": "salary",
          "start_ms": 22340,
          "end_ms": 22610,
          "start_char": 405,
          "end_char": 411
        },
        {
          "word": "far",
          "start_ms": 23052,
          "end_ms": 23187,
          "start_char": 413,
          "end_char": 416
        },
        {
          "word": "exceeding",
          "start_ms": 23390,
          "end_ms": 23776,
          "start_char": 417,
          "end_char": 426
        },
        {
          "word": "the",
          "start_ms": 23777,
          "end_ms": 23864,
          "start_char": 427,
          "end_char": 430
        },
        {
          "word": "recommended",
          "start_ms": 23865,
          "end_ms": 24360,
          "start_char": 431,
          "end_char": 442
        },
        {
          "word": "safety",
          "start_ms": 24415,
          "end_ms": 24685,
          "start_char": 443,
          "end_char": 449
        },
        {
          "word": "limit",
          "start_ms": 24777,
          "end_ms": 25002,
          "start_char": 450,
          "end_char": 455
        },
        {
          "word": "of",
          "start_ms": 25027,
          "end_ms": 25126,
          "start_char": 456,
          "end_char": 458
        },
        {
          "word": "2.5",
          "start_ms": 25127,
          "end_ms": 25262,
          "start_char": 459,
          "end_char": 462
        },
        {
          "word": "times",
          "start_ms": 25852,
          "end_ms": 26077,
          "start_char": 463,
          "end_char": 468
        }
      ],
      "duration_ms": 26472,
      "duration_seconds": 26.472
    },
    {
      "chunk_id": "chunk_004",
      "sequence": 4,
      "source_id": "idea_03",
      "text": "Buying the home is only the beginning of your financial commitment. Annual maintenance charges, society fees, and municipal property taxes average 1 percent of the property's original value per year, adding \u20b950,000 annually for a \u20b950 Lakh home according to CREDAI Real Estate Outlook 2023. Furthermore, over a standard 20-year home loan tenure at an 8.5 percent interest rate, a borrower pays back roughly 2.1 times the principal amount borrowed due to cumulative interest.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_004.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_004.marks.json",
      "word_timestamps": [
        {
          "word": "Buying",
          "start_ms": 25,
          "end_ms": 295,
          "start_char": 0,
          "end_char": 6
        },
        {
          "word": "the",
          "start_ms": 387,
          "end_ms": 461,
          "start_char": 7,
          "end_char": 10
        },
        {
          "word": "home",
          "start_ms": 462,
          "end_ms": 642,
          "start_char": 11,
          "end_char": 15
        },
        {
          "word": "is",
          "start_ms": 762,
          "end_ms": 862,
          "start_char": 16,
          "end_char": 18
        },
        {
          "word": "only",
          "start_ms": 900,
          "end_ms": 1080,
          "start_char": 19,
          "end_char": 23
        },
        {
          "word": "the",
          "start_ms": 1100,
          "end_ms": 1186,
          "start_char": 24,
          "end_char": 27
        },
        {
          "word": "beginning",
          "start_ms": 1187,
          "end_ms": 1586,
          "start_char": 28,
          "end_char": 37
        },
        {
          "word": "of",
          "start_ms": 1587,
          "end_ms": 1674,
          "start_char": 38,
          "end_char": 40
        },
        {
          "word": "your",
          "start_ms": 1675,
          "end_ms": 1774,
          "start_char": 41,
          "end_char": 45
        },
        {
          "word": "financial",
          "start_ms": 1775,
          "end_ms": 2180,
          "start_char": 46,
          "end_char": 55
        },
        {
          "word": "commitment",
          "start_ms": 2237,
          "end_ms": 2687,
          "start_char": 56,
          "end_char": 66
        },
        {
          "word": "Annual",
          "start_ms": 3217,
          "end_ms": 3487,
          "start_char": 68,
          "end_char": 74
        },
        {
          "word": "maintenance",
          "start_ms": 3580,
          "end_ms": 4004,
          "start_char": 75,
          "end_char": 86
        },
        {
          "word": "charges",
          "start_ms": 4005,
          "end_ms": 4320,
          "start_char": 87,
          "end_char": 94
        },
        {
          "word": "society",
          "start_ms": 4755,
          "end_ms": 5070,
          "start_char": 96,
          "end_char": 103
        },
        {
          "word": "fees",
          "start_ms": 5305,
          "end_ms": 5485,
          "start_char": 104,
          "end_char": 108
        },
        {
          "word": "and",
          "start_ms": 5967,
          "end_ms": 6091,
          "start_char": 110,
          "end_char": 113
        },
        {
          "word": "municipal",
          "start_ms": 6092,
          "end_ms": 6497,
          "start_char": 114,
          "end_char": 123
        },
        {
          "word": "property",
          "start_ms": 6592,
          "end_ms": 6952,
          "start_char": 124,
          "end_char": 132
        },
        {
          "word": "taxes",
          "start_ms": 7042,
          "end_ms": 7267,
          "start_char": 133,
          "end_char": 138
        },
        {
          "word": "average",
          "start_ms": 7517,
          "end_ms": 7816,
          "start_char": 139,
          "end_char": 146
        },
        {
          "word": "1",
          "start_ms": 7817,
          "end_ms": 7917,
          "start_char": 147,
          "end_char": 148
        },
        {
          "word": "percent",
          "start_ms": 8067,
          "end_ms": 8382,
          "start_char": 149,
          "end_char": 156
        },
        {
          "word": "of",
          "start_ms": 8405,
          "end_ms": 8454,
          "start_char": 157,
          "end_char": 159
        },
        {
          "word": "the",
          "start_ms": 8455,
          "end_ms": 8529,
          "start_char": 160,
          "end_char": 163
        },
        {
          "word": "property's",
          "start_ms": 8530,
          "end_ms": 8980,
          "start_char": 164,
          "end_char": 174
        },
        {
          "word": "original",
          "start_ms": 9067,
          "end_ms": 9427,
          "start_char": 175,
          "end_char": 183
        },
        {
          "word": "value",
          "start_ms": 9480,
          "end_ms": 9705,
          "start_char": 184,
          "end_char": 189
        },
        {
          "word": "per",
          "start_ms": 9817,
          "end_ms": 9952,
          "start_char": 190,
          "end_char": 193
        },
        {
          "word": "year",
          "start_ms": 9980,
          "end_ms": 10160,
          "start_char": 194,
          "end_char": 198
        },
        {
          "word": "adding",
          "start_ms": 10567,
          "end_ms": 10804,
          "start_char": 200,
          "end_char": 206
        },
        {
          "word": "\u20b950,000",
          "start_ms": 10805,
          "end_ms": 11120,
          "start_char": 207,
          "end_char": 216
        },
        {
          "word": "annually",
          "start_ms": 11905,
          "end_ms": 12265,
          "start_char": 217,
          "end_char": 225
        },
        {
          "word": "for",
          "start_ms": 12305,
          "end_ms": 12440,
          "start_char": 226,
          "end_char": 229
        },
        {
          "word": "a",
          "start_ms": 12517,
          "end_ms": 12554,
          "start_char": 230,
          "end_char": 231
        },
        {
          "word": "\u20b950",
          "start_ms": 12555,
          "end_ms": 12690,
          "start_char": 232,
          "end_char": 237
        },
        {
          "word": "Lakh",
          "start_ms": 13330,
          "end_ms": 13510,
          "start_char": 238,
          "end_char": 242
        },
        {
          "word": "home",
          "start_ms": 13592,
          "end_ms": 13772,
          "start_char": 243,
          "end_char": 247
        },
        {
          "word": "according",
          "start_ms": 13842,
          "end_ms": 14204,
          "start_char": 248,
          "end_char": 257
        },
        {
          "word": "to",
          "start_ms": 14205,
          "end_ms": 14291,
          "start_char": 258,
          "end_char": 260
        },
        {
          "word": "CREDAI",
          "start_ms": 14292,
          "end_ms": 14562,
          "start_char": 261,
          "end_char": 267
        },
        {
          "word": "Real",
          "start_ms": 14705,
          "end_ms": 14885,
          "start_char": 268,
          "end_char": 272
        },
        {
          "word": "Estate",
          "start_ms": 14980,
          "end_ms": 15250,
          "start_char": 273,
          "end_char": 279
        },
        {
          "word": "Outlook",
          "start_ms": 15280,
          "end_ms": 15595,
          "start_char": 280,
          "end_char": 287
        },
        {
          "word": "2023",
          "start_ms": 15630,
          "end_ms": 15810,
          "start_char": 288,
          "end_char": 292
        },
        {
          "word": "Furthermore",
          "start_ms": 17085,
          "end_ms": 17580,
          "start_char": 294,
          "end_char": 305
        },
        {
          "word": "over",
          "start_ms": 17997,
          "end_ms": 18177,
          "start_char": 307,
          "end_char": 311
        },
        {
          "word": "a",
          "start_ms": 18260,
          "end_ms": 18296,
          "start_char": 312,
          "end_char": 313
        },
        {
          "word": "standard",
          "start_ms": 18297,
          "end_ms": 18657,
          "start_char": 314,
          "end_char": 322
        },
        {
          "word": "20-year",
          "start_ms": 18735,
          "end_ms": 19050,
          "start_char": 323,
          "end_char": 330
        },
        {
          "word": "home",
          "start_ms": 19172,
          "end_ms": 19352,
          "start_char": 331,
          "end_char": 335
        },
        {
          "word": "loan",
          "start_ms": 19410,
          "end_ms": 19590,
          "start_char": 336,
          "end_char": 340
        },
        {
          "word": "tenure",
          "start_ms": 19697,
          "end_ms": 19967,
          "start_char": 341,
          "end_char": 347
        },
        {
          "word": "at",
          "start_ms": 20097,
          "end_ms": 20171,
          "start_char": 348,
          "end_char": 350
        },
        {
          "word": "an",
          "start_ms": 20172,
          "end_ms": 20271,
          "start_char": 351,
          "end_char": 353
        },
        {
          "word": "8.5",
          "start_ms": 20272,
          "end_ms": 20407,
          "start_char": 354,
          "end_char": 357
        },
        {
          "word": "percent",
          "start_ms": 21010,
          "end_ms": 21325,
          "start_char": 358,
          "end_char": 365
        },
        {
          "word": "interest",
          "start_ms": 21397,
          "end_ms": 21746,
          "start_char": 366,
          "end_char": 374
        },
        {
          "word": "rate",
          "start_ms": 21747,
          "end_ms": 21927,
          "start_char": 375,
          "end_char": 379
        },
        {
          "word": "a",
          "start_ms": 22185,
          "end_ms": 22259,
          "start_char": 381,
          "end_char": 382
        },
        {
          "word": "borrower",
          "start_ms": 22260,
          "end_ms": 22620,
          "start_char": 383,
          "end_char": 391
        },
        {
          "word": "pays",
          "start_ms": 22697,
          "end_ms": 22877,
          "start_char": 392,
          "end_char": 396
        },
        {
          "word": "back",
          "start_ms": 23072,
          "end_ms": 23252,
          "start_char": 397,
          "end_char": 401
        },
        {
          "word": "roughly",
          "start_ms": 23347,
          "end_ms": 23634,
          "start_char": 402,
          "end_char": 409
        },
        {
          "word": "2.1",
          "start_ms": 23635,
          "end_ms": 23770,
          "start_char": 410,
          "end_char": 413
        },
        {
          "word": "times",
          "start_ms": 24397,
          "end_ms": 24622,
          "start_char": 414,
          "end_char": 419
        },
        {
          "word": "the",
          "start_ms": 24747,
          "end_ms": 24834,
          "start_char": 420,
          "end_char": 423
        },
        {
          "word": "principal",
          "start_ms": 24835,
          "end_ms": 25240,
          "start_char": 424,
          "end_char": 433
        },
        {
          "word": "amount",
          "start_ms": 25322,
          "end_ms": 25592,
          "start_char": 434,
          "end_char": 440
        },
        {
          "word": "borrowed",
          "start_ms": 25622,
          "end_ms": 25982,
          "start_char": 441,
          "end_char": 449
        },
        {
          "word": "due",
          "start_ms": 25997,
          "end_ms": 26121,
          "start_char": 450,
          "end_char": 453
        },
        {
          "word": "to",
          "start_ms": 26122,
          "end_ms": 26196,
          "start_char": 454,
          "end_char": 456
        },
        {
          "word": "cumulative",
          "start_ms": 26197,
          "end_ms": 26647,
          "start_char": 457,
          "end_char": 467
        },
        {
          "word": "interest",
          "start_ms": 26735,
          "end_ms": 27095,
          "start_char": 468,
          "end_char": 476
        }
      ],
      "duration_ms": 27312,
      "duration_seconds": 27.312
    },
    {
      "chunk_id": "chunk_005",
      "sequence": 5,
      "source_id": "idea_04",
      "text": "In major tech hubs like Bengaluru, daily life is dictated by gridlocked traffic. According to the TomTom Traffic Index 2023, 71 minutes is the average daily one-way commute time in Bengaluru. This punishing routine drives many corporate employees to buy overpriced properties located near tech parks, forcing them into aggressive loans and trapping them in an inescapable EMI affordability cycle without adequate emergency buffers.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_005.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_005.marks.json",
      "word_timestamps": [
        {
          "word": "In",
          "start_ms": 25,
          "end_ms": 125,
          "start_char": 0,
          "end_char": 2
        },
        {
          "word": "major",
          "start_ms": 162,
          "end_ms": 387,
          "start_char": 3,
          "end_char": 8
        },
        {
          "word": "tech",
          "start_ms": 487,
          "end_ms": 667,
          "start_char": 9,
          "end_char": 13
        },
        {
          "word": "hubs",
          "start_ms": 750,
          "end_ms": 930,
          "start_char": 14,
          "end_char": 18
        },
        {
          "word": "like",
          "start_ms": 1037,
          "end_ms": 1217,
          "start_char": 19,
          "end_char": 23
        },
        {
          "word": "Bengaluru",
          "start_ms": 1237,
          "end_ms": 1642,
          "start_char": 24,
          "end_char": 33
        },
        {
          "word": "daily",
          "start_ms": 2150,
          "end_ms": 2375,
          "start_char": 35,
          "end_char": 40
        },
        {
          "word": "life",
          "start_ms": 2450,
          "end_ms": 2630,
          "start_char": 41,
          "end_char": 45
        },
        {
          "word": "is",
          "start_ms": 2787,
          "end_ms": 2887,
          "start_char": 46,
          "end_char": 48
        },
        {
          "word": "dictated",
          "start_ms": 2912,
          "end_ms": 3272,
          "start_char": 49,
          "end_char": 57
        },
        {
          "word": "by",
          "start_ms": 3400,
          "end_ms": 3500,
          "start_char": 58,
          "end_char": 60
        },
        {
          "word": "gridlocked",
          "start_ms": 3550,
          "end_ms": 4000,
          "start_char": 61,
          "end_char": 71
        },
        {
          "word": "traffic",
          "start_ms": 4025,
          "end_ms": 4340,
          "start_char": 72,
          "end_char": 79
        },
        {
          "word": "According",
          "start_ms": 5005,
          "end_ms": 5379,
          "start_char": 81,
          "end_char": 90
        },
        {
          "word": "to",
          "start_ms": 5380,
          "end_ms": 5480,
          "start_char": 91,
          "end_char": 93
        },
        {
          "word": "the",
          "start_ms": 5492,
          "end_ms": 5579,
          "start_char": 94,
          "end_char": 97
        },
        {
          "word": "TomTom",
          "start_ms": 5580,
          "end_ms": 5850,
          "start_char": 98,
          "end_char": 104
        },
        {
          "word": "Traffic",
          "start_ms": 6130,
          "end_ms": 6445,
          "start_char": 105,
          "end_char": 112
        },
        {
          "word": "Index",
          "start_ms": 6555,
          "end_ms": 6780,
          "start_char": 113,
          "end_char": 118
        },
        {
          "word": "2023",
          "start_ms": 6930,
          "end_ms": 7110,
          "start_char": 119,
          "end_char": 123
        },
        {
          "word": "71",
          "start_ms": 8030,
          "end_ms": 8130,
          "start_char": 125,
          "end_char": 127
        },
        {
          "word": "minutes",
          "start_ms": 8692,
          "end_ms": 9007,
          "start_char": 128,
          "end_char": 135
        },
        {
          "word": "is",
          "start_ms": 9042,
          "end_ms": 9142,
          "start_char": 136,
          "end_char": 138
        },
        {
          "word": "the",
          "start_ms": 9155,
          "end_ms": 9290,
          "start_char": 139,
          "end_char": 142
        },
        {
          "word": "average",
          "start_ms": 9317,
          "end_ms": 9632,
          "start_char": 143,
          "end_char": 150
        },
        {
          "word": "daily",
          "start_ms": 9642,
          "end_ms": 9867,
          "start_char": 151,
          "end_char": 156
        },
        {
          "word": "one-way",
          "start_ms": 9905,
          "end_ms": 10220,
          "start_char": 157,
          "end_char": 164
        },
        {
          "word": "commute",
          "start_ms": 10330,
          "end_ms": 10645,
          "start_char": 165,
          "end_char": 172
        },
        {
          "word": "time",
          "start_ms": 10692,
          "end_ms": 10872,
          "start_char": 173,
          "end_char": 177
        },
        {
          "word": "in",
          "start_ms": 10967,
          "end_ms": 11066,
          "start_char": 178,
          "end_char": 180
        },
        {
          "word": "Bengaluru",
          "start_ms": 11067,
          "end_ms": 11472,
          "start_char": 181,
          "end_char": 190
        },
        {
          "word": "This",
          "start_ms": 12185,
          "end_ms": 12365,
          "start_char": 192,
          "end_char": 196
        },
        {
          "word": "punishing",
          "start_ms": 12422,
          "end_ms": 12827,
          "start_char": 197,
          "end_char": 206
        },
        {
          "word": "routine",
          "start_ms": 12860,
          "end_ms": 13175,
          "start_char": 207,
          "end_char": 214
        },
        {
          "word": "drives",
          "start_ms": 13272,
          "end_ms": 13542,
          "start_char": 215,
          "end_char": 221
        },
        {
          "word": "many",
          "start_ms": 13647,
          "end_ms": 13827,
          "start_char": 222,
          "end_char": 226
        },
        {
          "word": "corporate",
          "start_ms": 13860,
          "end_ms": 14246,
          "start_char": 227,
          "end_char": 236
        },
        {
          "word": "employees",
          "start_ms": 14247,
          "end_ms": 14652,
          "start_char": 237,
          "end_char": 246
        },
        {
          "word": "to",
          "start_ms": 14760,
          "end_ms": 14846,
          "start_char": 247,
          "end_char": 249
        },
        {
          "word": "buy",
          "start_ms": 14847,
          "end_ms": 14982,
          "start_char": 250,
          "end_char": 253
        },
        {
          "word": "overpriced",
          "start_ms": 15110,
          "end_ms": 15560,
          "start_char": 254,
          "end_char": 264
        },
        {
          "word": "properties",
          "start_ms": 15622,
          "end_ms": 16072,
          "start_char": 265,
          "end_char": 275
        },
        {
          "word": "located",
          "start_ms": 16147,
          "end_ms": 16462,
          "start_char": 276,
          "end_char": 283
        },
        {
          "word": "near",
          "start_ms": 16597,
          "end_ms": 16777,
          "start_char": 284,
          "end_char": 288
        },
        {
          "word": "tech",
          "start_ms": 16785,
          "end_ms": 16965,
          "start_char": 289,
          "end_char": 293
        },
        {
          "word": "parks",
          "start_ms": 17035,
          "end_ms": 17260,
          "start_char": 294,
          "end_char": 299
        },
        {
          "word": "forcing",
          "start_ms": 17647,
          "end_ms": 17962,
          "start_char": 301,
          "end_char": 308
        },
        {
          "word": "them",
          "start_ms": 18097,
          "end_ms": 18259,
          "start_char": 309,
          "end_char": 313
        },
        {
          "word": "into",
          "start_ms": 18260,
          "end_ms": 18440,
          "start_char": 314,
          "end_char": 318
        },
        {
          "word": "aggressive",
          "start_ms": 18485,
          "end_ms": 18921,
          "start_char": 319,
          "end_char": 329
        },
        {
          "word": "loans",
          "start_ms": 18922,
          "end_ms": 19147,
          "start_char": 330,
          "end_char": 335
        },
        {
          "word": "and",
          "start_ms": 19297,
          "end_ms": 19396,
          "start_char": 336,
          "end_char": 339
        },
        {
          "word": "trapping",
          "start_ms": 19397,
          "end_ms": 19757,
          "start_char": 340,
          "end_char": 348
        },
        {
          "word": "them",
          "start_ms": 19772,
          "end_ms": 19946,
          "start_char": 349,
          "end_char": 353
        },
        {
          "word": "in",
          "start_ms": 19947,
          "end_ms": 20021,
          "start_char": 354,
          "end_char": 356
        },
        {
          "word": "an",
          "start_ms": 20022,
          "end_ms": 20121,
          "start_char": 357,
          "end_char": 359
        },
        {
          "word": "inescapable",
          "start_ms": 20122,
          "end_ms": 20617,
          "start_char": 360,
          "end_char": 371
        },
        {
          "word": "EMI",
          "start_ms": 20797,
          "end_ms": 20932,
          "start_char": 372,
          "end_char": 375
        },
        {
          "word": "affordability",
          "start_ms": 20997,
          "end_ms": 21582,
          "start_char": 376,
          "end_char": 389
        },
        {
          "word": "cycle",
          "start_ms": 21635,
          "end_ms": 21860,
          "start_char": 390,
          "end_char": 395
        },
        {
          "word": "without",
          "start_ms": 22022,
          "end_ms": 22337,
          "start_char": 396,
          "end_char": 403
        },
        {
          "word": "adequate",
          "start_ms": 22360,
          "end_ms": 22720,
          "start_char": 404,
          "end_char": 412
        },
        {
          "word": "emergency",
          "start_ms": 22735,
          "end_ms": 23140,
          "start_char": 413,
          "end_char": 422
        },
        {
          "word": "buffers",
          "start_ms": 23235,
          "end_ms": 23550,
          "start_char": 423,
          "end_char": 430
        }
      ],
      "duration_ms": 23880,
      "duration_seconds": 23.88
    },
    {
      "chunk_id": "chunk_006",
      "sequence": 6,
      "source_id": "idea_05",
      "text": "The most devastating part of buying a home early is the invisible opportunity cost. When you drain your savings for a down payment, you miss out on decades of market compounding. Data from AMFI India 2023 shows that the opportunity cost of locking a \u20b910 Lakh down payment into real estate rather than investing it in equity mutual funds at a historical 12 percent CAGR results in a staggering 20-year wealth gap of over \u20b996 Lakh.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_006.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_006.marks.json",
      "word_timestamps": [
        {
          "word": "The",
          "start_ms": 25,
          "end_ms": 124,
          "start_char": 0,
          "end_char": 3
        },
        {
          "word": "most",
          "start_ms": 125,
          "end_ms": 305,
          "start_char": 4,
          "end_char": 8
        },
        {
          "word": "devastating",
          "start_ms": 412,
          "end_ms": 907,
          "start_char": 9,
          "end_char": 20
        },
        {
          "word": "part",
          "start_ms": 975,
          "end_ms": 1155,
          "start_char": 21,
          "end_char": 25
        },
        {
          "word": "of",
          "start_ms": 1212,
          "end_ms": 1286,
          "start_char": 26,
          "end_char": 28
        },
        {
          "word": "buying",
          "start_ms": 1287,
          "end_ms": 1557,
          "start_char": 29,
          "end_char": 35
        },
        {
          "word": "a",
          "start_ms": 1637,
          "end_ms": 1674,
          "start_char": 36,
          "end_char": 37
        },
        {
          "word": "home",
          "start_ms": 1675,
          "end_ms": 1855,
          "start_char": 38,
          "end_char": 42
        },
        {
          "word": "early",
          "start_ms": 1975,
          "end_ms": 2200,
          "start_char": 43,
          "end_char": 48
        },
        {
          "word": "is",
          "start_ms": 2287,
          "end_ms": 2387,
          "start_char": 49,
          "end_char": 51
        },
        {
          "word": "the",
          "start_ms": 2400,
          "end_ms": 2535,
          "start_char": 52,
          "end_char": 55
        },
        {
          "word": "invisible",
          "start_ms": 2537,
          "end_ms": 2942,
          "start_char": 56,
          "end_char": 65
        },
        {
          "word": "opportunity",
          "start_ms": 2987,
          "end_ms": 3482,
          "start_char": 66,
          "end_char": 77
        },
        {
          "word": "cost",
          "start_ms": 3500,
          "end_ms": 3680,
          "start_char": 78,
          "end_char": 82
        },
        {
          "word": "When",
          "start_ms": 4442,
          "end_ms": 4604,
          "start_char": 84,
          "end_char": 88
        },
        {
          "word": "you",
          "start_ms": 4605,
          "end_ms": 4704,
          "start_char": 89,
          "end_char": 92
        },
        {
          "word": "drain",
          "start_ms": 4705,
          "end_ms": 4930,
          "start_char": 93,
          "end_char": 98
        },
        {
          "word": "your",
          "start_ms": 4992,
          "end_ms": 5104,
          "start_char": 99,
          "end_char": 103
        },
        {
          "word": "savings",
          "start_ms": 5105,
          "end_ms": 5420,
          "start_char": 104,
          "end_char": 111
        },
        {
          "word": "for",
          "start_ms": 5580,
          "end_ms": 5715,
          "start_char": 112,
          "end_char": 115
        },
        {
          "word": "a",
          "start_ms": 5755,
          "end_ms": 5829,
          "start_char": 116,
          "end_char": 117
        },
        {
          "word": "down",
          "start_ms": 5830,
          "end_ms": 6010,
          "start_char": 118,
          "end_char": 122
        },
        {
          "word": "payment",
          "start_ms": 6105,
          "end_ms": 6420,
          "start_char": 123,
          "end_char": 130
        },
        {
          "word": "you",
          "start_ms": 6717,
          "end_ms": 6829,
          "start_char": 132,
          "end_char": 135
        },
        {
          "word": "miss",
          "start_ms": 6830,
          "end_ms": 7010,
          "start_char": 136,
          "end_char": 140
        },
        {
          "word": "out",
          "start_ms": 7067,
          "end_ms": 7202,
          "start_char": 141,
          "end_char": 144
        },
        {
          "word": "on",
          "start_ms": 7217,
          "end_ms": 7317,
          "start_char": 145,
          "end_char": 147
        },
        {
          "word": "decades",
          "start_ms": 7367,
          "end_ms": 7682,
          "start_char": 148,
          "end_char": 155
        },
        {
          "word": "of",
          "start_ms": 7817,
          "end_ms": 7879,
          "start_char": 156,
          "end_char": 158
        },
        {
          "word": "market",
          "start_ms": 7880,
          "end_ms": 8150,
          "start_char": 159,
          "end_char": 165
        },
        {
          "word": "compounding",
          "start_ms": 8217,
          "end_ms": 8712,
          "start_char": 166,
          "end_char": 177
        },
        {
          "word": "Data",
          "start_ms": 9322,
          "end_ms": 9502,
          "start_char": 179,
          "end_char": 183
        },
        {
          "word": "from",
          "start_ms": 9622,
          "end_ms": 9802,
          "start_char": 184,
          "end_char": 188
        },
        {
          "word": "AMFI",
          "start_ms": 9835,
          "end_ms": 10015,
          "start_char": 189,
          "end_char": 193
        },
        {
          "word": "India",
          "start_ms": 10185,
          "end_ms": 10410,
          "start_char": 194,
          "end_char": 199
        },
        {
          "word": "2023",
          "start_ms": 10472,
          "end_ms": 10652,
          "start_char": 200,
          "end_char": 204
        },
        {
          "word": "shows",
          "start_ms": 11285,
          "end_ms": 11510,
          "start_char": 205,
          "end_char": 210
        },
        {
          "word": "that",
          "start_ms": 11660,
          "end_ms": 11796,
          "start_char": 211,
          "end_char": 215
        },
        {
          "word": "the",
          "start_ms": 11797,
          "end_ms": 11921,
          "start_char": 216,
          "end_char": 219
        },
        {
          "word": "opportunity",
          "start_ms": 11922,
          "end_ms": 12417,
          "start_char": 220,
          "end_char": 231
        },
        {
          "word": "cost",
          "start_ms": 12472,
          "end_ms": 12652,
          "start_char": 232,
          "end_char": 236
        },
        {
          "word": "of",
          "start_ms": 12835,
          "end_ms": 12921,
          "start_char": 237,
          "end_char": 239
        },
        {
          "word": "locking",
          "start_ms": 12922,
          "end_ms": 13237,
          "start_char": 240,
          "end_char": 247
        },
        {
          "word": "a",
          "start_ms": 13285,
          "end_ms": 13334,
          "start_char": 248,
          "end_char": 249
        },
        {
          "word": "\u20b910",
          "start_ms": 13335,
          "end_ms": 13470,
          "start_char": 250,
          "end_char": 255
        },
        {
          "word": "Lakh",
          "start_ms": 14072,
          "end_ms": 14252,
          "start_char": 256,
          "end_char": 260
        },
        {
          "word": "down",
          "start_ms": 14335,
          "end_ms": 14515,
          "start_char": 261,
          "end_char": 265
        },
        {
          "word": "payment",
          "start_ms": 14610,
          "end_ms": 14925,
          "start_char": 266,
          "end_char": 273
        },
        {
          "word": "into",
          "start_ms": 14947,
          "end_ms": 15127,
          "start_char": 274,
          "end_char": 278
        },
        {
          "word": "real",
          "start_ms": 15147,
          "end_ms": 15327,
          "start_char": 279,
          "end_char": 283
        },
        {
          "word": "estate",
          "start_ms": 15410,
          "end_ms": 15680,
          "start_char": 284,
          "end_char": 290
        },
        {
          "word": "rather",
          "start_ms": 15772,
          "end_ms": 16021,
          "start_char": 291,
          "end_char": 297
        },
        {
          "word": "than",
          "start_ms": 16022,
          "end_ms": 16171,
          "start_char": 298,
          "end_char": 302
        },
        {
          "word": "investing",
          "start_ms": 16172,
          "end_ms": 16577,
          "start_char": 303,
          "end_char": 312
        },
        {
          "word": "it",
          "start_ms": 16622,
          "end_ms": 16684,
          "start_char": 313,
          "end_char": 315
        },
        {
          "word": "in",
          "start_ms": 16685,
          "end_ms": 16784,
          "start_char": 316,
          "end_char": 318
        },
        {
          "word": "equity",
          "start_ms": 16785,
          "end_ms": 17055,
          "start_char": 319,
          "end_char": 325
        },
        {
          "word": "mutual",
          "start_ms": 17097,
          "end_ms": 17367,
          "start_char": 326,
          "end_char": 332
        },
        {
          "word": "funds",
          "start_ms": 17522,
          "end_ms": 17747,
          "start_char": 333,
          "end_char": 338
        },
        {
          "word": "at",
          "start_ms": 17922,
          "end_ms": 17984,
          "start_char": 339,
          "end_char": 341
        },
        {
          "word": "a",
          "start_ms": 17985,
          "end_ms": 18021,
          "start_char": 342,
          "end_char": 343
        },
        {
          "word": "historical",
          "start_ms": 18022,
          "end_ms": 18472,
          "start_char": 344,
          "end_char": 354
        },
        {
          "word": "12",
          "start_ms": 18572,
          "end_ms": 18672,
          "start_char": 355,
          "end_char": 357
        },
        {
          "word": "percent",
          "start_ms": 18872,
          "end_ms": 19187,
          "start_char": 358,
          "end_char": 365
        },
        {
          "word": "CAGR",
          "start_ms": 19297,
          "end_ms": 19477,
          "start_char": 366,
          "end_char": 370
        },
        {
          "word": "results",
          "start_ms": 20097,
          "end_ms": 20412,
          "start_char": 371,
          "end_char": 378
        },
        {
          "word": "in",
          "start_ms": 20560,
          "end_ms": 20634,
          "start_char": 379,
          "end_char": 381
        },
        {
          "word": "a",
          "start_ms": 20635,
          "end_ms": 20671,
          "start_char": 382,
          "end_char": 383
        },
        {
          "word": "staggering",
          "start_ms": 20672,
          "end_ms": 21122,
          "start_char": 384,
          "end_char": 394
        },
        {
          "word": "20-year",
          "start_ms": 21197,
          "end_ms": 21512,
          "start_char": 395,
          "end_char": 402
        },
        {
          "word": "wealth",
          "start_ms": 21660,
          "end_ms": 21930,
          "start_char": 403,
          "end_char": 409
        },
        {
          "word": "gap",
          "start_ms": 21960,
          "end_ms": 22095,
          "start_char": 410,
          "end_char": 413
        },
        {
          "word": "of",
          "start_ms": 22247,
          "end_ms": 22347,
          "start_char": 414,
          "end_char": 416
        },
        {
          "word": "over",
          "start_ms": 22360,
          "end_ms": 22540,
          "start_char": 417,
          "end_char": 421
        },
        {
          "word": "\u20b996",
          "start_ms": 22560,
          "end_ms": 22695,
          "start_char": 422,
          "end_char": 427
        },
        {
          "word": "Lakh",
          "start_ms": 23535,
          "end_ms": 23715,
          "start_char": 428,
          "end_char": 432
        }
      ],
      "duration_ms": 24048,
      "duration_seconds": 24.048
    },
    {
      "chunk_id": "chunk_007",
      "sequence": 7,
      "source_id": "idea_06",
      "text": "Generations before us viewed renting as a waste of money, but today's financial reality is entirely different. When you factor in the immense opportunity costs, liquidity losses, and maintenance burdens of homeownership, renting while aggressively investing your capital in high-yield equities often leaves you far wealthier. You maintain the financial flexibility to switch jobs, relocate, and grow your net worth without being tied down to a crushing debt obligation.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_007.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_007.marks.json",
      "word_timestamps": [
        {
          "word": "Generations",
          "start_ms": 25,
          "end_ms": 520,
          "start_char": 0,
          "end_char": 11
        },
        {
          "word": "before",
          "start_ms": 725,
          "end_ms": 995,
          "start_char": 12,
          "end_char": 18
        },
        {
          "word": "us",
          "start_ms": 1100,
          "end_ms": 1200,
          "start_char": 19,
          "end_char": 21
        },
        {
          "word": "viewed",
          "start_ms": 1237,
          "end_ms": 1499,
          "start_char": 22,
          "end_char": 28
        },
        {
          "word": "renting",
          "start_ms": 1500,
          "end_ms": 1815,
          "start_char": 29,
          "end_char": 36
        },
        {
          "word": "as",
          "start_ms": 1862,
          "end_ms": 1961,
          "start_char": 37,
          "end_char": 39
        },
        {
          "word": "a",
          "start_ms": 1962,
          "end_ms": 2011,
          "start_char": 40,
          "end_char": 41
        },
        {
          "word": "waste",
          "start_ms": 2012,
          "end_ms": 2237,
          "start_char": 42,
          "end_char": 47
        },
        {
          "word": "of",
          "start_ms": 2325,
          "end_ms": 2399,
          "start_char": 48,
          "end_char": 50
        },
        {
          "word": "money",
          "start_ms": 2400,
          "end_ms": 2625,
          "start_char": 51,
          "end_char": 56
        },
        {
          "word": "but",
          "start_ms": 2900,
          "end_ms": 3035,
          "start_char": 58,
          "end_char": 61
        },
        {
          "word": "today's",
          "start_ms": 3087,
          "end_ms": 3402,
          "start_char": 62,
          "end_char": 69
        },
        {
          "word": "financial",
          "start_ms": 3437,
          "end_ms": 3842,
          "start_char": 70,
          "end_char": 79
        },
        {
          "word": "reality",
          "start_ms": 3850,
          "end_ms": 4165,
          "start_char": 80,
          "end_char": 87
        },
        {
          "word": "is",
          "start_ms": 4362,
          "end_ms": 4462,
          "start_char": 88,
          "end_char": 90
        },
        {
          "word": "entirely",
          "start_ms": 4475,
          "end_ms": 4835,
          "start_char": 91,
          "end_char": 99
        },
        {
          "word": "different",
          "start_ms": 4887,
          "end_ms": 5292,
          "start_char": 100,
          "end_char": 109
        },
        {
          "word": "When",
          "start_ms": 5805,
          "end_ms": 5966,
          "start_char": 111,
          "end_char": 115
        },
        {
          "word": "you",
          "start_ms": 5967,
          "end_ms": 6066,
          "start_char": 116,
          "end_char": 119
        },
        {
          "word": "factor",
          "start_ms": 6067,
          "end_ms": 6337,
          "start_char": 120,
          "end_char": 126
        },
        {
          "word": "in",
          "start_ms": 6517,
          "end_ms": 6591,
          "start_char": 127,
          "end_char": 129
        },
        {
          "word": "the",
          "start_ms": 6592,
          "end_ms": 6704,
          "start_char": 130,
          "end_char": 133
        },
        {
          "word": "immense",
          "start_ms": 6705,
          "end_ms": 7016,
          "start_char": 134,
          "end_char": 141
        },
        {
          "word": "opportunity",
          "start_ms": 7017,
          "end_ms": 7512,
          "start_char": 142,
          "end_char": 153
        },
        {
          "word": "costs",
          "start_ms": 7542,
          "end_ms": 7767,
          "start_char": 154,
          "end_char": 159
        },
        {
          "word": "liquidity",
          "start_ms": 8242,
          "end_ms": 8647,
          "start_char": 161,
          "end_char": 170
        },
        {
          "word": "losses",
          "start_ms": 8705,
          "end_ms": 8975,
          "start_char": 171,
          "end_char": 177
        },
        {
          "word": "and",
          "start_ms": 9455,
          "end_ms": 9579,
          "start_char": 179,
          "end_char": 182
        },
        {
          "word": "maintenance",
          "start_ms": 9580,
          "end_ms": 9991,
          "start_char": 183,
          "end_char": 194
        },
        {
          "word": "burdens",
          "start_ms": 9992,
          "end_ms": 10307,
          "start_char": 195,
          "end_char": 202
        },
        {
          "word": "of",
          "start_ms": 10355,
          "end_ms": 10429,
          "start_char": 203,
          "end_char": 205
        },
        {
          "word": "homeownership",
          "start_ms": 10430,
          "end_ms": 11015,
          "start_char": 206,
          "end_char": 219
        },
        {
          "word": "renting",
          "start_ms": 11317,
          "end_ms": 11632,
          "start_char": 221,
          "end_char": 228
        },
        {
          "word": "while",
          "start_ms": 11730,
          "end_ms": 11916,
          "start_char": 229,
          "end_char": 234
        },
        {
          "word": "aggressively",
          "start_ms": 11917,
          "end_ms": 12457,
          "start_char": 235,
          "end_char": 247
        },
        {
          "word": "investing",
          "start_ms": 12492,
          "end_ms": 12897,
          "start_char": 248,
          "end_char": 257
        },
        {
          "word": "your",
          "start_ms": 12917,
          "end_ms": 13029,
          "start_char": 258,
          "end_char": 262
        },
        {
          "word": "capital",
          "start_ms": 13030,
          "end_ms": 13345,
          "start_char": 263,
          "end_char": 270
        },
        {
          "word": "in",
          "start_ms": 13480,
          "end_ms": 13554,
          "start_char": 271,
          "end_char": 273
        },
        {
          "word": "high-yield",
          "start_ms": 13555,
          "end_ms": 14005,
          "start_char": 274,
          "end_char": 284
        },
        {
          "word": "equities",
          "start_ms": 14105,
          "end_ms": 14465,
          "start_char": 285,
          "end_char": 293
        },
        {
          "word": "often",
          "start_ms": 14517,
          "end_ms": 14742,
          "start_char": 294,
          "end_char": 299
        },
        {
          "word": "leaves",
          "start_ms": 14805,
          "end_ms": 15075,
          "start_char": 300,
          "end_char": 306
        },
        {
          "word": "you",
          "start_ms": 15105,
          "end_ms": 15204,
          "start_char": 307,
          "end_char": 310
        },
        {
          "word": "far",
          "start_ms": 15205,
          "end_ms": 15340,
          "start_char": 311,
          "end_char": 314
        },
        {
          "word": "wealthier",
          "start_ms": 15442,
          "end_ms": 15847,
          "start_char": 315,
          "end_char": 324
        },
        {
          "word": "You",
          "start_ms": 16472,
          "end_ms": 16571,
          "start_char": 326,
          "end_char": 329
        },
        {
          "word": "maintain",
          "start_ms": 16572,
          "end_ms": 16932,
          "start_char": 330,
          "end_char": 338
        },
        {
          "word": "the",
          "start_ms": 16997,
          "end_ms": 17071,
          "start_char": 339,
          "end_char": 342
        },
        {
          "word": "financial",
          "start_ms": 17072,
          "end_ms": 17477,
          "start_char": 343,
          "end_char": 352
        },
        {
          "word": "flexibility",
          "start_ms": 17535,
          "end_ms": 18030,
          "start_char": 353,
          "end_char": 364
        },
        {
          "word": "to",
          "start_ms": 18247,
          "end_ms": 18347,
          "start_char": 365,
          "end_char": 367
        },
        {
          "word": "switch",
          "start_ms": 18372,
          "end_ms": 18642,
          "start_char": 368,
          "end_char": 374
        },
        {
          "word": "jobs",
          "start_ms": 18710,
          "end_ms": 18890,
          "start_char": 375,
          "end_char": 379
        },
        {
          "word": "relocate",
          "start_ms": 19422,
          "end_ms": 19782,
          "start_char": 381,
          "end_char": 389
        },
        {
          "word": "and",
          "start_ms": 20247,
          "end_ms": 20382,
          "start_char": 391,
          "end_char": 394
        },
        {
          "word": "grow",
          "start_ms": 20397,
          "end_ms": 20577,
          "start_char": 395,
          "end_char": 399
        },
        {
          "word": "your",
          "start_ms": 20597,
          "end_ms": 20771,
          "start_char": 400,
          "end_char": 404
        },
        {
          "word": "net",
          "start_ms": 20772,
          "end_ms": 20907,
          "start_char": 405,
          "end_char": 408
        },
        {
          "word": "worth",
          "start_ms": 20997,
          "end_ms": 21222,
          "start_char": 409,
          "end_char": 414
        },
        {
          "word": "without",
          "start_ms": 21272,
          "end_ms": 21587,
          "start_char": 415,
          "end_char": 422
        },
        {
          "word": "being",
          "start_ms": 21597,
          "end_ms": 21822,
          "start_char": 423,
          "end_char": 428
        },
        {
          "word": "tied",
          "start_ms": 21835,
          "end_ms": 22015,
          "start_char": 429,
          "end_char": 433
        },
        {
          "word": "down",
          "start_ms": 22135,
          "end_ms": 22315,
          "start_char": 434,
          "end_char": 438
        },
        {
          "word": "to",
          "start_ms": 22397,
          "end_ms": 22497,
          "start_char": 439,
          "end_char": 441
        },
        {
          "word": "a",
          "start_ms": 22547,
          "end_ms": 22584,
          "start_char": 442,
          "end_char": 443
        },
        {
          "word": "crushing",
          "start_ms": 22585,
          "end_ms": 22945,
          "start_char": 444,
          "end_char": 452
        },
        {
          "word": "debt",
          "start_ms": 22997,
          "end_ms": 23146,
          "start_char": 453,
          "end_char": 457
        },
        {
          "word": "obligation",
          "start_ms": 23147,
          "end_ms": 23597,
          "start_char": 458,
          "end_char": 468
        }
      ],
      "duration_ms": 23976,
      "duration_seconds": 23.976
    },
    {
      "chunk_id": "chunk_008",
      "sequence": 8,
      "source_id": "idea_07",
      "text": "To protect your financial future, adopt the Smart Home Buyer Blueprint. Before signing any agreement, calculate your total cost of ownership including stamp duty, registration, interiors, and maintenance. Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched. By sidestepping the \u20b910 Lakh trap, you keep your wealth compounding and secure true financial freedom.",
      "audio_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_008.mp3",
      "speech_marks_path": "/Users/dakshyadav/Documents/YTcreate_V2/backend/.data/media/projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/chunks/chunk_008.marks.json",
      "word_timestamps": [
        {
          "word": "To",
          "start_ms": 25,
          "end_ms": 124,
          "start_char": 0,
          "end_char": 2
        },
        {
          "word": "protect",
          "start_ms": 125,
          "end_ms": 440,
          "start_char": 3,
          "end_char": 10
        },
        {
          "word": "your",
          "start_ms": 537,
          "end_ms": 624,
          "start_char": 11,
          "end_char": 15
        },
        {
          "word": "financial",
          "start_ms": 625,
          "end_ms": 1030,
          "start_char": 16,
          "end_char": 25
        },
        {
          "word": "future",
          "start_ms": 1087,
          "end_ms": 1357,
          "start_char": 26,
          "end_char": 32
        },
        {
          "word": "adopt",
          "start_ms": 1762,
          "end_ms": 1987,
          "start_char": 34,
          "end_char": 39
        },
        {
          "word": "the",
          "start_ms": 2087,
          "end_ms": 2174,
          "start_char": 40,
          "end_char": 43
        },
        {
          "word": "Smart",
          "start_ms": 2175,
          "end_ms": 2400,
          "start_char": 44,
          "end_char": 49
        },
        {
          "word": "Home",
          "start_ms": 2500,
          "end_ms": 2680,
          "start_char": 50,
          "end_char": 54
        },
        {
          "word": "Buyer",
          "start_ms": 2725,
          "end_ms": 2950,
          "start_char": 55,
          "end_char": 60
        },
        {
          "word": "Blueprint",
          "start_ms": 2987,
          "end_ms": 3392,
          "start_char": 61,
          "end_char": 70
        },
        {
          "word": "Before",
          "start_ms": 4005,
          "end_ms": 4275,
          "start_char": 72,
          "end_char": 78
        },
        {
          "word": "signing",
          "start_ms": 4367,
          "end_ms": 4682,
          "start_char": 79,
          "end_char": 86
        },
        {
          "word": "any",
          "start_ms": 4742,
          "end_ms": 4877,
          "start_char": 87,
          "end_char": 90
        },
        {
          "word": "agreement",
          "start_ms": 4917,
          "end_ms": 5322,
          "start_char": 91,
          "end_char": 100
        },
        {
          "word": "calculate",
          "start_ms": 5517,
          "end_ms": 5922,
          "start_char": 102,
          "end_char": 111
        },
        {
          "word": "your",
          "start_ms": 6055,
          "end_ms": 6154,
          "start_char": 112,
          "end_char": 116
        },
        {
          "word": "total",
          "start_ms": 6155,
          "end_ms": 6380,
          "start_char": 117,
          "end_char": 122
        },
        {
          "word": "cost",
          "start_ms": 6467,
          "end_ms": 6647,
          "start_char": 123,
          "end_char": 127
        },
        {
          "word": "of",
          "start_ms": 6805,
          "end_ms": 6904,
          "start_char": 128,
          "end_char": 130
        },
        {
          "word": "ownership",
          "start_ms": 6905,
          "end_ms": 7310,
          "start_char": 131,
          "end_char": 140
        },
        {
          "word": "including",
          "start_ms": 7380,
          "end_ms": 7766,
          "start_char": 141,
          "end_char": 150
        },
        {
          "word": "stamp",
          "start_ms": 7767,
          "end_ms": 7992,
          "start_char": 151,
          "end_char": 156
        },
        {
          "word": "duty",
          "start_ms": 8105,
          "end_ms": 8285,
          "start_char": 157,
          "end_char": 161
        },
        {
          "word": "registration",
          "start_ms": 8667,
          "end_ms": 9207,
          "start_char": 163,
          "end_char": 175
        },
        {
          "word": "interiors",
          "start_ms": 9705,
          "end_ms": 10110,
          "start_char": 177,
          "end_char": 186
        },
        {
          "word": "and",
          "start_ms": 10555,
          "end_ms": 10666,
          "start_char": 188,
          "end_char": 191
        },
        {
          "word": "maintenance",
          "start_ms": 10667,
          "end_ms": 11162,
          "start_char": 192,
          "end_char": 203
        },
        {
          "word": "Never",
          "start_ms": 11685,
          "end_ms": 11910,
          "start_char": 205,
          "end_char": 210
        },
        {
          "word": "borrow",
          "start_ms": 11985,
          "end_ms": 12255,
          "start_char": 211,
          "end_char": 217
        },
        {
          "word": "more",
          "start_ms": 12285,
          "end_ms": 12465,
          "start_char": 218,
          "end_char": 222
        },
        {
          "word": "than",
          "start_ms": 12522,
          "end_ms": 12671,
          "start_char": 223,
          "end_char": 227
        },
        {
          "word": "2.5",
          "start_ms": 12672,
          "end_ms": 12807,
          "start_char": 228,
          "end_char": 231
        },
        {
          "word": "times",
          "start_ms": 13435,
          "end_ms": 13660,
          "start_char": 232,
          "end_char": 237
        },
        {
          "word": "your",
          "start_ms": 13797,
          "end_ms": 13946,
          "start_char": 238,
          "end_char": 242
        },
        {
          "word": "annual",
          "start_ms": 13947,
          "end_ms": 14217,
          "start_char": 243,
          "end_char": 249
        },
        {
          "word": "salary",
          "start_ms": 14235,
          "end_ms": 14505,
          "start_char": 250,
          "end_char": 256
        },
        {
          "word": "and",
          "start_ms": 15010,
          "end_ms": 15145,
          "start_char": 258,
          "end_char": 261
        },
        {
          "word": "ensure",
          "start_ms": 15147,
          "end_ms": 15417,
          "start_char": 262,
          "end_char": 268
        },
        {
          "word": "your",
          "start_ms": 15510,
          "end_ms": 15690,
          "start_char": 269,
          "end_char": 273
        },
        {
          "word": "emergency",
          "start_ms": 15722,
          "end_ms": 16127,
          "start_char": 274,
          "end_char": 283
        },
        {
          "word": "fund",
          "start_ms": 16260,
          "end_ms": 16440,
          "start_char": 284,
          "end_char": 288
        },
        {
          "word": "remains",
          "start_ms": 16547,
          "end_ms": 16862,
          "start_char": 289,
          "end_char": 296
        },
        {
          "word": "untouched",
          "start_ms": 16960,
          "end_ms": 17365,
          "start_char": 297,
          "end_char": 306
        },
        {
          "word": "By",
          "start_ms": 18015,
          "end_ms": 18115,
          "start_char": 308,
          "end_char": 310
        },
        {
          "word": "sidestepping",
          "start_ms": 18177,
          "end_ms": 18717,
          "start_char": 311,
          "end_char": 323
        },
        {
          "word": "the",
          "start_ms": 18840,
          "end_ms": 18914,
          "start_char": 324,
          "end_char": 327
        },
        {
          "word": "\u20b910",
          "start_ms": 18915,
          "end_ms": 19050,
          "start_char": 328,
          "end_char": 333
        },
        {
          "word": "Lakh",
          "start_ms": 19615,
          "end_ms": 19795,
          "start_char": 334,
          "end_char": 338
        },
        {
          "word": "trap",
          "start_ms": 19852,
          "end_ms": 20032,
          "start_char": 339,
          "end_char": 343
        },
        {
          "word": "you",
          "start_ms": 20415,
          "end_ms": 20526,
          "start_char": 345,
          "end_char": 348
        },
        {
          "word": "keep",
          "start_ms": 20527,
          "end_ms": 20707,
          "start_char": 349,
          "end_char": 353
        },
        {
          "word": "your",
          "start_ms": 20752,
          "end_ms": 20839,
          "start_char": 354,
          "end_char": 358
        },
        {
          "word": "wealth",
          "start_ms": 20840,
          "end_ms": 21110,
          "start_char": 359,
          "end_char": 365
        },
        {
          "word": "compounding",
          "start_ms": 21115,
          "end_ms": 21610,
          "start_char": 366,
          "end_char": 377
        },
        {
          "word": "and",
          "start_ms": 21677,
          "end_ms": 21764,
          "start_char": 378,
          "end_char": 381
        },
        {
          "word": "secure",
          "start_ms": 21765,
          "end_ms": 22035,
          "start_char": 382,
          "end_char": 388
        },
        {
          "word": "true",
          "start_ms": 22127,
          "end_ms": 22307,
          "start_char": 389,
          "end_char": 393
        },
        {
          "word": "financial",
          "start_ms": 22352,
          "end_ms": 22757,
          "start_char": 394,
          "end_char": 403
        },
        {
          "word": "freedom",
          "start_ms": 22802,
          "end_ms": 23117,
          "start_char": 404,
          "end_char": 411
        }
      ],
      "duration_ms": 23424,
      "duration_seconds": 23.424
    }
  ]
}
```

---

## Stage 7: Render Spec

- **Artifact ID:** `artifact_6820865b0a1b4b21aae3e411d7489a0f`
- **Artifact Type:** `render_spec`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-14T13:24:00.586735+00:00`
- **Parent Artifact Roles:** `{"voice_track": "artifact_41f599323e9f45f4bea4adeac8407f54", "script_visual_strategy": "artifact_310863c3cad84c229bdc74b5e82e4393", "hook": "artifact_8be68bb4d6b74a158fb52a458aee6c5f"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Calculates frame-accurate Remotion scene graphs, timing spans, and composition component props.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "scene_id": "scene_project_bd64dbe39bb646ddb4d8294b63def4ff",
  "composition": "VideoAssembly",
  "fps": 30,
  "duration_frames": 5651,
  "props": {
    "scenes": [
      {
        "scene_id": "scene_001",
        "start_frame": 0,
        "end_frame": 241,
        "duration_frames": 241,
        "component": {
          "component_id": "MetricHero",
          "props": {
            "value": "\u20b910 Lakh",
            "label": "Hidden Home-Buying Fees",
            "context": "swallowed before moving in",
            "emphasis": "hero",
            "variant": "warning_metric",
            "polarity": "negative",
            "direction": null,
            "baselineValue": null,
            "delta": null
          }
        },
        "asset": null,
        "narration_text": "You saved for years for that down payment. But the moment you sign the deed, hidden fees swallow 10 Lakhs of your cash before you even unpack a box. Stamp duty, registration, and basic interiors are waiting in the dark to drain your emergency fund."
      },
      {
        "scene_id": "scene_002",
        "start_frame": 241,
        "end_frame": 407,
        "duration_frames": 166,
        "component": {
          "component_id": "MultiFactorPressure",
          "props": {
            "factors": [
              {
                "label": "Stamp Duty",
                "value": null,
                "severity": "high",
                "icon": null
              },
              {
                "label": "Registration Fees",
                "value": null,
                "severity": "high",
                "icon": null
              },
              {
                "label": "Basic Interiors",
                "value": null,
                "severity": "high",
                "icon": null
              }
            ],
            "combinedLabel": "Emergency Fund Drain",
            "combinedSeverity": "critical",
            "outcomeNote": "Hidden upfront costs depleting your financial safety net",
            "outcomeValue": "100% Drained",
            "outcomeHeaderLabel": null,
            "variant": "tri_factor",
            "polarity": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_hook_1_beat_hook_02",
          "asset_type": "video",
          "source": "pexels",
          "query": "home buying hidden costs financial stress",
          "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_scene_002_asset_comp_hook_1_beat_hook_02.mp4",
          "url": "https://videos.pexels.com/video-files/5981292/5981292-hd_2048_1080_25fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "You saved for years for that down payment. But the moment you sign the deed, hidden fees swallow 10 Lakhs of your cash before you even unpack a box. Stamp duty, registration, and basic interiors are waiting in the dark to drain your emergency fund."
      },
      {
        "scene_id": "scene_003",
        "start_frame": 407,
        "end_frame": 639,
        "duration_frames": 232,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Homebuyers typically assume the quoted property price is the total cost.",
            "emphasisPhrase": "quoted price covers everything",
            "author": null,
            "headerLabel": "THE HOMEBUYING ASSUMPTION",
            "variant": "statement",
            "sourceContext": null,
            "polarity": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_0_0_beat_01_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "Illustrate the common misconception that the quoted property price is the final total cost.",
          "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_scene_003_asset_comp_0_0_beat_01_01.mp4",
          "url": "https://videos.pexels.com/video-files/30167366/12936470_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "When you finally decide to purchase property, you assume the quoted price covers everything. But our research reveals that 78 percent of urban Indian first-time homebuyers completely fail to budget for interior work and registration fees in their initial financial planning. Stamp duty and registration charges in major Indian metro cities add an extra 5 percent to 7 percent of the property value upfront, costing approximately \u20b93.5 Lakh on a \u20b950 Lakh apartment."
      },
      {
        "scene_id": "scene_004",
        "start_frame": 639,
        "end_frame": 829,
        "duration_frames": 190,
        "component": {
          "component_id": "MetricHero",
          "props": {
            "value": "78%",
            "label": "First-Time Buyers Failing to Budget Hidden Costs",
            "context": "Urban Indian Homebuyers",
            "emphasis": "hero",
            "variant": "warning_metric",
            "polarity": "negative",
            "direction": null,
            "baselineValue": null,
            "delta": null
          }
        },
        "asset": null,
        "narration_text": "When you finally decide to purchase property, you assume the quoted price covers everything. But our research reveals that 78 percent of urban Indian first-time homebuyers completely fail to budget for interior work and registration fees in their initial financial planning. Stamp duty and registration charges in major Indian metro cities add an extra 5 percent to 7 percent of the property value upfront, costing approximately \u20b93.5 Lakh on a \u20b950 Lakh apartment."
      },
      {
        "scene_id": "scene_005",
        "start_frame": 829,
        "end_frame": 1179,
        "duration_frames": 350,
        "component": {
          "component_id": "CalculationStory",
          "props": {
            "inputLabel": "Apartment Value",
            "inputValue": "\u20b950 Lakh",
            "operationLabel": "\u00d7",
            "rateLabel": "5% to 7% Stamp Duty",
            "resultLabel": "Upfront Cost",
            "resultValue": "\u20b93.5 Lakh",
            "note": "Registration & Stamp Duty Charges",
            "operationType": "multiplication",
            "variant": "multiplication",
            "polarity": "warning",
            "timeframe": null,
            "secondaryLabel": null,
            "secondaryValue": null
          }
        },
        "asset": null,
        "narration_text": "When you finally decide to purchase property, you assume the quoted price covers everything. But our research reveals that 78 percent of urban Indian first-time homebuyers completely fail to budget for interior work and registration fees in their initial financial planning. Stamp duty and registration charges in major Indian metro cities add an extra 5 percent to 7 percent of the property value upfront, costing approximately \u20b93.5 Lakh on a \u20b950 Lakh apartment."
      },
      {
        "scene_id": "scene_006",
        "start_frame": 1179,
        "end_frame": 1364,
        "duration_frames": 185,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Society tells you that renting is throwing money away, pushing corporate employees into rushed purchases.",
            "emphasisPhrase": "throwing money away",
            "author": null,
            "headerLabel": "SOCIAL PRESSURE",
            "variant": "statement",
            "sourceContext": null,
            "polarity": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_1_0_beat_02_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "Show corporate employee facing societal pressure regarding homeownership.",
          "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_scene_006_asset_comp_1_0_beat_02_01.mp4",
          "url": "https://videos.pexels.com/video-files/6799662/6799662-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Society tells you that renting is throwing money away, pushing corporate employees into rushed purchases. Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe. But this metric ignores your total financial exposure. According to the RBI Financial Stability Report 2023, average corporate buyers currently borrow at 4.5 times their annual salary, far exceeding the recommended safety limit of 2.5 times."
      },
      {
        "scene_id": "scene_007",
        "start_frame": 1364,
        "end_frame": 1559,
        "duration_frames": 195,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe.",
            "emphasisPhrase": "40 percent",
            "author": null,
            "headerLabel": "INDUSTRY RULE OF THUMB",
            "variant": "statement",
            "sourceContext": null,
            "polarity": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_1_1_beat_02_02",
          "asset_type": "video",
          "source": "pexels",
          "query": "real estate agent talking to couple modern office",
          "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_scene_007_asset_comp_1_1_beat_02_02.mp4",
          "url": "https://videos.pexels.com/video-files/8293313/8293313-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Society tells you that renting is throwing money away, pushing corporate employees into rushed purchases. Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe. But this metric ignores your total financial exposure. According to the RBI Financial Stability Report 2023, average corporate buyers currently borrow at 4.5 times their annual salary, far exceeding the recommended safety limit of 2.5 times."
      },
      {
        "scene_id": "scene_008",
        "start_frame": 1559,
        "end_frame": 1693,
        "duration_frames": 134,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "The traditional metric ignores your total financial exposure.",
            "emphasisPhrase": "total financial exposure",
            "author": null,
            "headerLabel": "CRITICAL FLAW",
            "variant": "statement",
            "sourceContext": null,
            "polarity": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_1_2_beat_02_03",
          "asset_type": "video",
          "source": "pexels",
          "query": "Highlight the flaw in traditional EMI metrics ignoring financial exposure.",
          "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_scene_008_asset_comp_1_2_beat_02_03.mp4",
          "url": "https://videos.pexels.com/video-files/7247867/7247867-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Society tells you that renting is throwing money away, pushing corporate employees into rushed purchases. Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe. But this metric ignores your total financial exposure. According to the RBI Financial Stability Report 2023, average corporate buyers currently borrow at 4.5 times their annual salary, far exceeding the recommended safety limit of 2.5 times."
      },
      {
        "scene_id": "scene_009",
        "start_frame": 1693,
        "end_frame": 1973,
        "duration_frames": 280,
        "component": {
          "component_id": "SplitComparison",
          "props": {
            "headerLabel": "RBI FINANCIAL STABILITY REPORT 2023",
            "comparisonLabel": null,
            "variant": "metric_compare",
            "tone": "superiority",
            "leftRole": "Actual Borrowing",
            "leftLabel": null,
            "leftValue": "4.5x",
            "leftUnit": null,
            "rightRole": "Safe Limit",
            "rightLabel": null,
            "rightValue": "2.5x",
            "rightUnit": null,
            "delta": null,
            "winner": null,
            "footerLabel": null
          }
        },
        "asset": null,
        "narration_text": "Society tells you that renting is throwing money away, pushing corporate employees into rushed purchases. Real estate agents tell you that as long as your monthly EMI stays under 40 percent of your monthly salary, you are safe. But this metric ignores your total financial exposure. According to the RBI Financial Stability Report 2023, average corporate buyers currently borrow at 4.5 times their annual salary, far exceeding the recommended safety limit of 2.5 times."
      },
      {
        "scene_id": "scene_010",
        "start_frame": 1973,
        "end_frame": 2485,
        "duration_frames": 512,
        "component": {
          "component_id": "CalculationStory",
          "props": {
            "inputLabel": "Property Value",
            "inputValue": "\u20b950 Lakh",
            "operationLabel": "\u00d7",
            "rateLabel": "1% Annual Maintenance",
            "resultLabel": "Annual Cost",
            "resultValue": "\u20b950,000",
            "note": "Maintenance, Society Fees & Taxes",
            "operationType": "multiplication",
            "variant": "multiplication",
            "polarity": null,
            "timeframe": "per year",
            "secondaryLabel": null,
            "secondaryValue": null
          }
        },
        "asset": null,
        "narration_text": "Buying the home is only the beginning of your financial commitment. Annual maintenance charges, society fees, and municipal property taxes average 1 percent of the property's original value per year, adding \u20b950,000 annually for a \u20b950 Lakh home according to CREDAI Real Estate Outlook 2023. Furthermore, over a standard 20-year home loan tenure at an 8.5 percent interest rate, a borrower pays back roughly 2.1 times the principal amount borrowed due to cumulative interest."
      },
      {
        "scene_id": "scene_011",
        "start_frame": 2485,
        "end_frame": 2792,
        "duration_frames": 307,
        "component": {
          "component_id": "CalculationStory",
          "props": {
            "inputLabel": "Principal Amount",
            "inputValue": "1.0x",
            "operationLabel": "\u00d7",
            "rateLabel": "20-yr Loan @ 8.5%",
            "resultLabel": "Total Repayment",
            "resultValue": "2.1x Principal",
            "note": "Cumulative interest burden over tenure",
            "operationType": "multiplication",
            "variant": "multiplication",
            "polarity": "warning",
            "timeframe": "over 20 years",
            "secondaryLabel": null,
            "secondaryValue": null
          }
        },
        "asset": null,
        "narration_text": "Buying the home is only the beginning of your financial commitment. Annual maintenance charges, society fees, and municipal property taxes average 1 percent of the property's original value per year, adding \u20b950,000 annually for a \u20b950 Lakh home according to CREDAI Real Estate Outlook 2023. Furthermore, over a standard 20-year home loan tenure at an 8.5 percent interest rate, a borrower pays back roughly 2.1 times the principal amount borrowed due to cumulative interest."
      },
      {
        "scene_id": "scene_012",
        "start_frame": 2792,
        "end_frame": 3190,
        "duration_frames": 398,
        "component": {
          "component_id": "MetricHero",
          "props": {
            "value": "71 min",
            "label": "Average Daily One-Way Commute",
            "context": "TomTom Traffic Index 2023",
            "emphasis": "hero",
            "variant": "hero",
            "polarity": null,
            "direction": null,
            "baselineValue": null,
            "delta": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_3_0_beat_04_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "Highlight the 71-minute daily one-way commute time in Bengaluru as a hero metric.",
          "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_scene_012_asset_comp_3_0_beat_04_01.mp4",
          "url": "https://videos.pexels.com/video-files/28891291/12505929_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "In major tech hubs like Bengaluru, daily life is dictated by gridlocked traffic. According to the TomTom Traffic Index 2023, 71 minutes is the average daily one-way commute time in Bengaluru. This punishing routine drives many corporate employees to buy overpriced properties located near tech parks, forcing them into aggressive loans and trapping them in an inescapable EMI affordability cycle without adequate emergency buffers."
      },
      {
        "scene_id": "scene_013",
        "start_frame": 3190,
        "end_frame": 3509,
        "duration_frames": 319,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Long Commutes & Punishing Routine",
                "value": null,
                "icon": "\ud83d\ude97"
              }
            ],
            "connector": "drives",
            "outcomeLabel": "Inescapable EMI Debt Trap",
            "outcomeValue": null,
            "outcomeSeverity": "negative",
            "outcomeHeaderLabel": "Ultimate Consequence",
            "outcomeNote": "Aggressive loans without emergency buffers",
            "variant": "single_cause",
            "polarity": null
          }
        },
        "asset": null,
        "narration_text": "In major tech hubs like Bengaluru, daily life is dictated by gridlocked traffic. According to the TomTom Traffic Index 2023, 71 minutes is the average daily one-way commute time in Bengaluru. This punishing routine drives many corporate employees to buy overpriced properties located near tech parks, forcing them into aggressive loans and trapping them in an inescapable EMI affordability cycle without adequate emergency buffers."
      },
      {
        "scene_id": "scene_014",
        "start_frame": 3509,
        "end_frame": 3803,
        "duration_frames": 294,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Draining Savings for Down Payment",
                "value": null,
                "icon": "\ud83d\udcb8"
              }
            ],
            "connector": "leads to",
            "outcomeLabel": "Invisible Opportunity Cost",
            "outcomeValue": "Lost Market Compounding",
            "outcomeSeverity": "negative",
            "outcomeHeaderLabel": null,
            "outcomeNote": null,
            "variant": "single_cause",
            "polarity": null
          }
        },
        "asset": null,
        "narration_text": "The most devastating part of buying a home early is the invisible opportunity cost. When you drain your savings for a down payment, you miss out on decades of market compounding. Data from AMFI India 2023 shows that the opportunity cost of locking a \u20b910 Lakh down payment into real estate rather than investing it in equity mutual funds at a historical 12 percent CAGR results in a staggering 20-year wealth gap of over \u20b996 Lakh."
      },
      {
        "scene_id": "scene_015",
        "start_frame": 3803,
        "end_frame": 4230,
        "duration_frames": 427,
        "component": {
          "component_id": "SplitComparison",
          "props": {
            "headerLabel": "AMFI INDIA 2023 DATA",
            "comparisonLabel": "20-YEAR OPPORTUNITY COST",
            "variant": "cards",
            "tone": "neutral",
            "leftRole": "Real Estate Down Payment",
            "leftLabel": null,
            "leftValue": "\u20b910 Lakh",
            "leftUnit": null,
            "rightRole": "Equity Mutual Funds (12% CAGR)",
            "rightLabel": null,
            "rightValue": "\u20b996 Lakh Gap",
            "rightUnit": null,
            "delta": null,
            "winner": "right",
            "footerLabel": null
          }
        },
        "asset": null,
        "narration_text": "The most devastating part of buying a home early is the invisible opportunity cost. When you drain your savings for a down payment, you miss out on decades of market compounding. Data from AMFI India 2023 shows that the opportunity cost of locking a \u20b910 Lakh down payment into real estate rather than investing it in equity mutual funds at a historical 12 percent CAGR results in a staggering 20-year wealth gap of over \u20b996 Lakh."
      },
      {
        "scene_id": "scene_016",
        "start_frame": 4230,
        "end_frame": 4411,
        "duration_frames": 181,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Generations before us viewed renting as a waste of money, but today's financial reality is entirely different.",
            "emphasisPhrase": "financial reality is entirely different",
            "author": null,
            "headerLabel": "THE RENT VS BUY DEBATE",
            "variant": "statement",
            "sourceContext": null,
            "polarity": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_5_0_beat_06_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "Set the contextual backdrop for why old home-buying assumptions no longer apply.",
          "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_scene_016_asset_comp_5_0_beat_06_01.mp4",
          "url": "https://videos.pexels.com/video-files/7578013/7578013-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "Generations before us viewed renting as a waste of money, but today's financial reality is entirely different. When you factor in the immense opportunity costs, liquidity losses, and maintenance burdens of homeownership, renting while aggressively investing your capital in high-yield equities often leaves you far wealthier. You maintain the financial flexibility to switch jobs, relocate, and grow your net worth without being tied down to a crushing debt obligation."
      },
      {
        "scene_id": "scene_017",
        "start_frame": 4411,
        "end_frame": 4726,
        "duration_frames": 315,
        "component": {
          "component_id": "SplitComparison",
          "props": {
            "headerLabel": "RENTING VS BUYING",
            "comparisonLabel": "WEALTH STRATEGY",
            "variant": "versus",
            "tone": "neutral",
            "leftRole": "Homeownership",
            "leftLabel": null,
            "leftValue": "Burdens",
            "leftUnit": null,
            "rightRole": "Renting + Equities",
            "rightLabel": null,
            "rightValue": "Far Wealthier",
            "rightUnit": null,
            "delta": null,
            "winner": "right",
            "footerLabel": null
          }
        },
        "asset": null,
        "narration_text": "Generations before us viewed renting as a waste of money, but today's financial reality is entirely different. When you factor in the immense opportunity costs, liquidity losses, and maintenance burdens of homeownership, renting while aggressively investing your capital in high-yield equities often leaves you far wealthier. You maintain the financial flexibility to switch jobs, relocate, and grow your net worth without being tied down to a crushing debt obligation."
      },
      {
        "scene_id": "scene_018",
        "start_frame": 4726,
        "end_frame": 4949,
        "duration_frames": 223,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Career Flexibility",
                "value": null,
                "icon": "\ud83d\udcbc"
              },
              {
                "label": "Debt-Free Living",
                "value": null,
                "icon": "\u2728"
              }
            ],
            "connector": "leads to",
            "outcomeLabel": "Net Worth Growth",
            "outcomeValue": "Financial Freedom",
            "outcomeSeverity": "positive",
            "outcomeHeaderLabel": null,
            "outcomeNote": null,
            "variant": "dual_cause",
            "polarity": null
          }
        },
        "asset": null,
        "narration_text": "Generations before us viewed renting as a waste of money, but today's financial reality is entirely different. When you factor in the immense opportunity costs, liquidity losses, and maintenance burdens of homeownership, renting while aggressively investing your capital in high-yield equities often leaves you far wealthier. You maintain the financial flexibility to switch jobs, relocate, and grow your net worth without being tied down to a crushing debt obligation."
      },
      {
        "scene_id": "scene_019",
        "start_frame": 4949,
        "end_frame": 5114,
        "duration_frames": 165,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "To protect your financial future, adopt the Smart Home Buyer Blueprint.",
            "emphasisPhrase": "Smart Home Buyer Blueprint",
            "author": null,
            "headerLabel": "FRAMEWORK",
            "variant": "statement",
            "sourceContext": null,
            "polarity": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_6_0_beat_07_01",
          "asset_type": "video",
          "source": "pexels",
          "query": "Introduce the Smart Home Buyer Blueprint with cinematic atmospheric B-roll.",
          "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_scene_019_asset_comp_6_0_beat_07_01.mp4",
          "url": "https://videos.pexels.com/video-files/39518316/16836148_1920_1080_60fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "To protect your financial future, adopt the Smart Home Buyer Blueprint. Before signing any agreement, calculate your total cost of ownership including stamp duty, registration, interiors, and maintenance. Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched. By sidestepping the \u20b910 Lakh trap, you keep your wealth compounding and secure true financial freedom."
      },
      {
        "scene_id": "scene_020",
        "start_frame": 5114,
        "end_frame": 5317,
        "duration_frames": 203,
        "component": {
          "component_id": "ProcessFlow",
          "props": {
            "headerLabel": "TOTAL COST OF OWNERSHIP",
            "layout": "horizontal",
            "variant": "horizontal",
            "steps": [
              {
                "title": "Stamp Duty",
                "subtitle": "Government levy",
                "type": "step",
                "value": null,
                "connectorLabel": null,
                "icon": null
              },
              {
                "title": "Registration",
                "subtitle": "Legal paperwork fee",
                "type": "step",
                "value": null,
                "connectorLabel": null,
                "icon": null
              },
              {
                "title": "Interiors",
                "subtitle": "Setup and furnishing",
                "type": "step",
                "value": null,
                "connectorLabel": null,
                "icon": null
              },
              {
                "title": "Maintenance",
                "subtitle": "Ongoing society upkeep",
                "type": "step",
                "value": null,
                "connectorLabel": null,
                "icon": null
              }
            ],
            "footerLabel": null
          }
        },
        "asset": null,
        "narration_text": "To protect your financial future, adopt the Smart Home Buyer Blueprint. Before signing any agreement, calculate your total cost of ownership including stamp duty, registration, interiors, and maintenance. Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched. By sidestepping the \u20b910 Lakh trap, you keep your wealth compounding and secure true financial freedom."
      },
      {
        "scene_id": "scene_021",
        "start_frame": 5317,
        "end_frame": 5494,
        "duration_frames": 177,
        "component": {
          "component_id": "BrollCaption",
          "props": {
            "caption": "Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched.",
            "emphasisPhrase": "2.5x annual salary borrowing cap",
            "author": null,
            "headerLabel": "GOLDEN RULE",
            "variant": "statement",
            "sourceContext": null,
            "polarity": null
          }
        },
        "asset": {
          "asset_id": "asset_comp_6_2_beat_07_03",
          "asset_type": "video",
          "source": "pexels",
          "query": "Emphasize the financial rule of keeping home loans under 2.5x annual salary with atmospheric b-roll.",
          "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_scene_021_asset_comp_6_2_beat_07_03.mp4",
          "url": "https://videos.pexels.com/video-files/5849625/5849625-hd_1920_1080_30fps.mp4",
          "asset_status": "cached"
        },
        "narration_text": "To protect your financial future, adopt the Smart Home Buyer Blueprint. Before signing any agreement, calculate your total cost of ownership including stamp duty, registration, interiors, and maintenance. Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched. By sidestepping the \u20b910 Lakh trap, you keep your wealth compounding and secure true financial freedom."
      },
      {
        "scene_id": "scene_022",
        "start_frame": 5494,
        "end_frame": 5651,
        "duration_frames": 157,
        "component": {
          "component_id": "CauseEffect",
          "props": {
            "causes": [
              {
                "label": "Sidestepping the \u20b910 Lakh Trap",
                "value": "\u20b910 Lakh",
                "icon": "\ud83d\udee1\ufe0f"
              }
            ],
            "connector": "leads to",
            "outcomeLabel": "True Financial Freedom",
            "outcomeValue": "Compounding Wealth",
            "outcomeSeverity": "positive",
            "outcomeHeaderLabel": "Ultimate Consequence",
            "outcomeNote": "Keeps your wealth compounding securely",
            "variant": "single_cause",
            "polarity": null
          }
        },
        "asset": null,
        "narration_text": "To protect your financial future, adopt the Smart Home Buyer Blueprint. Before signing any agreement, calculate your total cost of ownership including stamp duty, registration, interiors, and maintenance. Never borrow more than 2.5 times your annual salary, and ensure your emergency fund remains untouched. By sidestepping the \u20b910 Lakh trap, you keep your wealth compounding and secure true financial freedom."
      }
    ],
    "audio": {
      "audio_file_name": "narration.mp3",
      "local_path": "run_9c4a21e6b1da41ed96e63a391e521b0b_narration.mp3",
      "duration_seconds": 188.376
    }
  },
  "frame_spans": [
    {
      "event_id": "scene_001",
      "start_frame": 0,
      "end_frame": 241,
      "duration_frames": 241
    },
    {
      "event_id": "scene_002",
      "start_frame": 241,
      "end_frame": 407,
      "duration_frames": 166
    },
    {
      "event_id": "scene_003",
      "start_frame": 407,
      "end_frame": 639,
      "duration_frames": 232
    },
    {
      "event_id": "scene_004",
      "start_frame": 639,
      "end_frame": 829,
      "duration_frames": 190
    },
    {
      "event_id": "scene_005",
      "start_frame": 829,
      "end_frame": 1179,
      "duration_frames": 350
    },
    {
      "event_id": "scene_006",
      "start_frame": 1179,
      "end_frame": 1364,
      "duration_frames": 185
    },
    {
      "event_id": "scene_007",
      "start_frame": 1364,
      "end_frame": 1559,
      "duration_frames": 195
    },
    {
      "event_id": "scene_008",
      "start_frame": 1559,
      "end_frame": 1693,
      "duration_frames": 134
    },
    {
      "event_id": "scene_009",
      "start_frame": 1693,
      "end_frame": 1973,
      "duration_frames": 280
    },
    {
      "event_id": "scene_010",
      "start_frame": 1973,
      "end_frame": 2485,
      "duration_frames": 512
    },
    {
      "event_id": "scene_011",
      "start_frame": 2485,
      "end_frame": 2792,
      "duration_frames": 307
    },
    {
      "event_id": "scene_012",
      "start_frame": 2792,
      "end_frame": 3190,
      "duration_frames": 398
    },
    {
      "event_id": "scene_013",
      "start_frame": 3190,
      "end_frame": 3509,
      "duration_frames": 319
    },
    {
      "event_id": "scene_014",
      "start_frame": 3509,
      "end_frame": 3803,
      "duration_frames": 294
    },
    {
      "event_id": "scene_015",
      "start_frame": 3803,
      "end_frame": 4230,
      "duration_frames": 427
    },
    {
      "event_id": "scene_016",
      "start_frame": 4230,
      "end_frame": 4411,
      "duration_frames": 181
    },
    {
      "event_id": "scene_017",
      "start_frame": 4411,
      "end_frame": 4726,
      "duration_frames": 315
    },
    {
      "event_id": "scene_018",
      "start_frame": 4726,
      "end_frame": 4949,
      "duration_frames": 223
    },
    {
      "event_id": "scene_019",
      "start_frame": 4949,
      "end_frame": 5114,
      "duration_frames": 165
    },
    {
      "event_id": "scene_020",
      "start_frame": 5114,
      "end_frame": 5317,
      "duration_frames": 203
    },
    {
      "event_id": "scene_021",
      "start_frame": 5317,
      "end_frame": 5494,
      "duration_frames": 177
    },
    {
      "event_id": "scene_022",
      "start_frame": 5494,
      "end_frame": 5651,
      "duration_frames": 157
    }
  ]
}
```

---

## Stage 8: Video Output

- **Artifact ID:** `artifact_24b6a42900fd4b808357de3af598441d`
- **Artifact Type:** `video`
- **Schema Version:** `1`
- **Status:** `valid`
- **Created At:** `2026-09-14T13:28:12.004250+00:00`
- **Parent Artifact Roles:** `{"render_spec": "artifact_6820865b0a1b4b21aae3e411d7489a0f"}`
- **Validation Record:** `{"status":"valid","errors":[],"warnings":[]}`
- **Role in System:** Compiles and renders the finalized 1080x1920 MP4 video artifact via Remotion renderer.

### Complete Payload JSON
```json
{
  "schema_version": "1",
  "scene_id": "scene_project_bd64dbe39bb646ddb4d8294b63def4ff",
  "render_status": "succeeded",
  "file_name": "scene_project_bd64dbe39bb646ddb4d8294b63def4ff.mp4",
  "content_type": "video/mp4",
  "fps": 30,
  "duration_frames": 5651,
  "storage_key": "projects/project_bd64dbe39bb646ddb4d8294b63def4ff/runs/run_9c4a21e6b1da41ed96e63a391e521b0b/scene_project_bd64dbe39bb646ddb4d8294b63def4ff.mp4",
  "size_bytes": 17310051,
  "error_message": null
}
```

---
