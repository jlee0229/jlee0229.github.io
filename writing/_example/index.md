---
title: Formatting example
subtitle: A draft that shows every element a post can use. Folders starting with "_" are never published.
date: 2026-11-21
---

This is a paragraph with *italics*, **bold**, `inline code`, a [link](https://example.com), and inline math like $\mathrm{Aff}(\mathbb{Z}_n) = \mathbb{Z}_n \rtimes \mathbb{Z}_n^\times$ and $x \mapsto ax + b$. Dollar amounts such as $5 and $10 stay as text.[^money]

## A section heading

Display math goes between double dollar signs:

$$
\chi_\rho(g) = \operatorname{tr} \rho(g), \qquad \frac{1}{|G|} \sum_{g \in G} \chi_\rho(g)\overline{\chi_\sigma(g)} = \delta_{\rho\sigma}.
$$

Aligned equations work too:

\begin{align}
(a, b)(c, d) &= (ac,\; ad + b) \\
(a, b)^{-1} &= (a^{-1},\; -a^{-1}b)
\end{align}

![An 11 by 11 permutation matrix](images/perm11.svg "The permutation matrix of $x \mapsto 3x + 2 \bmod 11$. Captions come from the quoted text after the image path.")

### A smaller heading

1. Numbered lists
2. with a second item that runs long enough to wrap onto another line so you can see the hanging indent
3. and a third

- Bullets
- work the same way

> A block quote, for when you quote someone else's words at length.

```python
def affine(a, b, n):
    """Permutation x -> a*x + b mod n."""
    return [(a * x + b) % n for x in range(n)]  # a must be a unit mod n
```

| Group | Order | Models |
|---|---|---|
| $S_5$ | 120 | 50 |
| $D_{59}$ | 118 | 4 |
| $\mathrm{Aff}(\mathbb{Z}_{11})$ | 110 | 8 |

---

A last paragraph after a rule, with a second footnote.[^2]

[^money]: Footnotes collect at the bottom of the post.
[^2]: They can hold math too: $p^2$ neurons.
