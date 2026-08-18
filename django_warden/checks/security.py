import ast
import os

from django.apps import apps
from django.core.checks import Tags, Warning, register


class SecurityASTVisitor(ast.NodeVisitor):
    """
    AST visitor that scans Python source code for common security vulnerabilities
    and anti-patterns in Django applications.
    """

    def __init__(self, app_name: str, file_name: str):
        self.app_name = app_name
        self.file_name = file_name
        self.warnings: list[Warning] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        self._check_serializer_mass_assignment(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        self._check_extra_query_usage(node)
        self._check_pickle_usage(node)
        self._check_raw_sql_injection(node)
        self.generic_visit(node)

    def _check_serializer_mass_assignment(self, node: ast.ClassDef):
        """
        Checks for `fields = '__all__'` inside serializer class Meta.
        """
        for item in node.body:
            if isinstance(item, ast.ClassDef) and item.name == "Meta":
                for meta_stmt in item.body:
                    if isinstance(meta_stmt, ast.Assign):
                        for target in meta_stmt.targets:
                            if isinstance(target, ast.Name) and target.id == "fields":
                                if isinstance(meta_stmt.value, ast.Constant) and meta_stmt.value.value == "__all__":
                                    self.warnings.append(
                                        Warning(
                                            (
                                                f"Mass Assignment risk in '{self.app_name}/{self.file_name}' "
                                                f"on line {meta_stmt.lineno}: `fields = '__all__'` in "
                                                f"class '{node.name}.Meta'."
                                            ),
                                            hint=(
                                                "Avoid `fields = '__all__'` on write serializers. Explicitly "
                                                "declare allowed fields and protect sensitive fields with "
                                                "`read_only_fields`."
                                            ),
                                            id="warden.W008",
                                        )
                                    )

    def _check_extra_query_usage(self, node: ast.Call):
        """
        Detects calls to deprecated and dangerous QuerySet.extra().
        """
        if isinstance(node.func, ast.Attribute) and node.func.attr == "extra":
            self.warnings.append(
                Warning(
                    (
                        f"Usage of deprecated and unsafe `.extra()` query method detected in "
                        f"'{self.app_name}/{self.file_name}' on line {node.lineno}."
                    ),
                    hint=(
                        "Replace `.extra()` with `.annotate()`, custom expressions, or explicit "
                        "parameterized `RawSQL` to prevent SQL injection."
                    ),
                    id="warden.W009",
                )
            )

    def _check_pickle_usage(self, node: ast.Call):
        """
        Detects insecure pickle deserialization (pickle.loads/load).
        """
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in ("loads", "load"):
            if isinstance(func.value, ast.Name) and func.value.id in ("pickle", "_pickle"):
                self.warnings.append(
                    Warning(
                        (
                            f"Insecure deserialization via `pickle.{func.attr}()` detected in "
                            f"'{self.app_name}/{self.file_name}' on line {node.lineno}."
                        ),
                        hint=(
                            "Prohibit `pickle` deserialization on untrusted streams to prevent arbitrary code "
                            "execution. Use `json`, `django.core.signing`, or safe serializers."
                        ),
                        id="warden.W010",
                    )
                )

    def _check_raw_sql_injection(self, node: ast.Call):
        """
        Detects string formatting (f-strings, %, .format()) in raw SQL queries.
        """
        func = node.func
        is_raw_call = False

        if isinstance(func, ast.Name) and func.id in ("RawSQL",):
            is_raw_call = True
        elif isinstance(func, ast.Attribute) and func.attr in ("raw", "execute"):
            is_raw_call = True

        if is_raw_call and node.args:
            first_arg = node.args[0]
            if self._is_interpolated_string(first_arg):
                self.warnings.append(
                    Warning(
                        (
                            f"Potential SQL injection in raw query call in "
                            f"'{self.app_name}/{self.file_name}' on line {node.lineno}."
                        ),
                        hint=(
                            "Never interpolate raw queries using f-strings, `%`, or `.format()`. "
                            "Always use parameterized queries with query parameter binding (e.g. `params=[...]`)."
                        ),
                        id="warden.W011",
                    )
                )

    def _is_interpolated_string(self, node: ast.AST) -> bool:
        """
        Helper that checks if an AST expression represents an interpolated string.
        """
        if isinstance(node, ast.JoinedStr):
            return True
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
            return True
        return False


def _scan_file_with_ast(file_path: str, app_name: str, file_name: str) -> list[Warning]:
    """
    Parses a single Python file into an AST and scans it for security issues.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return []

    visitor = SecurityASTVisitor(app_name, file_name)
    visitor.visit(tree)
    return visitor.warnings


@register(Tags.security)
def check_security_best_practices(app_configs, **kwargs):
    """
    Scans the Python source files of local Django applications using AST analysis
    to detect critical security vulnerabilities (Mass Assignment, .extra(), pickle, SQL injection).
    """
    warnings = []
    configs_to_scan = app_configs if app_configs else apps.get_app_configs()

    for app_config in configs_to_scan:
        path = app_config.path
        if "site-packages" in path or app_config.name.startswith("django.contrib"):
            continue

        for root, _, files in os.walk(path):
            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                if "migrations" in file_path or "__pycache__" in file_path:
                    continue

                warnings.extend(_scan_file_with_ast(file_path, app_config.name, file))

    return warnings
