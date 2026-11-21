"""Checks the Substack converter on HTML shaped like Substack's body_html. Run: python3 tools/test_import.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from import_substack import Converter  # noqa: E402

SAMPLE = """
<p>Let <em>G </em>be a group and <strong>n_1</strong> a snake_case name. It costs $5.<a class="footnote-anchor" data-component-name="FootnoteAnchorToDOM" id="footnote-anchor-1" href="#footnote-1" target="_self">1</a></p>
<h2>Characters</h2>
<div class="latex-rendered" data-attrs="{&quot;persistentExpression&quot;:&quot;\\\\sum_{g} \\\\chi(g) = 0&quot;,&quot;id&quot;:&quot;X&quot;}" data-component-name="LatexBlockToDOM"></div>
<div class="captioned-image-container"><figure><a class="image-link image2" href="https://substackcdn.com/x"><div class="image2-inset"><picture><img src="https://substackcdn.com/w_1456/x.png" data-attrs="{&quot;src&quot;:&quot;https://substack-post-media.s3.amazonaws.com/public/images/abc.png&quot;}" alt="A matrix"></picture><div class="image-link-expand"><div class="pencraft"></div></div></div></a><figcaption class="image-caption">The matrix of <em>x</em> ↦ 2<em>x</em>+1</figcaption></figure></div>
<ul><li><p>one</p></li><li><p>two <code>a*b</code></p></li></ul>
<ol><li><p>first</p></li><li><p>second</p></li></ol>
<blockquote><p>quoted</p></blockquote>
<pre><code>def f(x):
    return x * 2</code></pre>
<div><hr></div>
<p>1. not a list</p>
<div class="subscription-widget-wrap-editor" data-component-name="SubscribeWidgetToDOM"><div class="subscription-widget"><p>Subscribe!</p></div></div>
<div class="footnote" data-component-name="FootnoteToDOM"><a id="footnote-1" href="#footnote-anchor-1" class="footnote-number" contenteditable="false" target="_self">1</a><div class="footnote-content"><p>A note with <em>emphasis</em>.</p></div></div>
"""

EXPECTED = r"""Let *G* be a group and **n_1** a snake_case name. It costs \$5.[^1]

## Characters

$$
\sum_{g} \chi(g) = 0
$$

![A matrix](https://substack-post-media.s3.amazonaws.com/public/images/abc.png "The matrix of *x* ↦ 2*x*+1")

- one
- two `a*b`

1. first
2. second

> quoted

```
def f(x):
    return x * 2
```

---

1\. not a list

[^1]: A note with *emphasis*.
"""

got = Converter(Path("/nonexistent"), download=False).convert(SAMPLE)
if got != EXPECTED:
    import difflib
    print("".join(difflib.unified_diff(EXPECTED.splitlines(True), got.splitlines(True), "expected", "got")))
    sys.exit(1)
print("ok")
