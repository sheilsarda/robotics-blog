#!/usr/bin/env python3
"""Audit arXiv PDFs: locate figures and render cropped extracts."""

import re
import urllib.request
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "_drafts" / "_pdf_audit"
AUDIT.mkdir(parents=True, exist_ok=True)

PAPERS = {
    "2410.24164": "pi0",
    "2506.07339": "rtc",
    "2505.23705": "knowledge-insulation",
    "2302.00111": "unipi",
    "2602.15922": "dreamzero",
    "2507.05331": "tri-lbm",
}


def download(arxiv_id: str) -> Path:
    path = AUDIT / f"{arxiv_id}.pdf"
    if not path.exists():
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        with urllib.request.urlopen(url, timeout=120) as r:
            path.write_bytes(r.read())
    return path


def find_figure_pages(doc: fitz.Document) -> list[tuple[int, str]]:
    hits = []
    pat = re.compile(r"Figure\s+(\d+)[:\.]?\s*(.{0,80})", re.I)
    for i in range(doc.page_count):
        text = doc.load_page(i).get_text()
        for m in pat.finditer(text):
            hits.append((i, f"Figure {m.group(1)}: {m.group(2).strip()}"))
    return hits


def page_image_bboxes(page: fitz.Page) -> list[fitz.Rect]:
    """Return bounding boxes of embedded images on a page."""
    boxes = []
    for img in page.get_images(full=True):
        xref = img[0]
        for rect in page.get_image_rects(xref):
            if rect.width > 80 and rect.height > 80:
                boxes.append(rect)
    return boxes


def render_page_thumb(doc: fitz.Document, page_idx: int, out: Path, zoom=1.5):
    page = doc.load_page(page_idx)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out))


def render_figure_crop(page: fitz.Page, rect: fitz.Rect, out: Path, pad=8, zoom=2.5):
    clip = fitz.Rect(
        max(0, rect.x0 - pad),
        max(0, rect.y0 - pad),
        min(page.rect.width, rect.x1 + pad),
        min(page.rect.height, rect.y1 + pad),
    )
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out))


def main():
    summary = []
    for arxiv_id, slug in PAPERS.items():
        doc = fitz.open(download(arxiv_id))
        fig_pages = find_figure_pages(doc)
        summary.append(f"\n## {arxiv_id} ({slug}) — {doc.page_count} pages\n")
        seen = set()
        for page_idx, caption in fig_pages:
            if page_idx in seen:
                continue
            seen.add(page_idx)
            page = doc.load_page(page_idx)
            boxes = page_image_bboxes(page)
            summary.append(f"- p{page_idx+1} ({len(boxes)} imgs): {caption}")
            render_page_thumb(doc, page_idx, AUDIT / slug / f"page-{page_idx+1:02d}.png")
            for j, box in enumerate(boxes[:4]):
                render_figure_crop(
                    page, box, AUDIT / slug / f"page-{page_idx+1:02d}-img-{j+1}.png"
                )
        doc.close()

    report = "# PDF figure audit\n" + "\n".join(summary)
    (AUDIT / "report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
