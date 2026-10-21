export interface WordTimestamp {
  word: string;
  start_ms: number;
  end_ms: number;
}

/**
 * Speech Anchor Resolver.
 *
 * Automatically resolves a phrase anchor (e.g. "50 lakh", "rises to 10.5", "monthly EMI")
 * to the exact spoken frame using real word-level audio timestamps.
 */
function decodeHtmlEntities(str: string): string {
  return str
    .replace(/&#x27;/g, "'")
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
}

export function resolveAnchorFrame(
  words: { word: string; start_ms: number; end_ms: number }[],
  anchorPhrase: string,
  fps: number = 30,
  minStartMs: number = 0
): number {
  if (!anchorPhrase || !anchorPhrase.trim()) {
    throw new Error("Anchor phrase cannot be empty.");
  }

  const cleanAnchor = decodeHtmlEntities(anchorPhrase)
    .replace(/<[^>]+>/g, " ")
    .replace(/-/g, " ");
  const cleanTokens = cleanAnchor
    .toLowerCase()
    .replace(/[^\w\s\.]/g, "")
    .split(/\s+/)
    .filter(Boolean);

  if (cleanTokens.length === 0) {
    throw new Error(`Anchor phrase '${anchorPhrase}' contains no searchable speech tokens.`);
  }

  const tokenEntries: { token: string; start_ms: number }[] = [];
  for (const w of words) {
    const wRaw = String(w.word || "");
    const wDecoded = decodeHtmlEntities(wRaw);
    const wStripped = wDecoded.replace(/<[^>]+>/g, " ");
    const wClean = wStripped.replace(/-/g, " ");
    const parts = wClean
      .toLowerCase()
      .replace(/[^\w\s\.]/g, "")
      .split(/\s+/)
      .filter(Boolean);
    for (const p of parts) {
      if (p && !p.startsWith("break") && !p.startsWith("pause")) {
        tokenEntries.push({ token: p, start_ms: w.start_ms });
      }
    }
  }

  const numTokens = cleanTokens.length;
  for (let i = 0; i <= tokenEntries.length - numTokens; i++) {
    if (tokenEntries[i].start_ms < minStartMs) {
      continue;
    }
    let match = true;
    for (let j = 0; j < numTokens; j++) {
      if (tokenEntries[i + j].token !== cleanTokens[j]) {
        match = false;
        break;
      }
    }
    if (match) {
      return Math.round((tokenEntries[i].start_ms / 1000) * fps);
    }
  }

  throw new Error(
    `Exact anchor phrase '${anchorPhrase}' could not be resolved to any contiguous spoken word timestamp.`
  );
}

