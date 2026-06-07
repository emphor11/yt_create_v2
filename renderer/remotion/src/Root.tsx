import { AbsoluteFill, Composition } from "remotion";

function PhaseZeroComposition() {
  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        backgroundColor: "#f6f8fb",
        color: "#172026",
        display: "flex",
        fontFamily: "Inter, system-ui, sans-serif",
        justifyContent: "center",
      }}
    >
      <div style={{ fontSize: 72, fontWeight: 800 }}>YTCreate V2</div>
    </AbsoluteFill>
  );
}

export function RemotionRoot() {
  return (
    <Composition
      id="PhaseZeroComposition"
      component={PhaseZeroComposition}
      durationInFrames={120}
      fps={30}
      width={1920}
      height={1080}
    />
  );
}

