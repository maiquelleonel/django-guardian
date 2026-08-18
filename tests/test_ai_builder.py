import json
import os
import shutil
import tempfile

from django.test import TestCase

from django_warden.ai_builder import ensure_ai_structure


class TestAIBuilder(TestCase):
    def setUp(self):
        # Create a temporary directory to act as the project base_dir
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_default_gemini_and_claude_directories_creation(self):
        context = {
            "project_name": "my_test_app",
            "settings_module": "my_test_app.settings",
        }

        targets, skill_created, settings_created = ensure_ai_structure(self.test_dir, context)

        # Assertions: both .gemini and .claude are provisioned by default
        self.assertEqual(set(targets), {".gemini", ".claude"})
        self.assertTrue(skill_created)
        self.assertTrue(settings_created)

        for target_dir in [".gemini", ".claude"]:
            skill_file = os.path.join(self.test_dir, target_dir, "skills", "django-warden", "SKILL.md")
            self.assertTrue(os.path.exists(skill_file))

            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("DJANGO GUARDIAN SKILL: MY_TEST_APP", content)
                self.assertIn("my_test_app", content)

            settings_file = os.path.join(self.test_dir, target_dir, "settings.json")
            self.assertTrue(os.path.exists(settings_file))

            with open(settings_file, "r", encoding="utf-8") as f:
                settings_data = json.load(f)
                self.assertIn("django-ai-boost", settings_data["mcpServers"])
                self.assertEqual(
                    settings_data["mcpServers"]["django-ai-boost"]["args"], ["--settings", "my_test_app.settings"]
                )
                self.assertIn("codebase-memory-mcp", settings_data["mcpServers"])
                self.assertEqual(settings_data["mcpServers"]["codebase-memory-mcp"]["command"], "codebase-memory-mcp")

    def test_agents_directory_detected_and_included(self):
        # Setup: create .agents directory
        os.makedirs(os.path.join(self.test_dir, ".agents"), exist_ok=True)

        context = {
            "project_name": "agents_project",
            "settings_module": "agents_project.settings",
        }

        targets, skill_created, settings_created = ensure_ai_structure(self.test_dir, context)

        # Assertions
        self.assertEqual(set(targets), {".gemini", ".claude", ".agents"})
        self.assertTrue(skill_created)
        self.assertTrue(settings_created)

        skill_file = os.path.join(self.test_dir, ".agents", "skills", "django-warden", "SKILL.md")
        self.assertTrue(os.path.exists(skill_file))

    def test_smart_merge_preserves_existing_settings(self):
        # Setup: create .gemini directory and existing settings.json
        os.makedirs(os.path.join(self.test_dir, ".gemini"), exist_ok=True)

        existing_data = {
            "mcpServers": {"custom-mcp": {"command": "node", "args": ["custom.js"]}},
            "customUserSetting": True,
            "theme": "dark",
        }

        settings_file_path = os.path.join(self.test_dir, ".gemini", "settings.json")
        with open(settings_file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)

        context = {
            "project_name": "merge_project",
            "settings_module": "merge_project.settings",
        }

        targets, skill_created, settings_created = ensure_ai_structure(self.test_dir, context)

        # Assertions
        self.assertEqual(set(targets), {".gemini", ".claude"})
        self.assertTrue(skill_created)

        with open(settings_file_path, "r", encoding="utf-8") as f:
            merged_data = json.load(f)

            # Assert custom user settings were preserved
            self.assertTrue(merged_data["customUserSetting"])
            self.assertEqual(merged_data["theme"], "dark")

            # Assert custom MCP was preserved
            self.assertIn("custom-mcp", merged_data["mcpServers"])
            self.assertEqual(merged_data["mcpServers"]["custom-mcp"]["args"], ["custom.js"])

            # Assert new MCPs were merged successfully
            self.assertIn("django-ai-boost", merged_data["mcpServers"])
            self.assertEqual(
                merged_data["mcpServers"]["django-ai-boost"]["args"], ["--settings", "merge_project.settings"]
            )
            self.assertIn("codebase-memory-mcp", merged_data["mcpServers"])
            self.assertEqual(merged_data["mcpServers"]["codebase-memory-mcp"]["command"], "codebase-memory-mcp")
