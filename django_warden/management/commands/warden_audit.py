import os
import re

from django.apps import apps
from django.conf import settings
from django.core.checks import run_checks
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs a comprehensive, opinionated architectural and security audit of the Django project."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== 🛡️ DJANGO WARDEN ARCHITECTURAL AUDIT ==="))
        self.stdout.write("Running deep analysis on settings, models, views, middlewares, and signals...\n")

        # Execute all auditing phases cleanly
        w1, i1 = self._audit_system_checks()
        w2, i2 = self._audit_settings()
        w3, i3 = self._audit_middlewares()
        w4, i4 = self._audit_views()

        warnings_count = w1 + w2 + w3 + w4
        infos_count = i1 + i2 + i3 + i4

        # Summary Report
        self.stdout.write(self.style.MIGRATE_LABEL("\n=== ARCHITECTURAL AUDIT SUMMARY ==="))
        if warnings_count == 0:
            self.stdout.write(self.style.SUCCESS("🏆 Perfect score! 0 Warnings, %d Info messages." % infos_count))
            self.stdout.write(self.style.SUCCESS("Your project strictly follows 'The Django Way'! Excellent job."))
        else:
            compliance_rate = max(0, 100 - (warnings_count * 15))
            self.stdout.write(
                self.style.WARNING(f"Audit completed with {warnings_count} Warnings and {infos_count} Info messages.")
            )
            self.stdout.write(self.style.WARNING(f"Estimated Architectural Compliance Rate: {compliance_rate}%"))
            self.stdout.write("Apply the hints above to scale your application seamlessly to millions of clients.")

    def _audit_system_checks(self):
        self.stdout.write(self.style.MIGRATE_LABEL("--- [1/5] Running System Integrity Checks ---"))
        warnings = 0
        infos = 0
        os.environ["DJANGO_WARDEN_AUDIT_RUNNING"] = "1"
        try:
            system_checks_issues = run_checks()
        finally:
            os.environ.pop("DJANGO_WARDEN_AUDIT_RUNNING", None)
        guardian_issues = [issue for issue in system_checks_issues if getattr(issue, "id", "").startswith("warden.")]

        if not guardian_issues:
            self.stdout.write(self.style.SUCCESS("  ✔ All system integrity checks passed successfully!"))
        else:
            for issue in guardian_issues:
                if issue.level >= 30:  # WARNING or higher
                    warnings += 1
                    self.stdout.write(self.style.WARNING(f"  ⚠ [{issue.id}] {issue.msg}"))
                    self.stdout.write(f"    Hint: {issue.hint}\n")
                else:
                    infos += 1
                    self.stdout.write(self.style.SUCCESS(f"  ℹ [{issue.id}] {issue.msg}"))
                    self.stdout.write(f"    Hint: {issue.hint}\n")
        return warnings, infos

    def _audit_settings(self):
        self.stdout.write(self.style.MIGRATE_LABEL("\n--- [2/5] Auditing Production Readiness & Settings ---"))
        warnings = 0
        infos = 0

        # Check DEBUG setting
        if settings.DEBUG:
            infos += 1
            self.stdout.write(self.style.WARNING("  ⚠ DEBUG is set to True."))
            self.stdout.write("    Hint: Ensure DEBUG = False in production settings to avoid leaks.\n")
        else:
            self.stdout.write(self.style.SUCCESS("  ✔ DEBUG is set to False (Production Mode)."))

        # Check session and CSRF cookie security
        session_secure = getattr(settings, "SESSION_COOKIE_SECURE", False)
        csrf_secure = getattr(settings, "CSRF_COOKIE_SECURE", False)
        if not session_secure or not csrf_secure:
            warnings += 1
            self.stdout.write(self.style.WARNING("  ⚠ Session or CSRF cookies are not secured."))
            self.stdout.write(
                "    Hint: Set SESSION_COOKIE_SECURE = True and CSRF_COOKIE_SECURE = True in production.\n"
            )
        else:
            self.stdout.write(self.style.SUCCESS("  ✔ Session and CSRF cookies are properly secured."))

        # Check for Ruff configuration (Opinionated Standard)
        ruff_configured = False
        base_dir = getattr(settings, "BASE_DIR", None)
        if base_dir:
            pyproject_path = os.path.join(base_dir, "pyproject.toml")
            parent_pyproject_path = os.path.join(os.path.dirname(base_dir), "pyproject.toml")
            ruff_toml = os.path.join(base_dir, "ruff.toml")
            dot_ruff_toml = os.path.join(base_dir, ".ruff.toml")

            if os.path.exists(ruff_toml) or os.path.exists(dot_ruff_toml):
                ruff_configured = True
            else:
                target_path = (
                    pyproject_path
                    if os.path.exists(pyproject_path)
                    else (parent_pyproject_path if os.path.exists(parent_pyproject_path) else None)
                )
                if target_path:
                    try:
                        with open(target_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        if "[tool.ruff]" in content:
                            ruff_configured = True
                    except OSError:
                        pass

        if not ruff_configured:
            infos += 1
            self.stdout.write(self.style.WARNING("  ⚠ Ruff linter/formatter is not configured for this project."))
            self.stdout.write(
                "    Hint: We highly recommend using Ruff for ultra-fast, PEP8-compliant "
                "linting and formatting. Create a [tool.ruff] section in your pyproject.toml.\n"
            )
        else:
            self.stdout.write(self.style.SUCCESS("  ✔ Ruff linter/formatter is configured for this project."))
        return warnings, infos

    def _audit_middlewares(self):
        self.stdout.write(self.style.MIGRATE_LABEL("\n--- [3/5] Auditing Middlewares (Performance Guards) ---"))
        warnings = 0
        infos = 0
        middlewares = getattr(settings, "MIDDLEWARE", [])
        custom_middlewares = [mw for mw in middlewares if not mw.startswith("django.")]
        if len(custom_middlewares) > 5:
            warnings += 1
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
        return warnings, infos

    def _audit_views(self):
        self.stdout.write(self.style.MIGRATE_LABEL("\n--- [4/5] Auditing Views & Architectural Boundaries ---"))
        warnings = 0
        infos = 0
        views_warnings = self.audit_views_for_service_boundary()
        if not views_warnings:
            self.stdout.write(self.style.SUCCESS("  ✔ Views comply with the Service Layer & Lean View boundaries!"))
        else:
            for vw in views_warnings:
                warnings += 1
                self.stdout.write(self.style.WARNING(f"  ⚠ {vw['msg']}"))
                self.stdout.write(f"    Hint: {vw['hint']}\n")
        return warnings, infos

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
