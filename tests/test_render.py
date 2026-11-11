"""
tests/test_render.py — stdlib unittest suite for scripts/render.py.

Verifies that synthetic YAML omitting each optional section renders without
crashing and cleanly omits the section (or omits content, noting current
hardcoded template headings where applicable), using synthetic fixtures only.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render.py"


def render_resume_yaml(yaml_content: str) -> str:
    """Helper to render synthetic YAML content through scripts/render.py.

    Returns the rendered HTML string or raises an AssertionError / CalledProcessError
    if rendering fails.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        yaml_file = tmp_path / "resume.yaml"
        html_file = tmp_path / "output.html"

        yaml_file.write_text(yaml_content, encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(RENDER_SCRIPT), str(yaml_file), str(html_file)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"render.py failed with returncode {result.returncode}:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

        return html_file.read_text(encoding="utf-8")


# Base synthetic fixture with all sections populated
FULL_SYNTHETIC_YAML = """
basics:
  name: "Jane Tester"
  label: "Principal Systems Architect"
  email: "jane.tester@example.com"
  url: "https://example.com/jane"
  location:
    city: "Metropolis"
    region: "NY"
    countryCode: "US"
  profiles:
    - network: "GitHub"
      username: "janetester"
      url: "https://github.com/janetester"

work:
  - name: "Acme Corp"
    position: "Staff Engineer"
    location: "New York, NY"
    startDate: "2020-01"
    endDate: "2023-01"
    summary: "Built scalable event pipelines."
    url: "https://acme.example.com"
    highlights:
      - "Reduced latency by 50%"
      - "Mentored 10 engineers"

projects:
  - name: "Project Aurora"
    description: "High-throughput message queue engine."
    url: "https://aurora.example.com"
    startDate: "2021"
    endDate: "2022"
    keywords: ["Go", "Distributed Systems"]

skills:
  - name: "Distributed Systems"
    level: "Expert"
    keywords: ["Consensus", "Raft", "Paxos"]

publications:
  - name: "Scalable Consensus Protocols"
    publisher: "ACM Distributed Computing"
    url: "https://doi.org/10.1000/example"
    releaseDate: "2022-06"
    summary: "Overview of modern consensus protocols."

interests:
  - name: "Photography"
    keywords: ["Landscape", "Analog"]

ai_context:
  narrative: "Jane is a distributed systems engineer with deep expertise in consensus."
  instructions: "Focus on technical leadership and architecture experience."
  keywords: ["Distributed Systems", "Consensus", "Go", "Cloud"]

education:
  - institution: "Polytechnic Institute"
    area: "Computer Science"
    studyType: "B.S."
    startDate: "2010"
    endDate: "2014"
"""

MINIMAL_SYNTHETIC_YAML = """
basics:
  name: "Jane Tester"
  label: "Software Engineer"
"""


class TestRenderMissingSections(unittest.TestCase):
    """Tests for rendering synthetic resumes omitting each optional section."""

    def test_full_synthetic_resume_renders_successfully(self):
        """Smoke test: full synthetic resume renders all populated sections without crashing."""
        html = render_resume_yaml(FULL_SYNTHETIC_YAML)
        self.assertIn("Jane Tester", html)
        self.assertIn("Staff Engineer", html)
        self.assertIn("Project Aurora", html)
        self.assertIn("Distributed Systems", html)
        self.assertIn("Scalable Consensus Protocols", html)
        self.assertIn("Photography", html)
        self.assertIn("AI Agent Context", html)

    def test_minimal_synthetic_resume_renders_without_crashing(self):
        """Minimal synthetic resume with only basics renders without crashing."""
        html = render_resume_yaml(MINIMAL_SYNTHETIC_YAML)
        self.assertIn("Jane Tester", html)
        self.assertIn("Software Engineer", html)

    # -------------------------------------------------------------------------
    # Clean omission sections: publications, interests, ai_context
    # -------------------------------------------------------------------------

    def test_omit_publications_cleanly(self):
        """Omitting publications renders without crashing and cleanly omits the section."""
        yaml_content = """
basics:
  name: "Jane Tester"
interests:
  - name: "Photography"
        """
        html = render_resume_yaml(yaml_content)
        self.assertNotIn("Writing", html)
        self.assertNotIn("<h2>Writing</h2>", html)

    def test_omit_interests_cleanly(self):
        """Omitting interests renders without crashing and cleanly omits the section."""
        yaml_content = """
basics:
  name: "Jane Tester"
publications:
  - name: "Scalable Protocols"
        """
        html = render_resume_yaml(yaml_content)
        self.assertNotIn("Interests", html)
        self.assertNotIn("<h2>Interests</h2>", html)

    def test_omit_ai_context_cleanly(self):
        """Omitting ai_context renders without crashing and cleanly omits the section."""
        yaml_content = """
basics:
  name: "Jane Tester"
interests:
  - name: "Photography"
        """
        html = render_resume_yaml(yaml_content)
        self.assertNotIn('<section class="ai-context">', html)
        self.assertNotIn("<h2>AI Agent Context</h2>", html)
        self.assertNotIn("AI Agent Context", html)
        self.assertNotIn("Direct brief to LLM-based ATS", html)

    # -------------------------------------------------------------------------
    # Content omission sections: work, projects, skills
    # (Assert no crash and no section content; expected-failure on no-empty-heading
    #  due to hardcoded HTML_TEMPLATE blocks in scripts/render.py)
    # -------------------------------------------------------------------------

    def test_omit_work_no_content(self):
        """Omitting work renders without crashing and omits work content."""
        yaml_content = """
basics:
  name: "Jane Tester"
projects:
  - name: "Project Beta"
        """
        html = render_resume_yaml(yaml_content)
        self.assertNotIn("Acme Corp", html)
        self.assertNotIn("Staff Engineer", html)

    @unittest.expectedFailure
    def test_omit_work_clean_heading_omission(self):
        """Omitting work should omit the Experience heading entirely.

        Currently expected to fail because HTML_TEMPLATE in scripts/render.py
        contains a hardcoded <section><h2>Experience</h2>{work_html}</section> block.
        """
        yaml_content = """
basics:
  name: "Jane Tester"
projects:
  - name: "Project Beta"
        """
        html = render_resume_yaml(yaml_content)
        self.assertNotIn("<h2>Experience</h2>", html)

    def test_omit_projects_no_content(self):
        """Omitting projects renders without crashing and omits project content."""
        yaml_content = """
basics:
  name: "Jane Tester"
work:
  - name: "Acme Corp"
        """
        html = render_resume_yaml(yaml_content)
        self.assertNotIn("Project Aurora", html)
        self.assertNotIn("Project Beta", html)

    @unittest.expectedFailure
    def test_omit_projects_clean_heading_omission(self):
        """Omitting projects should omit the Selected Projects heading entirely.

        Currently expected to fail because HTML_TEMPLATE in scripts/render.py
        contains a hardcoded <section><h2>Selected Projects</h2>{projects_html}</section> block.
        """
        yaml_content = """
basics:
  name: "Jane Tester"
work:
  - name: "Acme Corp"
        """
        html = render_resume_yaml(yaml_content)
        self.assertNotIn("<h2>Selected Projects</h2>", html)

    def test_omit_skills_no_content(self):
        """Omitting skills renders without crashing and omits skills content."""
        yaml_content = """
basics:
  name: "Jane Tester"
projects:
  - name: "Project Beta"
        """
        html = render_resume_yaml(yaml_content)
        self.assertNotIn("class=\"skill\"", html)
        self.assertNotIn("Distributed Systems", html)

    @unittest.expectedFailure
    def test_omit_skills_clean_heading_omission(self):
        """Omitting skills should omit the Skills heading entirely.

        Currently expected to fail because HTML_TEMPLATE in scripts/render.py
        contains a hardcoded <section><h2>Skills</h2><div class=\"skills\">{skills_html}</div></section> block.
        """
        yaml_content = """
basics:
  name: "Jane Tester"
projects:
  - name: "Project Beta"
        """
        html = render_resume_yaml(yaml_content)
        self.assertNotIn("<h2>Skills</h2>", html)

    # -------------------------------------------------------------------------
    # Education section (ignored-when-present case)
    # -------------------------------------------------------------------------

    def test_education_present_renders_without_crashing(self):
        """A fixture containing education renders without crashing (education is ignored today)."""
        yaml_content = """
basics:
  name: "Jane Tester"
education:
  - institution: "Polytechnic Institute"
    area: "Computer Science"
    studyType: "B.S."
    startDate: "2010"
    endDate: "2014"
        """
        html = render_resume_yaml(yaml_content)
        self.assertIn("Jane Tester", html)
        # Education has no renderer currently, so it does not appear in the HTML
        self.assertNotIn("Polytechnic Institute", html)

    def test_omit_education_renders_without_crashing(self):
        """Omitting education renders without crashing and omits any education content."""
        yaml_content = """
basics:
  name: "Jane Tester"
        """
        html = render_resume_yaml(yaml_content)
        self.assertIn("Jane Tester", html)
        self.assertNotIn("<h2>Education</h2>", html)

    # -------------------------------------------------------------------------
    # Iterative omission across all read sections
    # -------------------------------------------------------------------------

    def test_omitting_each_optional_section_individually(self):
        """Verify that omitting each optional section one-by-one from a full resume renders without crashing."""
        sections = [
            "work",
            "projects",
            "skills",
            "publications",
            "interests",
            "ai_context",
            "education",
        ]

        import yaml

        base_data = yaml.safe_load(FULL_SYNTHETIC_YAML)

        for section in sections:
            with self.subTest(omitted_section=section):
                data = dict(base_data)
                del data[section]
                yaml_str = yaml.dump(data)
                html = render_resume_yaml(yaml_str)
                self.assertIn("Jane Tester", html)

                if section == "publications":
                    self.assertNotIn("<h2>Writing</h2>", html)
                elif section == "interests":
                    self.assertNotIn("<h2>Interests</h2>", html)
                elif section == "ai_context":
                    self.assertNotIn('<section class="ai-context">', html)
                    self.assertNotIn("<h2>AI Agent Context</h2>", html)
                elif section == "work":
                    self.assertNotIn("Acme Corp", html)
                elif section == "projects":
                    self.assertNotIn("Project Aurora", html)
                elif section == "skills":
                    self.assertNotIn("class=\"skill\"", html)
                elif section == "education":
                    self.assertNotIn("Polytechnic Institute", html)


if __name__ == "__main__":
    unittest.main()
