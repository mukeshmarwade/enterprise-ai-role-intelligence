import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_URL = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'role_intelligence.db')}"
)

SEED_FILE = os.path.join(BASE_DIR, "data", "roles_seed.json")

# Optional: set ANTHROPIC_API_KEY to enable LLM-generated narrative summaries.
# Without it, the app falls back to deterministic, template-based narratives
# (this is the "AI vs traditional logic boundary" decision described in the brief:
# structured predictions = rule engine, narrative generation = optional LLM).
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-5")
