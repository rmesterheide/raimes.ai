#!/usr/bin/env python3
"""Chart for "Route to Private AI Services 3.0, part 5": the same 30 agent questions against four setups.
Left panel: median seconds per question. Right panel: tokens per question, input and output stacked.
Plain SVG, no libraries, same style as chart-vgpu-endpoints.py. Numbers from
homelab/vcf-lab/benchmarks/agent-tool-calls-2026-11-07.md (runs baseline, A, B, F).
Usage: scripts/chart-agent-tool-calls.py -> static/images/<slug>/agent-tool-calls.svg"""
import os
SLUG = "an-agent-that-calls-tools-on-a-small-local-model"
OUT = os.path.join(os.path.dirname(__file__), "..", "static", "images", SLUG)
GREY, MAIN, INK, MUTED, GRID = "#b4b2a9", "#76557e", "#2c2c2a", "#6b6a66", "#e1e0d9"
# label, sub label, median seconds, tokens in, tokens out (per question)
ROWS = [
    ("Qwen3 4B on a 4 GB slice", "first instructions · 24 of 30 good", 3.1, 1991, 252),
    ("Qwen3 4B on a 4 GB slice", "/no_think as first line · 30 of 30 good", 1.4, 896, 91),
    ("Qwen3 14B on the RTX 4090 route", "thinking stays on · 22 of 30 good", 9.9, 766, 346),
    ("Qwen3 8B on an 8 GB slice", "first instructions · 30 of 30 good", 1.6, 884, 87),
]
def main():
    title = "One agent with four tools, 30 questions: time and tokens per question"
    width, top, gap, barh = 980, 86, 52, 14
    ax, aw, amax = 300, 200, 10.0      # panel A: seconds
    bx, bw, bmax = 590, 240, 2500.0    # panel B: tokens
    h = top + len(ROWS) * gap + 70
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" width="{width}" height="{h}" '
         f'font-family="Inter, -apple-system, Helvetica, Arial, sans-serif" font-size="13" role="img" aria-label="{title}">',
         f'<rect width="{width}" height="{h}" fill="#ffffff"/>',
         f'<text x="20" y="24" font-size="15" font-weight="500" fill="{INK}">{title}</text>',
         f'<text x="{ax}" y="56" fill="{INK}" font-weight="500">Median time per question</text>',
         f'<text x="{bx}" y="56" fill="{INK}" font-weight="500">Tokens per question</text>',
         f'<rect x="{bx + 150}" y="46" width="10" height="10" rx="2" fill="{GREY}"/><text x="{bx + 166}" y="56" fill="{MUTED}">in</text>',
         f'<rect x="{bx + 190}" y="46" width="10" height="10" rx="2" fill="{MAIN}"/><text x="{bx + 206}" y="56" fill="{MUTED}">out</text>']
    y0, y1 = top - 14, top + len(ROWS) * gap - 16
    for i in range(0, 6):
        x = ax + aw * i / 5
        s.append(f'<line x1="{x:.0f}" y1="{y0}" x2="{x:.0f}" y2="{y1}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{x:.0f}" y="{y1 + 16}" text-anchor="middle" fill="{MUTED}" font-size="12">{amax * i / 5:g} s</text>')
        x = bx + bw * i / 5
        s.append(f'<line x1="{x:.0f}" y1="{y0}" x2="{x:.0f}" y2="{y1}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{x:.0f}" y="{y1 + 16}" text-anchor="middle" fill="{MUTED}" font-size="12">{int(bmax * i / 5):,}</text>')
    for i, (name, sub, sec, tin, tout) in enumerate(ROWS):
        y = top + i * gap
        s.append(f'<text x="{ax - 14}" y="{y + 4}" text-anchor="end" fill="{INK}">{name}</text>')
        s.append(f'<text x="{ax - 14}" y="{y + 21}" text-anchor="end" fill="{MUTED}" font-size="12">{sub}</text>')
        w = aw * sec / amax
        s.append(f'<rect x="{ax}" y="{y - 2}" width="{w:.1f}" height="{barh}" fill="{MAIN}"/>')
        s.append(f'<text x="{ax + w + 6:.1f}" y="{y + 10}" fill="{MUTED}" font-size="12">{sec:g} s</text>')
        wi, wo = bw * tin / bmax, bw * tout / bmax
        s.append(f'<rect x="{bx}" y="{y - 2}" width="{wi:.1f}" height="{barh}" fill="{GREY}"/>')
        s.append(f'<rect x="{bx + wi + 2:.1f}" y="{y - 2}" width="{wo:.1f}" height="{barh}" fill="{MAIN}"/>')
        s.append(f'<text x="{bx + wi + wo + 8:.1f}" y="{y + 10}" fill="{MUTED}" font-size="12">{tin:,} in · {tout:,} out</text>')
    s.append(f'<text x="20" y="{h - 26}" fill="{MUTED}" font-size="11">Private AI Services 3.0 agent endpoint, 30 questions from a list of 12 (8 need a tool), 3 in parallel, max_tokens 400, temperature 0. Tokens from the usage block of each answer.</text>')
    s.append(f'<text x="20" y="{h - 12}" fill="{MUTED}" font-size="11">Local endpoints: llama.cpp, Q4_K_M files, reasoning budget 0, vGPU slices of one RTX A5000. External route: Ollama on an RTX 4090. Lab numbers from one evening, 7 November 2026.</text>')
    s.append("</svg>")
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "agent-tool-calls.svg")
    with open(p, "w") as f: f.write("\n".join(s))
    print("written", p)
main()
