import os
import sys

from django.apps import AppConfig
from django.conf import settings


class DjangoWardenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_warden"
    verbose_name = "Django Warden"

    def ready(self):
        # Dynamically import and register all custom system checks on startup
        from django_warden.checks import database, signals, ai_boost, codebase, best_practices  # noqa

        # Auto-bootstrap AI instruction files in local development mode
        if getattr(settings, "DEBUG", False):
            # Do not run during test execution to prevent test pollution
            if "test" not in sys.argv:
                try:
                    from django_warden.ai_builder import ensure_ai_structure

                    base_dir = getattr(settings, "BASE_DIR", None)
                    if base_dir:
                        # Determine project name and settings module dynamically
                        wsgi_app = getattr(settings, "WSGI_APPLICATION", None)
                        project_name = wsgi_app.split(".")[0] if wsgi_app else os.path.basename(base_dir)
                        settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings")

                        context = {
                            "project_name": project_name,
                            "settings_module": settings_module,
                        }

                        target_dirs, skill_created, settings_created = ensure_ai_structure(base_dir, context)

                        # Output elegant feedback to the developer console on first-time setup
                        if skill_created or settings_created:
                            dirs_str = ", ".join(f"'{d}/'" for d in target_dirs)
                            print(
                                f"\n✨ [Warden] AI Bootstrapper: Successfully configured rules in {dirs_str} "
                                f"and integrated MCP servers in 'settings.json'!"
                            )
                except Exception:
                    pass
