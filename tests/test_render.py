import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render.py"


class TestRenderMalformedInput(unittest.TestCase):
    def test_malformed_yaml_exits_nonzero_and_writes_no_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            malformed_yaml = tmp_path / "malformed.yaml"
            output_html = tmp_path / "output.html"

            # Synthetic fixture with invalid YAML syntax
            malformed_yaml.write_text(":\n  bad_yaml: [unclosed_bracket")

            result = subprocess.run(
                [sys.executable, str(RENDER_SCRIPT), str(malformed_yaml), str(output_html)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output_html.exists(), "Output file should not be created on malformed input")


if __name__ == "__main__":
    unittest.main()
