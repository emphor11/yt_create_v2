import React from "react";

interface DataDiagnosticProps {
  componentId: string;
  props: Record<string, any>;
  enabled?: boolean;
}

export function DataDiagnostic({ componentId, props, enabled = false }: DataDiagnosticProps) {
  if (!enabled) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 20,
        right: 20,
        maxWidth: 450,
        maxHeight: 250,
        overflow: "auto",
        background: "rgba(0, 0, 0, 0.88)",
        border: "1px solid rgba(6, 182, 212, 0.6)",
        borderRadius: 8,
        padding: "12px 16px",
        fontFamily: "monospace",
        fontSize: 12,
        color: "#22d3ee",
        zIndex: 9999,
        boxShadow: "0 10px 30px rgba(0,0,0,0.8)",
        pointerEvents: "none",
      }}
    >
      <div style={{ fontWeight: "bold", marginBottom: 6, color: "#f43f5e", textTransform: "uppercase" }}>
        🔍 Anti-Bug Data Diagnostic — {componentId}
      </div>
      <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word", color: "#e2e8f0" }}>
        {JSON.stringify(props, null, 2)}
      </pre>
    </div>
  );
}
