import os

from django.conf import settings
from django.core.checks import Info, Warning, register

from django_warden.config import should_silence_mcp_info


@register()
def check_django_ai_boost_installed(app_configs, **kwargs):
    """
    Checks if 'django-ai-boost' is installed in the current environment.
    If not, returns a Warning with details on installation benefits and instructions.
    If installed, returns an Info check showing success.
    """
    checks_results = []

    # Try finding the package via importlib metadata or direct spec finding
    ai_boost_installed = False
    try:
        import importlib.metadata

        importlib.metadata.distribution("django-ai-boost")
        ai_boost_installed = True
    except importlib.metadata.PackageNotFoundError:
        import importlib.util

        if importlib.util.find_spec("django_ai_boost") is not None:
            ai_boost_installed = True

    if not ai_boost_installed:
        checks_results.append(
            Warning(
                "The package 'django-ai-boost' is not installed in the environment.",
                hint=(
                    "The 'django-ai-boost' is an essential MCP (Model Context Protocol) server "
                    "allowing AI assistants (such as Gemini CLI, Claude, Cursor) to read, "
                    "understand, and interact with your Django codebase intelligently and safely.\n\n"
                    "Benefits of having django-ai-boost in the system:\n"
                    "  - 🚀 High-level visibility: Allows the AI to inspect models, URLs, and settings.\n"
                    "  - ⚡ N+1 Prevention: Helps the AI suggest optimized ORM queries.\n"
                    "  - 🛠️ Active validation: Supports the 'run_check' tool to audit SLA compliance in real-time.\n\n"
                    "How to install:\n"
                    "  Run: pip install django-ai-boost\n"
                    "  Or using uv: uv pip install django-ai-boost\n"
                    "  For local development: uv pip install -e '.[dev]'"
                ),
                id="warden.W003",
            )
        )
    else:
        if not should_silence_mcp_info():
            checks_results.append(
                Info(
                    "The package 'django-ai-boost' is installed and ready for use!",
                    id="warden.I001",
                )
            )

    return checks_results


@register()
def check_ai_bootstrap_integrity(app_configs, **kwargs):
    """
    Checks that AI instructions (SKILL.md) and MCP configurations (settings.json)
    are present and up-to-date across all detected AI assistant environments.
    In development mode (DEBUG=True), automatically provisions missing configurations.
    """
    checks_results = []
    base_dir = getattr(settings, "BASE_DIR", None)
    if not base_dir:
        return checks_results

    from django_warden.ai_builder import _get_target_directories, ensure_ai_structure

    base_dir = str(base_dir)
    target_dirs = _get_target_directories(base_dir, create_defaults_if_empty=False)

    if not target_dirs:
        return checks_results

    missing_targets = []
    for d in target_dirs:
        skill_file = os.path.join(base_dir, d, "skills", "django-warden", "SKILL.md")
        settings_file = os.path.join(base_dir, d, "settings.json")
        if not os.path.exists(skill_file) or not os.path.exists(settings_file):
            missing_targets.append(d)

    # In local development mode, auto-bootstrap missing targets
    if missing_targets and getattr(settings, "DEBUG", False):
        wsgi_app = getattr(settings, "WSGI_APPLICATION", None)
        project_name = wsgi_app.split(".")[0] if wsgi_app else os.path.basename(base_dir)
        settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings")
        context = {
            "project_name": project_name,
            "settings_module": settings_module,
        }
        ensure_ai_structure(base_dir, context)
        missing_targets = [
            d
            for d in target_dirs
            if not os.path.exists(os.path.join(base_dir, d, "skills", "django-warden", "SKILL.md"))
        ]

    if missing_targets:
        targets_str = ", ".join(missing_targets)
        checks_results.append(
            Warning(
                f"Missing AI skill or MCP server settings in detected directories: {targets_str}",
                hint="Run 'python manage.py warden_audit' or enable DEBUG=True to auto-bootstrap AI rules.",
                id="warden.W016",
            )
        )
    else:
        if not should_silence_mcp_info():
            targets_str = ", ".join(target_dirs)
            checks_results.append(
                Info(
                    f"AI skill and MCP configurations are properly synchronized in: {targets_str}",
                    id="warden.I003",
                )
            )

    return checks_results
