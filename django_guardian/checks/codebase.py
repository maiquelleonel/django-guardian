import shutil

from django.core.checks import Info, Warning, register


@register()
def check_codebase_memory_installed(app_configs, **kwargs):
    """
    Checks if 'codebase-memory-mcp' is installed in the current environment or system path.
    If not, returns a Warning with details on installation benefits and instructions.
    If installed, returns an Info check showing how to run it.
    """
    checks_results = []

    # Check via shutil.which first, then try importlib metadata distribution
    codebase_memory_installed = False
    if shutil.which("codebase-memory-mcp") is not None:
        codebase_memory_installed = True
    else:
        try:
            import importlib.metadata

            importlib.metadata.distribution("codebase-memory-mcp")
            codebase_memory_installed = True
        except importlib.metadata.PackageNotFoundError:
            pass

    if not codebase_memory_installed:
        checks_results.append(
            Warning(
                "O pacote 'codebase-memory-mcp' não está instalado no sistema.",
                hint=(
                    "O 'codebase-memory-mcp' é um servidor MCP que indexa o seu código em "
                    "um grafo de conhecimento local, permitindo que agentes de IA compreendam "
                    "estruturas e relacionamentos entre classes sem desperdiçar tokens.\n\n"
                    "Ganhos de ter o codebase-memory-mcp no sistema:\n"
                    "  - 🗺️ Grafo de Conhecimento: Mapeia dependências, classes, rotas e tabelas.\n"
                    "  - 🔎 Buscas Inteligentes: Permite buscas semânticas avançadas ultra-rápidas.\n"
                    "  - 📉 Eficiência de Contexto: Reduz o consumo de tokens e evita leituras redundantes.\n\n"
                    "Como instalar:\n"
                    "  Execute (Linux/macOS): curl -fsSL "
                    "https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash\n"
                    "  Ou via pip: pip install codebase-memory-mcp\n"
                    "  Ou via npm: npm install -g codebase-memory-mcp\n\n"
                    "Visualize o grafo de conhecimento e explore sua estrutura usando a interface web:\n"
                    "  Interface UI: https://github.com/DeusData/codebase-memory-mcp-ui"
                ),
                id="guardian.W004",
            )
        )
    else:
        checks_results.append(
            Info(
                "O pacote 'codebase-memory-mcp' está instalado e pronto para uso!",
                hint=(
                    "Para indexar este repositório no grafo de conhecimento local do MCP, execute:\n"
                    "  codebase-memory-mcp index .\n\n"
                    "Visualize o grafo de conhecimento e explore sua estrutura usando a interface web:\n"
                    "  Interface UI: https://github.com/DeusData/codebase-memory-mcp-ui\n\n"
                    "Isso fornecerá buscas semânticas por grafos altamente precisas ao seu assistente de IA."
                ),
                id="guardian.I002",
            )
        )

    return checks_results
