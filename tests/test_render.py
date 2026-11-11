"""Tests for scripts/render.py unicode handling and rendering."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import yaml

# Add scripts directory to path to allow importing render module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import render


class TestUnicodeRendering(unittest.TestCase):
    """Test handling of Unicode (accented, CJK, and emoji) characters."""

    def setUp(self):
        # Synthetic fixture YAML with accented, CJK, and emoji characters across fields
        self.synthetic_yaml_str = """
basics:
  name: "Renée Müller-Åström (李小龍 / 🚀 Developer)"
  label: "Software Ingénieur 💻 日本語 & 한국어 Specialist"
  email: "renee.mueller@example.com"
  url: "https://example.org/~renée"
  summary: "Expert in unicode 🌐 i18n & l10n: café, naïve, façade, crème brûlée."
  location:
    city: "Zürich"
    region: "Île-de-France"
    countryCode: "CH"
  profiles:
    - network: "GitHub 🐙"
      username: "renée-dev"
      url: "https://github.com/renee-dev"
    - network: "Weibo 微博"
      username: "小龍"
      url: "https://weibo.com/xiaolong"

work:
  - name: "Acme Corp (Société Générale 🏢)"
    position: "Senior Développeur 🧑‍💻"
    url: "https://acme.example.com"
    startDate: "2020-01"
    endDate: "2023-05"
    summary: "Led localization across Tokyo (東京), Seoul (서울), and São Paulo 🇧🇷; loves café & crème brûlée."
    location: "Genève, Switzerland 🇨🇭"
    highlights:
      - "Improved CJK rendering: 漢字 / ひらがな / カタカナ / 한글."
      - "Implemented emoji reaction system: 👍 🚀 🎉 ❤️."
      - "Resolved accented character encoding issues (å, é, î, ö, ü, ñ, ç, naïve, façade)."

projects:
  - name: "Projet Étoile ⭐"
    description: "Multilingual translation tool using deep learning: 中文, Español, Français."
    url: "https://project-etoile.example.com"
    startDate: "2022-01"
    endDate: "2022-12"
    keywords:
      - "NLP 🤖"
      - "Unicode 🔤"
      - "Multilingual 多言語"

skills:
  - name: "Langues & Scripts 🌐"
    level: "Maître / 達人"
    keywords:
      - "Python 🐍"
      - "CJK Typography 字体"
      - "Diacritics & Accents: à, è, ì, ò, ù"

publications:
  - name: "Internationalization Guide: 从入门到精通 📖"
    publisher: "Éditions du Monde 🌍"
    releaseDate: "2021-08"
    url: "https://publications.example.com/unicode-guide"
    summary: "Comprehensive guide to UTF-8 encoding across distributed platforms."

interests:
  - name: "Arts Martiaux 🥋"
    keywords:
      - "Taekwondo 태권도"
      - "Judo 柔道"
      - "Capoeira 🤸"

ai_context:
  narrative: "Ingénieur d'exception with global mindset: 東京からパリまで 🗼."
  instructions: "Prioritize candidates with deep i18n knowledge & empathy ✨."
  keywords:
    - "Internationalization 🌐"
    - "CJK Support (中日韩)"
    - "Unicode 15.0 🦄"
"""
        self.resume_data = yaml.safe_load(self.synthetic_yaml_str)

    def test_unicode_in_render_resume(self):
        """Verify render_resume produces un-mangled accented, CJK, and emoji characters."""
        html = render.render_resume(self.resume_data, updated_at="2025-01-01")

        # Accented characters
        accented_strings = [
            "Renée Müller-Åström",
            "Ingénieur",
            "café",
            "Zürich",
            "Île-de-France",
            "Société Générale",
            "Développeur",
            "Genève",
            "São Paulo",
            "Projet Étoile",
            "Langues",
            "Maître",
            "Éditions du Monde",
        ]
        for s in accented_strings:
            with self.subTest(accented=s):
                self.assertIn(s, html)

        # CJK characters
        cjk_strings = [
            "李小龍",
            "日本語",
            "한국어",
            "微博",
            "小龍",
            "東京",
            "서울",
            "漢字",
            "ひらがな",
            "カタカナ",
            "한글",
            "中文",
            "多言語",
            "達人",
            "字体",
            "从入门到精通",
            "태권도",
            "柔道",
            "中日韩",
            "東京からパリまで",
        ]
        for s in cjk_strings:
            with self.subTest(cjk=s):
                self.assertIn(s, html)

        # Emoji characters
        emojis = [
            "🚀",
            "💻",
            "🌐",
            "🐙",
            "🏢",
            "🧑‍💻",
            "🇧🇷",
            "🇨🇭",
            "👍",
            "🎉",
            "❤️",
            "⭐",
            "🤖",
            "🔤",
            "🐍",
            "📖",
            "🌍",
            "🥋",
            "🤸",
            "🗼",
            "✨",
            "🦄",
        ]
        for e in emojis:
            with self.subTest(emoji=e):
                self.assertIn(e, html)

        # Ensure schema.org json-ld contains unescaped unicode (not \uXXXX)
        self.assertIn('"Renée Müller-Åström (李小龍 / 🚀 Developer)"', html)
        self.assertIn('"Software Ingénieur 💻 日本語 & 한국어 Specialist"', html)
        self.assertIn('"Unicode 15.0 🦄"', html)

    def test_cli_execution_with_unicode_files(self):
        """Test executing scripts/render.py via CLI with synthetic fixture input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_yaml = Path(tmpdir) / "synthetic_resume.yaml"
            output_html = Path(tmpdir) / "output.html"

            input_yaml.write_text(self.synthetic_yaml_str, encoding="utf-8")

            render_script = Path(__file__).resolve().parent.parent / "scripts" / "render.py"
            result = subprocess.run(
                [sys.executable, str(render_script), str(input_yaml), str(output_html)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(result.returncode, 0, msg=f"CLI failed: {result.stderr}")
            self.assertTrue(output_html.exists())

            rendered_content = output_html.read_text(encoding="utf-8")
            self.assertIn("Renée Müller-Åström", rendered_content)
            self.assertIn("李小龍", rendered_content)
            self.assertIn("日本語", rendered_content)
            self.assertIn("한국어", rendered_content)
            self.assertIn("🚀", rendered_content)
            self.assertIn("🦄", rendered_content)
            self.assertIn("Zürich", rendered_content)


if __name__ == "__main__":
    unittest.main()
