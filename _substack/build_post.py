"""Turn a markdown draft (title, blank line, body) into <draft>-substack.html, a Substack
copy-paste page in the format of the Sep 12 Codex template. Substack has no table block, so each table becomes
<draft>-table-N.png (render_tables.cjs) and each ```mermaid block becomes <draft>-figure-N.png (mermaid-cli),
embedded in the article as image data so it travels with the paste. A markdown image of a local PNG (a figure
reproduced from a paper, say) is embedded the same way.
--omit-section and --omit-bullet leave doc content out of the post. Setup once: npm install. Run:
  uvx --with markdown-it-py python build_post.py sft-miles-rl.md --omit-section "Our repo today" --omit-bullet "Zero successes."
  uvx --with markdown-it-py python build_post.py sft-miles-rl-v2.md
sft-miles-rl.md is the Claude Docs export of "SFT, Miles and RL for Robot Policies" (rev 23, 2026-10-02); v2 is the
rewritten blog draft."""

import argparse
import base64
import html
import pathlib
import re
import subprocess
import tempfile

import markdown_it

HERE = pathlib.Path(__file__).parent

STYLE = """body { max-width: 850px; margin: 40px auto; padding: 0 24px 80px; color: #202020; background: #fff; font: 19px/1.6 Georgia, serif; }
h1 { font-size: 36px; line-height: 1.15; margin: 30px 0; }
h2 { font-size: 27px; line-height: 1.25; margin: 40px 0 12px; }
a { color: #285d8f; }
.transfer { padding: 18px 22px; border: 1px solid #ccd5df; background: #f4f7fa; border-radius: 8px; font: 15px/1.5 system-ui, sans-serif; }
.transfer p { margin: 0 0 12px; }
button { padding: 9px 15px; margin-right: 8px; font: inherit; cursor: pointer; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; padding: 16px; background: #f5f5f5; border: 1px solid #e3e3e3; font: 13px/1.5 ui-monospace, monospace; }
code { font-family: ui-monospace, monospace; font-size: .85em; }
pre code { font-size: inherit; }
article img { display: block; width: 100%; max-width: 728px; margin: 24px 0; }
@media print { .transfer { display: none; } }"""

SHOT_STYLE = """body { margin: 0; background: #fff; }
.shot { width: 728px; padding: 2px; box-sizing: border-box; background: #fff; }
table { border-collapse: collapse; width: 100%; color: #202020; font: 16px/1.45 system-ui, sans-serif; }
th,td { padding: 10px 12px; border: 1px solid #d4d4d4; text-align: left; vertical-align: top; }
th { background: #f2f2f2; font-weight: 600; }
a { color: inherit; text-decoration: none; }
code { font-family: ui-monospace, monospace; font-size: .85em; }"""

SCRIPT = """function selectPart(id) {
  const range = document.createRange();
  range.selectNodeContents(document.getElementById(id));
  const selection = window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
  document.getElementById('selection-status').textContent = 'Selected. Press Cmd+C (Mac) or Ctrl+C (Windows).';
}"""


def without_sections(markdown, headings):
    """Drop each named "## " section, from its heading up to the next "## " heading."""
    parts = re.split(r"(?m)^(?=## )", markdown)
    kept = [part for part in parts if part.split("\n", 1)[0].removeprefix("## ") not in headings]
    assert len(parts) - len(kept) == len(headings), f"expected to drop sections {headings}"
    return "".join(kept)


def without_bullets(markdown, leads):
    """Drop each one-line list item that opens with one of these bold leads."""
    lines = markdown.split("\n")
    kept = [line for line in lines if not any(line.startswith(f"- **{lead}**") for lead in leads)]
    assert len(lines) - len(kept) == len(leads), f"expected to drop bullets {leads}"
    return "\n".join(kept)


def with_column_widths(table):
    """Size columns by the square root of their text length, so the long-text columns get room in a 728 px image."""
    rows = [re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S) for row in re.findall(r"<tr>(.*?)</tr>", table, re.S)]
    roots = [sum(len(re.sub(r"<[^>]+>", "", row[i])) for row in rows) ** 0.5 for i in range(len(rows[0]))]
    cols = "".join(f'<col style="width: {100 * root / sum(roots):.1f}%">' for root in roots)
    return table.replace("<table>", f"<table><colgroup>{cols}</colgroup>", 1)


def render_tables(stem, tables):
    """Screenshot each table to <stem>-table-N.png."""
    shots = "\n".join(f'<div class="shot" id="{stem}-table-{n}">{with_column_widths(table)}</div>'
                      for n, table in enumerate(tables, 1))
    for stale in HERE.glob(f"{stem}-table-*.png"):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        page = pathlib.Path(tmp) / "tables.html"
        page.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{SHOT_STYLE}</style></head>'
                        f'<body>{shots}</body></html>')
        subprocess.run(["node", str(HERE / "render_tables.cjs"), str(page), str(HERE)], check=True)


def render_figures(stem, sources):
    """Render each mermaid source to <stem>-figure-N.png at the 728 px column, 2x for retina."""
    for stale in HERE.glob(f"{stem}-figure-*.png"):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        for n, source in enumerate(sources, 1):
            diagram = pathlib.Path(tmp) / f"figure-{n}.mmd"
            diagram.write_text(source)
            subprocess.run([str(HERE / "node_modules/.bin/mmdc"), "-i", str(diagram), "-o", str(HERE / f"{stem}-figure-{n}.png"),
                            "-c", str(HERE / "mermaid.json"), "-p", str(HERE / "puppeteer.json"),
                            "-s", "2", "-b", "white", "-q"], check=True)


def embedded(path, alt):
    """An <img> carrying the PNG's bytes, so it travels with a copy and paste."""
    data = base64.b64encode(path.read_bytes()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{html.escape(alt)}">'


def as_image(stem, n, table):
    """The article's stand-in for a table: its image, plus its links, which an image cannot carry."""
    headers = [re.sub(r"<[^>]+>", "", header) for header in re.findall(r"<th>(.*?)</th>", table)]
    image = embedded(HERE / f"{stem}-table-{n}.png", f"Table {n}: " + ", ".join(headers))
    links = re.findall(r'<a href="[^"]+">.*?</a>', table)
    if not links:
        return image
    return f"{image}\n<p>{headers[0]} links: {', '.join(links)}.</p>"


def main():
    parser = argparse.ArgumentParser(description="Build a Substack copy-paste page from a markdown draft.")
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("--omit-section", action="append", default=[], help="heading of a ## section to leave out")
    parser.add_argument("--omit-bullet", action="append", default=[], help="bold lead of a one-line bullet to leave out")
    args = parser.parse_args()
    stem = args.source.stem
    lines = (HERE / args.source).read_text().splitlines()
    assert lines[0].startswith("# ") and lines[1] == "", "expected a # title line, then a blank line"
    title = lines[0].removeprefix("# ")
    markdown = without_bullets(without_sections("\n".join(lines[2:]), args.omit_section), args.omit_bullet)
    article = markdown_it.MarkdownIt("commonmark").enable("table").render(markdown)
    tables = re.findall(r"<table>.*?</table>", article, re.S)
    render_tables(stem, tables)
    for n, table in enumerate(tables, 1):
        article = article.replace(table, as_image(stem, n, table), 1)
    figures = re.findall(r'<pre><code class="language-mermaid">.*?</code></pre>', article, re.S)
    sources = [html.unescape(re.sub(r"^<pre><code[^>]*>|</code></pre>$", "", figure)) for figure in figures]
    render_figures(stem, sources)
    for n, (figure, source) in enumerate(zip(figures, sources), 1):
        alt = re.search(r"^\s*accDescr:\s*(.+)$", source, re.M).group(1)
        article = article.replace(figure, embedded(HERE / f"{stem}-figure-{n}.png", alt), 1)
    pictures = re.findall(r'<img src="([^":]+\.png)" alt="([^"]*)" ?/?>', article)
    for src, alt in pictures:
        tag = re.search(rf'<img src="{re.escape(src)}" alt="{re.escape(alt)}" ?/?>', article).group(0)
        article = article.replace(tag, embedded(HERE / src, html.unescape(alt)), 1)
    copies = ", ".join([f"{stem}-table-{n}.png" for n in range(1, len(tables) + 1)] +
                       [f"{stem}-figure-{n}.png" for n in range(1, len(figures) + 1)] +
                       [src for src, _ in pictures])
    left_out = "; ".join(f"{kind} {', '.join(items)}" for kind, items in
                         (("sections", args.omit_section), ("bullets", args.omit_bullet)) if items)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
{STYLE}
</style></head><body>
<div class="transfer"><p>For Substack: select and copy the title into its title field. Then select and copy the article into the post body using ordinary paste (Cmd+V). The tables, diagrams and figures come along as embedded images; {copies} in this folder are the image files. Check the inline code after pasting. Source: {args.source.name}.{f" Left out here: {left_out}" if left_out else ""}</p>
<button type="button" onclick="selectPart('post-title')">Select title</button>
<button type="button" onclick="selectPart('post-body')">Select article</button>
<span id="selection-status" aria-live="polite"></span>
</div>
<h1 id="post-title">{html.escape(title)}</h1>
<article id="post-body">
{article}</article>
<script>
{SCRIPT}
</script></body></html>
"""
    out = HERE / f"{stem}-substack.html"
    out.write_text(page)
    print(f"wrote {out} ({len(page):,} bytes): {article.count('<h2>')} sections, {article.count('<a ')} links, "
          f"{len(tables)} tables, {len(figures)} diagrams and {len(pictures)} pictures embedded as images")


if __name__ == "__main__":
    main()
