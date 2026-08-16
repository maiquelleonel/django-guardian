# django-guardian commands
default:
    @just --list

# Run tests
test:
    uv run tests/manage.py test tests

# Run code styling check
lint:
    uv run ruff check .

# Run static type and formatting fix
fmt:
    uv run ruff format .
