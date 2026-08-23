"""
Optional LLM layer used ONLY for narrative polish / free-text Q&A
(e.g. "Which five roles are likely to change the most, and why?").

Design principle from the brief: reduce unnecessary LLM calls.
- Structured predictions (automation %, reason codes) never call an LLM — see scoring.py.
- This module is called only for open-ended narrative questions, and only if
  ANTHROPIC_API_KEY is configured. Otherwise it degrades gracefully to a
  deterministic summary built from the same structured data (fallback strategy
  for "external AI service unavailable").
"""
import json
from backend import config


def is_enabled() -> bool:
    return bool(config.ANTHROPIC_API_KEY)


def generate_narrative(prompt: str, context: dict) -> str:
    if not is_enabled():
        return _fallback_narrative(context)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        system = (
            "You are an enterprise workforce-AI analyst. Answer using ONLY the "
            "structured role data provided in the context JSON. Be concise, "
            "cite concrete automation/augmentation percentages, and never invent "
            "figures not present in the context."
        )
        msg = client.messages.create(
            model=config.LLM_MODEL,
            max_tokens=600,
            system=system,
            messages=[{
                "role": "user",
                "content": f"Context:\n{json.dumps(context, indent=2)}\n\nQuestion: {prompt}"
            }],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    except Exception as e:
        # Graceful degradation, per the brief's "external AI service unavailable" requirement
        return _fallback_narrative(context) + f"\n\n(Note: LLM narrative unavailable — {e})"


def _fallback_narrative(context: dict) -> str:
    """Rule-based fallback so the app is fully usable with zero API keys configured."""
    if "roles" in context and isinstance(context["roles"], list) and len(context["roles"]) >= 2:
        lines = []
        for r in context["roles"]:
            lines.append(
                f"- {r.get('title')}: {r.get('automation_pct')}% automated, "
                f"{r.get('augmentation_pct')}% augmented (confidence: {r.get('confidence')})."
            )
        return "Baseline comparison (structured, non-LLM summary):\n" + "\n".join(lines)
    return "Baseline analysis unavailable in fallback mode — showing structured data only."
