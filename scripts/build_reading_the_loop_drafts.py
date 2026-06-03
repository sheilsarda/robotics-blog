#!/usr/bin/env python3
"""Build Reading the Loop draft markdown variants (1–3 plus hybrid+paper middle ground)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "_posts" / "2026-06-03-reading-the-loop.md"
DRAFTS = ROOT / "_drafts"

FM = """---
title: "Reading the loop: what robot foundation model scorecards admit about system design"
short_title: "Reading the loop"
date: 2026-06-03
slug: model-scorecards
description: "Three lenses on five companies, one pick, and where robot control as a video prediction problem actually pays off."
visual_variant: "{variant}"
draft: true
---

"""

# Relative paths so VS Code/Cursor markdown preview resolves images from _drafts/
IMG = "../assets/posts/model-scorecards/{opt}/{file}"


def fig(opt: str, file: str, alt: str) -> str:
    return f"![{alt}]({IMG.format(opt=opt, file=file)})\n"


def insert_after(body: str, anchor: str, block: str) -> str:
    idx = body.find(anchor)
    if idx == -1:
        raise ValueError(f"Anchor not found: {anchor[:80]}...")
    end = idx + len(anchor)
    rest = body[end:].lstrip("\n").lstrip(" ")
    return body[:end] + "\n\n" + block + "\n\n" + rest


def insert_figures_after(body: str, anchor: str, *specs: tuple[str, str, str]) -> str:
    """Insert multiple images in order immediately after anchor."""
    block = "".join(fig(opt, file, alt) for opt, file, alt in specs)
    return insert_after(body, anchor, block)


def main():
    DRAFTS.mkdir(exist_ok=True)
    base = BASE.read_text(encoding="utf-8")
    body = base.split("---", 2)[2].lstrip("\n")

    # ── Option 1: editorial scorecard pack ───────────────────────────────────
    o1 = "option1"
    b1 = body
    b1 = insert_after(b1, "DreamZero is the reference implementation.", fig(o1, "rate-stack-ladder.png", "Rate stack ladder: where each company closes the control loop"))
    b1 = insert_after(b1, "and what kind of data is it.", fig(o1, "disclosure-heatmap.png", "Public disclosure scorecard across five robot foundation model companies"))
    b1 = insert_after(b1, "That is a control loop you can audit, latency budget included.", fig(o1, "rtc-timing.png", "Real-time chunking: generating the next action chunk during execution"))
    b1 = insert_after(b1, "## Control as a video prediction problem\n", fig(o1, "two-camp-split.png", "Two camps: inference economics versus data economics"))
    b1 = insert_after(b1, "Everything else the video camp needed, it now has.", fig(o1, "falsifiable-gate.png", "Falsifiable gate: what DreamZero settled and what remains open"))
    figs1 = """
## Figures

Sarda, Sheil. "Disclosure Scorecard Heatmap." *Diagram*, 2 June 2026. Robotics blog illustration. Based on comparative scorecard in internal research dossier (May 2026).

Sarda, Sheil. "Falsifiable Gate for Video-Prediction Policies." *Diagram*, 2 June 2026. Robotics blog illustration.

Sarda, Sheil. "Rate Stack Ladder for Robot Foundation Models." *Diagram*, 2 June 2026. Robotics blog illustration. Rate ranges from Figure Helix product disclosures and Physical Intelligence arXiv papers; Rhoda rate undisclosed in primary sources.

Sarda, Sheil. "Real-Time Chunking Timeline." *Diagram*, 2 June 2026. Robotics blog illustration. Latency values from Black, Kevin, et al., arXiv:2506.07339.

Sarda, Sheil. "Two-Camp Split: Inference vs Data Economics." *Diagram*, 2 June 2026. Robotics blog illustration. Benchmark values from Ye, Seonghyeon, et al., arXiv:2602.15922, and Physical Intelligence openpi disclosures.
"""
    (DRAFTS / "reading-the-loop-option-1-editorial.md").write_text(
        FM.format(variant="option-1-editorial") + b1 + figs1, encoding="utf-8"
    )

    # ── Option 2: paper figure tour ──────────────────────────────────────────
    o2 = "option2"
    b2 = body
    b2 = insert_after(b2, "without a non-disclosure gap.", fig(o2, "pi0-architecture-paper.png", "π0 architecture: VLM backbone and flow-matching action expert (Black et al.)"))
    b2 = insert_after(b2, "That is a control loop you can audit, latency budget included.", fig(o2, "rtc-paper.png", "Real-time execution of action chunking flow policies (Black et al., NeurIPS 2025)"))
    b2 = insert_after(b2, "so the language prior survives training.", fig(o2, "knowledge-insulation-paper.png", "Knowledge Insulating Vision-Language-Action Models (Physical Intelligence et al.)"))
    b2 = insert_after(b2, "with an inverse model recovering the actions, back in 2023.", fig(o2, "unipi-paper.png", "UniPi: learning universal policies via text-guided video generation (Du et al.)"))
    b2 = insert_after(b2, "with weights, code, and eval sets released. This is the disclosure Rhoda withholds, from the same thesis.", fig(o2, "dreamzero-architecture-paper.png", "DreamZero World Action Model architecture (Ye et al.)"))
    b2 = insert_after(b2, "Edge deployment is named as future work.", fig(o2, "dreamzero-benchmark-paper.png", "DreamZero head-to-head benchmark vs π0.5 and GR00T N1.6 (Ye et al.)"))
    b2 = insert_after(b2, "The high-speed half of the market is exactly where that gap bites.", fig(o2, "dreamzero-latency-paper.png", "DreamZero inference latency optimization (Ye et al.)"))
    b2 = insert_after(b2, "multitask pretraining cuts per-task data by about 80%.", fig(o2, "tri-lbm-paper.png", "Toyota Research Institute Large Behavior Models (TRI et al.)"))
    figs2 = """
## Figures

Black, Kevin, et al. "π0: A Vision-Language-Action Flow Model for General Robot Control." *arXiv*, 31 Oct. 2024, arxiv.org/abs/2410.24164. Fig. 3 reproduced from arXiv PDF page 4 for commentary.

Black, Kevin, et al. "Real-Time Execution of Action Chunking Flow Policies." *arXiv*, 7 June 2025, arxiv.org/abs/2506.07339. Figure 1 reproduced from arXiv PDF page 1 for commentary. NeurIPS 2025.

Du, Yilun, et al. "Learning Universal Policies via Text-Guided Video Generation." *arXiv*, 31 Jan. 2023, arxiv.org/abs/2302.00111. Figure 2 reproduced from arXiv PDF page 4 for commentary.

Physical Intelligence, et al. "Knowledge Insulating Vision-Language-Action Models: Train Fast, Run Fast, Generalize Better." *arXiv*, May 2025, arxiv.org/abs/2505.23705. Figure 1 reproduced from arXiv PDF page 2 for commentary.

Toyota Research Institute. "A Careful Examination of Large Behavior Models for Multitask Dexterous Manipulation." *arXiv*, 7 July 2025, arxiv.org/abs/2507.05331. Figure 9 reproduced from arXiv PDF page 12 for commentary.

Ye, Seonghyeon, et al. "World Action Models are Zero-shot Policies." *arXiv*, 17 Feb. 2026, arxiv.org/abs/2602.15922. Figure 4, Figure 8, and Table 1 reproduced from arXiv PDF pages 6, 13, and 10 for commentary.
"""
    (DRAFTS / "reading-the-loop-option-2-paper-tour.md").write_text(
        FM.format(variant="option-2-paper-tour") + b2 + figs2, encoding="utf-8"
    )

    # ── Option 3: hybrid loop atlas ──────────────────────────────────────────
    o3 = "option3"
    b3 = body
    b3 = insert_after(b3, "DreamZero is the reference implementation.", fig(o3, "rate-stack-ladder.png", "Rate stack: where each company closes the loop"))
    b3 = insert_after(b3, "without a non-disclosure gap.", fig(o3, "pi0-architecture-paper.png", "π0 VLM plus flow-matching action expert (Black et al.)"))
    b3 = insert_after(b3, "with weights, code, and eval sets released. This is the disclosure Rhoda withholds, from the same thesis.", fig(o3, "dreamzero-wam-paper.png", "DreamZero World Action Model closed-loop architecture (Ye et al.)"))
    b3 = insert_after(b3, "Edge deployment is named as future work.", fig(o3, "dreamzero-benchmark-paper.png", "DreamZero unseen-task generalization benchmark (Ye et al.)"))
    b3 = insert_after(b3, "not the fast loop where the robot actually lives.", fig(o3, "slow-propose-fast-comply.png", "Slow-propose, fast-comply hybrid control stack"))
    figs3 = """
## Figures

Black, Kevin, et al. "π0: A Vision-Language-Action Flow Model for General Robot Control." *arXiv*, 31 Oct. 2024, arxiv.org/abs/2410.24164. Fig. 3 reproduced from arXiv PDF page 4 for commentary.

Sarda, Sheil. "Rate Stack Ladder for Robot Foundation Models." *Diagram*, 2 June 2026. Robotics blog illustration.

Sarda, Sheil. "Slow-Propose, Fast-Comply Hybrid Stack." *Diagram*, 2 June 2026. Robotics blog illustration.

Ye, Seonghyeon, et al. "World Action Models are Zero-shot Policies." *arXiv*, 17 Feb. 2026, arxiv.org/abs/2602.15922. Figure 4 and Figure 9 reproduced from arXiv PDF pages 6 and 14 for commentary.
"""
    (DRAFTS / "reading-the-loop-option-3-hybrid.md").write_text(
        FM.format(variant="option-3-hybrid") + b3 + figs3, encoding="utf-8"
    )

    # ── Option 3+2 middle: hybrid frame + full paper tour (append all option-2 figures) ─
    o2, o3 = "option2", "option3"
    bm = body
    bm = insert_after(bm, "DreamZero is the reference implementation.", fig(o3, "rate-stack-ladder.png", "Rate stack: where each company closes the loop"))
    bm = insert_after(bm, "without a non-disclosure gap.", fig(o3, "pi0-architecture-paper.png", "π0 VLM plus flow-matching action expert (Black et al.)"))
    bm = insert_after(bm, "so the language prior survives training.", fig(o2, "knowledge-insulation-paper.png", "Knowledge Insulating Vision-Language-Action Models (Physical Intelligence et al.)"))
    bm = insert_after(bm, "That is a control loop you can audit, latency budget included.", fig(o2, "rtc-paper.png", "Real-time execution of action chunking flow policies (Black et al., NeurIPS 2025)"))
    bm = insert_after(bm, "with an inverse model recovering the actions, back in 2023.", fig(o2, "unipi-paper.png", "UniPi: learning universal policies via text-guided video generation (Du et al.)"))
    bm = insert_after(bm, "with weights, code, and eval sets released. This is the disclosure Rhoda withholds, from the same thesis.", fig(o3, "dreamzero-wam-paper.png", "DreamZero World Action Model closed-loop architecture (Ye et al.)"))
    bm = insert_figures_after(
        bm,
        "Edge deployment is named as future work.",
        (o2, "dreamzero-benchmark-paper.png", "DreamZero seen-task evaluation vs π0.5 and GR00T N1.6 (Ye et al.)"),
        (o3, "dreamzero-benchmark-paper.png", "DreamZero unseen-task generalization benchmark (Ye et al.)"),
    )
    bm = insert_after(bm, "The high-speed half of the market is exactly where that gap bites.", fig(o2, "dreamzero-latency-paper.png", "DreamZero inference latency optimization (Ye et al.)"))
    bm = insert_after(bm, "multitask pretraining cuts per-task data by about 80%.", fig(o2, "tri-lbm-paper.png", "Toyota Research Institute Large Behavior Models (TRI et al.)"))
    bm = insert_after(bm, "not the fast loop where the robot actually lives.", fig(o3, "slow-propose-fast-comply.png", "Slow-propose, fast-comply hybrid control stack"))
    figs_mid = """
## Figures

Black, Kevin, et al. "π0: A Vision-Language-Action Flow Model for General Robot Control." *arXiv*, 31 Oct. 2024, arxiv.org/abs/2410.24164. Fig. 3 reproduced from arXiv PDF page 4 for commentary.

Black, Kevin, et al. "Real-Time Execution of Action Chunking Flow Policies." *arXiv*, 7 June 2025, arxiv.org/abs/2506.07339. Figure 1 reproduced from arXiv PDF page 1 for commentary. NeurIPS 2025.

Du, Yilun, et al. "Learning Universal Policies via Text-Guided Video Generation." *arXiv*, 31 Jan. 2023, arxiv.org/abs/2302.00111. Figure 2 reproduced from arXiv PDF page 4 for commentary.

Physical Intelligence, et al. "Knowledge Insulating Vision-Language-Action Models: Train Fast, Run Fast, Generalize Better." *arXiv*, May 2025, arxiv.org/abs/2505.23705. Figure 1 reproduced from arXiv PDF page 2 for commentary.

Sarda, Sheil. "Rate Stack Ladder for Robot Foundation Models." *Diagram*, 2 June 2026. Robotics blog illustration.

Sarda, Sheil. "Slow-Propose, Fast-Comply Hybrid Stack." *Diagram*, 2 June 2026. Robotics blog illustration.

Toyota Research Institute. "A Careful Examination of Large Behavior Models for Multitask Dexterous Manipulation." *arXiv*, 7 July 2025, arxiv.org/abs/2507.05331. Figure 9 reproduced from arXiv PDF page 12 for commentary.

Ye, Seonghyeon, et al. "World Action Models are Zero-shot Policies." *arXiv*, 17 Feb. 2026, arxiv.org/abs/2602.15922. Figure 4, Figure 8, Figure 9, and Table 1 reproduced from arXiv PDF pages 6, 13, 14, and 10 for commentary.
"""
    (DRAFTS / "reading-the-loop-option-3-hybrid-plus-paper.md").write_text(
        FM.format(variant="option-3-hybrid-plus-paper") + bm + figs_mid, encoding="utf-8"
    )
    print("Wrote 4 drafts to _drafts/")


def publish_hybrid_plus_paper():
    """Promote hybrid+paper draft to _posts with Jekyll image URLs."""
    src = DRAFTS / "reading-the-loop-option-3-hybrid-plus-paper.md"
    text = src.read_text(encoding="utf-8")
    lines = []
    for line in text.splitlines():
        if line.strip().startswith(("draft: true", "visual_variant:")):
            continue
        lines.append(line)
    body = "\n".join(lines)
    body = body.replace("../assets/posts/model-scorecards/", "{{ site.baseurl }}/assets/posts/model-scorecards/")
    (ROOT / "_posts" / "2026-06-03-reading-the-loop.md").write_text(body, encoding="utf-8")
    print("Published _posts/2026-06-03-reading-the-loop.md")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "publish":
        publish_hybrid_plus_paper()
    else:
        main()
