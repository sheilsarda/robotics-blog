#!/usr/bin/env python3
"""Extract correct figure/table crops from arXiv PDFs and regenerate editorial diagrams."""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

import fitz
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "_drafts" / "_pdf_audit"
ASSETS = ROOT / "assets" / "posts" / "model-scorecards"

C_TEXT = "#1a1a2e"
C_MUTED = "#64748b"
C_ACCENT = "#6366f1"
C_ACCENT2 = "#0ea5e9"
C_ACCENT3 = "#10b981"
C_WARN = "#f59e0b"
C_BAD = "#ef4444"
C_GRID = "#e2e8f0"


def save_fig(fig, path: Path, dpi: int = 220):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


def download_pdf(arxiv_id: str) -> Path:
    path = CACHE / f"{arxiv_id}.pdf"
    if not path.exists():
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        with urllib.request.urlopen(url, timeout=120) as r:
            path.write_bytes(r.read())
    return path


def render_clip(doc: fitz.Document, page_idx: int, clip: fitz.Rect, out: Path, zoom: float = 2.5):
    page = doc.load_page(page_idx)
    clip = clip & page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out))
    print(f"  wrote {out.relative_to(ROOT)} (p{page_idx + 1} clip)")


def render_largest_image(doc: fitz.Document, page_idx: int, out: Path, zoom: float = 2.5, min_area: float = 8_000):
    page = doc.load_page(page_idx)
    best = None
    best_area = 0
    for img in page.get_images(full=True):
        xref = img[0]
        for rect in page.get_image_rects(xref):
            area = rect.width * rect.height
            if area > best_area and area >= min_area:
                best_area = area
                best = rect
    if not best:
        raise RuntimeError(f"No suitable image on page {page_idx + 1}")
    pad = 6
    clip = fitz.Rect(
        max(0, best.x0 - pad),
        max(0, best.y0 - pad),
        min(page.rect.width, best.x1 + pad),
        min(page.rect.height, best.y1 + pad),
    )
    render_clip(doc, page_idx, clip, out, zoom)


def clip_above_caption(page: fitz.Page, caption_pat: str, top_margin: float = 48, gap: float = 6) -> fitz.Rect:
    cap_y = None
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            txt = "".join(s["text"] for s in line.get("spans", []))
            if re.search(caption_pat, txt, re.I):
                cap_y = line["bbox"][1]
                break
        if cap_y is not None:
            break
    if cap_y is None:
        raise RuntimeError(f"Caption not found: {caption_pat}")
    return fitz.Rect(page.rect.x0 + 32, top_margin, page.rect.x1 - 32, cap_y - gap)


def clip_figure_union_above_caption(
    page: fitz.Page,
    caption_pat: str,
    *,
    min_x_frac: float = 0.0,
    min_img_w: float = 25,
    min_img_h: float = 12,
    pad: float = 10,
    gap: float = 6,
) -> fitz.Rect:
    """Crop the figure region above a caption when the page mixes text and graphics."""
    cap_y = None
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            txt = "".join(s["text"] for s in line.get("spans", []))
            if re.search(caption_pat, txt, re.I):
                cap_y = line["bbox"][1]
                break
        if cap_y is not None:
            break
    if cap_y is None:
        raise RuntimeError(f"Caption not found: {caption_pat}")

    min_x = page.rect.x0 + page.rect.width * min_x_frac
    boxes = []
    for img in page.get_images(full=True):
        for rect in page.get_image_rects(img[0]):
            if rect.y1 >= cap_y - gap:
                continue
            if rect.width < min_img_w or rect.height < min_img_h:
                continue
            if rect.x0 < min_x:
                continue
            boxes.append(rect)

    if not boxes:
        return clip_above_caption(page, caption_pat, top_margin=48)

    x0 = min(r.x0 for r in boxes) - pad
    y0 = min(r.y0 for r in boxes) - pad
    x1 = max(r.x1 for r in boxes) + pad
    y1 = cap_y - gap
    return fitz.Rect(
        max(page.rect.x0 + 24, x0),
        max(48, y0),
        min(page.rect.x1 - 24, x1),
        y1,
    )


def clip_below_caption(page: fitz.Page, caption_pat: str, gap: float = 6, bottom_pad: float = 48) -> fitz.Rect:
    cap_bottom = None
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            txt = "".join(s["text"] for s in line.get("spans", []))
            if re.search(caption_pat, txt, re.I):
                cap_bottom = line["bbox"][3]
                break
        if cap_bottom is not None:
            break
    if cap_bottom is None:
        raise RuntimeError(f"Caption not found: {caption_pat}")
    return fitz.Rect(page.rect.x0 + 32, cap_bottom + gap, page.rect.x1 - 32, page.rect.height - bottom_pad)


def extract_all_paper_figures():
    print("Extracting paper figures (cropped)...")

    # π0 Fig. 3 — framework overview (architecture diagram above caption on p4)
    doc = fitz.open(download_pdf("2410.24164"))
    page = doc.load_page(3)
    clip = clip_above_caption(page, r"Fig\.\s*3")
    for opt in ("option2", "option3"):
        render_clip(doc, 3, clip, ASSETS / opt / "pi0-architecture-paper.png")
    doc.close()

    # RTC Fig. 1 — photos + graphs only (below abstract)
    doc = fitz.open(download_pdf("2506.07339"))
    page = doc.load_page(0)
    clip = clip_above_caption(page, r"Figure\s*1", top_margin=430)
    render_clip(doc, 0, clip, ASSETS / "option2" / "rtc-paper.png")
    doc.close()

    # Knowledge Insulation Fig. 1 — architecture (p2)
    doc = fitz.open(download_pdf("2505.23705"))
    page = doc.load_page(1)
    clip = clip_above_caption(page, r"Figure\s*1")
    render_clip(doc, 1, clip, ASSETS / "option2" / "knowledge-insulation-paper.png")
    doc.close()

    # UniPi Fig. 2 — two-column page: union right-column graphics above caption
    doc = fitz.open(download_pdf("2302.00111"))
    page = doc.load_page(3)
    clip = clip_figure_union_above_caption(page, r"Figure\s*2", min_x_frac=0.47)
    render_clip(doc, 3, clip, ASSETS / "option2" / "unipi-paper.png")
    doc.close()

    # DreamZero Fig. 4 — model architecture (p6, embedded raster)
    doc = fitz.open(download_pdf("2602.15922"))
    render_largest_image(doc, 5, ASSETS / "option2" / "dreamzero-architecture-paper.png")
    render_largest_image(doc, 5, ASSETS / "option3" / "dreamzero-wam-paper.png")

    # DreamZero Fig. 8 — seen-task benchmark bars (p13)
    page = doc.load_page(12)
    clip = clip_above_caption(page, r"Figure\s*8", top_margin=310)
    render_clip(doc, 12, clip, ASSETS / "option2" / "dreamzero-benchmark-paper.png")

    # DreamZero Fig. 9 — unseen-task benchmark (p14; option 3)
    clip9 = clip_above_caption(doc.load_page(13), r"Figure\s*9", top_margin=52)
    render_clip(doc, 13, clip9, ASSETS / "option3" / "dreamzero-benchmark-paper.png")

    # DreamZero Table 1 — table sits above its caption on p10
    page = doc.load_page(9)
    clip = fitz.Rect(page.rect.x0 + 48, 112, page.rect.x1 - 48, 286)
    render_clip(doc, 9, clip, ASSETS / "option2" / "dreamzero-latency-paper.png")
    doc.close()

    # TRI Fig. 9 — LBM architecture
    doc = fitz.open(download_pdf("2507.05331"))
    render_largest_image(doc, 11, ASSETS / "option2" / "tri-lbm-paper.png")
    doc.close()


# ── Editorial diagrams (option 1 + option 3) ─────────────────────────────────

def fig_rate_stack(out: Path):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    layers = [
        ("S2: scene / language (5–10 Hz)", 5, 10, "#ddd6fe", C_ACCENT),
        ("S1: visuomotor / chunks (50–200 Hz)", 50, 200, "#bae6fd", C_ACCENT2),
        ("S0: balance / contact (~1 kHz)", 500, 1000, "#bbf7d0", C_ACCENT3),
    ]
    for i, (label, lo, hi, fill, edge) in enumerate(layers):
        ax.barh(2 - i, hi - lo, left=lo, height=0.55, color=fill, edgecolor=edge, linewidth=1.5)
        ax.text(lo + (hi - lo) * 0.02, 2 - i, label, va="center", ha="left", fontsize=9, color=C_TEXT)

    markers = [
        ("Figure Helix S2", 8, 2.65),
        ("Figure Helix S1", 200, 1.65),
        ("Physical Intelligence π0", 50, 1.65),
        ("DreamZero WAM", 7, 1.65),
        ("Rhoda DVA (undisclosed)", None, 0.65),
    ]
    for name, hz, y in markers:
        if hz is None:
            ax.scatter([15], [y], s=90, marker="x", color=C_MUTED, linewidths=2, zorder=5)
            ax.text(22, y, name, fontsize=8.5, color=C_MUTED, va="center")
        else:
            ax.scatter([hz], [y], s=70, color=C_TEXT, zorder=5, edgecolors="white", linewidths=1.2)
            ax.text(hz + 12, y, f"{name} — {hz} Hz", fontsize=8.5, color=C_TEXT, va="center")

    ax.set_xscale("log")
    ax.set_xlim(4, 1200)
    ax.set_ylim(0.2, 3.1)
    ax.set_yticks([])
    ax.set_xlabel("Control rate (Hz, log scale)", fontsize=10, color=C_TEXT)
    ax.set_title("Rate stack: where each company closes the loop", fontsize=12, fontweight="600", color=C_TEXT, pad=12)
    ax.grid(axis="x", alpha=0.25, color=C_GRID)
    save_fig(fig, out)


def fig_disclosure_heatmap(out: Path):
    companies = ["Physical\nIntelligence", "Dyna", "Generalist", "Skild", "Rhoda"]
    axes_labels = ["Loop\ntrans.", "System\ndecomp.", "Action\nrepr.", "Data\nstrategy", "Inference\nrealism", "Result\ncred."]
    labels = ["VL", "L", "M", "H", "VH"]
    scores = np.array([[4, 4, 4, 4, 4, 4], [1, 1, 1, 2, 1, 3], [2, 2, 2, 4, 2, 3], [0, 0, 0, 2, 1, 1], [1, 3, 2, 4, 1, 2]])
    fig, ax = plt.subplots(figsize=(11, 4.8))
    cmap = plt.cm.colors.LinearSegmentedColormap.from_list("d", ["#fecaca", "#fef3c7", "#dbeafe", "#bbf7d0", "#059669"])
    im = ax.imshow(scores, cmap=cmap, vmin=0, vmax=4, aspect="auto")
    ax.set_xticks(range(6))
    ax.set_xticklabels(axes_labels, fontsize=9, color=C_TEXT)
    ax.set_yticks(range(5))
    ax.set_yticklabels(companies, fontsize=9, color=C_TEXT)
    full = [["Very high"] * 6, ["Low", "Low", "Low", "Med", "Low", "High"], ["Med"] * 4 + ["High", "Med"], ["Very low"] * 3 + ["Med", "Low", "Low"], ["Low", "High", "Med", "Very high", "Low", "Med"]]
    for i in range(5):
        for j in range(6):
            ax.text(j, i, labels[int(scores[i, j])], ha="center", va="center", fontsize=10, fontweight="600", color=C_TEXT)
    ax.set_title("Public disclosure scorecard (May 2026 research dossier)", fontsize=12, fontweight="600", color=C_TEXT, pad=12)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_ticks([0, 1, 2, 3, 4])
    cbar.set_ticklabels(["Very low", "Low", "Med", "High", "Very high"], fontsize=8)
    save_fig(fig, out)


def fig_rtc_timing(out: Path):
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.fill_between([0, 0.5], 0, 1, color=C_ACCENT, alpha=0.25, label="Executing chunk N")
    ax.fill_between([0.12, 0.217], 1.15, 1.65, color=C_ACCENT2, alpha=0.45, label="Generating chunk N+1 (~97 ms)")
    ax.annotate("", xy=(0.217, 1.4), xytext=(0.12, 1.4), arrowprops=dict(arrowstyle="<->", color=C_ACCENT2, lw=1.8))
    ax.text(0.168, 1.72, "97 ms model latency", ha="center", fontsize=9, color=C_ACCENT2)
    ax.annotate("", xy=(0.05, 0.5), xytext=(0.35, 0.5), arrowprops=dict(arrowstyle="<->", color=C_TEXT, lw=1.4))
    ax.text(0.2, 0.22, ">300 ms delay tolerance\n(>30% of chunk horizon)", ha="center", fontsize=9, color=C_TEXT)
    ax.set_xlim(-0.02, 0.62)
    ax.set_ylim(-0.05, 1.95)
    ax.set_xlabel("Normalized time within action chunk", fontsize=10, color=C_TEXT)
    ax.set_yticks([])
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    ax.set_title("Real-time chunking (RTC): async inference during execution", fontsize=12, fontweight="600", color=C_TEXT, pad=10)
    save_fig(fig, out)


def fig_two_camp_split(out: Path):
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.scatter([2.2], [48], s=500, c=C_ACCENT, alpha=0.75, edgecolors="white", linewidths=2, zorder=3)
    ax.scatter([8.2], [7], s=500, c=C_WARN, alpha=0.75, edgecolors="white", linewidths=2, zorder=3)
    ax.text(2.2, 54, "Action-chunking VLA\n(flow matching + RTC)", ha="center", fontsize=10, fontweight="600", color=C_TEXT)
    ax.text(2.2, 38, "50 Hz · ~97 ms latency · 10k+ hr robot pretrain", ha="center", fontsize=8.5, color=C_MUTED)
    ax.text(8.2, 13, "Video-prediction WAM (DreamZero)", ha="center", fontsize=10, fontweight="600", color=C_TEXT)
    ax.text(8.2, 2, "7 Hz · 2× GB200 · 30 min embodiment adapt", ha="center", fontsize=8.5, color=C_MUTED)
    ax.axhline(10, color=C_BAD, linestyle=":", linewidth=1.5, alpha=0.8)
    ax.text(0.4, 10.8, "10 Hz deployment gate", fontsize=9, color=C_BAD)
    ax.set_xlabel("Data cost for next task (lower is better →)", fontsize=10, color=C_TEXT)
    ax.set_ylabel("Closed-loop rate on deployable hardware (Hz)", fontsize=10, color=C_TEXT)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 58)
    ax.grid(alpha=0.25, color=C_GRID)
    ax.set_title("Two camps: inference economics vs data economics", fontsize=12, fontweight="600", color=C_TEXT, pad=12)
    save_fig(fig, out)


def fig_falsifiable_gate(out: Path):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axis("off")
    boxes = [
        (0.04, 0.56, 0.36, 0.28, "Head-to-head vs\nflow-matching VLA", C_ACCENT3, "Done\nDreamZero (Feb 2026)"),
        (0.04, 0.12, 0.36, 0.28, "Embodiment transfer\n≤10 hr IDM data", C_ACCENT3, "Done\n30 min (DreamZero)"),
        (0.48, 0.34, 0.48, 0.36, "≥10 Hz closed-loop\non embedded / consumer GPU", C_BAD, "Not yet\n7 Hz on 2× GB200"),
    ]
    from matplotlib.patches import FancyBboxPatch
    for x, y, w, h, title, color, status in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", facecolor=color, alpha=0.12, edgecolor=color, linewidth=2))
        ax.text(x + w / 2, y + h * 0.68, title, ha="center", va="center", fontsize=10, fontweight="600", color=C_TEXT)
        ax.text(x + w / 2, y + h * 0.28, status, ha="center", va="center", fontsize=9, color=color)
    ax.annotate("", xy=(0.72, 0.12), xytext=(0.72, 0.34), arrowprops=dict(arrowstyle="->", color=C_TEXT, lw=2))
    ax.text(0.72, 0.04, "Pick flips here", ha="center", fontsize=10, fontweight="600", color=C_TEXT)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Falsifiable gate: what DreamZero settled (and what it did not)", fontsize=12, fontweight="600", color=C_TEXT, pad=14)
    save_fig(fig, out)


def fig_slow_propose_fast_comply(out: Path):
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.axis("off")
    slow = FancyBboxPatch((0.08, 0.54), 0.84, 0.3, boxstyle="round,pad=0.02", facecolor="#fef3c7", edgecolor=C_WARN, linewidth=2)
    fast = FancyBboxPatch((0.08, 0.12), 0.84, 0.3, boxstyle="round,pad=0.02", facecolor="#e0e7ff", edgecolor=C_ACCENT, linewidth=2)
    ax.add_patch(slow)
    ax.add_patch(fast)
    ax.text(0.5, 0.72, "Slow propose (5–10 Hz)", ha="center", fontsize=11, fontweight="600", color=C_TEXT)
    ax.text(0.5, 0.62, "Video WAM / VLM · internet-video prior · scene + language planning", ha="center", fontsize=9, color=C_MUTED)
    ax.text(0.5, 0.34, "Fast comply (100–200 Hz)", ha="center", fontsize=11, fontweight="600", color=C_TEXT)
    ax.text(0.5, 0.24, "Flow-matching controller · RTC · impedance / safety filter", ha="center", fontsize=9, color=C_MUTED)
    ax.annotate("", xy=(0.5, 0.52), xytext=(0.5, 0.44), arrowprops=dict(arrowstyle="->", color=C_TEXT, lw=2))
    ax.text(0.62, 0.48, "modulate committed\naction chunks", ha="left", va="center", fontsize=8, color=C_MUTED)
    ax.set_title("Slow-propose, fast-comply hybrid stack", fontsize=12, fontweight="600", color=C_TEXT, pad=14)
    save_fig(fig, out)


def generate_editorial():
    print("Regenerating editorial diagrams...")
    for opt in ("option1", "option3"):
        o = ASSETS / opt
        fig_rate_stack(o / "rate-stack-ladder.png")
    o1 = ASSETS / "option1"
    fig_disclosure_heatmap(o1 / "disclosure-heatmap.png")
    fig_rtc_timing(o1 / "rtc-timing.png")
    fig_two_camp_split(o1 / "two-camp-split.png")
    fig_falsifiable_gate(o1 / "falsifiable-gate.png")
    fig_slow_propose_fast_comply(ASSETS / "option3" / "slow-propose-fast-comply.png")


def cleanup_stale():
    """Remove wrong full-page extracts and unused recreation PNGs."""
    stale = [
        "pi0-architecture.png", "knowledge-insulation.png", "unipi-pipeline.png",
        "dreamzero-wam.png", "dreamzero-benchmark.png", "dreamzero-latency.png", "tri-scaling.png",
    ]
    for opt in ("option2", "option3"):
        for name in stale:
            p = ASSETS / opt / name
            if p.exists():
                p.unlink()
                print(f"  removed stale {p.relative_to(ROOT)}")


def main():
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"]})
    extract_all_paper_figures()
    generate_editorial()
    cleanup_stale()
    print("Done.")


if __name__ == "__main__":
    main()
