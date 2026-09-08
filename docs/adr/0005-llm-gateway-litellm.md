# ADR-0005: LLM gateway — LiteLLM proxy

- **Status:** Accepted (2026-08-31)
- **Deciders:** @MuhammadSeyam (project lead and AI/ML lead), @0Abanoub
  (Backend & Platform lead), and @hishamabdo0100 (DevOps lead)

## Context

OpenLearn AI needs provider-independent access to language models for RAG,
concept extraction, and generation. Provider SDKs differ in authentication,
model naming, retry behavior, and observability. The project also needs a
predictable local development path when cloud providers are unavailable or
rate-limited.

The execution plan resolves the provider conflict by using a gateway as the
implementation of the PAL `ReasoningInterface`.

## Decision

Use the **LiteLLM proxy** as the LLM gateway.

Production providers are OpenAI, Anthropic, and GLM through LiteLLM. Local
development and demos use Ollama with Qwen 2.5. The PAL priority chain may
fall back from cloud providers to the local provider on rate limits or
provider unavailability.

Applications call the PAL interface rather than provider-specific SDKs.
Provider credentials, routing, retries, key rotation, and cost tracking are
configured at the gateway and deployment layer.

## Consequences

- Provider changes and fallback routing do not require application-wide SDK
  changes.
- Pod B defines model and evaluation needs; Pod D owns gateway deployment,
  secret handling, and observability; Pod A consumes the PAL interface.
- The Week 7 deployment must use the LiteLLM proxy image, default port 4000,
  at least two cloud-provider configurations, key rotation, and a
  cost-tracking endpoint.
- LiteLLM adds configuration and operational work that must be maintained as
  part of the deployment stack.

## Alternatives considered

- **Direct provider SDKs:** simpler initially, but couple application code to
  individual providers and duplicate routing and fallback logic.
- **Local-only Ollama:** useful for development, but insufficient as the sole
  production path.
- **A custom gateway:** would duplicate mature LiteLLM capabilities without a
  demonstrated project-specific need.
