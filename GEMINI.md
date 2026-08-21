# 🧬 GEMINI HARNESS & AI BOOTSTRAP DIRECTIVES

This file dictates initialization rules and boot directives for any Artificial Intelligence or Automated Agent operating in this repository. Its instructions have **absolute precedence** over any general workflow.

---

## 🚨 1. FIRST-TURN INITIALIZATION RULE (First-Turn Command Rule)

- **Action Number One (MANDATORY):** Upon starting this session, on your **FIRST conversational turn (First Turn)**, you MUST immediately execute the `read_file` tool to load and analyze the skill specification in `SKILL.md`.
- **No Premature Actions:** You are strictly PROHIBITED from proposing strategies, generating code, answering questions, or applying any modifications without having read `SKILL.md` completely.
- **🛡️ Mandatory Skill Validation (Django Guardian):**
  - You must verify if the skill is installed and active in this session (it must be activated on demand via `activate_skill` if installed).
  - **🔌 Mandatory MCP Server Validation:**
    - You MUST validate that tools from the `django-ai-boost` MCP (e.g., `list_apps`, `get_model_schema`) are loaded and ready in the assistant's execution environment.

---

## 🛡️ 2. QUALITY AND CODE COMPLIANCE CONTRACT (SLA Compliance)

When operating in this repository, align all code-writing and refactoring behaviors to the following established excellence standards:

- **100% Code Coverage SLA:** Any and all logical lines added or modified in the application must include corresponding unit tests to maintain high project test coverage.
- **McCabe Complexity < 10:** No standard business function may exceed a cyclomatic complexity of 10.
- **Event/Handler Delegation:** Heavy webhooks and dispatchers must be refactored using the Private Handler Delegation pattern, keeping the main event router's complexity extremely low (< 4).
- **No Hardcoded Prompts:** AI system prompts must live isolated in dedicated `.prompt` or markdown files and never embedded directly into Python files.
- **No-Storytelling Rule (Clean Comments):** Adding verbose or narrative comments about specifications or business decisions is strictly forbidden. Block comments (`#`) must not exceed **3 lines**, individual comment lines must not exceed **120 characters**, and redundant or obsolete explanatory jargon is actively rejected by the Harness.
- **Idempotent Indexing in Migrations:** Any operation involving database index creation must explicitly include the existence check/clause (e.g., `IF NOT EXISTS`), preventing accidental failures during sequential migration execution in development and production environments.

---

## ⚡ 3. INTEGRATION WITH DJANGO-AI-BOOST (MCP Server)

This project uses `django-ai-boost` as an MCP server to optimize the AI tools' context and introspection capabilities.

- **Dynamic Context Configuration:** The agent must automatically self-adjust and update local MCP Server configurations for the corresponding editor (e.g., inside the MCP configuration file), ensuring the designated settings module always points to the correct Django project module.
- **Active Code Validation:** The assistant must actively use the `run_check` tool provided by `django-ai-boost` to validate in real time whether any architectural rule from `SKILL.md` has been violated.

---

## 🛠️ 4. PROJECT COMMANDS (Justfile Automation)

The repository uses `Justfile` for development cycle automation and compliance verification:

- `just test`: Runs the test suite with `uv run tests/manage.py test tests -v 0`.
- `just lint`: Runs static lint checks with `uv run ruff check .`.
- `just fmt`: Formats code automatically with `uv run ruff format .`.
