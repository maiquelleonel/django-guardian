# 🛡️ django-guardian

An opinionated AI skill, watchdog, and custom system checks framework to scale Django projects from zero to millions of users.

`django-guardian` ensures that human developers and Gemini CLI assistants write clean, performant, and secure Django code. It combines static LLM instructions (the Guardian Skill) with dynamic, active Django system checks and Model Context Protocol (MCP) tooling, embodying battle-tested industry guidelines.

## 🚀 Features

- **Active System Checks:** Detects missing database indexes on common search/lookup fields and dangerous infinite recursive signal save loops (Windmill loops) at startup.
- **Windmill Loop Protection:** Provides a `@prevent_windmill_loops` decorator to safely handle internal signals.
- **AI Skill Integration:** Comes pre-packaged with an AI System Prompt (`SKILL.md`) that teaches the Gemini CLI assistant how to write code according to "The Django Way."
- **First-Class MCP Integration:** Fully compatible with `django-ai-boost` (for framework introspection) and `codebase-memory-mcp` (for advanced codebase graph-based memory), enabling the Gemini CLI assistant to run architectural integrity audits instantly and perform high-precision semantic searches. You can visualize and navigate your project's codebase graph using the companion web UI [codebase-memory-mcp-ui](https://github.com/DeusData/codebase-memory-mcp-ui).

## 🧩 Opinionated Architecture Philosophy

`django-guardian` is designed to guide a Django project from **day zero to millions of clients**, enforcing architectural boundaries that keep codebases decoupling-friendly, highly testable, and robust under scale:

- **Lean Models & Thin Views:** Views should only handle HTTP concerns. Models should only handle data structure and simple properties.
- **Services vs. Orchestrators (SOLID):**
  - `services/` contains pure, third-party API protocol wrappers (e.g. Stripe, WhatsApp API) with no local business logic.
  - `orchestrators/` (or `use_cases/`) houses multi-model business workflows, transactions, and complex state machines.
- **Anti-God Objects:** Actively prevents models and views from accumulating unrelated features, facilitating transition to DRF or Django Ninja seamlessly.
- **Proactive AI Consent:** Instructs AI assistants to collaborate through explicit interactive verification and gain developer approval before mutating code.

## 📦 Installation

To install the custom system checks linter package:

```bash
uv add django-guardian
```

Then add `"django_guardian"` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django_guardian",
]
```

## 🤖 How to Load the AI Skill (Gemini CLI Setup)

To make the Gemini CLI assistant strictly follow the `django-guardian` architectural guidelines, load the root-level `SKILL.md` file into its context before coding using the native CLI command:

```bash
# Install globally for all your projects
bunx @google/gemini-cli skills install git@github.com:maiquelleonel/django-guardian.git --consent

# Or install locally for the current project workspace only
bunx @google/gemini-cli skills install git@github.com:maiquelleonel/django-guardian.git --scope workspace --consent
```

## 📜 License

MIT License.
