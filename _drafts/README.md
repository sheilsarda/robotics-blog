# Reading the Loop — visual variant drafts

Three complete drafts of `_posts/2026-06-03-reading-the-loop.md`, each with a different illustration strategy. Pick one and copy/rename to replace the live post (or tell the agent which to promote).

| File | Strategy | Illustrations |
|------|----------|---------------|
| [reading-the-loop-option-1-editorial.md](reading-the-loop-option-1-editorial.md) | **Editorial scorecard pack** — custom diagrams only | 5 PNGs in `assets/posts/model-scorecards/option1/` |
| [reading-the-loop-option-2-paper-tour.md](reading-the-loop-option-2-paper-tour.md) | **Paper figure tour** — cropped arXiv figures/tables | 8 PNGs in `assets/posts/model-scorecards/option2/` |
| [reading-the-loop-option-3-hybrid.md](reading-the-loop-option-3-hybrid.md) | **Hybrid loop atlas** — 2 custom + 3 paper figures | 5 PNGs in `assets/posts/model-scorecards/option3/` |
| [reading-the-loop-option-3-hybrid-plus-paper.md](reading-the-loop-option-3-hybrid-plus-paper.md) | **Hybrid + full paper tour** — option 3 frame plus every option 2 figure appended | 11 PNGs (`option2/` + `option3/`) |

Each draft includes a **Figures** section with MLA citations for every illustration.

**Regenerate assets (caption-aware cropping):**
```bash
python scripts/generate_reading_the_loop_assets.py
python scripts/build_reading_the_loop_drafts.py
```

Paper extracts crop the figure *above* its caption (or the table block above "Table 1:" on DreamZero p10), not full PDF pages.

Draft image links use `../assets/...` (plain Markdown) so they render in VS Code preview.

**Published:** `reading-the-loop-option-3-hybrid-plus-paper` is live in `_posts/2026-06-03-reading-the-loop.md`. Re-publish with `python scripts/build_reading_the_loop_drafts.py publish`.
