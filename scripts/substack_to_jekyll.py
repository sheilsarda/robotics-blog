#!/usr/bin/env python3
"""Convert Substack export HTML to Jekyll post markdown."""

import re
from pathlib import Path
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "_substack-export"
POSTS_HTML = EXPORT / "posts"

MAPPING = {
    "196717347.is-it-possible-to-run-a-vision-language.html": "_posts/2026-05-07-vlas-in-safety-critical-applications.md",
    "197806815.vlas-in-contact-the-need-for-speed.html": "_posts/2026-05-31-vlas-in-contact.md",
}

SUBSTACK_POST_LINKS = {
    "is-it-possible-to-run-a-vision-language": "/blog/vlas-in-safety-critical-applications/",
}


def read_front_matter(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", text, re.S)
    if not m:
        raise ValueError(f"No front matter in {path}")
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, m.group(2)


def dump_front_matter(fm: dict) -> str:
    lines = ["---"]
    order = ["title", "short_title", "date", "slug", "description"]
    done = set()
    for k in order:
        if k in fm:
            v = fm[k]
            if k in ("title", "description", "short_title") or ":" in v:
                lines.append(f'{k}: "{v}"')
            else:
                lines.append(f"{k}: {v}")
            done.add(k)
    for k, v in fm.items():
        if k not in done:
            lines.append(f'{k}: "{v}"' if ":" in v else f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def download_image(url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        return True
    except Exception as e:
        print(f"  WARN download failed {url}: {e}")
        return False


def extract_images(soup: BeautifulSoup, slug: str):
    for img in soup.find_all("img"):
        src = img.get("src") or ""
        if not src.startswith("http") or "substack-post-media" not in src:
            continue
        name = Path(urlparse(src).path).name
        rel = f"/assets/posts/{slug}/{name}"
        local_path = ROOT / "assets" / "posts" / slug / name
        if not download_image(src, local_path):
            continue
        alt = (img.get("alt") or "").strip()
        if alt.lower() in ("refer to caption", ""):
            alt = "figure"
        replacement = f'![{alt}]({{{{ site.baseurl }}}}{rel})'
        img.replace_with(BeautifulSoup(replacement, "html.parser"))


def fix_substack_links(html: str) -> str:
    baseurl = "{{ site.baseurl }}"
    for sub_slug, jekyll_path in SUBSTACK_POST_LINKS.items():
        html = html.replace(
            f"https://sheilsarda.substack.com/p/{sub_slug}",
            f"{baseurl}{jekyll_path}",
        )
    return html


def html_to_markdown(html: str) -> str:
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_links = False
    h.ignore_images = False
    h.single_line_break = False
    md = h.handle(html)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = md.replace("{{ site.baseurl }}{{ site.baseurl }}", "{{ site.baseurl }}")
    return md.strip() + "\n"


def convert_html_file(html_name: str, out_rel: str):
    html_path = POSTS_HTML / html_name
    out_path = ROOT / out_rel
    fm, _ = read_front_matter(out_path)
    slug = fm.get("slug", "post")

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    for el in soup.select(".digest-post-embed"):
        link = "{{ site.baseurl }}/blog/vlas-in-safety-critical-applications/"
        el.replace_with(
            BeautifulSoup(
                '<p>For more on this problem and potential solutions, see '
                f'<a href="{link}">Is It Possible to Run a Vision-Language-Action Model '
                "in a Safety-Critical Loop?</a>.</p>",
                "html.parser",
            )
        )

    extract_images(soup, slug)
    html = fix_substack_links(str(soup))
    md_body = html_to_markdown(html)

    title = fm.get("title", "")
    md_body = re.sub(rf"^#\s*{re.escape(title)}\s*\n+", "", md_body, flags=re.I)

    out_path.write_text(dump_front_matter(fm) + "\n\n" + md_body, encoding="utf-8")
    print(f"Wrote {out_path}")


def main():
    for html_name, out_rel in MAPPING.items():
        convert_html_file(html_name, out_rel)


if __name__ == "__main__":
    main()
