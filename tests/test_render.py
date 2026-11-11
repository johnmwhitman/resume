import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure scripts directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import render


class TestRenderPresentButEmptyFields(unittest.TestCase):
    """Test that synthetic fixtures with present-but-empty fields render without crashing

    and produce complete HTML documents.
    """

    def setUp(self):
        # Synthetic fixture where all optional sections and nested fields are present
        # but hold empty strings or empty lists.
        self.synthetic_empty_sections = {
            "basics": {
                "name": "",
                "label": "",
                "email": "",
                "url": "",
                "summary": "",
                "location": {
                    "city": "",
                    "region": "",
                    "countryCode": "",
                },
                "profiles": [],
            },
            "work": [],
            "projects": [],
            "skills": [],
            "publications": [],
            "interests": [],
            "ai_context": {
                "narrative": "",
                "instructions": "",
                "keywords": [],
            },
        }

        # Synthetic fixture where sections contain items with present-but-empty fields.
        self.synthetic_empty_entries = {
            "basics": {
                "name": "",
                "label": "",
                "email": "",
                "url": "",
                "summary": "",
                "location": {
                    "city": "",
                    "region": "",
                    "countryCode": "",
                },
                "profiles": [
                    {
                        "network": "",
                        "username": "",
                        "url": "",
                    }
                ],
            },
            "work": [
                {
                    "name": "",
                    "position": "",
                    "location": "",
                    "startDate": "",
                    "endDate": "",
                    "summary": "",
                    "url": "",
                    "highlights": [],
                }
            ],
            "projects": [
                {
                    "name": "",
                    "description": "",
                    "url": "",
                    "startDate": "",
                    "endDate": "",
                    "keywords": [],
                }
            ],
            "skills": [
                {
                    "name": "",
                    "level": "",
                    "keywords": [],
                }
            ],
            "publications": [
                {
                    "name": "",
                    "publisher": "",
                    "url": "",
                    "releaseDate": "",
                    "summary": "",
                }
            ],
            "interests": [
                {
                    "name": "",
                    "keywords": [],
                }
            ],
            "ai_context": {
                "narrative": "",
                "instructions": "",
                "keywords": [],
            },
        }

    def _assert_valid_complete_html(self, html):
        self.assertIsInstance(html, str)
        self.assertTrue(len(html) > 0)
        self.assertTrue(html.strip().startswith("<!doctype html>"))
        self.assertTrue(html.strip().endswith("</html>"))
        self.assertIn("<head>", html)
        self.assertIn("</head>", html)
        self.assertIn("<body>", html)
        self.assertIn("</body>", html)
        self.assertIn("application/ld+json", html)

    def test_render_html_with_empty_sections(self):
        html = render.render_html(self.synthetic_empty_sections)
        self._assert_valid_complete_html(html)

    def test_render_html_with_empty_entries(self):
        html = render.render_html(self.synthetic_empty_entries)
        self._assert_valid_complete_html(html)

    def test_main_cli_with_empty_fixture(self):
        import yaml

        with tempfile.TemporaryDirectory() as td:
            in_yaml = Path(td) / "resume.yaml"
            out_html = Path(td) / "docs" / "index.html"
            with open(in_yaml, "w") as f:
                yaml.dump(self.synthetic_empty_sections, f)

            with patch.object(sys, "argv", ["render.py", str(in_yaml), str(out_html)]):
                render.main()

            self.assertTrue(out_html.exists())
            html = out_html.read_text(encoding="utf-8")
            self._assert_valid_complete_html(html)


if __name__ == "__main__":
    unittest.main()
