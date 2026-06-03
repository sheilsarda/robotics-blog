import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "beautifulsoup4", "-q"])
    from bs4 import BeautifulSoup

posts_dir = Path("_substack-export/posts")
for name in [
    "196717347.is-it-possible-to-run-a-vision-language.html",
    "197806815.vlas-in-contact-the-need-for-speed.html",
]:
    html = (posts_dir / name).read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one(".body.markup") or soup.select_one(".available-content") or soup.body
    if not body:
        print(name, "NO BODY")
        continue
    print("===", name)
    # walk top-level elements
    for i, el in enumerate(body.find_all(["p", "h1", "h2", "h3", "h4", "figure", "div"], recursive=False)[:30]):
        t = el.get_text(" ", strip=True)[:100]
        imgs = el.find_all("img")
        links = [a.get("href") for a in el.find_all("a", href=True)]
        print(f"{i} {el.name}: {t}")
        if imgs:
            for img in imgs:
                print(f"   IMG: {img.get('alt','')[:40]} -> {img.get('src','')[:80]}")
        if links:
            for l in links[:3]:
                print(f"   LINK: {l[:80]}")
    print()
