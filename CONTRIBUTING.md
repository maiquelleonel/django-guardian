# 🤝 Contributing to django-guardian

Thank you for your interest in contributing to **django-guardian**! We welcome contributions from human developers and AI assistants alike to help build the best architectural watchdog and AI safety framework for Django projects.

## 🛡️ Coding Standards & SLAs

To maintain the highest level of codebase quality, all contributions must strictly satisfy our project Service Level Agreements (SLAs):

1. **100% Code Coverage SLA:** Every single line of logical code added or modified must have corresponding unit tests. Your pull request will not be merged without complete test coverage.
2. **McCabe Cyclomatic Complexity < 10:** No business or validation function may exceed a McCabe complexity of 10. Keep your functions small, modular, and highly focused.
3. **No-Storytelling Rule (Clean Comments):** Avoid verbose, narrative-style comments. Single-line comments must not exceed 120 characters, and block comments (`#`) must not exceed 3 lines.
4. **Style & Quality:** All Python code must comply with our Ruff and Formatting configurations.

## 🚀 Development Workflow

To set up your local development environment:

1. **Clone the repository:**
   ```bash
   git clone git@github.com:maiquelleonel/django-guardian.git
   cd django-guardian
   ```
2. **Set up virtual environment using `uv`:**
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```
3. **Running the Quality Suite:**
   We use `just` to orchestrate our quality check pipeline:
   - Run linter: `just lint` (executes `ruff check .`)
   - Run formatter: `just fmt` (executes `ruff format .`)
   - Run test suite: `just test` (executes `uv run tests/manage.py test tests`)

Ensure both `just lint` and `just test` pass completely before submitting a pull request.
