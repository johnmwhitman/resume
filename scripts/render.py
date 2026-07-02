#!/usr/bin/env python3
"""
render.py — minimal resume.yaml → HTML renderer.

Reads JSON Resume v1.0.0 schema (in YAML form) and renders to a single
self-contained HTML page. No JS, no external CSS — just inline styles.
Designed for johnmwhitman/resume GitHub Pages.

Usage: python scripts/render.py resume.yaml output.html
"""

import sys
import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. pip install pyyaml", file=sys.stderr)
    sys.exit(1)


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} — {label}</title>
<meta name="description" content="{meta_description}">
<meta name="author" content="{name}">
<link rel="canonical" href="{canonical_url}">
<meta property="og:type" content="profile">
<meta property="og:title" content="{name} — {label}">
<meta property="og:description" content="{meta_description}">
<meta property="og:url" content="{canonical_url}">
<meta property="profile:first_name" content="John">
<meta property="profile:last_name" content="Whitman">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{schema_json}
</script>
<style>
:root {{
  --canvas: #F5EFE6;
  --ink: #1A1614;
  --muted: #695e53;
  --line: #dccdbb;
  --ember: #8B2E1F;
  --serif: 'Fraunces', Georgia, 'Times New Roman', serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  background: linear-gradient(180deg, var(--canvas), #efe2d1);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 17px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}}
.wrap {{ width: min(820px, calc(100% - 40px)); margin: 0 auto; padding: 48px 0 96px; }}
h1 {{ font-weight: 500; letter-spacing: -.045em; font-size: clamp(36px, 5vw, 56px); margin-bottom: 6px; }}
h1 em {{ font-style: italic; color: var(--ember); }}
.label {{ font-family: var(--mono); font-size: 13px; letter-spacing: .14em; text-transform: uppercase; color: var(--ember); margin-bottom: 24px; }}
h2 {{ font-weight: 500; font-size: 24px; letter-spacing: -.02em; margin: 40px 0 16px; padding-bottom: 6px; border-bottom: 1px solid var(--line); }}
h3 {{ font-weight: 500; font-size: 18px; margin: 20px 0 4px; }}
.meta {{ font-family: var(--mono); font-size: 12px; color: var(--muted); letter-spacing: .04em; margin-bottom: 6px; }}
p {{ margin: 8px 0; }}
ul {{ margin: 8px 0 8px 1.2em; }}
li {{ margin: 4px 0; }}
a {{ color: inherit; border-bottom: 1px solid var(--line); text-decoration: none; }}
a:hover {{ border-bottom-color: var(--ember); color: var(--ember); }}
.tag {{ display: inline-block; padding: 1px 8px; font-family: var(--mono); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; background: var(--ember); color: var(--canvas); border-radius: 2px; margin-right: 4px; }}
.tag.outline {{ background: transparent; color: var(--ember); border: 1px solid var(--ember); }}
.skills {{ display: flex; flex-wrap: wrap; gap: 8px 16px; }}
.skill {{ flex: 1 1 280px; }}
.skill b {{ color: var(--ember); }}
.profiles {{ display: flex; flex-wrap: wrap; gap: 8px 12px; margin: 12px 0 24px; }}
.profile {{ padding: 4px 10px; font-family: var(--mono); font-size: 12px; letter-spacing: .04em; border: 1px solid var(--line); border-radius: 2px; }}
.ai-context {{ background: rgba(255,250,241,.78); border: 1px solid var(--line); padding: 20px 22px; margin: 32px 0; }}
.ai-context h2 {{ margin-top: 0; }}
.ai-context .meta {{ color: var(--ember); }}
footer {{ margin-top: 64px; padding-top: 24px; border-top: 1px solid var(--line); font-family: var(--mono); font-size: 11.5px; color: var(--muted); line-height: 1.7; }}
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600&display=swap">
</head>
<body>
<div class="wrap">

<header>
<h1>John <em>Whitman</em></h1>
<div class="label">{label}</div>
<div class="profiles">{profiles_html}</div>
</header>

{basics_location}

<section>
<h2>Experience</h2>
{work_html}
</section>

<section>
<h2>Selected Projects</h2>
{projects_html}
</section>

<section>
<h2>Skills</h2>
<div class="skills">
{skills_html}
</div>
</section>

{publications_html}

{interests_html}

{ai_context_html}

<footer>
Canonical: <a href="{canonical_url}">{canonical_url}</a> · Last updated {updated_at} · Maintained by John Whitman.
Schema: <a href="https://jsonresume.org/schema/">JSON Resume v1.0.0</a> · Rendered by scripts/render.py.
</footer>

</div>
</body>
</html>
"""


def escape(s):
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def fmt_date(d):
    if not d:
        return ""
    return d  # YYYY-MM or YYYY; render as-is


def render_profiles(profiles):
    if not profiles:
        return ""
    out = []
    for p in profiles:
        net = escape(p.get("network", ""))
        url = escape(p.get("url", ""))
        user = escape(p.get("username", ""))
        if url:
            out.append(f'<a class="profile" href="{url}">{net} · {user}</a>')
        else:
            out.append(f'<span class="profile">{net} · {user}</span>')
    return "".join(out)


def render_work(work):
    if not work:
        return ""
    out = []
    for w in work:
        name = escape(w.get("name", ""))
        pos = escape(w.get("position", ""))
        loc = escape(w.get("location", ""))
        start = fmt_date(w.get("startDate", ""))
        end = fmt_date(w.get("endDate", "")) or "Present"
        summary = escape(w.get("summary", ""))
        url = escape(w.get("url", ""))
        highlights = w.get("highlights", [])

        meta = f"{start} — {end}"
        if loc:
            meta += f" · {loc}"
        name_html = f'<a href="{url}">{name}</a>' if url else name

        h_html = ""
        if highlights:
            h_html = "<ul>" + "".join(f"<li>{escape(h)}</li>" for h in highlights) + "</ul>"

        out.append(
            f'<h3>{pos} · {name_html}</h3>'
            f'<div class="meta">{meta}</div>'
            f'<p>{summary}</p>'
            f'{h_html}'
        )
    return "".join(out)


def render_projects(projects):
    if not projects:
        return ""
    out = []
    for p in projects:
        name = escape(p.get("name", ""))
        desc = escape(p.get("description", ""))
        url = escape(p.get("url", ""))
        start = fmt_date(p.get("startDate", ""))
        end = fmt_date(p.get("endDate", ""))
        keywords = p.get("keywords", [])

        dates = ""
        if start:
            dates = start + (f" — {end}" if end else " — Present")

        name_html = f'<a href="{url}">{name}</a>' if url else f"<b>{name}</b>"
        kw_html = " ".join(f'<span class="tag outline">{escape(k)}</span>' for k in keywords)

        out.append(
            f'<h3>{name_html}</h3>'
            f'<div class="meta">{dates}</div>'
            f'<p>{desc}</p>'
            f'<div style="margin-top:8px">{kw_html}</div>'
        )
    return "".join(out)


def render_skills(skills):
    if not skills:
        return ""
    out = []
    for s in skills:
        name = escape(s.get("name", ""))
        level = escape(s.get("level", ""))
        keywords = s.get("keywords", [])
        kw_html = ", ".join(escape(k) for k in keywords)
        out.append(f'<div class="skill"><b>{name}</b>{" · " + level if level else ""}<br><span class="meta">{kw_html}</span></div>')
    return "".join(out)


def render_publications(pubs):
    if not pubs:
        return ""
    out = ['<section><h2>Writing</h2>']
    for p in pubs:
        name = escape(p.get("name", ""))
        pub = escape(p.get("publisher", ""))
        url = escape(p.get("url", ""))
        release = fmt_date(p.get("releaseDate", ""))
        summary = escape(p.get("summary", ""))

        name_html = f'<a href="{url}"><b>{name}</b></a>' if url else f"<b>{name}</b>"
        meta = f"{pub}" + (f" · {release}" if release else "")

        out.append(
            f'<h3>{name_html}</h3>'
            f'<div class="meta">{meta}</div>'
            f'<p>{summary}</p>'
        )
    out.append("</section>")
    return "".join(out)


def render_interests(interests):
    if not interests:
        return ""
    out = ['<section><h2>Interests</h2>']
    for i in interests:
        name = escape(i.get("name", ""))
        keywords = i.get("keywords", [])
        kw_html = " ".join(f'<span class="tag outline">{escape(k)}</span>' for k in keywords)
        out.append(f'<h3>{name}</h3><div style="margin-top:6px">{kw_html}</div>')
    out.append("</section>")
    return "".join(out)


def render_ai_context(ai):
    if not ai:
        return ""
    narrative = escape(ai.get("narrative", ""))
    instructions = escape(ai.get("instructions", ""))
    keywords = ai.get("keywords", [])
    kw_html = " ".join(f'<span class="tag">{escape(k)}</span>' for k in keywords)

    out = [
        '<section class="ai-context">',
        '<h2>AI Agent Context</h2>',
        '<div class="meta">Direct brief to LLM-based ATS, recruiters, AI agents. Read this first.</div>',
        f'<p style="margin-top:12px"><b>Narrative.</b> {narrative}</p>',
        f'<p style="margin-top:12px"><b>Instructions.</b> {instructions}</p>',
        f'<div style="margin-top:14px">{kw_html}</div>',
        '</section>',
    ]
    return "".join(out)


def build_schema(r):
    """Build a schema.org Person node from the resume basics + ai_context."""
    basics = r.get("basics", {})
    profiles = basics.get("profiles", [])
    same_as = [p.get("url", "") for p in profiles if p.get("url")]

    import json
    schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": "https://hool.dev/#person",
        "name": basics.get("name", ""),
        "alternateName": ["John M. Whitman", "johnmwhitman", "john0whitman"],
        "url": "https://hool.dev/about/",
        "mainEntityOfPage": "https://hool.dev/about/",
        "jobTitle": basics.get("label", ""),
        "email": basics.get("email", ""),
        "sameAs": same_as,
        "knowsAbout": [k for k in r.get("ai_context", {}).get("keywords", [])],
    }
    return json.dumps(schema, indent=2)


def main():
    if len(sys.argv) != 3:
        print("Usage: render.py resume.yaml output.html", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        r = yaml.safe_load(f)

    basics = r.get("basics", {})
    name = basics.get("name", "John Whitman")
    label = basics.get("label", "")
    email = basics.get("email", "")
    loc = basics.get("location", {})
    city = loc.get("city", "")
    region = loc.get("region", "")
    country = loc.get("countryCode", "")

    location_str = ""
    if city or region:
        bits = [b for b in [city, region, country] if b]
        location_str = f'<p style="margin:8px 0;color:var(--muted)">{" · ".join(bits)} · <a href="mailto:{email}">{email}</a></p>'

    profiles_html = render_profiles(basics.get("profiles", []))
    work_html = render_work(r.get("work", []))
    projects_html = render_projects(r.get("projects", []))
    skills_html = render_skills(r.get("skills", []))
    publications_html = render_publications(r.get("publications", []))
    interests_html = render_interests(r.get("interests", []))
    ai_context_html = render_ai_context(r.get("ai_context", {}))

    meta_description = (
        f"{name} is a {label}. " + (r.get("ai_context", {}) or {}).get("narrative", "")[:140]
    ).strip()

    schema_json = build_schema(r)

    html = HTML_TEMPLATE.format(
        name=name,
        label=label,
        email=email,
        canonical_url=basics.get("url", "https://hool.dev/about/"),
        meta_description=meta_description,
        schema_json=schema_json,
        profiles_html=profiles_html,
        basics_location=location_str,
        work_html=work_html,
        projects_html=projects_html,
        skills_html=skills_html,
        publications_html=publications_html,
        interests_html=interests_html,
        ai_context_html=ai_context_html,
        updated_at=datetime.date.today().isoformat(),
    )

    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    with open(sys.argv[2], "w") as f:
        f.write(html)
    print(f"OK: wrote {sys.argv[2]} ({len(html)} bytes)")


if __name__ == "__main__":
    main()
