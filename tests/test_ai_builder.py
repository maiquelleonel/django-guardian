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

    def test_gemini_directory_detection_and_creation(self):
        # Setup: create the .gemini directory
        os.makedirs(os.path.join(self.test_dir, ".gemini"), exist_ok=True)

        context = {
            "project_name": "my_test_app",
            "settings_module": "my_test_app.settings",
        }

        targets, skill_created, settings_created = ensure_ai_structure(self.test_dir, context)

        # Assertions
        self.assertEqual(targets, [".gemini"])
        self.assertTrue(skill_created)
        self.assertTrue(settings_created)

        skill_file = os.path.join(self.test_dir, ".gemini", "skills", "django-warden", "SKILL.md")
        self.assertTrue(os.path.exists(skill_file))

        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("DJANGO GUARDIAN SKILL: MY_TEST_APP", content)
            self.assertIn("my_test_app", content)

        settings_file = os.path.join(self.test_dir, ".gemini", "settings.json")
        self.assertTrue(os.path.exists(settings_file))

        with open(settings_file, "r", encoding="utf-8") as f:
            settings_data = json.load(f)
            self.assertIn("django-ai-boost", settings_data["mcpServers"])
            self.assertEqual(
                settings_data["mcpServers"]["django-ai-boost"]["args"], ["--settings", "my_test_app.settings"]
            )

    def test_claude_directory_detection(self):
        # Setup: create the .claude directory
        os.makedirs(os.path.join(self.test_dir, ".claude"), exist_ok=True)

        context = {
            "project_name": "claude_project",
            "settings_module": "claude_project.settings",
        }

        targets, skill_created, settings_created = ensure_ai_structure(self.test_dir, context)

        # Assertions
        self.assertEqual(targets, [".claude"])
        self.assertTrue(skill_created)
        self.assertTrue(settings_created)

        skill_file = os.path.join(self.test_dir, ".claude", "skills", "django-warden", "SKILL.md")
        self.assertTrue(os.path.exists(skill_file))

    def test_both_gemini_and_claude_directories_detection_and_creation(self):
        # Setup: create BOTH .gemini and .claude directories
        os.makedirs(os.path.join(self.test_dir, ".gemini"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, ".claude"), exist_ok=True)

        context = {
            "project_name": "dual_project",
            "settings_module": "dual_project.settings",
        }

        targets, skill_created, settings_created = ensure_ai_structure(self.test_dir, context)

        # Assertions
        self.assertEqual(set(targets), {".gemini", ".claude"})
        self.assertTrue(skill_created)
        self.assertTrue(settings_created)

        # Check SKILL.md and settings.json in .gemini
        gemini_skill = os.path.join(self.test_dir, ".gemini", "skills", "django-warden", "SKILL.md")
        gemini_settings = os.path.join(self.test_dir, ".gemini", "settings.json")
        self.assertTrue(os.path.exists(gemini_skill))
        self.assertTrue(os.path.exists(gemini_settings))

        # Check SKILL.md and settings.json in .claude
        claude_skill = os.path.join(self.test_dir, ".claude", "skills", "django-warden", "SKILL.md")
        claude_settings = os.path.join(self.test_dir, ".claude", "settings.json")
        self.assertTrue(os.path.exists(claude_skill))
        self.assertTrue(os.path.exists(claude_settings))

    def test_fallback_to_agents_directory(self):
        # Setup: do NOT create .gemini or .claude
        context = {
            "project_name": "generic_project",
            "settings_module": "generic_project.settings",
        }

        targets, skill_created, settings_created = ensure_ai_structure(self.test_dir, context)

        # Assertions
        self.assertEqual(targets, [".agents"])
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
        self.assertEqual(targets, [".gemini"])
        self.assertTrue(skill_created)
        self.assertFalse(settings_created)  # False because settings.json already existed

        with open(settings_file_path, "r", encoding="utf-8") as f:
            merged_data = json.load(f)

            # Assert custom user settings were preserved
            self.assertTrue(merged_data["customUserSetting"])
            self.assertEqual(merged_data["theme"], "dark")

            # Assert custom MCP was preserved
            self.assertIn("custom-mcp", merged_data["mcpServers"])
            self.assertEqual(merged_data["mcpServers"]["custom-mcp"]["args"], ["custom.js"])

            # Assert new MCP was merged successfully
            self.assertIn("django-ai-boost", merged_data["mcpServers"])
            self.assertEqual(
                merged_data["mcpServers"]["django-ai-boost"]["args"], ["--settings", "merge_project.settings"]
            )
