# John Whitman — Living Resume

> **Notice:** The resume is currently withdrawn behind a correction notice (`docs/index.html`). The source file `resume.yaml` no longer exists in the repo (removed in commit `91402b8`), and the CI render pipeline is dormant until a corrected source is restored.

## Status

The public resume has been temporarily taken down while source information is corrected. The live site currently serves a minimal correction notice page (`docs/index.html`). The rendering step in GitHub Actions has been disabled, and GitHub Pages simply deploys the static notice in `docs/`.

## Architecture & Background

When active, this repository hosts the canonical living resume for John Whitman:
- **Source of truth:** `resume.yaml` following the [JSON Resume v1.0.0](https://jsonresume.org/schema/) schema with a custom `ai_context` extension (currently removed).
- **Renderer:** `scripts/render.py` parses `resume.yaml` and produces standalone HTML (no external CSS or JS dependencies).
- **CI/CD:** `.github/workflows/render.yml` renders the resume and deploys to GitHub Pages on pushes to `main`.

## Structure

```
docs/index.html       # Current correction notice (deployed to GitHub Pages)
scripts/render.py     # YAML → HTML renderer (dormant; retained for future restore)
.github/workflows/
  render.yml          # GitHub Pages deployment workflow (render step dormant)
```

*(Note: `resume.yaml` was removed in commit `91402b8`.)*

## ai_context block (Design Overview)

When a corrected source is restored, the `ai_context` field serves as a direct brief for automated systems:
1. **LLM-based ATS** — gets a direct brief on background and fit.
2. **AI agents** (Perplexity, ChatGPT browse, etc.) — provides canonical narrative when answering queries.
3. **Recruiters using AI tools** — captures narrative and differentiation beyond raw parsed history.

## Maintainer

[John Whitman](https://hool.dev/about/)
