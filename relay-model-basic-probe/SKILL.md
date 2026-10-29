---
name: relay-model-basic-probe
description: "Use when testing relay model availability."
---
# Relay basic-call testing

## User-approved scope and naming
- For newly supplied relay providers, test only the following retained model list unless the user explicitly changes scope. Do not expand to every advertised model.
- Retained models: GPT-6 Astra; GPT-6.1 Sol; Claude Opus 5.5; Claude Sonnet 5.5; Claude Haiku 5.5 (pending availability, not known usable); Claude Fable 5; Gemini 3.8 Flash; Gemini 3.5 Flash Lite; Gemini 3.7 Flash; Gemini 4 Argon; Claude Opus 5; Claude Sonnet 5; Claude Fable 5.1.
- Exclude DeepSeek, Grok and Claude Haiku 5 from this retained list.
- Confirm exact request IDs from each provider; Gemini 4 Argon uses `gemini-4-argon`. Fable 5.1 variants `claude-fable-5.1` and `claude-fable-5-1` require separate evidence and are not automatically interchangeable.
- When reporting relay providers to the user, use their English names/identifiers only (e.g. `beiluo`, `namax`, `yujian`, `timicc`, `78code`, `zhongy`); avoid Chinese name translations. Continue explanations in Chinese.

- Resolve only the active profile's config and .env; do not print credentials or modify another profile.
- Separate advertised catalogue membership from actual successful calls. Dot and hyphen IDs are distinct until independently verified.
- Test streaming and nonstreaming with a deterministic sentinel. HTTP 200 without expected content is not a pass.
- Persist each result to JSONL immediately; verify every planned route has a result before summarizing.
- Retry anomalies and independently repeat surprising successes. Connection/TLS errors do not establish model failure.
- Bound total request duration, not just httpx read timeout: SSE heartbeats can keep requests alive indefinitely. Recover partial JSONL after tool timeout without rerunning successful calls.
- Use uv --offline with cached dependencies when PyPI TLS fails.
- Report coverage precisely: one profile's custom_providers is not an all-site audit.
- Sentinel success proves only basic API availability, not model identity, quality, reliability, or tool/multimodal support.
- Use fresh primary-source docs for official names and IDs rather than recalled availability.
