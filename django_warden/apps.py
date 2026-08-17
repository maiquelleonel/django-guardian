from django.apps import AppConfig


class DjangoWardenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_warden"
    verbose_name = "Django Warden"

    def ready(self):
        # Dynamically import and register all custom system checks on startup
        from django_warden.checks import database, signals, ai_boost, codebase, best_practices  # noqa
