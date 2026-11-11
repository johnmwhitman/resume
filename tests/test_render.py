"""Unit tests for scripts/render.py HTML escaping."""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add repo root to sys.path so we can import scripts.render
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.render import escape, render_resume


SYNTHETIC_RESUME_YAML = """
basics:
  name: "Synthetic <script>alert('name')</script> & User \\"Quote\\""
  label: "Software & <script>alert('label')</script> \\"Architect\\""
  email: "synth<test>&\\"user\\"@example.com"
  url: "https://example.com/synth?user=1&role=test<script>\\"quote\\""
  location:
    city: "City <script>&\\"1\\""
    region: "Region <script>&\\"2\\""
    countryCode: "CC <script>&\\"3\\""
  profiles:
    - network: "Network <script>alert('net')</script> & Co \\"Quotes\\""
      username: "user <script>alert('user')</script> & \\"name\\""
      url: "https://example.com/net?a=1&b=2<script>\\"quote\\""
    - network: "Network2 <script> & \\"none\\""
      username: "user2 <script> & \\"none\\""
work:
  - name: "Company <script>alert('company')</script> & Co \\"Inc\\""
    position: "Position <script>alert('pos')</script> & Lead \\"Senior\\""
    location: "Location <script>alert('loc')</script> & Remote \\"HQ\\""
    startDate: "2020-01<script>&\\""
    endDate: "2021-01<script>&\\""
    summary: "Summary <script>alert('work_sum')</script> & text \\"quoted\\""
    url: "https://example.com/work?id=1&ref=2<script>\\"quote\\""
    highlights:
      - "Highlight 1 <script>alert('hl1')</script> & bullet \\"quoted\\""
      - "Highlight 2 <script>alert('hl2')</script> & bullet2 \\"quoted\\""
projects:
  - name: "Project <script>alert('proj')</script> & App \\"Cool\\""
    description: "Description <script>alert('pdesc')</script> & details \\"info\\""
    url: "https://example.com/proj?a=1&b=2<script>\\"quote\\""
    startDate: "2021-02<script>&\\""
    endDate: "2022-02<script>&\\""
    keywords:
      - "Keyword <script>alert('pkw')</script> & Tag \\"tag1\\""
skills:
  - name: "Skill <script>alert('skill')</script> & Tech \\"Main\\""
    level: "Level <script>alert('level')</script> & Advanced \\"Senior\\""
    keywords:
      - "SkillKW <script>alert('skw')</script> & Item \\"Sub\\""
publications:
  - name: "Publication <script>alert('pub')</script> & Article \\"Title\\""
    publisher: "Publisher <script>alert('publisher')</script> & Press \\"Media\\""
    url: "https://example.com/pub?a=1&b=2<script>\\"quote\\""
    releaseDate: "2022-05<script>&\\""
    summary: "PubSummary <script>alert('pub_sum')</script> & writeup \\"quoted\\""
interests:
  - name: "Interest <script>alert('interest')</script> & Hobby \\"Fun\\""
    keywords:
      - "IntKW <script>alert('ikw')</script> & Topic \\"Item\\""
ai_context:
  narrative: "Narrative <script>alert('narrative')</script> & description \\"overview\\""
  instructions: "Instructions <script>alert('instructions')</script> & guidance \\"rules\\""
  keywords:
    - "AIKW <script>alert('aikw')</script> & Concept \\"Key\\""
"""


class TestRenderHtmlEscaping(unittest.TestCase):
    def setUp(self):
        import yaml
        self.synthetic_data = yaml.safe_load(SYNTHETIC_RESUME_YAML)

    def test_escape_helper_function(self):
        """Test the escape helper directly on malicious inputs."""
        self.assertEqual(escape(None), "")
        self.assertEqual(escape(123), "123")
        self.assertEqual(
            escape('<script>alert("XSS & test")</script>'),
            "&lt;script&gt;alert(&quot;XSS &amp; test&quot;)&lt;/script&gt;",
        )

    def test_render_resume_escapes_all_synthetic_fields(self):
        """Rendered HTML should have all script tags, ampersands, and quotes escaped."""
        html = render_resume(self.synthetic_data, updated_at="2026-01-01")

        # Outside the JSON-LD script tag itself, there should be no other <script> or </script> tags
        non_ldjson = re.sub(
            r'<script type="application/ld\+json">.*?</script>',
            "",
            html,
            flags=re.DOTALL,
        )
        self.assertNotIn("<script", non_ldjson.lower())
        self.assertNotIn("</script", non_ldjson.lower())

        # Verify exact escaped occurrences of injected test strings
        # Basics
        self.assertIn("Synthetic &lt;script&gt;alert('name')&lt;/script&gt; &amp; User &quot;Quote&quot;", html)
        self.assertIn("Software &amp; &lt;script&gt;alert('label')&lt;/script&gt; &quot;Architect&quot;", html)
        self.assertIn("synth&lt;test&gt;&amp;&quot;user&quot;@example.com", html)
        self.assertIn("City &lt;script&gt;&amp;&quot;1&quot;", html)
        self.assertIn("Region &lt;script&gt;&amp;&quot;2&quot;", html)
        self.assertIn("CC &lt;script&gt;&amp;&quot;3&quot;", html)
        self.assertIn("Network &lt;script&gt;alert('net')&lt;/script&gt; &amp; Co &quot;Quotes&quot;", html)
        self.assertIn("user &lt;script&gt;alert('user')&lt;/script&gt; &amp; &quot;name&quot;", html)
        self.assertIn("Network2 &lt;script&gt; &amp; &quot;none&quot;", html)

        # Work
        self.assertIn("Company &lt;script&gt;alert('company')&lt;/script&gt; &amp; Co &quot;Inc&quot;", html)
        self.assertIn("Position &lt;script&gt;alert('pos')&lt;/script&gt; &amp; Lead &quot;Senior&quot;", html)
        self.assertIn("Location &lt;script&gt;alert('loc')&lt;/script&gt; &amp; Remote &quot;HQ&quot;", html)
        self.assertIn("Summary &lt;script&gt;alert('work_sum')&lt;/script&gt; &amp; text &quot;quoted&quot;", html)
        self.assertIn("Highlight 1 &lt;script&gt;alert('hl1')&lt;/script&gt; &amp; bullet &quot;quoted&quot;", html)
        self.assertIn("Highlight 2 &lt;script&gt;alert('hl2')&lt;/script&gt; &amp; bullet2 &quot;quoted&quot;", html)

        # Projects
        self.assertIn("Project &lt;script&gt;alert('proj')&lt;/script&gt; &amp; App &quot;Cool&quot;", html)
        self.assertIn("Description &lt;script&gt;alert('pdesc')&lt;/script&gt; &amp; details &quot;info&quot;", html)
        self.assertIn("Keyword &lt;script&gt;alert('pkw')&lt;/script&gt; &amp; Tag &quot;tag1&quot;", html)

        # Skills
        self.assertIn("Skill &lt;script&gt;alert('skill')&lt;/script&gt; &amp; Tech &quot;Main&quot;", html)
        self.assertIn("Level &lt;script&gt;alert('level')&lt;/script&gt; &amp; Advanced &quot;Senior&quot;", html)
        self.assertIn("SkillKW &lt;script&gt;alert('skw')&lt;/script&gt; &amp; Item &quot;Sub&quot;", html)

        # Publications
        self.assertIn("Publication &lt;script&gt;alert('pub')&lt;/script&gt; &amp; Article &quot;Title&quot;", html)
        self.assertIn("Publisher &lt;script&gt;alert('publisher')&lt;/script&gt; &amp; Press &quot;Media&quot;", html)
        self.assertIn("PubSummary &lt;script&gt;alert('pub_sum')&lt;/script&gt; &amp; writeup &quot;quoted&quot;", html)

        # Interests
        self.assertIn("Interest &lt;script&gt;alert('interest')&lt;/script&gt; &amp; Hobby &quot;Fun&quot;", html)
        self.assertIn("IntKW &lt;script&gt;alert('ikw')&lt;/script&gt; &amp; Topic &quot;Item&quot;", html)

        # AI Context
        self.assertIn("Narrative &lt;script&gt;alert('narrative')&lt;/script&gt; &amp; description &quot;overview&quot;", html)
        self.assertIn("Instructions &lt;script&gt;alert('instructions')&lt;/script&gt; &amp; guidance &quot;rules&quot;", html)
        self.assertIn("AIKW &lt;script&gt;alert('aikw')&lt;/script&gt; &amp; Concept &quot;Key&quot;", html)

        # Meta attributes
        self.assertIn('meta name="description" content="Synthetic &lt;script&gt;alert(&#x27;name&#x27;)&lt;/script&gt;' if "&#x27;" in html else 'meta name="description" content="Synthetic &lt;script&gt;alert(\'name\')&lt;/script&gt;', html)
        self.assertIn('meta name="author" content="Synthetic &lt;script&gt;alert(\'name\')&lt;/script&gt; &amp; User &quot;Quote&quot;"', html)
        self.assertIn('href="https://example.com/synth?user=1&amp;role=test&lt;script&gt;&quot;quote&quot;"', html)

    def test_cli_execution_with_synthetic_yaml_escapes(self):
        """CLI execution `python scripts/render.py synthetic.yaml out.html` escapes HTML."""
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as yf, \
             tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as hf:
            yf.write(SYNTHETIC_RESUME_YAML)
            yf_path = yf.name
            hf_path = hf.name

        try:
            res = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "render.py"), yf_path, hf_path],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("OK: wrote", res.stdout)
            with open(hf_path, "r", encoding="utf-8") as f:
                output_html = f.read()

            non_ldjson = re.sub(
                r'<script type="application/ld\+json">.*?</script>',
                "",
                output_html,
                flags=re.DOTALL,
            )
            self.assertNotIn("<script>", non_ldjson)
            self.assertNotIn("</script>", non_ldjson)
            self.assertIn("&lt;script&gt;alert('name')&lt;/script&gt;", non_ldjson)
            self.assertIn("&amp;", non_ldjson)
            self.assertIn("&quot;", non_ldjson)
        finally:
            Path(yf_path).unlink(missing_ok=True)
            Path(hf_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
