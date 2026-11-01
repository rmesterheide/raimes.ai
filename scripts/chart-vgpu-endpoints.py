#!/usr/bin/env python3
"""Bar chart for "Route to Private AI Services 3.0, part 4": tokens per second from one RTX A5000 split into NVIDIA vGPU
slices, Gemma 4 12B QAT on llama.cpp through the PAIS gateway, 400 tokens per answer. Per row: what one tenant gets and
what the card delivers in total. Plain SVG, no libraries, same style as chart-gpu-sharing.py. Numbers from
homelab/vcf-lab/benchmarks/vgpu-a5000-2026-10-31.md.
Usage: scripts/chart-vgpu-endpoints.py -> static/images/<slug>/tokens-per-second.svg"""
import os
SLUG = "one-card-three-endpoints-the-numbers"
OUT = os.path.join(os.path.dirname(__file__), "..", "static", "images", SLUG)
ONE, SUM, INK, MUTED, GRID = "#b4b2a9", "#76557e", "#2c2c2a", "#6b6a66", "#e1e0d9"
# label, what one tenant gets (tok/s), what the card delivers in total (tok/s)
ROWS = [
    ("Passthrough, whole card (part 3), 4 requests", 242.7, 242.7),
    ("One 12 GB slice alone, 4 requests", 228.1, 228.1),
    ("Two 12 GB slices, both busy, 4 + 4 requests", 109.1, 213.2),
    ("Two 12 GB slices, both busy, 8 + 8 requests", 88.7, 177.2),
    ("12 GB chat next to a 4 GB embedding tenant, 4 requests", 220.0, 220.0),
]
def main():
    title = "One RTX A5000 as vGPU slices, Gemma 4 12B: tokens per second through the PAIS gateway"
    left, top, barh, gap, width, xmax = 350, 58, 11, 36, 880, 250
    plot_w = width - left - 70
    h = top + len(ROWS) * gap + 76
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" width="{width}" height="{h}" '
         f'font-family="Inter, -apple-system, Helvetica, Arial, sans-serif" font-size="13" role="img" aria-label="{title}">',
         f'<rect width="{width}" height="{h}" fill="#ffffff"/>',
         f'<text x="{left}" y="22" font-size="15" font-weight="500" fill="{INK}">{title}</text>',
         f'<rect x="{left}" y="34" width="10" height="10" rx="2" fill="{ONE}"/><text x="{left + 16}" y="43" fill="{MUTED}">one tenant gets</text>',
         f'<rect x="{left + 130}" y="34" width="10" height="10" rx="2" fill="{SUM}"/><text x="{left + 146}" y="43" fill="{MUTED}">the card delivers in total</text>']
    for i in range(0, 6):
        v = xmax * i / 5; x = left + plot_w * i / 5
        s.append(f'<line x1="{x:.0f}" y1="{top - 4}" x2="{x:.0f}" y2="{h - 64}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{x:.0f}" y="{h - 46}" text-anchor="middle" fill="{MUTED}" font-size="12">{v:g} tok/s</text>')
    for i, (name, a, b) in enumerate(ROWS):
        y = top + i * gap
        s.append(f'<text x="{left - 10}" y="{y + barh + 1}" text-anchor="end" fill="{INK}">{name}</text>')
        for val, color, dy in ((a, ONE, 0), (b, SUM, barh + 2)):
            w = max(2, plot_w * min(val, xmax) / xmax)
            s.append(f'<rect x="{left}" y="{y + dy - 4}" width="{w:.1f}" height="{barh}" fill="{color}"/>')
            s.append(f'<text x="{left + w + 6:.1f}" y="{y + dy + barh - 6}" fill="{MUTED}" font-size="12">{val:g}</text>')
    s.append(f'<text x="{left}" y="{h - 24}" fill="{MUTED}" font-size="11">llama.cpp server-cuda-b11913, Gemma 4 12B QAT q4_0, 400 tokens per answer, 16k context, requests through the PAIS gateway; one request alone on a 12 GB slice: 68.9 tok/s.</text>')
    s.append(f'<text x="{left}" y="{h - 10}" fill="{MUTED}" font-size="11">vGPU Manager 580.178.05 (NVIDIA AI Enterprise 7.8), guest driver 580.105.08, RTXA5000-12C and -4C profiles, best-effort scheduler, ECC on. Lab numbers, one card, one evening.</text>')
    s.append("</svg>")
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "tokens-per-second.svg")
    with open(p, "w") as f: f.write("\n".join(s))
    print("written", p)
main()
