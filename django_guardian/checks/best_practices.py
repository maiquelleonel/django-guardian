import os
import re

from django.apps import apps
from django.core.checks import Tags, Warning, register


def _scan_file_for_issues(file_path, app_name, file_name):
    """
    Scans a single Python file for best practice violations.
    """
    warnings = []
    datetime_now_regex = re.compile(r"\bdatetime\.(now|utcnow)\s*\(")
    requests_regex = re.compile(r"\brequests\.(get|post|put|delete|patch|request)\s*\(")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []

    for line_num, line in enumerate(lines, 1):
        # Check for naive datetime
        match_dt = datetime_now_regex.search(line)
        if match_dt:
            stripped = line.strip()
            if not stripped.startswith("#"):
                func_used = match_dt.group(1)
                warnings.append(
                    Warning(
                        (f"Usage of naive datetime detected in '{app_name}/{file_name}' on line {line_num}."),
                        hint=(
                            f"Replace 'datetime.{func_used}()' with "
                            "'django.utils.timezone.now()' to ensure proper "
                            "timezone support and production compliance."
                        ),
                        id="guardian.W005",
                    )
                )

        # Check for requests without timeout
        match_req = requests_regex.search(line)
        if match_req:
            stripped = line.strip()
            if not stripped.startswith("#") and "timeout=" not in line:
                http_method = match_req.group(1)
                warnings.append(
                    Warning(
                        (f"HTTP call to 'requests' without timeout in '{app_name}/{file_name}' on line {line_num}."),
                        hint=(
                            f"Add the 'timeout' parameter (e.g., "
                            f"requests.{http_method}(url, timeout=5)) to prevent "
                            "sync threads from hanging indefinitely."
                        ),
                        id="guardian.W006",
                    )
                )
    return warnings


@register(Tags.compatibility)
def check_best_practices_in_code(app_configs, **kwargs):
    """
    Scans the Python source files of local Django applications to detect
    common anti-patterns (naive datetimes and requests without timeouts).
    """
    warnings = []

    configs_to_scan = app_configs if app_configs else apps.get_app_configs()

    for app_config in configs_to_scan:
        path = app_config.path
        if "site-packages" in path or app_config.name.startswith("django.contrib"):
            continue

        # Recursively walk Python files in the app directory
        for root, _, files in os.walk(path):
            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                if "migrations" in file_path or "__pycache__" in file_path:
                    continue

                warnings.extend(_scan_file_for_issues(file_path, app_config.name, file))

    return warnings
