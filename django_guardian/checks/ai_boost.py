import os

from django.core.checks import Info, Warning, register


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
        if importlib.util.find_spec("django_ai_boost") is not None:
            ai_boost_installed = True

    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "tests.settings")

    if not ai_boost_installed:
        checks_results.append(
            Warning(
                "O pacote 'django-ai-boost' não está instalado no ambiente.",
                hint=(
                    "O 'django-ai-boost' é um servidor MCP (Model Context Protocol) essencial "
                    "para que assistentes de IA (como Gemini CLI, Claude, Cursor) possam ler, "
                    "compreender e interagir com seu projeto Django de forma inteligente e segura.\n\n"
                    "Ganhos de ter o django-ai-boost no sistema:\n"
                    "  - 🚀 Visibilidade de alto nível: Permite à IA inspecionar models, URLs e configurações.\n"
                    "  - ⚡ Prevenção de N+1: Ajuda a IA a sugerir queries otimizadas no ORM.\n"
                    "  - 🛠️ Validação ativa: Dá suporte ao comando 'run_check' para "
                    "auditar conformidade SLA em tempo real.\n\n"
                    "Como instalar:\n"
                    "  Execute: pip install django-ai-boost\n"
                    "  Ou usando uv: uv pip install django-ai-boost\n"
                    "  No ambiente de dev local: uv pip install -e '.[dev]'"
                ),
                id="guardian.W003",
            )
        )
    else:
        checks_results.append(
            Info(
                "O pacote 'django-ai-boost' está instalado e pronto para uso!",
                hint=(
                    f"Para conectar seu assistente de IA a este projeto Django, execute:\n"
                    f"  django-ai-boost --settings {settings_module}\n\n"
                    f"Ou adicione esta configuração ao seu cliente MCP (ex: Claude Desktop):\n"
                    f"{{\n"
                    f'  "mcpServers": {{\n'
                    f'    "django-guardian": {{\n'
                    f'      "command": "django-ai-boost",\n'
                    f'      "args": ["--settings", "{settings_module}"]\n'
                    f"    }}\n"
                    f"  }}\n"
                    f"}}"
                ),
                id="guardian.I001",
            )
        )

    return checks_results
