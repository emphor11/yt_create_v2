import { readFile } from "node:fs/promises";

const appSource = await readFile(new URL("../src/App.tsx", import.meta.url), "utf8");
const homePageSource = await readFile(new URL("../src/pages/HomePage.tsx", import.meta.url), "utf8");
const htmlSource = await readFile(new URL("../index.html", import.meta.url), "utf8");

if (!appSource.includes("HomePage") || !homePageSource.includes("YTCreate V2")) {
  throw new Error("Frontend shell does not render the product name.");
}

if (!htmlSource.includes('<div id="root"></div>')) {
  throw new Error("Frontend HTML root element is missing.");
}

console.log("frontend smoke ok");
