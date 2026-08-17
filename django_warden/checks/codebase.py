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
                "The package 'codebase-memory-mcp' is not installed globally on the system.",
                hint=(
                    "The 'codebase-memory-mcp' is a global system MCP server that indexes your "
                    "codebase into a local knowledge graph, allowing AI agents to understand "
                    "structures and relationships between classes without wasting tokens.\n\n"
                    "Benefits of having codebase-memory-mcp in the system:\n"
                    "  - 🗺️ Knowledge Graph: Maps dependencies, classes, routes, and tables.\n"
                    "  - 🔎 Intelligent Search: Enables advanced, ultra-fast semantic searches.\n"
                    "  - 📉 Context Efficiency: Reduces token consumption and avoids redundant reads.\n\n"
                    "How to install globally:\n"
                    "  Run (Linux/macOS): curl -fsSL "
                    "https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh "
                    "| bash -s -- --ui\n"
                    "  Or via npm: npm install -g codebase-memory-mcp"
                ),
                id="warden.W004",
            )
        )
    else:
        checks_results.append(
            Info(
                "The package 'codebase-memory-mcp' is installed globally and ready for use!",
                hint=(
                    "To enable auto-indexing at your project root, run:\n"
                    "  codebase-memory-mcp config set auto_index true\n\n"
                    "To visualize the knowledge graph and explore its structure, run the UI:\n"
                    "  codebase-memory-mcp --ui=true --port=9749\n\n"
                    "This will provide highly precise graph-based semantic searches to your AI assistant."
                ),
                id="warden.I002",
            )
        )

    return checks_results
