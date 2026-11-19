# jlee0229.github.io

Jaeho Lee's personal site. Plain static HTML and one stylesheet, served by GitHub Pages (`.nojekyll`, no build step). Links are relative so the site works on github.io, a custom domain, or opened locally.

## Layout

- `index.html`: the whole site in one page: two-line bio, Papers, Experiments, footer links.
- `cosets-vs-irreps/`: experiment page (URL is linked from the resume; keep it). `writeup.html` is a standalone report with its own older styling.
- `figures/`: SVG figures (`build_figures.py` regenerates `width_threshold.svg`).
- `style.css`: the only stylesheet; dark mode through `prefers-color-scheme`.

## What goes on the site

Be selective. Published papers, finished experiments, and links out. No planned or unrun work, no course lists, no awards list, no "now" page, no "last updated" date.

- Writing lives on Substack or another platform. When a post is worth pointing to, uncomment the Writing block in `index.html` and link the post directly; add a "Writing" footer link to the publication. Don't host posts here.
- Paper: add a `.row` under Papers (year, linked title, "With coauthors. *Venue*.", `.links` only for links that exist).
- Finished experiment: copy `cosets-vs-irreps/index.html` into a new folder and replace the content; list it under Experiments with one sentence that states the result. For math, add KaTeX in the page head:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\(',right:'\\)',display:false}],throwOnError:false})"></script>
```

## Style rules

- One serif (Source Serif 4), white page, blue underlined links, a 640px column set left. Nothing else.
- No cards, pills/badges, shadows, gradients, rounded boxes, icons, emoji, uppercase letter-spaced labels, numbered section eyebrows, left-border callouts, or hero taglines.
- Caveats are plain italic grey text, not tags.
- Copy: first person, plain, specific. No em dashes. Lead with the result; say what failed.

## Open items

- Custom domain: add a `CNAME` file with the domain, set DNS (apex A records to GitHub Pages, or a `www` CNAME to `jlee0229.github.io`), then enable HTTPS in repo Settings > Pages.
- `cosets-vs-irreps/writeup.html` still uses the old look (Fraunces headings, mono eyebrows, colored callout boxes); restyle to `style.css` when convenient.
