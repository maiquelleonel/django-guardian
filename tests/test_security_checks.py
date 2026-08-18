from unittest.mock import patch

from django.core.checks import run_checks
from django.test import TestCase

from django_warden.checks.security import _scan_file_with_ast


class TestSecurityASTChecks(TestCase):
    @patch("django_warden.checks.security.os.walk")
    @patch("django_warden.checks.security.open", create=True)
    def test_check_detects_serializer_mass_assignment(self, mock_open, mock_walk):
        mock_walk.return_value = [("/mock/path", [], ["serializers.py"])]
        mock_open.return_value.__enter__.return_value.read.return_value = """
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
"""
        errors = run_checks(tags=["security"])
        warnings = [e for e in errors if e.id == "warden.W008"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("Mass Assignment risk", warnings[0].msg)
        self.assertIn("UserSerializer.Meta", warnings[0].msg)
        self.assertIn("read_only_fields", warnings[0].hint)

    @patch("django_warden.checks.security.os.walk")
    @patch("django_warden.checks.security.open", create=True)
    def test_check_detects_extra_query_usage(self, mock_open, mock_walk):
        mock_walk.return_value = [("/mock/path", [], ["views.py"])]
        mock_open.return_value.__enter__.return_value.read.return_value = """
def my_view(request):
    qs = User.objects.extra(where=["id = 1"])
    return qs
"""
        errors = run_checks(tags=["security"])
        warnings = [e for e in errors if e.id == "warden.W009"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("Usage of deprecated and unsafe `.extra()`", warnings[0].msg)
        self.assertIn("views.py", warnings[0].msg)
        self.assertIn("annotate", warnings[0].hint)

    @patch("django_warden.checks.security.os.walk")
    @patch("django_warden.checks.security.open", create=True)
    def test_check_detects_pickle_usage(self, mock_open, mock_walk):
        mock_walk.return_value = [("/mock/path", [], ["tasks.py"])]
        mock_open.return_value.__enter__.return_value.read.return_value = """
import pickle

def handle_payload(raw_bytes):
    return pickle.loads(raw_bytes)
"""
        errors = run_checks(tags=["security"])
        warnings = [e for e in errors if e.id == "warden.W010"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("Insecure deserialization via `pickle.loads()`", warnings[0].msg)
        self.assertIn("tasks.py", warnings[0].msg)
        self.assertIn("signing", warnings[0].hint)

    @patch("django_warden.checks.security.os.walk")
    @patch("django_warden.checks.security.open", create=True)
    def test_check_detects_raw_sql_injection(self, mock_open, mock_walk):
        mock_walk.return_value = [("/mock/path", [], ["models.py"])]
        mock_open.return_value.__enter__.return_value.read.return_value = """
from django.db.models.expressions import RawSQL

def search_users(term):
    qs1 = User.objects.raw(f"SELECT * FROM users WHERE name = '{term}'")
    qs2 = RawSQL("SELECT * FROM users WHERE status = '%s'" % term, [])
    cursor.execute("SELECT * FROM users WHERE type = {}".format(term))
    return qs1
"""
        errors = run_checks(tags=["security"])
        warnings = [e for e in errors if e.id == "warden.W011"]
        self.assertEqual(len(warnings), 3)
        self.assertIn("Potential SQL injection in raw query call", warnings[0].msg)
        self.assertIn("models.py", warnings[0].msg)
        self.assertIn("params", warnings[0].hint)

    def test_scan_file_handles_syntax_and_io_errors(self):
        # Non-existent file (OSError)
        warnings_io = _scan_file_with_ast("/non/existent/file.py", "test_app", "file.py")
        self.assertEqual(warnings_io, [])

        # Mocking invalid python syntax
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "def broken_syntax(:"
            warnings_syntax = _scan_file_with_ast("/mock/path/broken.py", "test_app", "broken.py")
            self.assertEqual(warnings_syntax, [])
