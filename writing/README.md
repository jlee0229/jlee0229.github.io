# Writing

Each post is a folder: `writing/<slug>/index.md`, with its images in `writing/<slug>/images/`.
The post appears at `/writing/<slug>/` and in the Writing list on the home page.

## Import a Substack post (easiest)

On GitHub, open **Actions → Build site → Run workflow**, paste the post URL, and click Run.
The workflow downloads the post and its images, builds the page, and commits both. The post is
live a minute or two later. Tick "draft" to import without publishing.

From a terminal, the same thing:

```
pip install -r requirements.txt
python3 tools/import_substack.py https://yourname.substack.com/p/some-post
python3 build.py
```

Substack has no inline math, so after importing, you can open `index.md` and turn things like
`G_1` into `$G_1$`. LaTeX blocks come across as `$$ ... $$`.

## Write or paste one by hand

Create `writing/my-post/index.md`:

```markdown
---
title: My post
subtitle: One optional line under the title
date: 2026-11-21
substack: https://yourname.substack.com/p/my-post   (optional, adds an "Also on Substack" link)
---

Text with inline math $x \mapsto 2x + 1$ and display math:

$$
\sum_{g \in G} \chi(g) = 0
$$

![Alt text for screen readers](images/figure.png "Caption shown under the image, can use $math$")
```

Push it to main and the Action builds it. To preview locally first: `python3 build.py --preview`,
then open `_preview/index.html`.

`writing/_example/index.md` shows every element: footnotes, tables, code, aligned equations.

## Drafts

A folder whose name starts with `_` is a draft. It is never built into the site; rename the
folder to publish. The repository is public, though, so a draft's Markdown can be read on GitHub.
Keep drafts you don't want seen on Substack or your own computer until they're ready.

## Notes

- Dollar signs for money (`$5 and $10`) stay text. Math needs no space after the opening `$`.
- `\begin{align} ... \end{align}` works on its own lines.
- Code blocks take a language for highlighting: ```` ```python ````.
- An image on its own line becomes a figure; its quoted title becomes the caption.
