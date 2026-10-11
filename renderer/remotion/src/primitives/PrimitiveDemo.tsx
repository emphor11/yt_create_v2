import React from "react";
import { PrimitiveRenderer } from "./PrimitiveRenderer";
import { type PrimitiveTreeSpec } from "./types";

export const demoPrimitiveTree: PrimitiveTreeSpec = {
  scene_id: "demo_all_primitives",
  duration_frames: 180,
  root_primitive_ids: [
    "bg_video",
    "header_text",
    "card_left",
    "card_right",
    "flow_connector",
    "chart_group",
    "gauge_group",
    "asset_image",
  ],
  primitives: {
    // 1. VIDEO Primitive (Background ambient loop)
    bg_video: {
      identity: { id: "bg_video", type: "video", z_index: 0 },
      layout: { position_mode: "absolute", x: 0, y: 0, width: 1920, height: 1080 },
      style: { opacity: 0.12 },
      timing: { enter_frame: 0, visible: true },
      props: {
        source: "run_f7af2e1973ab4b5fb5fe52997a7ddcce_scene_002_asset_hook_0_1_beat_02.mp4",
        loop: true,
        muted: true,
      },
    },

    // 2. TEXT Primitive (Scene Header with Highlight)
    header_text: {
      identity: { id: "header_text", type: "text", z_index: 2 },
      layout: { position_mode: "absolute", x: 100, y: 60, width: 1200 },
      timing: { enter_frame: 0, visible: true },
      props: {
        content: "Primitive Architecture Demonstration: All 13 Capabilities",
        font_size: 40,
        font_weight: 800,
        highlight_spans: [{ word: "All 13 Capabilities", color: "#38bdf8", background: "rgba(56, 189, 248, 0.2)" }],
      },
    },

    // 3. GROUP Primitive (Card Left composed of shape, icon, text, number)
    card_left: {
      identity: { id: "card_left", type: "group", z_index: 5 },
      layout: { position_mode: "absolute", x: 100, y: 160, width: 380, height: 260 },
      timing: { enter_frame: 10, visible: true },
      props: {
        layout_flow: "column",
        gap: 16,
        child_ids: ["card_left_bg", "card_left_icon", "card_left_title", "card_left_val"],
      },
      animations: [
        {
          action_id: "slide_card",
          trigger_frame: 10,
          duration_frames: 25,
          behavior: "appear",
          target_property: "shift_y",
          from_value: 30,
          to_value: 0,
        },
      ],
    },
    // 4. SHAPE Primitive (Card Left Background)
    card_left_bg: {
      identity: { id: "card_left_bg", type: "shape", parent_id: "card_left", z_index: 0 },
      layout: { position_mode: "absolute", x: 0, y: 0, width: 380, height: 260 },
      style: {
        fill: "rgba(24, 24, 27, 0.85)",
        stroke: "rgba(56, 189, 248, 0.4)",
        stroke_width: 1.5,
        corner_radius: 16,
        blur_backdrop: 16,
        shadow: { color: "rgba(0,0,0,0.5)", blur: 20, x: 0, y: 10 },
      },
      timing: { enter_frame: 10, visible: true },
      props: { shape_type: "rectangle" },
    },
    // 5. ICON Primitive
    card_left_icon: {
      identity: { id: "card_left_icon", type: "icon", parent_id: "card_left", z_index: 1 },
      layout: { position_mode: "relative", margin: { top: 24, left: 24 } },
      timing: { enter_frame: 15, visible: true },
      props: { name: "briefcase", size: 36, color: "#38bdf8" },
    },
    card_left_title: {
      identity: { id: "card_left_title", type: "text", parent_id: "card_left", z_index: 1 },
      layout: { position_mode: "relative", margin: { left: 24 } },
      timing: { enter_frame: 20, visible: true },
      props: { content: "Gross Nominal Salary", font_size: 20, font_weight: 600 },
      style: { fill: "#a1a1aa" },
    },
    // 6. NUMBER Primitive (Animates from 0 to 50k, then transforms down to 30k at frame 60)
    card_left_val: {
      identity: { id: "card_left_val", type: "number", parent_id: "card_left", z_index: 1 },
      layout: { position_mode: "relative", margin: { left: 24, bottom: 24 } },
      timing: { enter_frame: 20, visible: true },
      props: { value: 50000, start_value: 0, prefix: "₹", font_size: 56, font_weight: 800 },
      animations: [
        {
          action_id: "count_init",
          trigger_frame: 20,
          duration_frames: 35,
          behavior: "appear",
          target_property: "value",
          from_value: 0,
          to_value: 50000,
          easing: "ease-out",
        },
        {
          action_id: "transform_rent",
          trigger_frame: 75,
          duration_frames: 30,
          behavior: "transform",
          target_property: "value",
          from_value: 50000,
          to_value: 30000,
          easing: "spring",
        },
        {
          action_id: "color_warn",
          trigger_frame: 75,
          duration_frames: 20,
          behavior: "transform",
          target_property: "style.fill",
          from_value: "#ffffff",
          to_value: "#f43f5e",
          easing: "ease-out",
        },
      ],
    },

    // Card Right
    card_right: {
      identity: { id: "card_right", type: "group", z_index: 5 },
      layout: { position_mode: "absolute", x: 680, y: 160, width: 380, height: 260 },
      timing: { enter_frame: 40, visible: true },
      props: {
        layout_flow: "column",
        gap: 16,
        child_ids: ["card_right_bg", "card_right_icon", "card_right_title", "card_right_val"],
      },
    },
    card_right_bg: {
      identity: { id: "card_right_bg", type: "shape", parent_id: "card_right", z_index: 0 },
      layout: { position_mode: "absolute", x: 0, y: 0, width: 380, height: 260 },
      style: {
        fill: "rgba(24, 24, 27, 0.85)",
        stroke: "rgba(255, 255, 255, 0.1)",
        corner_radius: 16,
        blur_backdrop: 16,
      },
      props: { shape_type: "rectangle" },
    },
    card_right_icon: {
      identity: { id: "card_right_icon", type: "icon", parent_id: "card_right", z_index: 1 },
      layout: { position_mode: "relative", margin: { top: 24, left: 24 } },
      props: { name: "alert", size: 36, color: "#f59e0b" },
    },
    card_right_title: {
      identity: { id: "card_right_title", type: "text", parent_id: "card_right", z_index: 1 },
      layout: { position_mode: "relative", margin: { left: 24 } },
      props: { content: "Metro Urban Rent", font_size: 20, font_weight: 600 },
      style: { fill: "#a1a1aa" },
    },
    card_right_val: {
      identity: { id: "card_right_val", type: "number", parent_id: "card_right", z_index: 1 },
      layout: { position_mode: "relative", margin: { left: 24, bottom: 24 } },
      props: { value: 20000, start_value: 0, prefix: "₹", font_size: 56, font_weight: 800 },
    },

    // 7. CONNECTOR Primitive (Linking Card Left to Card Right with labeled arrow)
    flow_connector: {
      identity: { id: "flow_connector", type: "connector", z_index: 4 },
      timing: { enter_frame: 50, visible: true },
      props: {
        from_anchor: { target_id: "card_left", side: "right" },
        to_anchor: { target_id: "card_right", side: "left" },
        routing: "curved",
        has_arrow: true,
        stroke: "#f43f5e",
        stroke_width: 2.5,
        label: { text: "- ₹20,000 Rent", font_size: 14, background: "rgba(244, 63, 94, 0.2)" },
      },
      animations: [
        {
          action_id: "draw_arrow",
          trigger_frame: 50,
          duration_frames: 25,
          behavior: "draw_path",
          target_property: "draw_progress",
          from_value: 0,
          to_value: 1,
          easing: "ease-out",
        },
      ],
    },

    // 8. BAR Primitive & 9. SEGMENT Primitive in a group
    chart_group: {
      identity: { id: "chart_group", type: "group", z_index: 5 },
      layout: { position_mode: "absolute", x: 100, y: 480, width: 960 },
      timing: { enter_frame: 60, visible: true },
      props: {
        layout_flow: "column",
        gap: 16,
        child_ids: ["chart_title", "main_bar", "trend_line", "milestone_point"],
      },
    },
    chart_title: {
      identity: { id: "chart_title", type: "text", parent_id: "chart_group", z_index: 1 },
      props: { content: "Budget Allocation & Purchasing Trend", font_size: 22, font_weight: 600 },
    },
    main_bar: {
      identity: { id: "main_bar", type: "bar", parent_id: "chart_group", z_index: 1 },
      props: {
        orientation: "horizontal",
        fill_percentage: 0.85,
        max_length: 960,
        thickness: 28,
        corner_radius: 8,
        foreground_color: "#10b981",
      },
      animations: [
        {
          action_id: "grow_bar",
          trigger_frame: 60,
          duration_frames: 30,
          behavior: "grow",
          target_property: "fill_percentage",
          from_value: 0.1,
          to_value: 0.85,
          easing: "spring",
        },
      ],
    },

    // 10. LINE Primitive (Trend curve)
    trend_line: {
      identity: { id: "trend_line", type: "line", parent_id: "chart_group", z_index: 2 },
      props: {
        points: [
          { x: 0, y: 70 },
          { x: 240, y: 55 },
          { x: 480, y: 80 },
          { x: 720, y: 30 },
          { x: 960, y: 95 },
        ],
        curve_type: "monotone_cubic",
        stroke: "#38bdf8",
        stroke_width: 3.5,
        area_fill: "#38bdf8",
      },
      animations: [
        {
          action_id: "draw_trend",
          trigger_frame: 80,
          duration_frames: 40,
          behavior: "draw_line",
          target_property: "draw_progress",
          from_value: 0,
          to_value: 1,
          easing: "ease-out",
        },
      ],
    },

    // 11. POINT Primitive (Milestone on line)
    milestone_point: {
      identity: { id: "milestone_point", type: "point", parent_id: "chart_group", z_index: 3 },
      props: { x: 720, y: 30, radius: 8, fill: "#f59e0b", label: "Peak Inflation" },
      animations: [
        {
          action_id: "pulse_milestone",
          trigger_frame: 100,
          duration_frames: 20,
          behavior: "pulse",
          target_property: "pulse_scale",
          from_value: 1.0,
          to_value: 1.6,
          easing: "spring",
        },
      ],
    },

    // 12. PROGRESS Primitive (Radial Gauge)
    gauge_group: {
      identity: { id: "gauge_group", type: "group", z_index: 5 },
      layout: { position_mode: "absolute", x: 1200, y: 160 },
      timing: { enter_frame: 45, visible: true },
      props: {
        layout_flow: "column",
        gap: 12,
        align_items: "center",
        child_ids: ["gauge_ring", "gauge_lbl"],
      },
    },
    gauge_ring: {
      identity: { id: "gauge_ring", type: "progress", parent_id: "gauge_group", z_index: 1 },
      props: {
        variant: "radial_ring",
        progress_ratio: 0.72,
        radius: 80,
        stroke_width: 12,
        fill_color: "#a855f7",
        center_label: "72%",
      },
      animations: [
        {
          action_id: "sweep_gauge",
          trigger_frame: 45,
          duration_frames: 35,
          behavior: "sweep",
          target_property: "progress_ratio",
          from_value: 0.0,
          to_value: 0.72,
          easing: "ease-out",
        },
      ],
    },
    gauge_lbl: {
      identity: { id: "gauge_lbl", type: "text", parent_id: "gauge_group", z_index: 1 },
      props: { content: "Budget Stress Index", font_size: 18, font_weight: 600 },
      style: { fill: "#a1a1aa" },
    },

    // 13. IMAGE Primitive (Clean photo anchor)
    asset_image: {
      identity: { id: "asset_image", type: "image", z_index: 5 },
      layout: { position_mode: "absolute", x: 1200, y: 460, width: 400, height: 220 },
      timing: { enter_frame: 70, visible: true },
      props: {
        source: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='220'><rect width='100%' height='100%' fill='%231e293b'/><text x='50%' y='50%' fill='%2338bdf8' font-size='22' font-family='sans-serif' text-anchor='middle' dominant-baseline='middle'>Primitive Image Asset</text></svg>",
        object_fit: "cover",
        border_radius: 16,
      },
    },
  },
};

export const PrimitiveDemo: React.FC = () => {
  return <PrimitiveRenderer tree={demoPrimitiveTree} />;
};
