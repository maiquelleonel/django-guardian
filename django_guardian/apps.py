from django.apps import AppConfig


class DjangoGuardianConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_guardian"
    verbose_name = "Django Guardian"

    def ready(self):
        # Dynamically import and register all custom system checks on startup
        from django_guardian.checks import database, signals, ai_boost, codebase, best_practices  # noqa
