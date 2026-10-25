/**
 * Shared visual language for the hand-drawn story slice.
 *
 * This file intentionally contains presentation tokens only. It does not
 * change story timing, layout, object state, or choreography.
 */
export const handDrawn = {
  colors: {
    paper: "#F7F1E5",
    paperAlt: "#FFFDF7",
    paperDeep: "#EDE1CB",
    ink: "#202522",
    inkMuted: "#66706A",
    coral: "#E76F51",
    coralSoft: "#F7C2B3",
    teal: "#2A9D8F",
    tealSoft: "#BFE3DC",
    blue: "#457B9D",
    blueSoft: "#C8DDE8",
    amber: "#E9A23B",
    amberSoft: "#F6DEAD",
    green: "#4D9B62",
    red: "#C94C4C",
    white: "#FFFFFF",
  },
  font: {
    body: "Avenir Next, Trebuchet MS, ui-sans-serif, system-ui, sans-serif",
    display: "Avenir Next, Trebuchet MS, ui-sans-serif, system-ui, sans-serif",
    label: "Trebuchet MS, Avenir Next, ui-sans-serif, system-ui, sans-serif",
  },
  radius: {
    card: 14,
    small: 8,
    pill: 9999,
  },
  shadow: {
    paper: "4px 6px 0 rgba(32, 37, 34, 0.10), 0 12px 24px rgba(32, 37, 34, 0.08)",
    lifted: "6px 8px 0 rgba(32, 37, 34, 0.12), 0 18px 30px rgba(32, 37, 34, 0.10)",
  },
  stroke: {
    ink: 2,
    accent: 3,
  },
} as const;

export function handDrawnAccent(state?: string, custom?: string): string {
  if (custom) return custom;
  if (state === "danger" || state === "eroded") return handDrawn.colors.red;
  if (state === "warning") return handDrawn.colors.amber;
  if (state === "success") return handDrawn.colors.green;
  return handDrawn.colors.teal;
}
