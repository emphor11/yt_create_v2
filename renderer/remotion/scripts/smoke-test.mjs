import { readFile } from "node:fs/promises";

const rootSource = await readFile(new URL("../src/Root.tsx", import.meta.url), "utf8");
const indexSource = await readFile(new URL("../src/index.ts", import.meta.url), "utf8");

if (!rootSource.includes("Composition")) {
  throw new Error("Remotion root does not define a composition.");
}

if (!indexSource.includes("registerRoot")) {
  throw new Error("Remotion entrypoint does not register a root.");
}

console.log("renderer smoke ok");

