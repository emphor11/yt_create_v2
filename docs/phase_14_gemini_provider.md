# Phase 14 — Gemini Provider Integration

Phase 14 now has the first real LLM adapter.

The app can call Gemini for AI-mode `script_brief` when `GEMINI_API_KEY` is configured.

## Runtime Flow

```text
AI-mode run
-> PipelineService.run_script_brief()
-> ScriptBriefAIEngine
-> GeminiProvider
-> Gemini generateContent API
-> ScriptBrief model validation
-> ScriptBriefValidator
-> ArtifactStore
```

## Environment Variables

The backend automatically loads:

```text
backend/.env
```

The real `.env` file is ignored by git.

Use this committed example as the template:

```text
backend/.env.example
```

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash
```

`GEMINI_API_KEY` is preferred.

`GOOGLE_API_KEY` is also accepted as a fallback alias.

`GEMINI_MODEL` is optional.

If it is not set, the backend uses:

```text
gemini-3.5-flash
```

Do not commit API keys.

## Gemini Request Shape

`GeminiProvider` uses the official Gemini REST endpoint:

```text
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

The API key is sent through the `x-goog-api-key` header.

Structured JSON output is requested through:

```json
{
  "generationConfig": {
    "responseFormat": {
      "text": {
        "mimeType": "application/json",
        "schema": {}
      }
    }
  }
}
```

## ScriptBrief AI Boundary

Gemini does not write directly to the pipeline.

Gemini returns JSON.

That JSON must become a `ScriptBrief`.

Then `ScriptBriefValidator` decides whether it is valid.

## Failure Policy

Valid JSON shape but invalid business rules:

```text
blocked artifact
```

Malformed ScriptBrief shape:

```text
failed artifact
```

Provider/API error:

```text
failed artifact
```

## Not Implemented Yet

- `NarrativeArcAIEngine`
- `ScriptDraftAIEngine`
- frontend provider controls
- prompt inspector
- voice
- publishing
- OpenAI, Groq, or OpenRouter adapters

## Key Rule

All real LLM calls must go through provider adapters.

Routes and renderers must never call LLMs directly.
