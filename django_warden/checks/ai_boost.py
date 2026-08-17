import os

from django.core.checks import Info, Warning, register

from django_warden.config import should_silence_mcp_info


@register()
def check_django_ai_boost_installed(app_configs, **kwargs):
    """
    Checks if 'django-ai-boost' is installed in the current environment.
    If not, returns a Warning with details on installation benefits and instructions.
    If installed, returns an Info check showing how to run it for the current project.
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

    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "tests.settings")

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
                    hint=(
                        f"To connect your AI assistant to this Django project, run:\n"
                        f"  django-ai-boost --settings {settings_module}\n\n"
                        f"Or add this configuration to your MCP client (e.g., Claude Desktop):\n"
                        f"{{\n"
                        f'  "mcpServers": {{\n'
                        f'    "django-warden": {{\n'
                        f'      "command": "django-ai-boost",\n'
                        f'      "args": ["--settings", "{settings_module}"]\n'
                        f"    }}\n"
                        f"  }}\n"
                        f"}}"
                    ),
                    id="warden.I001",
                )
            )

    return checks_results
