import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { WorldObject } from "./rendering/WorldObject";

const group = {
  object_id: "test_group",
  primitive_type: "group",
  parent_object_id: null,
  child_object_ids: ["test_year", "test_salary"],
  local_geometry: {
    x: 180,
    y: 400,
    width: 500,
    height: 120,
  },
  style: {
    fill: "#222",
    stroke: null,
    stroke_width: null,
    stroke_style: "solid",
    corner_radius: 12,
    opacity: 1,
    shadow: null,
    blur_backdrop: null,
    blend_mode: "normal",
  },
  properties: {},
  connector_path: null,
};

const year = {
  object_id: "test_year",
  primitive_type: "text",
  parent_object_id: "test_group",
  child_object_ids: [],
  local_geometry: {
    x: 30,
    y: 35,
    width: 100,
    height: 40,
  },
  style: {
    fill: null,
    stroke: null,
    stroke_width: null,
    stroke_style: "solid",
    corner_radius: null,
    opacity: 1,
    shadow: null,
    blur_backdrop: null,
    blend_mode: "normal",
  },
  properties: {
    content: "2024",
    font_size: 32,
  },
  connector_path: null,
};

const salary = {
  object_id: "test_salary",
  primitive_type: "text",
  parent_object_id: "test_group",
  child_object_ids: [],
  local_geometry: {
    x: 180,
    y: 35,
    width: 180,
    height: 40,
  },
  style: {
    fill: null,
    stroke: null,
    stroke_width: null,
    stroke_style: "solid",
    corner_radius: null,
    opacity: 1,
    shadow: null,
    blur_backdrop: null,
    blend_mode: "normal",
  },
  properties: {
    content: "₹13 LPA",
    font_size: 32,
  },
  connector_path: null,
};

export const HierarchyTestComposition: React.FC = () => {
  const frame = useCurrentFrame();

  const progress = Math.min(1, Math.max(0, (frame - 30) / 60));
  const groupX = 180 + (1100 - 180) * progress;
  
  type TestPrimitive =
    | typeof group
    | typeof year
    | typeof salary;

  const primitives: Record<string, TestPrimitive> = {
    test_group: {
      ...group,
      local_geometry: {
        ...group.local_geometry,
        x: groupX,
      },
    },
    test_year: year,
    test_salary: salary,
  };

  const world = {
    world_id: "hierarchy_test",
    canvas_config: {
      width: 1920,
      height: 1080,
      fps: 30,
    },
    total_duration_frames: 120,
    primitives,
  } as any;

  const runtime = {
    world,

    roots: ["test_group"],

    getPrimitive: (id: string) => primitives[id],

    resolveObject: (id: string) => ({
      geometry: primitives[id].local_geometry,
      visible: true,
      opacity: 1,
      props: primitives[id].properties,
      style: primitives[id].style,
    }),
  } as any;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#111",
      }}
    >
      <WorldObject
        runtime={runtime}
        objectId="test_group"
        frame={frame}
        parentSpace={{
          width: 1920,
          height: 1080,
        }}
      />
    </AbsoluteFill>
  );
};