# jlee0229.github.io

Jaeho Lee's personal site. Plain static HTML and one stylesheet, served by GitHub Pages (`.nojekyll`, no build step). Links are relative so the site works on github.io, a custom domain, or opened locally.

Design source: option A ("Panmagic motif") on the "Jaeho Lee — site options" Design canvas on claude.ai (Nov 2026).

## Layout

- `index.html`: the whole site. Top bar (name, section links), intro (bio on the left; the 7x7 panmagic matrix x -> 2x+1 mod 7 with its caption and the contact block on the right), then News, Research, Projects.
- `cosets-vs-irreps/`: experiment page (URL is linked from the resume; keep it). `writeup.html` is a standalone report with its own older styling.
- `figures/`: thumbnails and figures. `width_threshold.svg` (from `build_figures.py`), `perm7.svg` (x -> 2x+1 mod 7), `perm11.svg` (x -> 3x+2 mod 11), `hivemusic.jpg` (screenshot of playhivemusic.com).
- `style.css`: the only stylesheet. System font stack, one accent (`--accent`, crimson; lighter in dark mode), dark mode through `prefers-color-scheme`. Section headings get the accent square and hairline rule from CSS, so new `<h2>`s need no extra markup.

## What goes on the site

Be selective. Published or accepted papers, finished experiments, finished projects, short news, and links out. No planned or unrun work, no papers under review, no course lists, no awards list, no "last updated" date.

- News: Jaeho keeps it current. Newest first, `<time datetime="YYYY-MM">Mon YYYY</time>`, one plain sentence each. Keep about five; drop the oldest. Do not add the YC IAP acceptance.
- Papers: an `.items` row with a real figure as the thumbnail (8:5, 200x125 box), title, byline `Coauthors, <b>Jaeho Lee</b> · <i>Venue, year</i>`, one sentence that states the result, and `.links` only for links that exist. Jaeho and Koshkin post to arXiv only after a paper is published, so an accepted paper has no links (title is a plain `<span class="item-title">`) until the journal publishes it; then link the journal page and add arXiv once posted.
- Pending: "The affine group of integers modulo n: conjugacy classes and representations" (Integers, accepted Nov 2026). When it's published, link the title to the journal page, change "to appear" to the volume and year, and add arXiv when posted.
- The PUMP paper is a companion line inside the Discrete Mathematics entry, not its own entry.
- Writing lives on Substack. When there's a post worth pointing to, uncomment the Writing block in `index.html` and add a "Writing" nav link. Don't host posts here.
- Photo: none yet. If one is added, put it at `figures/photo.jpg` above the matrix figure in `.side` (or ask whether it should replace the matrix).
- New experiment page: copy `cosets-vs-irreps/index.html` into a new folder and replace the content. For math, add KaTeX in the page head:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\(',right:'\\)',display:false}],throwOnError:false})"></script>
```

## No AI tells

- Visual: no cards, pill badges, shadows, gradients, rounded boxes, icon rows, emoji, uppercase letter-spaced labels, numbered eyebrows, left-border callouts, hero taglines, or decorative stock images. Thumbnails are real figures from the work. No logo mark next to the name.
- Copy: first person, plain, specific. No em dashes. No forced groups of three, no "Most recently:" style fragments, no inflated words (pivotal, showcase, passionate, leverage). Active voice. Lead with the result; say what failed. Say "research in the Fiete Lab", not "UROP".
- Headings and nav in sentence case.

## Open items

- Custom domain: add a `CNAME` file with the domain, set DNS (apex A records to GitHub Pages, or a `www` CNAME to `jlee0229.github.io`), then enable HTTPS in repo Settings > Pages.
- `cosets-vs-irreps/writeup.html` still uses the old look (Fraunces headings, mono eyebrows, colored callout boxes); restyle to `style.css`.
