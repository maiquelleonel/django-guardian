# 🛡️ django-guardian

Architectural watchdog, custom system checks, and AI safety guardrails for Django projects.

`django-guardian` ensures that human developers and AI coding agents (such as Claude Code, Cursor, and Gemini CLI) write clean, performant, and secure Django code. It combines static LLM instructions (the Guardian Skill) with dynamic, active Django system checks and Model Context Protocol (MCP) tooling.

## 🚀 Features

- **Active System Checks:** Detects missing database indexes on common search/lookup fields and dangerous infinite recursive signal save loops (Windmill loops) at startup.
- **Windmill Loop Protection:** Provides a `@prevent_windmill_loops` decorator to safely handle internal signals.
- **AI Skill Integration:** Comes pre-packaged with an AI System Prompt (`SKILL.md`) that teaches any AI agent how to write code according to "The Django Way."
- **First-Class MCP Integration:** Fully compatible with `django-ai-boost` (for framework introspection) and `codebase-memory-mcp` (for advanced codebase graph-based memory), enabling AI assistants to run architectural integrity audits instantly and perform high-precision semantic searches. You can visualize and navigate your project's codebase graph using the companion web UI [codebase-memory-mcp-ui](https://github.com/DeusData/codebase-memory-mcp-ui).

## 📦 Installation

```bash
pip install django-guardian
```

Then add `"django_guardian"` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django_guardian",
]
```

## 📜 License

MIT License.
