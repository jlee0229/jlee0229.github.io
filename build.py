#!/usr/bin/env python3
"""Build the blog: writing/<slug>/index.md  ->  writing/<slug>/index.html

Also refreshes the post list on the home page (between the <!-- posts --> markers)
and writes feed.xml. Run it after adding or editing a post:

    pip install -r requirements.txt
    python3 build.py            # published posts only
    python3 build.py --preview  # copy the site to _preview/ and build drafts there too

A post is a draft while its folder name starts with "_" (writing/_my-post/). Drafts are
never built into the real site; rename the folder to publish.

The GitHub Action in .github/workflows/build.yml runs this on every push to main,
so you can also just push the Markdown and let it build.
"""
import datetime as dt
import html
import re
import shutil
import sys
from email.utils import format_datetime
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.amsmath import amsmath_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parent
SITE_NAME = "Jaeho Lee"


def site_url():
    cname = ROOT / "CNAME"
    if cname.exists() and cname.read_text().strip():
        return "https://" + cname.read_text().strip()
    return "https://jlee0229.github.io"


# ---------------------------------------------------------------- markdown

def _highlight(code, lang, _attrs):
    try:
        lexer = get_lexer_by_name(lang) if lang else None
    except ClassNotFound:
        lexer = None
    if lexer is None:
        return ""  # markdown-it falls back to an escaped <pre><code>
    out = highlight(code, lexer, HtmlFormatter(nowrap=True))
    return f'<pre><code class="language-{html.escape(lang)}">{out}</code></pre>\n'


def make_md():
    md = (
        MarkdownIt("commonmark", {"typographer": True, "highlight": _highlight, "html": True})
        .enable(["table", "strikethrough", "replacements", "smartquotes"])
        # allow_space/allow_digits off, so "$5 and $10" stays money, not math
        .use(dollarmath_plugin, allow_space=False, allow_digits=False, double_inline=True)
        .use(amsmath_plugin)
        .use(footnote_plugin)
    )
    r = md.renderer.rules
    esc = html.escape

    r["math_inline"] = lambda t, i, o, e: f'<span class="math">{esc(t[i].content)}</span>'
    r["math_inline_double"] = lambda t, i, o, e: f'<span class="math display">{esc(t[i].content)}</span>'
    r["math_block"] = lambda t, i, o, e: f'<div class="math display">{esc(t[i].content.strip())}</div>\n'
    r["math_block_label"] = lambda t, i, o, e: (
        f'<div class="math display" id="eq-{esc(t[i].info)}">{esc(t[i].content.strip())}</div>\n')
    r["amsmath"] = lambda t, i, o, e: f'<div class="math display">{esc(t[i].content.strip())}</div>\n'

    # footnotes: plain superscript numbers, no brackets
    def fn_ref(t, i, o, e):
        n = t[i].meta["id"] + 1
        sub = f':{t[i].meta["subId"]}' if t[i].meta.get("subId", 0) > 0 else ""
        return f'<sup class="fn"><a href="#fn{n}" id="fnref{n}{sub}">{n}</a></sup>'
    r["footnote_ref"] = fn_ref
    r["footnote_block_open"] = lambda t, i, o, e: '<section class="footnotes">\n<ol>\n'
    r["footnote_block_close"] = lambda t, i, o, e: "</ol>\n</section>\n"
    r["footnote_anchor"] = lambda t, i, o, e: (
        f' <a href="#fnref{t[i].meta["id"] + 1}" class="fn-back" aria-label="Back to text">↩</a>')

    # images: lazy-load, and an image alone in a paragraph becomes a <figure>,
    # with the Markdown title ("...") as the caption
    def image(s, t, i, o, e):
        tok = t[i]
        alt = esc(s.renderInlineAsText(tok.children or [], o, e))
        src = esc(tok.attrGet("src") or "")
        return f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async">'
    md.add_render_rule("image", image)
    md.core.ruler.push("figures", _figures)
    return md


def _figures(state):
    toks = state.tokens
    for i in range(len(toks) - 2):
        a, inl, c = toks[i], toks[i + 1], toks[i + 2]
        if not (a.type == "paragraph_open" and inl.type == "inline" and c.type == "paragraph_close"):
            continue
        kids = [k for k in (inl.children or []) if not (k.type == "text" and not k.content.strip())]
        # [image] or [link_open, image, link_close]
        imgs = [k for k in kids if k.type == "image"]
        if len(imgs) != 1 or len(kids) not in (1, 3):
            continue
        if len(kids) == 3 and not (kids[0].type == "link_open" and kids[2].type == "link_close"):
            continue
        a.tag = c.tag = "figure"
        a.type, c.type = "figure_open", "figure_close"
        a.meta["caption"] = imgs[0].attrGet("title") or ""
        c.meta["caption"] = a.meta["caption"]


def render_figure_rules(md):
    inline_md = MarkdownIt("commonmark", {"typographer": True}).use(
        dollarmath_plugin, allow_space=False, allow_digits=False)
    inline_md.renderer.rules["math_inline"] = (
        lambda t, i, o, e: f'<span class="math">{html.escape(t[i].content)}</span>')
    md.add_render_rule("figure_open", lambda s, t, i, o, e: "<figure>")

    def close(s, t, i, o, e):
        cap = t[i].meta.get("caption", "")
        cap_html = f"<figcaption>{inline_md.renderInline(cap)}</figcaption>" if cap else ""
        return f"{cap_html}</figure>\n"
    md.add_render_rule("figure_close", close)


MD = make_md()
render_figure_rules(MD)


# ---------------------------------------------------------------- posts

def parse(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if m:
        body = text[m.end():]
        for line in m.group(1).splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                k, v = line.split(":", 1)
                v = v.strip()
                if len(v) >= 2 and v[0] == v[-1] == '"':
                    v = v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
                elif len(v) >= 2 and v[0] == v[-1] == "'":
                    v = v[1:-1]
                meta[k.strip().lower()] = v
    if "title" not in meta:
        sys.exit(f"{path}: missing 'title:' in the front matter")
    try:
        meta["date"] = dt.date.fromisoformat(str(meta.get("date", "")).strip())
    except ValueError:
        sys.exit(f"{path}: 'date:' must look like 2026-11-21")
    meta["slug"] = path.parent.name
    meta["body"] = body
    return meta


def fmt_date(d):
    return f"{d:%B} {d.day}, {d.year}"


def words(md_text):
    return len(re.findall(r"\w+", re.sub(r"\$\$.*?\$\$|```.*?```", " ", md_text, flags=re.S)))


HEADER = """<header class="top">
<a class="name" href="{up}">Jaeho Lee</a>
<nav aria-label="Sections"><a href="{up}#writing">Writing</a><a href="{up}#research">Research</a><a href="{up}#projects">Projects</a></nav>
</header>"""

KATEX = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.css" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.js" crossorigin="anonymous"></script>
<script defer src="{up}math.js"></script>"""


def page(post, up="../../"):
    body_html = MD.render(post["body"])
    has_math = 'class="math' in body_html
    title = html.escape(post["title"])
    sub = html.escape(post.get("subtitle", ""))
    desc = sub or title
    mins = max(1, round(words(post["body"]) / 230))
    meta_bits = [f'<time datetime="{post["date"].isoformat()}">{fmt_date(post["date"])}</time>', f"{mins} min read"]
    if post.get("substack"):
        meta_bits.append(f'<a href="{html.escape(post["substack"])}">Also on Substack</a>')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · {SITE_NAME}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME}" href="{up}feed.xml">
<link rel="stylesheet" href="{up}style.css">
{KATEX.format(up=up) if has_math else ""}
</head>
<body>
<div class="wrap">
{HEADER.format(up=up)}
<main>
<article class="post">
<header class="post-head">
<h1>{title}</h1>
{f'<p class="subtitle">{sub}</p>' if sub else ""}
<p class="meta">{" · ".join(meta_bits)}</p>
</header>
<div class="prose">
{body_html}</div>
<footer class="post-foot"><a href="{up}#writing">← All writing</a></footer>
</article>
</main>
</div>
</body>
</html>
"""


def post_list(posts, up=""):
    rows = []
    for p in posts:
        sub = f'\n<span class="s">{html.escape(p["subtitle"])}</span>' if p.get("subtitle") else ""
        rows.append(
            f'<li><div><a class="t" href="{up}writing/{p["slug"]}/">{html.escape(p["title"])}</a>{sub}</div>'
            f'<time class="d" datetime="{p["date"].isoformat()}">{p["date"]:%b %Y}</time></li>')
    return ('<section id="writing">\n<h2>Writing</h2>\n<ul class="rows">\n'
            + "\n".join(rows) + "\n</ul>\n</section>")


def feed(posts):
    base = site_url()
    items = []
    for p in posts[:20]:
        link = f"{base}/writing/{p['slug']}/"
        when = dt.datetime.combine(p["date"], dt.time(12), dt.timezone.utc)
        items.append(f"""<item><title>{html.escape(p['title'])}</title><link>{link}</link><guid>{link}</guid>
<pubDate>{format_datetime(when)}</pubDate><description>{html.escape(p.get('subtitle', ''))}</description></item>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel>
<title>{SITE_NAME}</title><link>{base}/</link><description>Writing by {SITE_NAME}</description>
{chr(10).join(items)}
</channel></rss>
"""


def build(root, drafts=False):
    posts = []
    for md_path in sorted((root / "writing").glob("*/index.md")):
        p = parse(md_path)
        out = md_path.with_name("index.html")
        if p["slug"].startswith("_") and not drafts:
            if out.exists():
                out.unlink()  # never leave a public copy of a draft
            continue
        out.write_text(page(p), encoding="utf-8")
        posts.append(p)
        print("built", out.relative_to(root))
    posts.sort(key=lambda p: p["date"], reverse=True)

    index = root / "index.html"
    text = index.read_text(encoding="utf-8")
    new = re.sub(r"(<!-- posts -->).*?(<!-- /posts -->)",
                 lambda m: m.group(1) + ("\n" + post_list(posts) + "\n" if posts else "") + m.group(2),
                 text, flags=re.S)
    if new != text:
        index.write_text(new, encoding="utf-8")

    # pages with a <!-- nav-writing --> slot get a Writing link once there is a post
    for f in root.glob("**/*.html"):
        if "_preview" in f.relative_to(root).parts:
            continue
        text = f.read_text(encoding="utf-8")
        if "<!-- nav-writing -->" not in text:
            continue
        up = "../" * (len(f.relative_to(root).parts) - 1)
        link = f'<a href="{up}#writing">Writing</a>' if posts else ""
        new = re.sub(r"(<!-- nav-writing -->).*?(<!-- /nav-writing -->)",
                     lambda m: m.group(1) + link + m.group(2), text, flags=re.S)
        if new != text:
            f.write_text(new, encoding="utf-8")
    (root / "feed.xml").write_text(feed(posts), encoding="utf-8")
    print(f"{len(posts)} post(s)")


def main():
    if "--preview" in sys.argv:
        dest = ROOT / "_preview"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(".git", "_preview", "__pycache__"))
        build(dest, drafts=True)
        print(f"preview: open {dest / 'index.html'} (or run: python3 -m http.server -d _preview)")
    else:
        build(ROOT)


if __name__ == "__main__":
    main()
