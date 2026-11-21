# jlee0229.github.io

Jaeho Lee's personal site and blog. Static HTML and one stylesheet, served by GitHub Pages from the main branch (`.nojekyll`). Hand-written pages need no build. Blog posts are Markdown that `build.py` turns into HTML; `.github/workflows/build.yml` runs it on push to main and commits the output, so Pages settings stay "deploy from branch". Links are relative so the site works on github.io, a custom domain, or opened locally.

Design (Nov 2026): patterned on the personal sites featured on deadsimplesites.com (Steph Ango, Paco Coursey, Lee Robinson, Tom MacWright, the Thinking Machines blog). One 640px column; name left and muted links right in the header; Inter 15px for pages, Source Serif 4 18px for post bodies (`--read` in `style.css`); weight 500 and a muted color instead of large headings; warm off-white `#fcfcfa` / off-black `#1c1b1a`, dark mode through `prefers-color-scheme`. Fonts are self-hosted in `fonts/`. The 7x7 panmagic matrix is a small mark above the bio.

## Layout

- `index.html`: home. Header, the matrix mark (x -> 2x+1 mod 7), bio, contact line, then Writing (generated between `<!-- posts -->` markers; don't edit by hand), Research, Projects, News as one-line rows (`.rows`: title, muted `.s` lines, muted date `.d` on the right).
- `writing/<slug>/index.md` + `images/`: blog posts. Front matter `title`, `date` (YYYY-MM-DD), optional `subtitle`, `substack`. `build.py` writes `index.html` next to each, the home Writing list, the Writing nav link (`<!-- nav-writing -->` slots), and `feed.xml`. Folders starting with `_` are drafts and never built (`build.py --preview` builds them into the gitignored `_preview/`). Math: `$...$` and `$$...$$`, rendered by KaTeX via `math.js`. See `writing/README.md`.
- `tools/import_substack.py`: Substack post URL -> Markdown post with images downloaded. `tools/test_import.py` checks the converter. The Action takes a `substack_url` input.
- `cosets-vs-irreps/`: experiment page (URL is linked from the resume; keep it). `writeup.html` is a standalone report with its own older styling.
- `figures/`: `width_threshold.svg` (from `build_figures.py`, used on the cosets page), `perm7.svg`, `perm11.svg`, `hivemusic.jpg`, `humanpath.jpg` (thumbnails from the previous design; the home page no longer shows thumbnails).
- `style.css`: the only stylesheet. Sections are `<section id=...><h2>Name</h2>`; the h2 renders as a muted label, so it needs no extra markup.

## What goes on the site

Be selective. Published or accepted papers, finished experiments, finished projects, short news, and links out. No planned or unrun work, no papers under review, no course lists, no awards list, no "last updated" date.

- News: Jaeho keeps it current. Newest first, `<time datetime="YYYY-MM">Mon YYYY</time>`, one plain sentence each. Keep about five; drop the oldest. Do not add the YC IAP acceptance.
- Papers: a `.rows` entry: title, a muted line `With Coauthors · <i>Venue</i>` plus links that exist, one sentence that states the result, year on the right. Jaeho and Koshkin post to arXiv only after a paper is published, so an accepted paper has no links (title is a plain `<span class="t">`) until the journal publishes it; then link the journal page and add arXiv once posted.
- Pending: "The affine group of integers modulo n: conjugacy classes and representations" (Integers, accepted Nov 2026). When it's published, link the title to the journal page, change "to appear" to the volume and year, and add arXiv when posted.
- The PUMP paper is a companion line inside the Discrete Mathematics entry, not its own entry.
- Writing: Jaeho writes on Substack and copies posts here (Nov 2026 decision; this replaces the earlier "don't host posts here"). Import with the Action or `tools/import_substack.py`.
- Photo: none yet. If one is added, ask whether it should replace the matrix mark.
- New experiment page: usually better as a Markdown post. For a hand-written page, copy `cosets-vs-irreps/index.html` into a new folder and replace the content. For math, add KaTeX in the page head:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\(',right:'\\)',display:false}],throwOnError:false})"></script>
```

## No AI tells

- Visual: no cards, pill badges, shadows, gradients, rounded boxes, icon rows, emoji, uppercase letter-spaced labels, numbered eyebrows, left-border callouts, hero taglines, or decorative stock images. Images are real figures from the work. No logo mark next to the name.
- Copy: first person, plain, specific. No em dashes. No forced groups of three, no "Most recently:" style fragments, no inflated words (pivotal, showcase, passionate, leverage). Active voice. Lead with the result; say what failed. Say "research in the Fiete Lab", not "UROP".
- Headings and nav in sentence case.

## Open items

- Custom domain: add a `CNAME` file with the domain, set DNS (apex A records to GitHub Pages, or a `www` CNAME to `jlee0229.github.io`), then enable HTTPS in repo Settings > Pages.
- `cosets-vs-irreps/writeup.html` still uses the old look (Fraunces headings, mono eyebrows, colored callout boxes); restyle to `style.css`.
