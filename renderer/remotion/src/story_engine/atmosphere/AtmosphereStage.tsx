import React, { useMemo } from "react";
import type { AtmosphereProps, AtmospherePreset } from "../types.ts";

interface AtmosphereStageProps {
  atmosphere?: AtmosphereProps;
  backdropDim?: number;
  frame: number;
  width?: number;
  height?: number;
}

// Pre-baked static SVG grain pattern data-URI so Chromium computes noise once and GPU-caches the tile.
const GRAIN_DATA_URI =
  "data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.7'/%3E%3C/svg%3E";

interface PresetConfig {
  baseBackground: string;
  gridStroke: string;
  gridOpacity: number;
  gridPattern: "accounting" | "blueprint" | "dots" | "none";
  keyLightColor: string;
  keyLightBaseOpacity: number;
  vignetteBase: number;
  grainOpacity: number;
  crosshairColor: string;
}

const PRESET_CONFIGS: Record<AtmospherePreset, PresetConfig> = {
  desk_noir: {
    // Aliased to paper_clean so dark background is completely eliminated from the system
    baseBackground: "radial-gradient(ellipse at 50% 28%, #FDFBF7 0%, #F5EFEB 68%, #E7DFD4 100%)",
    gridStroke: "#202522",
    gridOpacity: 0.045,
    gridPattern: "accounting",
    keyLightColor: "255, 253, 247", // clean 5000K daylight
    keyLightBaseOpacity: 0.55,
    vignetteBase: 0.20,
    grainOpacity: 0.035,
    crosshairColor: "rgba(32, 37, 34, 0.2)",
  },
  paper_clean: {
    baseBackground: "radial-gradient(ellipse at 50% 28%, #FDFBF7 0%, #F5EFEB 68%, #E7DFD4 100%)",
    gridStroke: "#202522",
    gridOpacity: 0.045,
    gridPattern: "accounting",
    keyLightColor: "255, 253, 247", // clean 5000K daylight
    keyLightBaseOpacity: 0.55,
    vignetteBase: 0.20,
    grainOpacity: 0.035,
    crosshairColor: "rgba(32, 37, 34, 0.2)",
  },
  blueprint: {
    baseBackground: "radial-gradient(ellipse at 50% 30%, #102A43 0%, #0B1D3A 70%, #061024 100%)",
    gridStroke: "#38BEC9",
    gridOpacity: 0.07,
    gridPattern: "blueprint",
    keyLightColor: "56, 178, 172", // cool drafting cyan
    keyLightBaseOpacity: 0.20,
    vignetteBase: 0.55,
    grainOpacity: 0.05,
    crosshairColor: "rgba(56, 178, 172, 0.35)",
  },
  vault: {
    baseBackground: "radial-gradient(ellipse at 50% 30%, #262D35 0%, #1A1F26 68%, #101317 100%)",
    gridStroke: "#94A3B8",
    gridOpacity: 0.05,
    gridPattern: "dots",
    keyLightColor: "226, 232, 240", // cold brushed steel
    keyLightBaseOpacity: 0.18,
    vignetteBase: 0.70,
    grainOpacity: 0.06,
    crosshairColor: "rgba(148, 163, 184, 0.25)",
  },
  newsroom: {
    baseBackground: "radial-gradient(ellipse at 50% 30%, #2A2421 0%, #1C1816 70%, #110E0D 100%)",
    gridStroke: "#D97706",
    gridOpacity: 0.04,
    gridPattern: "accounting",
    keyLightColor: "251, 191, 36", // investigative incandescent
    keyLightBaseOpacity: 0.24,
    vignetteBase: 0.62,
    grainOpacity: 0.07,
    crosshairColor: "rgba(251, 191, 36, 0.3)",
  },
};

export const AtmosphereStage: React.FC<AtmosphereStageProps> = ({
  atmosphere,
  backdropDim = 0,
  frame,
  width = 1920,
  height = 1080,
}) => {
  const presetKey: AtmospherePreset = atmosphere?.preset ?? "desk_noir";
  const config = PRESET_CONFIGS[presetKey] ?? PRESET_CONFIGS.desk_noir;

  // 1. Organic Key Light Drift (Sinusoidal subtle drift over 20-25s)
  // At 30fps: 600 frames = 20s. At 60fps: 1200 frames = 20s.
  const driftAngle = (frame * 2 * Math.PI) / 720;
  const driftX = Math.sin(driftAngle) * 36;
  const driftY = Math.cos(driftAngle * 0.8) * 24;

  const keyLightIntensity =
    (atmosphere?.keyLight?.intensity ?? config.keyLightBaseOpacity) * (1 - backdropDim * 0.5);

  const vignetteIntensity = Math.min(
    0.95,
    (atmosphere?.vignette ?? config.vignetteBase) + backdropDim * 0.35
  );

  const grainOpacity = (atmosphere?.grain ?? config.grainOpacity) * (1 + backdropDim * 0.25);

  // 2. Grain offset stepped every 5 frames (12 fps film shutter)
  const grainStep = Math.floor(frame / 5) % 4;
  const grainOffsetX = grainStep * 47;
  const grainOffsetY = (grainStep * 31) % 64;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        width,
        height,
        overflow: "hidden",
        pointerEvents: "none",
        zIndex: 0,
      }}
    >
      {/* 1. Base Tactile Material Surface */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: config.baseBackground,
        }}
      />

      {/* 2. Procedural Grid / Ledger Texture */}
      {config.gridPattern !== "none" && (
        <svg
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            opacity: config.gridOpacity,
          }}
        >
          <defs>
            {config.gridPattern === "accounting" && (
              <pattern
                id="atm-accounting-grid"
                width="48"
                height="48"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M 48 0 L 0 0 0 48"
                  fill="none"
                  stroke={config.gridStroke}
                  strokeWidth="0.85"
                />
                <circle cx="0" cy="0" r="1.2" fill={config.gridStroke} />
              </pattern>
            )}

            {config.gridPattern === "blueprint" && (
              <pattern
                id="atm-blueprint-grid"
                width="40"
                height="40"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M 40 0 L 0 0 0 40"
                  fill="none"
                  stroke={config.gridStroke}
                  strokeWidth="0.65"
                />
                <path
                  d="M 200 0 L 0 0 0 200"
                  fill="none"
                  stroke={config.gridStroke}
                  strokeWidth="1.2"
                />
              </pattern>
            )}

            {config.gridPattern === "dots" && (
              <pattern
                id="atm-dots-grid"
                width="36"
                height="36"
                patternUnits="userSpaceOnUse"
              >
                <circle cx="18" cy="18" r="1.2" fill={config.gridStroke} />
              </pattern>
            )}
          </defs>
          <rect
            width="100%"
            height="100%"
            fill={
              config.gridPattern === "accounting"
                ? "url(#atm-accounting-grid)"
                : config.gridPattern === "blueprint"
                ? "url(#atm-blueprint-grid)"
                : "url(#atm-dots-grid)"
            }
          />
        </svg>
      )}

      {/* 3. Dynamic Key Light Spotlight (Corner Angle with Organic Drift) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse 950px 750px at ${180 + driftX}px ${140 + driftY}px, rgba(${config.keyLightColor}, ${keyLightIntensity}) 0%, rgba(${config.keyLightColor}, 0) 100%)`,
          mixBlendMode: "screen",
        }}
      />

      {/* 4. Film Grain Overlay (12 fps Stepped Jitter, Zero CPU Penalty) */}
      <div
        style={{
          position: "absolute",
          inset: -64,
          backgroundImage: `url("${GRAIN_DATA_URI}")`,
          backgroundRepeat: "repeat",
          backgroundSize: "200px 200px",
          transform: `translate(${grainOffsetX}px, ${grainOffsetY}px)`,
          opacity: grainOpacity,
          mixBlendMode: "overlay",
        }}
      />

      {/* 5. Cinematic Optical Vignette (Focuses Attention Inward) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at 50% 48%, transparent 42%, rgba(0, 0, 0, ${vignetteIntensity * 0.7}) 76%, rgba(0, 0, 0, ${vignetteIntensity}) 100%)`,
        }}
      />

      {/* 6. Archival Documentary Crosshairs & Edge Registration */}
      <div
        style={{
          position: "absolute",
          inset: 36,
          border: `1px solid ${config.crosshairColor}`,
          opacity: 0.5,
        }}
      >
        <span
          style={{
            position: "absolute",
            top: -9,
            left: -8,
            fontSize: 14,
            fontWeight: 600,
            color: config.crosshairColor,
            fontFamily: "monospace",
            userSelect: "none",
          }}
        >
          +
        </span>
        <span
          style={{
            position: "absolute",
            top: -9,
            right: -8,
            fontSize: 14,
            fontWeight: 600,
            color: config.crosshairColor,
            fontFamily: "monospace",
            userSelect: "none",
          }}
        >
          +
        </span>
        <span
          style={{
            position: "absolute",
            bottom: -9,
            left: -8,
            fontSize: 14,
            fontWeight: 600,
            color: config.crosshairColor,
            fontFamily: "monospace",
            userSelect: "none",
          }}
        >
          +
        </span>
        <span
          style={{
            position: "absolute",
            bottom: -9,
            right: -8,
            fontSize: 14,
            fontWeight: 600,
            color: config.crosshairColor,
            fontFamily: "monospace",
            userSelect: "none",
          }}
        >
          +
        </span>
      </div>
    </div>
  );
};
