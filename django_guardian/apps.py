import os
import shutil

from django.apps import AppConfig


class DjangoGuardianConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_guardian"
    verbose_name = "Django Guardian"

    def ready(self):
        # Automagic AI Skill bootstrapping in local workspace
        # This completely eliminates any installation friction for the developer.
        # When Django boots, we automatically copy the packaged SKILL.md directly
        # into the project's local workspace (.gemini/skills/django-guardian/SKILL.md)
        # so their AI assistants (and any subagents) instantly gain all guidelines.
        try:
            project_root = os.getcwd()
            local_skills_dir = os.path.join(project_root, ".gemini", "skills", "django-guardian")
            local_skill_file = os.path.join(local_skills_dir, "SKILL.md")

            current_dir = os.path.dirname(os.path.abspath(__file__))
            source_skill_file = os.path.join(current_dir, "skills", "SKILL.md")

            if os.path.exists(source_skill_file):
                os.makedirs(local_skills_dir, exist_ok=True)
                shutil.copy2(source_skill_file, local_skill_file)
        except Exception:
            pass

        # Dynamically import and register all custom system checks on startup
        from django_guardian.checks import database, signals, ai_boost, codebase, best_practices  # noqa
