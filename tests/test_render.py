import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SYNTHETIC_BASE_YAML = """
basics:
  name: "Jane Doe"
  label: "Software Engineer"
  email: "jane.doe@example.com"
  url: "https://example.com/janedoe"
  location:
    city: "Metropolis"
    region: "NY"
    countryCode: "US"
  profiles:
    - network: "GitHub"
      username: "janedoe"
      url: "https://github.com/janedoe"
work:
  - name: "Acme Corp"
    position: "Backend Engineer"
    url: "https://example.com/acme"
    startDate: "2020-01"
    endDate: "2023-01"
    summary: "Built scalable web services."
    highlights:
      - "Improved throughput"
projects:
  - name: "OpenProject"
    description: "An open source utility."
    url: "https://example.com/openproject"
    startDate: "2021"
    endDate: "2022"
    keywords: ["Python", "CLI"]
skills:
  - name: "Programming"
    level: "Advanced"
    keywords: ["Python", "Rust"]
"""

SYNTHETIC_UNKNOWN_KEYS_YAML = SYNTHETIC_BASE_YAML + """
extra_metadata:
  license: "MIT"
  revision: 5
unexpected_flag: true
custom_metrics_payload: "synthetic_secret_token_12345"
arbitrary_top_level_section:
  - key1: "value1"
    key2: "value2"
"""


class TestRenderUnknownKeyTolerance(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.render_script = self.repo_root / "scripts" / "render.py"
        self.assertTrue(self.render_script.exists(), "scripts/render.py must exist")

    def run_render(self, yaml_content: str):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f_yaml, \
             tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f_out:
            f_yaml.write(yaml_content)
            yaml_path = f_yaml.name
            out_path = f_out.name

        try:
            cmd = [sys.executable, str(self.render_script), yaml_path, out_path]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
            )
            html_output = None
            if os.path.exists(out_path):
                with open(out_path, "r", encoding="utf-8") as f:
                    html_output = f.read()
            return proc, html_output
        finally:
            if os.path.exists(yaml_path):
                os.remove(yaml_path)
            if os.path.exists(out_path):
                os.remove(out_path)

    def test_unknown_top_level_keys_tolerance(self):
        """
        Verify that a synthetic fixture with extra unknown top-level YAML keys
        either renders successfully with the unknown keys absent from the output
        or exits non-zero with a clear error, never an unhandled traceback.
        """
        proc, html = self.run_render(SYNTHETIC_UNKNOWN_KEYS_YAML)

        # Neither exit branch may crash with an unhandled Python traceback
        self.assertNotIn("Traceback (most recent call last):", proc.stderr)

        if proc.returncode == 0:
            # Renders successfully: ensure output was generated and unknown keys/values are absent
            self.assertIsNotNone(html)
            self.assertGreater(len(html), 0)

            # Check that known synthetic content is present
            self.assertIn("Jane Doe", html)
            self.assertIn("Software Engineer", html)

            # Check that unknown top-level keys and values are absent from the rendered HTML
            self.assertNotIn("extra_metadata", html)
            self.assertNotIn("unexpected_flag", html)
            self.assertNotIn("custom_metrics_payload", html)
            self.assertNotIn("synthetic_secret_token_12345", html)
            self.assertNotIn("arbitrary_top_level_section", html)
        else:
            # Exits non-zero with a clear error message on stderr
            self.assertTrue(
                len(proc.stderr.strip()) > 0,
                "Expected non-empty error message on stderr when exiting non-zero",
            )

    def test_single_unknown_key_tolerance(self):
        """
        Verify tolerance with a single unknown scalar key.
        """
        yaml_content = SYNTHETIC_BASE_YAML + "\ncustom_single_key: custom_value_98765\n"
        proc, html = self.run_render(yaml_content)

        self.assertNotIn("Traceback (most recent call last):", proc.stderr)

        if proc.returncode == 0:
            self.assertIsNotNone(html)
            self.assertNotIn("custom_single_key", html)
            self.assertNotIn("custom_value_98765", html)
        else:
            self.assertTrue(len(proc.stderr.strip()) > 0)


if __name__ == "__main__":
    unittest.main()
