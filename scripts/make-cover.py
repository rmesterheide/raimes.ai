#!/usr/bin/env python3
"""Render a typographic 1200x630 cover in the topic color.

Usage: scripts/make-cover.py <slug> <topic> "<title>" "<subtitle>"
  topic: homelab-ai (teal) or vmware (aubergine)
Writes static/images/covers/<slug>.jpg via headless Chrome and sips.
Colors are OKLCH siblings: same lightness and chroma, rotated hue.
"""
import html, os, subprocess, sys, tempfile

TOPICS = {
    "homelab-ai": ("#1f6f78", "#175057"),
    "vmware": ("#76557e", "#553d5b"),
}
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def main():
    if len(sys.argv) != 5 or sys.argv[2] not in TOPICS:
        sys.exit(__doc__)
    slug, topic, title, subtitle = sys.argv[1:]
    c1, c2 = TOPICS[topic]
    page = f"""<!doctype html><meta charset="utf-8"><style>
html,body{{margin:0}} body{{width:1200px;height:630px;overflow:hidden;
background:linear-gradient(135deg,{c1} 0%,{c2} 100%);
font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;color:#fff;position:relative}}
.mark{{position:absolute;left:80px;top:88px;font-size:34px;font-weight:700}}
.title{{position:absolute;left:80px;top:205px;width:720px;font-size:56px;font-weight:700;line-height:1.2;letter-spacing:-0.01em}}
.sub{{position:absolute;left:80px;top:532px;font-size:28px;color:rgba(255,255,255,.85)}}
</style><div class="mark">raimes.ai</div><div class="title">{html.escape(title)}</div><div class="sub">{html.escape(subtitle)}</div>"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "static", "images", "covers", f"{slug}.jpg")
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "cover.html"); png = os.path.join(tmp, "cover.png")
        open(src, "w").write(page)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1200,630",
                        f"--screenshot={png}", f"file://{src}"], check=True, capture_output=True)
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", png, "--out", out],
                       check=True, capture_output=True)
    print(out)

if __name__ == "__main__":
    main()
