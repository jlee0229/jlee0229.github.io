#!/usr/bin/env python3
"""Generate figures/width_threshold.svg from the repo's grid_summary.csv (stdlib only).

Run:  python3 build_figures.py
Plots fraction of seeds that grok vs. hidden width / p^2 for Aff(F_p), ReLU, Wu recipe.
Cells marked EARLIER are not in grid_summary.csv; they are transcribed from the prose of
results/affine/width_grid.md ("earlier runs") and are flagged as such in the caption.
"""
import csv, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CSV = ROOT.parent / "cosets-vs-irreps/results/affine/grid_summary.csv"

P = {"aff7": 7, "aff11": 11, "aff13": 13}
cells = collections.defaultdict(lambda: [0, 0])  # (series, width) -> [grokked, n]
for r in csv.DictReader(open(CSV)):
    if r["act"] != "relu" or r["group"] not in P:
        continue
    series = (r["group"], r["frac"])
    k = (series, int(r["width"]))
    cells[k][1] += 1
    cells[k][0] += r["grokked"] == "True"

# transcribed from width_grid.md prose (earlier runs, not in the csv)
EARLIER = {
    (("aff11", "0.4"), 128): [5, 6],
    (("aff13", "0.4"), 128): [0, 6],
    (("aff13", "0.4"), 256): [2, 2],
}
for k, v in EARLIER.items():
    cells[k] = v

SERIES = [  # key, label, css class
    (("aff7", "0.6"), "p = 7 (60% of pairs)", "s7"),
    (("aff11", "0.4"), "p = 11", "s11"),
    (("aff13", "0.4"), "p = 13", "s13"),
]

W, H = 720, 420
L, R, T, B = 64, 24, 24, 64
XMIN, XMAX = 0.7, 1.6


def px(x): return L + (x - XMIN) / (XMAX - XMIN) * (W - L - R)
def py(y): return T + (1 - y) * (H - T - B)


out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
       f'aria-label="Fraction of seeds that grok versus width over p squared">',
       """<style>
:root{--bg:#fff;--fg:#1c1c1e;--mut:#6b6b70;--grid:#e4e4e8;--s7:#b45309;--s11:#1d4ed8;--s13:#047857}
@media (prefers-color-scheme:dark){:root{--bg:#161618;--fg:#ececf0;--mut:#9a9aa2;--grid:#2e2e34;--s7:#f59e0b;--s11:#6ea0ff;--s13:#34d399}}
text{font:13px system-ui,sans-serif;fill:var(--fg)} .m{fill:var(--mut);font-size:12px}
.g{stroke:var(--grid);stroke-width:1} .ax{stroke:var(--mut);stroke-width:1}
.s7{--c:var(--s7)}.s11{--c:var(--s11)}.s13{--c:var(--s13)}
.ln{fill:none;stroke:var(--c);stroke-width:2} .pt{fill:var(--c)} .lab{fill:var(--c);font-size:12px}
</style>""",
       f'<rect width="{W}" height="{H}" fill="var(--bg)"/>']

for y in (0, 0.25, 0.5, 0.75, 1):
    out.append(f'<line class="g" x1="{L}" x2="{W-R}" y1="{py(y)}" y2="{py(y)}"/>')
    out.append(f'<text class="m" x="{L-8}" y="{py(y)+4}" text-anchor="end">{int(y*100)}%</text>')
for x in (0.8, 1.0, 1.2, 1.4, 1.6):
    out.append(f'<text class="m" x="{px(x)}" y="{H-B+20}" text-anchor="middle">{x:.1f}</text>')
out.append(f'<line x1="{px(1)}" x2="{px(1)}" y1="{T}" y2="{H-B}" stroke="var(--mut)" stroke-dasharray="4 4"/>')
out.append(f'<text class="m" x="{px(1)+6}" y="{T+12}">width = p²</text>')
out.append(f'<line class="ax" x1="{L}" x2="{W-R}" y1="{H-B}" y2="{H-B}"/>')
out.append(f'<text x="{(L+W-R)/2}" y="{H-14}" text-anchor="middle">hidden width / p²</text>')
out.append(f'<text transform="translate(16 {(T+H-B)/2}) rotate(-90)" text-anchor="middle">seeds that grok</text>')

for key, label, cls in SERIES:
    p = P[key[0]]
    pts = sorted((w, g, n) for (s, w), (g, n) in cells.items() if s == key)
    path = " ".join(f"{'M' if i == 0 else 'L'}{px(w/p**2):.1f},{py(g/n):.1f}" for i, (w, g, n) in enumerate(pts))
    out.append(f'<g class="{cls}"><path class="ln" d="{path}"/>')
    for w, g, n in pts:
        out.append(f'<circle class="pt" cx="{px(w/p**2):.1f}" cy="{py(g/n):.1f}" r="{3+min(n,6)*0.8:.1f}">'
                   f'<title>p={p}, width {w}: {g}/{n} seeds grok</title></circle>')
    i = [s[0] for s in SERIES].index(key)
    out.append(f'<circle class="pt" cx="{L+16}" cy="{T+30+i*18}" r="5"/>'
               f'<text class="lab" x="{L+28}" y="{T+34+i*18}">{label}</text></g>')
out.append("</svg>")

(ROOT / "figures").mkdir(exist_ok=True)
(ROOT / "figures/width_threshold.svg").write_text("\n".join(out))
for key, label, _ in SERIES:
    print(label, sorted((w, f"{g}/{n}") for (s, w), (g, n) in cells.items() if s == key))
