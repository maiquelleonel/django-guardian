import os
import re

from django.apps import apps
from django.conf import settings
from django.core.checks import run_checks
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs a comprehensive, opinionated architectural and security audit of the Django project."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== 🛡️ DJANGO GUARDIAN ARCHITECTURAL AUDIT ==="))
        self.stdout.write("Running deep analysis on settings, models, views, middlewares, and signals...\n")

        warnings_count = 0
        infos_count = 0

        # 1. Run Django System Checks under the hood (specifically our custom ones)
        self.stdout.write(self.style.MIGRATE_LABEL("--- [1/5] Running System Integrity Checks ---"))
        system_checks_issues = run_checks()
        guardian_issues = [issue for issue in system_checks_issues if getattr(issue, "id", "").startswith("guardian.")]

        if not guardian_issues:
            self.stdout.write(self.style.SUCCESS("  ✔ All system integrity checks passed successfully!"))
        else:
            for issue in guardian_issues:
                if issue.level >= 30:  # WARNING or higher
                    warnings_count += 1
                    self.stdout.write(self.style.WARNING(f"  ⚠ [{issue.id}] {issue.msg}"))
                    self.stdout.write(f"    Hint: {issue.hint}\n")
                else:
                    infos_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  ℹ [{issue.id}] {issue.msg}"))
                    self.stdout.write(f"    Hint: {issue.hint}\n")

        # 2. Audit Settings (Security & Env Discipline)
        self.stdout.write(self.style.MIGRATE_LABEL("\n--- [2/5] Auditing Production Readiness & Settings ---"))
        if settings.DEBUG:
            infos_count += 1
            self.stdout.write(self.style.WARNING("  ⚠ DEBUG is set to True."))
            self.stdout.write("    Hint: Ensure DEBUG = False in production settings to avoid leaks.\n")
        else:
            self.stdout.write(self.style.SUCCESS("  ✔ DEBUG is set to False (Production Mode)."))

        # Check for session security settings
        session_secure = getattr(settings, "SESSION_COOKIE_SECURE", False)
        csrf_secure = getattr(settings, "CSRF_COOKIE_SECURE", False)
        if not session_secure or not csrf_secure:
            warnings_count += 1
            self.stdout.write(self.style.WARNING("  ⚠ Session or CSRF cookies are not secured."))
            self.stdout.write(
                "    Hint: Set SESSION_COOKIE_SECURE = True and CSRF_COOKIE_SECURE = True in production.\n"
            )
        else:
            self.stdout.write(self.style.SUCCESS("  ✔ Session and CSRF cookies are properly secured."))

        # 3. Audit Middlewares (Fat Middleware Check)
        self.stdout.write(self.style.MIGRATE_LABEL("\n--- [3/5] Auditing Middlewares (Performance Guards) ---"))
        middlewares = getattr(settings, "MIDDLEWARE", [])
        custom_middlewares = [mw for mw in middlewares if not mw.startswith("django.")]
        if len(custom_middlewares) > 5:
            warnings_count += 1
            self.stdout.write(
                self.style.WARNING(f"  ⚠ High number of custom middlewares detected ({len(custom_middlewares)}).")
            )
            self.stdout.write(
                "    Hint: High number of middlewares adds linear latency to every request. "
                "Ensure they do not perform synchronous database queries or block threads.\n"
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"  ✔ Healthy middleware stack ({len(custom_middlewares)} custom middlewares).")
            )

        # 4. Audit Views & Services Boundary
        self.stdout.write(self.style.MIGRATE_LABEL("\n--- [4/5] Auditing Views & Architectural Boundaries ---"))
        views_warnings = self.audit_views_for_service_boundary()
        if not views_warnings:
            self.stdout.write(self.style.SUCCESS("  ✔ Views comply with the Service Layer & Lean View boundaries!"))
        else:
            for vw in views_warnings:
                warnings_count += 1
                self.stdout.write(self.style.WARNING(f"  ⚠ {vw['msg']}"))
                self.stdout.write(f"    Hint: {vw['hint']}\n")

        # 5. Summary Report
        self.stdout.write(self.style.MIGRATE_LABEL("\n=== ARCHITECTURAL AUDIT SUMMARY ==="))
        if warnings_count == 0:
            self.stdout.write(self.style.SUCCESS(f"🏆 Perfect score! 0 Warnings, {infos_count} Info messages."))
            self.stdout.write(self.style.SUCCESS("Your project strictly follows 'The Django Way'! Excellent job."))
        else:
            compliance_rate = max(0, 100 - (warnings_count * 15))
            self.stdout.write(
                self.style.WARNING(f"Audit completed with {warnings_count} Warnings and {infos_count} Info messages.")
            )
            self.stdout.write(self.style.WARNING(f"Estimated Architectural Compliance Rate: {compliance_rate}%"))
            self.stdout.write("Apply the hints above to scale your application seamlessly to millions of clients.")

    def audit_views_for_service_boundary(self):
        """
        Scans views files to detect if they are performing direct complex database
        writes or business logic instead of delegating to Services/Orchestrators.
        """
        views_warnings = []
        # Find local apps
        local_apps = [
            app_config
            for app_config in apps.get_app_configs()
            if not app_config.name.startswith("django.contrib") and "site-packages" not in app_config.path
        ]

        save_regex = re.compile(r"\.save\s*\(")

        for app_config in local_apps:
            for root, _, files in os.walk(app_config.path):
                for file in files:
                    if file == "views.py" or (file.endswith(".py") and "views" in root):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                        except (OSError, UnicodeDecodeError):
                            continue

                        # If a view file performs more than 3 .save() calls, it might have heavy business logic
                        saves = save_regex.findall(content)
                        if len(saves) > 3:
                            views_warnings.append(
                                {
                                    "msg": (
                                        f"Possible heavy business logic in "
                                        f"'{app_config.name}/{file}' "
                                        f"({len(saves)} `.save()` calls)."
                                    ),
                                    "hint": (
                                        "Views should only handle serialization/deserialization and HTTP status. "
                                        "Consider encapsulating this multi-phase persistence in a "
                                        "Service ('services.py') or Orchestrator ('orchestrators/')."
                                    ),
                                }
                            )
        return views_warnings
