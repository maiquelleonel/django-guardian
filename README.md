# 🛡️ django-guardian

An opinionated AI skill, watchdog, and custom system checks framework to scale Django projects from zero to millions of users.

`django-guardian` ensures that human developers and AI coding agents (such as Claude Code, Cursor, and Gemini CLI) write clean, performant, and secure Django code. It combines static LLM instructions (the Guardian Skill) with dynamic, active Django system checks and Model Context Protocol (MCP) tooling, embodying battle-tested industry guidelines.

## 🚀 Features

- **Active System Checks:** Detects missing database indexes on common search/lookup fields and dangerous infinite recursive signal save loops (Windmill loops) at startup.
- **Windmill Loop Protection:** Provides a `@prevent_windmill_loops` decorator to safely handle internal signals.
- **AI Skill Integration:** Comes pre-packaged with an AI System Prompt (`SKILL.md`) that teaches any AI agent how to write code according to "The Django Way."
- **First-Class MCP Integration:** Fully compatible with `django-ai-boost` (for framework introspection) and `codebase-memory-mcp` (for advanced codebase graph-based memory), enabling AI assistants to run architectural integrity audits instantly and perform high-precision semantic searches. You can visualize and navigate your project's codebase graph using the companion web UI [codebase-memory-mcp-ui](https://github.com/DeusData/codebase-memory-mcp-ui).

## 🧩 Opinionated Architecture Philosophy

`django-guardian` is designed to guide a Django project from **day zero to millions of clients**, enforcing architectural boundaries that keep codebases decoupling-friendly, highly testable, and robust under scale:

- **Lean Models & Thin Views:** Views should only handle HTTP concerns. Models should only handle data structure and simple properties.
- **Services vs. Orchestrators (SOLID):**
  - `services/` contains pure, third-party API protocol wrappers (e.g. Stripe, WhatsApp API) with no local business logic.
  - `orchestrators/` (or `use_cases/`) houses multi-model business workflows, transactions, and complex state machines.
- **Anti-God Objects:** Actively prevents models and views from accumulating unrelated features, facilitating transition to DRF or Django Ninja seamlessly.
- **Proactive AI Consent:** Instructs AI assistants to collaborate through explicit interactive verification and gain developer approval before mutating code.

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

## 🤖 How to Load the AI Skill (AI Assistants Setup)

To make AI assistants (such as Gemini CLI, Claude, Cursor, and Windsurf) strictly follow the `django-guardian` architectural guidelines, you should load the root-level `SKILL.md` file into their context before coding:

### 1. For Gemini CLI (Global or Workspace Skill)
Install the expert skill directly from this repository using the native CLI command:
```bash
# Install globally for all your projects
bunx @google/gemini-cli skills install git@github.com:maiquelleonel/django-guardian.git --consent

# Or install locally for the current project workspace only
bunx @google/gemini-cli skills install git@github.com:maiquelleonel/django-guardian.git --scope workspace --consent
```

### 2. For Cursor & Windsurf (`.cursorrules` / `.windsurfrules`)
To enforce these rules inside Cursor or Windsurf, download or copy the root-level `SKILL.md` file to `.cursorrules` in your project root:
```bash
curl -fsSL https://raw.githubusercontent.com/maiquelleonel/django-guardian/master/SKILL.md -o .cursorrules
```

### 3. For Claude Desktop / Custom MCP Clients
Configure your Claude Desktop configuration file (`config.json`) to run the MCP server with the settings pointed to your project, so that Claude has full, real-time framework introspection as described in the skill file.

## 📜 License

MIT License.
