import re
from pathlib import Path

posts_dir = Path("_substack-export/posts")
for name in [
    "196717347.is-it-possible-to-run-a-vision-language.html",
    "197806815.vlas-in-contact-the-need-for-speed.html",
]:
    html = (posts_dir / name).read_text(encoding="utf-8", errors="replace")
    print("===", name, "len", len(html))
    imgs = re.findall(r"<img[^>]+>", html, re.I)
    print("images:", len(imgs))
    for img in imgs:
        src = re.search(r'src="([^"]+)"', img)
        alt = re.search(r'alt="([^"]*)"', img)
        print(" ", alt.group(1) if alt else "", src.group(1)[:100] if src else "")
    links = re.findall(r'href="(https?://[^"]+)"', html)
    seen = set()
    for l in links:
        if l not in seen and ("arxiv" in l or "doi" in l or "ieee" in l or "openreview" in l):
            seen.add(l)
            print(" link:", l)
    print()
