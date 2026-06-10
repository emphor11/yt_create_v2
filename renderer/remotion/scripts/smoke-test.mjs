import { readFile } from "node:fs/promises";

const rootSource = await readFile(new URL("../src/Root.tsx", import.meta.url), "utf8");
const indexSource = await readFile(new URL("../src/index.ts", import.meta.url), "utf8");
const splitComparisonSource = await readFile(
  new URL("../src/SplitComparison.tsx", import.meta.url),
  "utf8"
);
const renderScriptSource = await readFile(
  new URL("./render-spec.mjs", import.meta.url),
  "utf8"
);

if (!rootSource.includes("SplitComparison")) {
  throw new Error("Remotion root does not define SplitComparison.");
}

if (!indexSource.includes("registerRoot")) {
  throw new Error("Remotion entrypoint does not register a root.");
}

if (!splitComparisonSource.includes("frame_spans")) {
  throw new Error("SplitComparison does not consume render frame spans.");
}

if (!renderScriptSource.includes("renderMedia")) {
  throw new Error("Render script does not call Remotion renderMedia.");
}

console.log("renderer smoke ok");
