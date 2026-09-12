export const tokens = {
  bg: {
    base: "rgba(9, 9, 11, 0.84)",
    surface: "rgba(24, 24, 27, 0.80)",
    border: "rgba(255, 255, 255, 0.08)",
    cardLeft: "rgba(15, 23, 42, 0.80)",
    cardRight: "rgba(24, 24, 27, 0.85)",
  },
  accent: {
    primary: "#3b82f6",   // Vibrant Blue
    blue: "#3b82f6",      // Blue Accent
    cyan: "#38bdf8",      // Sky Blue
    emerald: "#10b981",   // Emerald Green
    purple: "#a855f7",    // Purple Accent
    rose: "#f43f5e",      // Rose Red
    amber: "#f59e0b",     // Warm Amber
  },
  text: {
    primary: "#f4f4f5",
    secondary: "#a1a1aa",
    muted: "#71717a",
  },
  font: {
    family: "Inter, ui-sans-serif, system-ui, sans-serif",
    display: 144,
    headline: 72,
    subheadline: 44,
    eyebrow: 24,
    body: 32,
    caption: 24,
  },
  spacing: {
    padding: "80px 100px",
  },
  radius: {
    card: 16,
    chip: 8,
    pill: 9999,
  },
  semantic: {
    info: "#38bdf8",     // Sky / Cyan
    success: "#10b981",  // Emerald
    warning: "#f59e0b",  // Warm Amber
    danger: "#f43f5e",   // Rose / Red
    hero: "#06b6d4",     // Vivid Cyan
    neutral: "#71717a",  // Zinc
  },
  motion: {
    reveal: { damping: 16, stiffness: 120 },
    settle: { damping: 14, stiffness: 90 },
    impact: { damping: 18, stiffness: 140, mass: 1.2 },
    gentle: { damping: 20, stiffness: 80 },
  },
  gradients: {
    darkAtmosphere: "radial-gradient(ellipse at center, rgba(15, 23, 42, 0.6) 0%, rgba(9, 9, 11, 0.95) 100%)",
    heroGlow: "radial-gradient(circle, rgba(56, 189, 248, 0.16) 0%, transparent 70%)",
    warningGlow: "radial-gradient(circle, rgba(244, 63, 94, 0.18) 0%, transparent 70%)",
    successGlow: "radial-gradient(circle, rgba(16, 185, 129, 0.18) 0%, transparent 70%)",
  },
};
