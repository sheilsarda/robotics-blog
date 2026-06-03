# Post images

All blog post images live here, not under `_posts/`.

## Layout

```
assets/posts/<slug>/<filename>
```

- **`<slug>`** — matches the post front matter `slug:` (e.g. `vlas-in-contact`, `interoperable-sim-hardware-backends`).
- **`<filename>`** — descriptive name for new work (`01-bridge-overview.png`). Substack imports may keep hash-style names; that is fine.

## Markdown in `_posts/`

```markdown
![Alt text]({{ site.baseurl }}/assets/posts/<slug>/filename.png)
```

## Drafts in `_drafts/`

Use a relative path so VS Code preview works:

```markdown
![Alt text](../assets/posts/<slug>/filename.png)
```

Promote to `_posts/` with `{{ site.baseurl }}` before publishing.

## Do not commit

- arXiv PDFs or audit caches (`_drafts/_pdf_audit/`)
- Large binaries outside this tree

Regenerate reading-the-loop figures: `python scripts/generate_reading_the_loop_assets.py`
