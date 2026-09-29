import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { tokens } from '../design-tokens';
import { ValueFlowNetworkProps, FlowNodeProp, FlowEdgeProp } from '../types';
import { safeAnimationWindow } from '../animation-safety';

function EditorialBackdrop({ glowColor = '#38bdf8', glowOpacity = 0.10 }: { glowColor?: string; glowOpacity?: number }) {
  return (
    <AbsoluteFill style={{ backgroundColor: '#060911', overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse 95% 75% at 50% 46%, #0b1222 0%, #060913 65%, #020408 100%)' }} />
      <div style={{ position: 'absolute', width: '900px', height: '600px', left: '50%', top: '50%', transform: 'translate(-50%,-50%)', borderRadius: '50%', background: `radial-gradient(ellipse at center, ${glowColor} 0%, transparent 68%)`, filter: 'blur(48px)', opacity: glowOpacity }} />
      <div style={{ position: 'absolute', top: '84px', left: '140px', right: '140px', height: '1px', background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.035) 15%, rgba(255,255,255,0.035) 85%, transparent 100%)' }} />
      <div style={{ position: 'absolute', bottom: '84px', left: '140px', right: '140px', height: '1px', background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.035) 15%, rgba(255,255,255,0.035) 85%, transparent 100%)' }} />
    </AbsoluteFill>
  );
}

const POLARITY_COLORS: Record<string, string> = {
  positive: tokens.accent.emerald ?? '#10b981',
  negative: tokens.accent.rose ?? '#f43f5e',
  warning: tokens.accent.amber ?? '#f59e0b',
  neutral: tokens.accent.cyan ?? '#38bdf8',
};

function nodeColor(role?: string | null): string {
  if (role === 'source') return tokens.accent.cyan ?? '#38bdf8';
  if (role === 'destination') return tokens.accent.emerald ?? '#10b981';
  if (role === 'fee') return tokens.accent.rose ?? '#f43f5e';
  return tokens.accent.cyan ?? '#38bdf8';
}

export function ValueFlowNetwork(props: ValueFlowNetworkProps | any) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const resolvedProps: ValueFlowNetworkProps = (props as any).props || props;
  const duration_frames: number = (props as any).duration_frames || 180;

  const nodes: FlowNodeProp[] = Array.isArray(resolvedProps.nodes) && resolvedProps.nodes.length >= 2
    ? resolvedProps.nodes.slice(0, 5)
    : [{ id: 'a', label: 'Source' }, { id: 'b', label: 'Destination' }];

  const flows: FlowEdgeProp[] = Array.isArray(resolvedProps.flows) ? resolvedProps.flows : [];
  const headline = resolvedProps.headline || null;
  const headerLabel = resolvedProps.header_label || 'VALUE FLOW';

  // Scene fade
  const sceneOpacity = interpolate(frame, [0, Math.min(8, duration_frames - 1)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Position nodes horizontally
  const nodeCount = nodes.length;
  const nodeSpacing = 1280 / (nodeCount + 1);

  // Per-node spring entrances
  const nodeDelayFrames = 10;
  const nodeAnimations = nodes.map((_, i) => {
    const delay = i * nodeDelayFrames;
    const sp = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 18, stiffness: 100, mass: 1 } });
    return { opacity: sp, y: interpolate(sp, [0, 1], [30, 0]) };
  });

  // Edge animation — draw after nodes appear
  const edgeStart = nodeCount * nodeDelayFrames + 5;
  const edgeProgress = interpolate(frame, [edgeStart, edgeStart + 40], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity }}>
      <EditorialBackdrop glowColor={tokens.accent.cyan ?? '#38bdf8'} glowOpacity={0.08} />

      <AbsoluteFill style={{ zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 100px' }}>

        {/* Header */}
        <div style={{ position: 'absolute', top: '56px', left: '100px', right: '100px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '11px', fontWeight: 700, letterSpacing: '0.22em', color: tokens.accent.cyan ?? '#38bdf8', textTransform: 'uppercase', opacity: 0.7 }}>
            {headerLabel}
          </div>
        </div>

        {/* Nodes layer */}
        <div style={{ position: 'relative', width: '100%', height: '280px', marginTop: '40px' }}>
          {/* Draw edges via SVG */}
          <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible' }}>
            {flows.map((flow, fi) => {
              const fromIdx = nodes.findIndex(n => n.id === flow.from_node);
              const toIdx = nodes.findIndex(n => n.id === flow.to_node);
              if (fromIdx < 0 || toIdx < 0) return null;
              const x1 = (fromIdx + 1) * nodeSpacing;
              const x2 = (toIdx + 1) * nodeSpacing;
              const y = 140;
              const midX = (x1 + x2) / 2;
              const curveY = y - 60;
              const flowColor = POLARITY_COLORS[flow.polarity ?? 'neutral'] ?? (tokens.accent.cyan ?? '#38bdf8');
              const pathD = `M ${x1} ${y} Q ${midX} ${curveY} ${x2} ${y}`;
              return (
                <g key={fi} opacity={edgeProgress}>
                  <path d={pathD} stroke={flowColor} strokeWidth={2} fill="none" opacity={0.6} strokeDasharray="6 4" />
                  {/* Arrow */}
                  <polygon
                    points={`${x2},${y} ${x2-8},${y-6} ${x2-8},${y+6}`}
                    fill={flowColor}
                    opacity={0.8}
                  />
                  {/* Edge label */}
                  {flow.label && (
                    <text
                      x={midX}
                      y={curveY - 12}
                      textAnchor="middle"
                      fill={flowColor}
                      fontSize="13"
                      fontFamily={"Inter, ui-sans-serif, system-ui, sans-serif"}
                      fontWeight="700"
                      opacity={0.9}
                    >
                      {flow.label}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>

          {/* Nodes */}
          {nodes.map((node, i) => {
            const x = (i + 1) * nodeSpacing;
            const anim = nodeAnimations[i];
            const color = nodeColor(node.role);
            return (
              <div
                key={node.id}
                style={{
                  position: 'absolute',
                  left: x - 70,
                  top: 100,
                  width: 140,
                  opacity: anim.opacity,
                  transform: `translateY(${anim.y}px)`,
                }}
              >
                {/* Node circle */}
                <div style={{
                  width: 80, height: 80, borderRadius: '50%',
                  border: `2px solid ${color}`,
                  background: `radial-gradient(ellipse at center, ${color}18 0%, transparent 70%)`,
                  margin: '0 auto',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: `0 0 20px ${color}30`,
                }}>
                  {node.value && (
                    <div style={{ fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '14px', fontWeight: 800, color, textAlign: 'center', lineHeight: 1.1 }}>
                      {node.value}
                    </div>
                  )}
                </div>
                {/* Node label */}
                <div style={{ marginTop: 12, textAlign: 'center', fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif", fontSize: '14px', fontWeight: 600, color: 'rgba(255,255,255,0.85)', letterSpacing: '0.02em' }}>
                  {node.label}
                </div>
              </div>
            );
          })}
        </div>

        {/* Headline */}
        {headline && (
          <div style={{
            marginTop: 40,
            fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
            fontSize: '22px',
            fontWeight: 700,
            color: 'rgba(255,255,255,0.75)',
            textAlign: 'center',
            letterSpacing: '0.01em',
            opacity: edgeProgress,
          }}>
            {headline}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
