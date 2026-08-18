# 🛡️ django-warden

An opinionated AI skill, watchdog, and custom system checks framework to scale Django projects from zero to millions of users.

`django-warden` ensures that human developers and Gemini CLI assistants write clean, performant, and secure Django code. It combines static LLM instructions (the Warden Skill) with dynamic, active Django system checks and Model Context Protocol (MCP) tooling, embodying battle-tested industry guidelines.

## 🚀 Features

- **Example App:** Check out [gpurent](https://github.com/maiquelleonel/gpurent), a production-grade Django example project configured with `django-warden` demonstrating thin views, service layers, and zero-N+1 active auditing.
- **Active System Checks:** Detects missing database indexes on common search/lookup fields and dangerous infinite recursive signal save loops (Windmill loops) at startup.
- **Windmill Loop Protection:** Provides a `@prevent_windmill_loops` decorator to safely handle internal signals.
- **AI Skill Integration:** Comes pre-packaged with an AI System Prompt (`SKILL.md`) that teaches the Gemini CLI assistant how to write code according to "The Django Way."
- **First-Class MCP Integration:** Fully compatible with `django-ai-boost` (for framework introspection) and `codebase-memory-mcp` (for advanced codebase graph-based memory), enabling the Gemini CLI assistant to run architectural integrity audits instantly and perform high-precision semantic searches. You can visualize and navigate your project's codebase graph using the companion web UI [codebase-memory-mcp-ui](https://github.com/DeusData/codebase-memory-mcp-ui).

## 🧩 Opinionated Architecture Philosophy

`django-warden` is designed to guide a Django project from **day zero to millions of clients**, enforcing architectural boundaries that keep codebases decoupling-friendly, highly testable, and robust under scale:

- **Lean Models & Thin Views:** Views should only handle HTTP concerns. Models should only handle data structure and simple properties.
- **Services vs. Orchestrators (SOLID):**
  - `services/` contains pure, third-party API protocol wrappers (e.g. Stripe, WhatsApp API) with no local business logic.
  - `orchestrators/` (or `use_cases/`) houses multi-model business workflows, transactions, and complex state machines.
- **Anti-God Objects:** Actively prevents models and views from accumulating unrelated features, facilitating transition to DRF or Django Ninja seamlessly.
- **Proactive AI Consent:** Instructs AI assistants to collaborate through explicit interactive verification and gain developer approval before mutating code.

## 📦 Installation & Setup

1. Add `django-warden` to your project dependencies:

```bash
uv add django-warden
```

2. Add `"django_warden"` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django_warden",
]
```

3. Run the architectural audit:

```bash
python manage.py warden_audit
# or: uv run python manage.py warden_audit
```

✨ **Zero-Config AI Setup:** Running `warden_audit` (or starting the development server with `DEBUG = True`) automatically provisions the Warden Skill (`SKILL.md`) and configures the Model Context Protocol (MCP) integrations in both `.gemini/` and `.claude/` directories. On your next session with Gemini CLI, Claude Code, or compatible AI agents, the skill and tools will be immediately active and ready to enforce "The Django Way"!

## 🤖 Global Installation (Optional)

If you want the skill available globally across all your projects on your machine (without installing the package in each one), you can copy or download `SKILL.md` directly into your global agent folder:

```bash
# Global setup for Gemini CLI
mkdir -p ~/.gemini/skills/django-warden
curl -fsSL https://raw.githubusercontent.com/maiquelleonel/django-warden/master/SKILL.md -o ~/.gemini/skills/django-warden/SKILL.md

# Global setup for Claude Code
mkdir -p ~/.claude/skills/django-warden
curl -fsSL https://raw.githubusercontent.com/maiquelleonel/django-warden/master/SKILL.md -o ~/.claude/skills/django-warden/SKILL.md
```

Or if you have this repository cloned locally:

```bash
mkdir -p ~/.gemini/skills/django-warden && cp SKILL.md ~/.gemini/skills/django-warden/SKILL.md
```

## 📜 License

MIT License.
