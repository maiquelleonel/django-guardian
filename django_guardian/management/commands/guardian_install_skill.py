import os
import shutil

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Installs the django-guardian expert AI Skill into the user's global Gemini CLI skills folder."

    def handle(self, *args, **options):
        self.stdout.write("Sincronizando a Skill global do django-guardian...")

        # Path to our pre-packaged SKILL.md
        current_dir = os.path.dirname(os.path.abspath(__file__))
        package_skills_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "skills"))
        source_skill_file = os.path.join(package_skills_dir, "SKILL.md")

        if not os.path.exists(source_skill_file):
            self.stdout.write(self.style.ERROR(f"Error: Source skill file not found at {source_skill_file}"))
            return

        # Target directory in user's home folder
        home_dir = os.path.expanduser("~")
        target_skills_dir = os.path.join(home_dir, ".gemini", "skills", "django-guardian")
        target_skill_file = os.path.join(target_skills_dir, "SKILL.md")

        # Create target directories if missing
        os.makedirs(target_skills_dir, exist_ok=True)

        try:
            shutil.copy2(source_skill_file, target_skill_file)
            self.stdout.write(self.style.SUCCESS(f"✔ Expert AI Skill successfully installed to: {target_skill_file}"))
            self.stdout.write(
                self.style.SUCCESS("All subagents and future sessions will now automatically inherit these guidelines!")
            )
        except OSError as e:
            self.stdout.write(self.style.ERROR(f"Failed to copy skill file: {e}"))
