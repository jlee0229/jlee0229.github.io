# jlee0229.github.io

Jaeho Lee's personal site. Plain static HTML and one stylesheet, served by GitHub Pages (`.nojekyll`, no build step).

## Layout

- `index.html`: home (short bio, research list, newest writing once posts exist)
- `research/index.html`: papers, then experiments
- `writing/index.html`: post index, newest first, grouped by year
- `writing/<slug>/index.html`: one folder per post
- `cosets-vs-irreps/`: experiment page (URL is linked from the resume; keep it). `writeup.html` is a standalone report with its own older styling.
- `_templates/post.html`: copy this to start a post or experiment page
- `figures/`: SVG figures (`build_figures.py` regenerates `width_threshold.svg`)
- `style.css`: the only stylesheet; supports dark mode through `prefers-color-scheme`

## Adding things

- Post: copy `_templates/post.html` to `writing/<slug>/index.html`, fill every TODO, delete the `noindex` line and the KaTeX lines if there is no math. Add an entry to `writing/index.html` (remove the "Nothing here yet" line on the first post) and to the commented Writing block on the home page (keep the three newest).
- Paper: add a `.row` to Papers in `research/index.html` (year, linked title, authors, venue, `.links` with arXiv/Journal/PDF/BibTeX that exist). Add it to the home Research list too.
- Experiment: page built from the post template under its own folder; list it under Experiments with a status line in `.note` (Planned / Pilot not run / Done).
- Bump the "Updated" date in each touched page's footer.

## Style rules (the point of the redesign)

- One serif (Source Serif 4), white page, blue underlined links, a 640px column set left. Nothing else.
- No cards, pills/badges, shadows, gradients, rounded boxes, icons, emoji, uppercase letter-spaced labels, numbered section eyebrows, left-border callouts, or hero taglines.
- Status and caveats are plain italic grey text, not tags.
- Copy: first person, plain, specific. No em dashes. Lead with the result; say what failed.
- Math: KaTeX via `\( \)` inline and `$$ $$` display on pages that need it; plain HTML sub/sup is fine for short expressions.

## Open items

- Custom domain: add a `CNAME` file with the domain, set DNS (apex A records to GitHub Pages, or a `www` CNAME to `jlee0229.github.io`), then enable HTTPS in repo Settings > Pages.
- RSS: add `feed.xml` once there are posts, then link it from the writing page and footer.
- PDFs and BibTeX for the two papers: put them in `papers/` and add the links.
- `cosets-vs-irreps/writeup.html` still uses the old look (Fraunces headings, mono eyebrows, colored callout boxes); restyle to `style.css` when convenient.
