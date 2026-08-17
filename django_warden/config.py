import os
import sys

from django.conf import settings

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        tomllib = None


def get_warden_config() -> dict:
    """
    Reads the [tool.django-warden] configuration from pyproject.toml in the current workspace.
    """
    config = {}
    base_dirs = []

    # Try BASE_DIR
    base_dir = getattr(settings, "BASE_DIR", None)
    if base_dir:
        base_dirs.append(base_dir)
        # Also check parent of BASE_DIR (common for project roots)
        base_dirs.append(os.path.dirname(base_dir))

    # Also check current working directory
    base_dirs.append(os.getcwd())

    for d in base_dirs:
        if d:
            pyproject_path = os.path.join(d, "pyproject.toml")
            if os.path.exists(pyproject_path):
                try:
                    if tomllib is not None:
                        with open(pyproject_path, "rb") as f:
                            data = tomllib.load(f)
                        return data.get("tool", {}).get("django-warden", {})
                except Exception:
                    pass
    return config


def should_silence_mcp_info() -> bool:
    """
    Determines if MCP success (Info) messages should be silenced.
    They are never silenced during `warden_audit` runs (detected via DJANGO_WARDEN_AUDIT_RUNNING env).
    Otherwise, defaults to True to keep standard runs clean.
    """
    # If we are explicitly auditing, never silence
    if os.environ.get("DJANGO_WARDEN_AUDIT_RUNNING") == "1":
        return False

    config = get_warden_config()
    # Let's default to True so the user gets clean startups by default.
    return config.get("silence_mcp_info", True)
