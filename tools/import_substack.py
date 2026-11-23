#!/usr/bin/env python3
"""Import a Substack post as writing/<slug>/index.md, with its images downloaded next to it.

    python3 tools/import_substack.py https://yourname.substack.com/p/some-post
    python3 tools/import_substack.py post.html --title "Title" --date 2026-11-21   # a file from Substack's export

Then run `python3 build.py`. The GitHub Action can do both: Actions > "Build site" > Run workflow,
and paste the post URL.

What carries over: paragraphs, headings, bold/italic/strike, links, lists, block quotes, code
blocks, images with captions, LaTeX blocks (as $$ display math), footnotes, horizontal rules,
tables, and YouTube embeds (as a link). Subscribe and share buttons and app promos are dropped.
Substack has no inline math, so any inline math you want is yours to add as $...$ after import.
"""
import argparse
import datetime as dt
import json
import mimetypes
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (static site importer)"}

DROP_CLASSES = (
    "subscription-widget", "subscribe-widget", "install-substack-app", "button-wrapper",
    "share-widget", "captioned-button", "digest-post-embed", "embedded-post", "community-chat",
    "paywall", "poll-embed", "image-link-expand", "pencraft",
)


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get("Content-Type", "")


def fetch_post(url):
    u = urllib.parse.urlparse(url)
    m = re.search(r"/p/([^/?#]+)", u.path)
    if not m:
        sys.exit("Expected a post URL like https://name.substack.com/p/post-slug")
    api = f"{u.scheme or 'https'}://{u.netloc}/api/v1/posts/{m.group(1)}"
    data, _ = get(api)
    post = json.loads(data)
    if post.get("audience") not in (None, "everyone"):
        print("warning: this post is not public, so Substack may only return a preview of it", file=sys.stderr)
    return post


MAX_WIDTH = 2000  # px; the post column is 640px, so this still covers 3x screens


def shrink(path):
    """Downscale very large photos so a post doesn't ship a 10 MB image."""
    try:
        from PIL import Image
    except ImportError:
        return
    try:
        with Image.open(path) as im:
            if im.width <= MAX_WIDTH or im.format not in ("JPEG", "PNG", "WEBP"):
                return
            fmt = im.format
            im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
            im.save(path, fmt, **({"quality": 85, "optimize": True} if fmt in ("JPEG", "WEBP") else {}))
    except OSError:
        pass


# ---------------------------------------------------------------- HTML -> Markdown

def esc(text):
    text = text.replace("\\", "\\\\")
    text = re.sub(r"([`*\[\]<$])", r"\\\1", text)
    # underscores only matter at word edges; snake_case is left alone
    text = re.sub(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])", r"\\_", text)
    return text


def guard_line_start(line):
    if re.match(r"(#{1,6}\s|>|[-+=]\s|[-+*]$|\d+[.)]\s)", line):
        return "\\" + line if not line[0].isdigit() else re.sub(r"^(\d+)([.)])", r"\1\\\2", line)
    return line


def classes(el):
    return " ".join(el.get("class") or [])


def has_class(el, *names):
    c = classes(el)
    return any(n in c for n in names)


class Converter:
    def __init__(self, img_dir, download=True):
        self.img_dir = img_dir
        self.download = download
        self.n_images = 0
        self.footnotes = []

    # inline ------------------------------------------------------
    def inline(self, el):
        out = []
        for c in el.children:
            out.append(self.inline_node(c))
        return "".join(out)

    def wrap(self, inner, mark):
        if not inner.strip():
            return inner
        lead = inner[: len(inner) - len(inner.lstrip())]
        trail = inner[len(inner.rstrip()):]
        return f"{lead}{mark}{inner.strip()}{mark}{trail}"

    def inline_node(self, n):
        if isinstance(n, NavigableString):
            if n.__class__.__name__ in ("Comment", "Doctype"):
                return ""
            return esc(re.sub(r"\s+", " ", str(n)))
        if not isinstance(n, Tag):
            return ""
        t = n.name
        if t in ("strong", "b"):
            return self.wrap(self.inline(n), "**")
        if t in ("em", "i"):
            return self.wrap(self.inline(n), "*")
        if t in ("s", "strike", "del"):
            return self.wrap(self.inline(n), "~~")
        if t == "code":
            code = n.get_text()
            fence = "``" if "`" in code else "`"
            pad = " " if code.startswith("`") or code.endswith("`") else ""
            return f"{fence}{pad}{code}{pad}{fence}"
        if t == "br":
            return "\\\n"
        if t == "a":
            if has_class(n, "footnote-anchor"):
                return f"[^{n.get_text(strip=True)}]"
            href = n.get("href", "")
            text = self.inline(n)
            if not href:
                return text
            return f"[{text}]({href.replace(' ', '%20').replace(')', '%29')})"
        if t in ("sup", "sub"):
            return f"<{t}>{self.inline(n)}</{t}>"
        if t == "img":
            return self.image(n)
        if t in ("button", "svg", "script", "style", "form", "input"):
            return ""
        return self.inline(n)

    # images ------------------------------------------------------
    def image(self, img, caption=""):
        src = img.get("src", "")
        try:
            attrs = json.loads(img.get("data-attrs") or "{}")
            src = attrs.get("src") or src
        except ValueError:
            pass
        if not src:
            return ""
        alt = (img.get("alt") or "").replace("\n", " ").replace("]", "")
        local = self.save_image(src)
        title = ' "' + caption.replace('"', '\\"') + '"' if caption else ""
        return f"![{alt}]({local}{title})"

    def save_image(self, src):
        self.n_images += 1
        if not self.download:
            return src
        try:
            data, ctype = get(src)
        except Exception as e:  # keep the remote URL rather than lose the image
            print(f"warning: could not download {src}: {e}", file=sys.stderr)
            return src
        ext = mimetypes.guess_extension((ctype or "").split(";")[0].strip()) or Path(
            urllib.parse.urlparse(src).path).suffix or ".png"
        ext = {".jpe": ".jpg", ".jpeg": ".jpg"}.get(ext, ext)
        name = f"{self.n_images:02d}{ext}"
        self.img_dir.mkdir(parents=True, exist_ok=True)
        (self.img_dir / name).write_bytes(data)
        shrink(self.img_dir / name)
        return f"images/{name}"

    # blocks ------------------------------------------------------
    def blocks(self, el):
        out = []
        for c in el.children:
            b = self.block(c)
            if b and b.strip():
                out.append(b.strip("\n"))
        return "\n\n".join(out)

    def block(self, n):
        if isinstance(n, NavigableString):
            s = str(n).strip()
            return esc(s) if s and n.__class__.__name__ not in ("Comment", "Doctype") else ""
        if not isinstance(n, Tag):
            return ""
        t = n.name
        if has_class(n, *DROP_CLASSES) and not has_class(n, "captioned-image"):
            return ""
        if t == "p":
            text = self.inline(n).strip()
            # Substack writers often use a bold line as a section heading
            m = re.fullmatch(r"\*\*([^*\n]{1,90})\*\*", text)
            if m and len(n.find_all(["strong", "b"])) == 1:
                return "## " + m.group(1).strip()
            return "\n".join(guard_line_start(l) for l in text.split("\n"))
        if re.fullmatch(r"h[1-6]", t):
            level = max(2, int(t[1]))
            return "#" * level + " " + self.inline(n).strip()
        if t == "hr":
            return "---"
        if t == "blockquote":
            inner = self.blocks(n)
            return "\n".join(("> " + l) if l else ">" for l in inner.split("\n"))
        if t in ("ul", "ol"):
            return self.list(n, ordered=(t == "ol"))
        if t == "pre":
            code = n.get_text()
            fence = "~~~" if "```" in code else "```"
            return f"{fence}\n{code.rstrip()}\n{fence}"
        if t == "table":
            return str(n)
        if t == "figure" or has_class(n, "captioned-image-container"):
            img = n.find("img")
            cap = n.find("figcaption")
            caption = self.inline(cap).strip() if cap else ""
            return self.image(img, caption) if img else ""
        if has_class(n, "latex-rendered"):
            try:
                expr = json.loads(n.get("data-attrs") or "{}").get("persistentExpression", "")
            except ValueError:
                expr = ""
            return f"$$\n{expr.strip()}\n$$" if expr.strip() else ""
        if has_class(n, "footnote") and n.find(class_="footnote-content"):
            num = n.find(class_="footnote-number")
            body = self.blocks(n.find(class_="footnote-content"))
            body = body.replace("\n", "\n    ")
            self.footnotes.append(f"[^{num.get_text(strip=True) if num else len(self.footnotes) + 1}]: {body}")
            return ""
        if has_class(n, "youtube-wrap") or n.get("data-component-name") == "Youtube2ToDOM":
            try:
                vid = json.loads(n.get("data-attrs") or "{}").get("videoId")
            except ValueError:
                vid = None
            return f"[Video on YouTube](https://www.youtube.com/watch?v={vid})" if vid else ""
        if t == "img":
            return self.image(n)
        if n.get("data-component-name") and t == "div" and not n.find(["p", "img", "hr"]):
            return f"<!-- Substack embed not imported: {n.get('data-component-name')} -->"
        if t in ("div", "section", "article", "span", "picture", "a"):
            return self.blocks(n)
        if t in ("script", "style", "form", "button", "svg", "iframe"):
            return ""
        return self.inline(n).strip()

    def list(self, n, ordered):
        items = []
        for i, li in enumerate(n.find_all("li", recursive=False), 1):
            marker = f"{i}. " if ordered else "- "
            body = self.blocks(li) if li.find(["p", "ul", "ol", "pre", "blockquote"]) else self.inline(li).strip()
            pad = " " * len(marker)
            lines = body.split("\n")
            items.append(marker + lines[0] + "".join("\n" + (pad + l if l else "") for l in lines[1:]))
        loose = any("\n\n" in it for it in items)
        return ("\n\n" if loose else "\n").join(items)

    def convert(self, body_html):
        soup = BeautifulSoup(body_html, "html.parser")
        md = self.blocks(soup)
        md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
        if self.footnotes:
            md += "\n" + "\n\n".join(self.footnotes) + "\n"
        return md


# ---------------------------------------------------------------- main

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "post"


def yaml_str(s):
    return '"' + (s or "").replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="Substack post URL, or a saved .html file")
    ap.add_argument("--title")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--date", help="YYYY-MM-DD (defaults to the post's date, or today)")
    ap.add_argument("--slug", help="folder name under writing/ (defaults to the Substack slug)")
    ap.add_argument("--draft", action="store_true", help="import into writing/_<slug>/ so it isn't published yet")
    ap.add_argument("--force", action="store_true", help="overwrite an existing post folder")
    args = ap.parse_args()

    if re.match(r"https?://", args.source):
        post = fetch_post(args.source)
        title = args.title or post.get("title", "")
        subtitle = args.subtitle or post.get("subtitle") or ""
        date = args.date or (post.get("post_date") or "")[:10]
        slug = args.slug or post.get("slug")
        body = post.get("body_html") or ""
        canonical = post.get("canonical_url") or args.source
    else:
        path = Path(args.source)
        body = path.read_text(encoding="utf-8")
        title = args.title or path.stem
        subtitle, date, canonical = args.subtitle, args.date, ""
        slug = args.slug or re.sub(r"^\d+\.", "", path.stem)

    slug = slugify(slug or title)
    date = date or dt.date.today().isoformat()
    folder = ROOT / "writing" / (("_" if args.draft else "") + slug)
    if (folder / "index.md").exists() and not args.force:
        sys.exit(f"{folder.relative_to(ROOT)} already exists; pass --force to overwrite it")

    conv = Converter(folder / "images")
    md = conv.convert(body)
    front = ["---", f"title: {yaml_str(title)}"]
    if subtitle:
        front.append(f"subtitle: {yaml_str(subtitle)}")
    front.append(f"date: {date}")
    if canonical:
        front.append(f"substack: {canonical}")
    front.append("---")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.md").write_text("\n".join(front) + "\n\n" + md, encoding="utf-8")
    print(f"wrote {(folder / 'index.md').relative_to(ROOT)} with {conv.n_images} image(s)")


if __name__ == "__main__":
    main()
