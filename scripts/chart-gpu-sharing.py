#!/usr/bin/env python3
"""Bar chart for "Sharing one GPU on the Kubernetes layer": tokens per second from one RTX A5000, Gemma 4 12B QAT on
llama.cpp, 400 tokens per answer, load sent straight to llama-server. Three ways to use the card: one instance alone,
two instances with time-slicing, two instances with MPS. Per row: what one busy instance gets, what both get together.
Plain SVG, no libraries. Numbers from homelab/vcf-lab/gpu-sharing-dra-plan.md (section 5) once the runs are in.
Usage: scripts/chart-gpu-sharing.py -> static/images/sharing-one-gpu-on-the-kubernetes-layer/tokens-per-second.svg"""
import os
OUT = os.path.join(os.path.dirname(__file__), "..", "static", "images", "sharing-one-gpu-on-the-kubernetes-layer")
ONE, SUM, INK, MUTED, GRID = "#b4b2a9", "#76557e", "#2c2c2a", "#6b6a66", "#e1e0d9"
# label, per-instance tok/s at 4 parallel requests, card total at 4 parallel per instance (None = pending)
ROWS = [
    ("One instance, whole card (control)", 201.6, 201.6),
    ("Two instances, time-slicing, one busy", 202.9, 202.9),
    ("Two instances, time-slicing, both busy", 96.0, 192.0),
    ("Two instances, MPS 50/50, both busy", 106.1, 212.2),
    ("Two VMs, vGPU 12 GB each (part 4)", None, None),
]
SINGLE_STREAM = {"control": 75.9}   # shown in the footnote
def main():
    title = "One RTX A5000, Gemma 4 12B: tokens per second with four requests per instance"
    left, top, barh, gap, width, xmax = 290, 58, 11, 36, 820, 250
    plot_w = width - left - 70
    h = top + len(ROWS) * gap + 64
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" width="{width}" height="{h}" '
         f'font-family="Inter, -apple-system, Helvetica, Arial, sans-serif" font-size="13" role="img" aria-label="{title}">',
         f'<rect width="{width}" height="{h}" fill="#ffffff"/>',
         f'<text x="{left}" y="22" font-size="15" font-weight="500" fill="{INK}">{title}</text>',
         f'<rect x="{left}" y="34" width="10" height="10" rx="2" fill="{ONE}"/><text x="{left + 16}" y="43" fill="{MUTED}">one instance gets</text>',
         f'<rect x="{left + 130}" y="34" width="10" height="10" rx="2" fill="{SUM}"/><text x="{left + 146}" y="43" fill="{MUTED}">the card delivers in total</text>']
    for i in range(0, 6):
        v = xmax * i / 5; x = left + plot_w * i / 5
        s.append(f'<line x1="{x:.0f}" y1="{top - 4}" x2="{x:.0f}" y2="{h - 52}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{x:.0f}" y="{h - 34}" text-anchor="middle" fill="{MUTED}" font-size="12">{v:g} tok/s</text>')
    for i, (name, a, b) in enumerate(ROWS):
        y = top + i * gap
        s.append(f'<text x="{left - 10}" y="{y + barh + 1}" text-anchor="end" fill="{INK}">{name}</text>')
        for val, color, dy in ((a, ONE, 0), (b, SUM, barh + 2)):
            if val is None:
                s.append(f'<text x="{left + 6}" y="{y + dy + barh - 6}" fill="{MUTED}" font-size="12">pending</text>'); continue
            w = max(2, plot_w * min(val, xmax) / xmax)
            s.append(f'<rect x="{left}" y="{y + dy - 4}" width="{w:.1f}" height="{barh}" fill="{color}"/>')
            s.append(f'<text x="{left + w + 6:.1f}" y="{y + dy + barh - 6}" fill="{MUTED}" font-size="12">{val:g}</text>')
    s.append(f'<text x="{left}" y="{h - 12}" fill="{MUTED}" font-size="11">llama.cpp server-cuda-b11913, Gemma 4 12B QAT q4_0, 400 tokens per answer, 16k context, four parallel requests per instance; '
             f'one request alone: {SINGLE_STREAM["control"]:g} tok/s. VKS 1.36.4, GPU Operator 26.7.2, DRA driver 0.5.1. Lab numbers, one card, one evening.</text>')
    s.append("</svg>")
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "tokens-per-second.svg")
    with open(p, "w") as f: f.write("\n".join(s))
    print("written", p)
main()
