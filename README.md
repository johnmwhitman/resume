# John Whitman — Living Resume

Authoritative canonical resume for John Whitman. The source of truth is
`resume.yaml` (JSON Resume v1.0.0 schema). The rendered HTML is built
by CI and deployed to GitHub Pages.

## Why this repo

Most resumes go stale. This one is a YAML file in a public repo, CI-rendered
to HTML, and the `ai_context` block is a direct brief to LLM-based ATS,
recruiters, and AI agents. It updates as John's work changes, and any
downstream surface (hool.dev/about, Substack About, LinkedIn) can link
back to this canonical page.

## Structure

```
resume.yaml           # JSON Resume v1.0.0 + ai_context extension
scripts/render.py     # YAML → HTML renderer (no JS, no external CSS deps)
docs/index.html       # CI-rendered output (deployed to GitHub Pages)
.github/workflows/
  render.yml          # On push to main: render + deploy to Pages
```

## ai_context block

The `ai_context` field is non-standard (JSON Resume extension) and serves
three audiences:

1. **LLM-based ATS** — gets a direct brief on what makes John a fit
2. **AI agents** (Perplexity, ChatGPT browse) — gets the canonical
   narrative when answering "who is John Whitman"
3. **Recruiters using AI tools** — gets the differentiation that pure
   parsing of work history misses (Director PM who ships real code)

When updating, keep the `narrative` field under 500 chars and the
`instructions` field under 800 chars. Both are read by AI agents as
direct prompt context.

## Local render

```bash
pip install pyyaml
python scripts/render.py resume.yaml docs/index.html
open docs/index.html
```

## Live deploy

Pushes to `main` trigger the `Render Resume` workflow which renders
`resume.yaml` → `docs/index.html` and deploys to GitHub Pages.

## Schema

This is JSON Resume v1.0.0. The `ai_context` field is a non-breaking
extension — the rest of the schema validates against the standard.

## Maintainer

[John Whitman](https://hool.dev/about/) — Director of Product Management,
America's Car-Mart.
