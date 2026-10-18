#!/usr/bin/env python3
"""Before/after bar charts for the post "From 125 ms spikes to 1 ms" as plain SVG (no libraries).

Usage: scripts/chart-sonos-wifi.py            -> writes static/images/sonos-wifi-tune-up/*.svg
Numbers come from homelab/sonos/README.md and homelab/netzwerk/wlan.md (2026-10-18).
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "static", "images", "sonos-wifi-tune-up")
BEFORE, AFTER, INK, MUTED, GRID = "#b4b2a9", "#1f6f78", "#2c2c2a", "#6b6a66", "#e1e0d9"


def chart(path, title, unit, rows, xmax, before_label, after_label):
    left, top, barh, gap, width = 190, 56, 11, 34, 760
    plot_w = width - left - 70
    h = top + len(rows) * gap + 48
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" width="{width}" height="{h}" '
         f'font-family="Inter, -apple-system, Helvetica, Arial, sans-serif" font-size="13" role="img" aria-label="{title}">',
         f'<rect width="{width}" height="{h}" fill="#ffffff"/>',
         f'<text x="{left}" y="22" font-size="15" font-weight="500" fill="{INK}">{title}</text>',
         f'<rect x="{left}" y="32" width="10" height="10" rx="2" fill="{BEFORE}"/><text x="{left + 16}" y="41" fill="{MUTED}">{before_label}</text>',
         f'<rect x="{left + 150}" y="32" width="10" height="10" rx="2" fill="{AFTER}"/><text x="{left + 166}" y="41" fill="{MUTED}">{after_label}</text>']
    for i in range(0, 5):
        v = xmax * i / 4
        x = left + plot_w * i / 4
        s.append(f'<line x1="{x:.0f}" y1="{top - 4}" x2="{x:.0f}" y2="{h - 36}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{x:.0f}" y="{h - 18}" text-anchor="middle" fill="{MUTED}" font-size="12">{v:g} {unit}</text>')
    for i, (name, b, a) in enumerate(rows):
        y = top + i * gap
        s.append(f'<text x="{left - 10}" y="{y + barh + 1}" text-anchor="end" fill="{INK}">{name}</text>')
        for val, color, dy in ((b, BEFORE, 0), (a, AFTER, barh + 2)):
            w = max(2, plot_w * min(val, xmax) / xmax)
            s.append(f'<rect x="{left}" y="{y + dy - 4}" width="{w:.1f}" height="{barh}" fill="{color}"/>')
            s.append(f'<text x="{left + w + 6:.1f}" y="{y + dy + barh - 6}" fill="{MUTED}" font-size="12">{val:g}</text>')
    s.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(s))


def main():
    os.makedirs(OUT, exist_ok=True)
    chart(os.path.join(OUT, "sonos-latency.svg"),
          "Sonos players: average round-trip time from a wired host, ms", "ms",
          [("Living room soundbar", 22, 1.0), ("Living room sub", 28, 2.3), ("Dining room", 4.9, 2.9),
           ("Bar", 6.7, 4.6), ("Portable 1", 6.5, 2.4), ("Portable 2", 6.2, 2.3), ("Kitchen", 4.3, 3.5),
           ("Office pair", 3.1, 2.4)],
          30, "morning, all on Wi-Fi", "evening, soundbar wired, SonosNet off, new radio plan")
    chart(os.path.join(OUT, "wifi-busy.svg"),
          "2.4 GHz channel utilisation per access point, %", "%",
          [("Outdoor", 91, 19), ("Ground-floor living room", 82, 19), ("Outdoor extender", 53, 19),
           ("Stairwell", 47, 15), ("Hallway extender", 47, 17), ("Boiler room", 42, 18),
           ("Attic office", 41, 22), ("Upstairs living room", 39, 19), ("Attic", 39, 22)],
          100, "auto channels, 40 MHz, five SSIDs", "fixed channels, 20 MHz, lower power")
    print("written:", OUT)


if __name__ == "__main__":
    main()
