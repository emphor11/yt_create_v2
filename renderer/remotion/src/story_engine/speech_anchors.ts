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
export function resolveAnchorFrame(
  words: { word: string; start_ms: number; end_ms: number }[],
  anchorPhrase: string,
  fps: number = 30
): number {
  const cleanTokens = anchorPhrase
    .toLowerCase()
    .replace(/[^\w\s\.]/g, "")
    .split(/\s+/)
    .filter(Boolean);

  if (cleanTokens.length === 0) return 0;

  for (let i = 0; i <= words.length - cleanTokens.length; i++) {
    let match = true;
    for (let j = 0; j < cleanTokens.length; j++) {
      const w = words[i + j].word.toLowerCase().replace(/[^\w\s\.]/g, "");
      if (w !== cleanTokens[j] && !w.includes(cleanTokens[j])) {
        match = false;
        break;
      }
    }
    if (match) {
      return Math.round((words[i].start_ms / 1000) * fps);
    }
  }

  // Fallback: look for first token
  const first = cleanTokens[0];
  const idx = words.findIndex((w) => {
    const cleanW = w.word.toLowerCase().replace(/[^\w\s\.]/g, "");
    return cleanW === first || cleanW.includes(first);
  });
  if (idx !== -1) {
    return Math.round((words[idx].start_ms / 1000) * fps);
  }

  return 0;
}
