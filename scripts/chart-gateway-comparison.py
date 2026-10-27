#!/usr/bin/env python3
"""Bar chart for part 3: tokens per second through the same gateway, one request and eight at once, per backend.
Plain SVG, no libraries. Numbers from homelab/vcf-lab/benchmarks/gateway-comparison-2026-10-27.md.
Usage: scripts/chart-gateway-comparison.py -> static/images/rtx-a5000-behind-the-same-service-name/tokens-per-second.svg"""
import os
OUT = os.path.join(os.path.dirname(__file__), "..", "static", "images", "rtx-a5000-behind-the-same-service-name")
SINGLE, PAR, INK, MUTED, GRID = "#b4b2a9", "#76557e", "#2c2c2a", "#6b6a66", "#e1e0d9"
ROWS = [  # label, single, 8 parallel aggregate (None = not run)
    ("Gemma 4 12B, 16 vCPU (PAIS)", 9.3, None),
    ("Gemma 4 12B, RTX A5000 (PAIS)", 72.6, 200),
    ("Qwen3.8 27B, RTX A5000 (PAIS)", 31.2, 154),
    ("qwen3:14b, Ollama on the 4090", 70.5, 103),
    ("Claude Haiku 5.5, Anthropic", 83.9, 703),
    ("Claude Sonnet 5.5, Anthropic", 107.1, 741),
]
def main():
    title = "Tokens per second through the same gateway, same prompt, 400 tokens per answer"
    left, top, barh, gap, width, xmax = 250, 58, 11, 36, 820, 800
    plot_w = width - left - 70
    h = top + len(ROWS) * gap + 48
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" width="{width}" height="{h}" '
         f'font-family="Inter, -apple-system, Helvetica, Arial, sans-serif" font-size="13" role="img" aria-label="{title}">',
         f'<rect width="{width}" height="{h}" fill="#ffffff"/>',
         f'<text x="{left}" y="22" font-size="15" font-weight="500" fill="{INK}">{title}</text>',
         f'<rect x="{left}" y="34" width="10" height="10" rx="2" fill="{SINGLE}"/><text x="{left + 16}" y="43" fill="{MUTED}">one request</text>',
         f'<rect x="{left + 120}" y="34" width="10" height="10" rx="2" fill="{PAR}"/><text x="{left + 136}" y="43" fill="{MUTED}">eight requests at once, added up</text>']
    for i in range(0, 5):
        v = xmax * i / 4; x = left + plot_w * i / 4
        s.append(f'<line x1="{x:.0f}" y1="{top - 4}" x2="{x:.0f}" y2="{h - 36}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{x:.0f}" y="{h - 18}" text-anchor="middle" fill="{MUTED}" font-size="12">{v:g} tok/s</text>')
    for i, (name, a, b) in enumerate(ROWS):
        y = top + i * gap
        s.append(f'<text x="{left - 10}" y="{y + barh + 1}" text-anchor="end" fill="{INK}">{name}</text>')
        for val, color, dy in ((a, SINGLE, 0), (b, PAR, barh + 2)):
            if val is None:
                s.append(f'<text x="{left + 6}" y="{y + dy + barh - 6}" fill="{MUTED}" font-size="12">not run</text>'); continue
            w = max(2, plot_w * min(val, xmax) / xmax)
            s.append(f'<rect x="{left}" y="{y + dy - 4}" width="{w:.1f}" height="{barh}" fill="{color}"/>')
            s.append(f'<text x="{left + w + 6:.1f}" y="{y + dy + barh - 6}" fill="{MUTED}" font-size="12">{val:g}</text>')
    s.append("</svg>")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "tokens-per-second.svg"), "w") as f: f.write("\n".join(s))
    print("written", os.path.join(OUT, "tokens-per-second.svg"))
main()
