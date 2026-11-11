import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add repo root to sys.path so scripts can be imported
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml
from scripts.render import render, render_html


SYNTHETIC_RESUME_1 = {
    "basics": {
        "name": "Jane Doe",
        "label": "Senior Systems Engineer",
        "email": "jane.doe@example.com",
        "url": "https://example.com/jane",
        "summary": "Experienced engineer with a focus on determinism and reliability.",
        "location": {
            "city": "Austin",
            "region": "Texas",
            "countryCode": "US",
        },
        "profiles": [
            {
                "network": "GitHub",
                "username": "janedoe",
                "url": "https://github.com/janedoe",
            },
            {
                "network": "LinkedIn",
                "username": "janedoe",
                "url": "https://linkedin.com/in/janedoe",
            },
            {
                "network": "Bluesky",
                "username": "janedoe.bsky.social",
            },
        ],
    },
    "work": [
        {
            "name": "Acme Corp",
            "position": "Staff Engineer",
            "url": "https://acme.example.com",
            "startDate": "2020-01",
            "endDate": "2024-03",
            "summary": "Led architecture of distributed event pipeline.",
            "location": "Remote",
            "highlights": [
                "Achieved 99.999% uptime for core ingestion service.",
                "Reduced processing latency by 45%.",
            ],
        },
        {
            "name": "Startup Inc",
            "position": "Software Engineer",
            "startDate": "2017-06",
            "endDate": "",
            "summary": "Built foundational microservices.",
        },
    ],
    "projects": [
        {
            "name": "Determinism Tool",
            "description": "A tool that guarantees byte-for-byte deterministic builds.",
            "url": "https://github.com/janedoe/determinism-tool",
            "startDate": "2021-01",
            "endDate": "2021-12",
            "keywords": ["Python", "CI/CD", "Reproducibility"],
        },
        {
            "name": "Internal Dashboard",
            "description": "Internal monitoring and health dashboard.",
            "startDate": "2022-02",
            "keywords": ["React", "TypeScript"],
        },
    ],
    "skills": [
        {
            "name": "Distributed Systems",
            "level": "Expert",
            "keywords": ["Raft", "Kafka", "PostgreSQL"],
        },
        {
            "name": "Languages",
            "keywords": ["Python", "Rust", "Go"],
        },
    ],
    "publications": [
        {
            "name": "Deterministic Output in Build Pipelines",
            "publisher": "Tech Quarterly",
            "releaseDate": "2023-05-15",
            "url": "https://example.com/article",
            "summary": "An exploration of techniques for bitwise identical artifacts.",
        },
        {
            "name": "Reproducible Environments",
            "publisher": "Engineering Blog",
            "summary": "Why hermetic builds matter for continuous integration.",
        },
    ],
    "interests": [
        {
            "name": "Open Source",
            "keywords": ["Compilers", "Tooling"],
        },
        {
            "name": "Photography",
            "keywords": ["Analog", "Monochrome"],
        },
    ],
    "ai_context": {
        "narrative": "Senior Systems Engineer specializing in hermetic build systems and reliable platforms.",
        "instructions": "Assess candidate for principal infrastructure and deterministic toolchain roles.",
        "keywords": ["reproducible builds", "distributed systems", "tooling"],
    },
}

SYNTHETIC_RESUME_MINIMAL = {
    "basics": {
        "name": "Minimal Person",
    }
}


class TestRenderDeterminism(unittest.TestCase):
    def test_programmatic_render_deterministic_identical_bytes(self):
        """Rendering the same synthetic fixture twice produces byte-identical HTML."""
        fixed_date = "2026-01-01"
        render_1 = render(SYNTHETIC_RESUME_1, updated_at=fixed_date)
        render_2 = render(SYNTHETIC_RESUME_1, updated_at=fixed_date)

        self.assertIsInstance(render_1, str)
        self.assertIsInstance(render_2, str)
        self.assertEqual(render_1.encode("utf-8"), render_2.encode("utf-8"))

    def test_minimal_fixture_deterministic_identical_bytes(self):
        """Rendering minimal synthetic fixture twice produces byte-identical HTML."""
        fixed_date = "2026-01-01"
        bytes_1 = render(SYNTHETIC_RESUME_MINIMAL, updated_at=fixed_date).encode("utf-8")
        bytes_2 = render(SYNTHETIC_RESUME_MINIMAL, updated_at=fixed_date).encode("utf-8")

        self.assertEqual(bytes_1, bytes_2)

    def test_cli_render_deterministic_identical_bytes(self):
        """Running scripts/render.py CLI twice against the same synthetic fixture produces byte-identical HTML."""
        render_script = REPO_ROOT / "scripts" / "render.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            fixture_yaml = tmp_path / "synthetic_resume.yaml"
            out1 = tmp_path / "out1.html"
            out2 = tmp_path / "out2.html"

            with open(fixture_yaml, "w", encoding="utf-8") as f:
                yaml.dump(SYNTHETIC_RESUME_1, f)

            # First CLI run
            res1 = subprocess.run(
                [sys.executable, str(render_script), str(fixture_yaml), str(out1)],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("OK: wrote", res1.stdout)

            # Second CLI run
            res2 = subprocess.run(
                [sys.executable, str(render_script), str(fixture_yaml), str(out2)],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("OK: wrote", res2.stdout)

            bytes1 = out1.read_bytes()
            bytes2 = out2.read_bytes()

            self.assertGreater(len(bytes1), 0)
            self.assertEqual(bytes1, bytes2)


if __name__ == "__main__":
    unittest.main()
