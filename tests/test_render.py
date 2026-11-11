import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render.py"


class TestRenderCLIContract(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(RENDER_SCRIPT), *args],
            capture_output=True,
            text=True,
        )

    def test_wrong_argument_count_no_args(self):
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stderr)

    def test_wrong_argument_count_one_arg(self):
        result = self.run_cli("input.yaml")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stderr)

    def test_wrong_argument_count_too_many_args(self):
        result = self.run_cli("input.yaml", "output.html", "extra_arg")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stderr)

    def test_missing_input_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_input = Path(tmpdir) / "does_not_exist.yaml"
            output_file = Path(tmpdir) / "output.html"
            result = self.run_cli(str(missing_input), str(output_file))
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output_file.exists())

    def test_minimal_valid_synthetic_fixture(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "minimal_resume.yaml"
            output_file = Path(tmpdir) / "output.html"

            minimal_yaml_content = (
                "basics:\n"
                "  name: Jane Doe\n"
                "  label: Software Engineer\n"
            )
            input_file.write_text(minimal_yaml_content, encoding="utf-8")

            result = self.run_cli(str(input_file), str(output_file))
            self.assertEqual(result.returncode, 0, msg=f"CLI failed with stderr: {result.stderr}")
            self.assertTrue(output_file.exists())
            content = output_file.read_text(encoding="utf-8")
            self.assertIn("Jane Doe", content)
            self.assertIn("Software Engineer", content)
            self.assertIn("OK: wrote", result.stdout)


if __name__ == "__main__":
    unittest.main()
