# jlee0229.github.io

Jaeho Lee's personal site. Plain static HTML and one stylesheet, served by GitHub Pages (`.nojekyll`, no build step). Links are relative so the site works on github.io, a custom domain, or opened locally.

Design source: the "Jaeho Lee — personal website" Design canvas on claude.ai (v2, Nov 2026). Inspired by academic homepages (ankitbiswas.me, Lena Voita, Soumith Chintala) but without al-folio's card grid and pill badges.

## Layout

- `index.html`: the whole site: top bar with section links, name + three-paragraph bio with contact on the right, News, Research, Projects.
- `cosets-vs-irreps/`: experiment page (URL is linked from the resume; keep it). `writeup.html` is a standalone report with its own older styling.
- `figures/`: thumbnails and figures. `width_threshold.svg` (from `build_figures.py`), `perm7.svg` and `perm11.svg` (affine panmagic permutation matrices x -> 2x+1 mod 7 and x -> 3x+2 mod 11), `hivemusic.jpg` (screenshot of playhivemusic.com).
- `style.css`: the only stylesheet; system font stack; dark mode through `prefers-color-scheme`.

## What goes on the site

Be selective. Published papers, finished experiments, finished projects, short news, and links out. No planned or unrun work, no course lists, no awards list, no "last updated" date.

- News: keep it current (Jaeho will update it). Newest first, `<time datetime="YYYY-MM">Mon YYYY</time>`, one plain sentence each. Keep about five; drop the oldest. Do not add the YC IAP acceptance.
- Research or project entry: an `.items` row with a real figure or screenshot as the thumbnail (8:5, 192x120 box), linked title, authors with Jaeho in `<b>`, venue line, one sentence that states the result, and `.links` only for links that exist.
- Writing lives on Substack. When there's a post worth pointing to, uncomment the Writing block in `index.html` and add a "Writing" nav link. Don't host posts here.
- Photo: none yet. When there is one, put it at `figures/photo.jpg` and use the commented `<img>` in the contact aside.
- New experiment page: copy `cosets-vs-irreps/index.html` into a new folder and replace the content. For math, add KaTeX in the page head:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\(',right:'\\)',display:false}],throwOnError:false})"></script>
```

## No AI tells

- Visual: no cards, pill badges, shadows, gradients, rounded boxes, icon rows, emoji, uppercase letter-spaced labels, numbered eyebrows, left-border callouts, hero taglines, or decorative stock images. Thumbnails are real figures from the work.
- Copy: first person, plain, specific. No em dashes. No forced groups of three, no "Most recently:" style fragments, no inflated words (pivotal, showcase, passionate, leverage). Active voice. Lead with the result; say what failed.
- Headings and nav in sentence case.

## Open items

- Custom domain: add a `CNAME` file with the domain, set DNS (apex A records to GitHub Pages, or a `www` CNAME to `jlee0229.github.io`), then enable HTTPS in repo Settings > Pages.
- `cosets-vs-irreps/writeup.html` still uses the old look (Fraunces headings, mono eyebrows, colored callout boxes); restyle to `style.css`.
