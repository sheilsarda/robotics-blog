# Pocketprep NREMT Missed-Question Scraper

Logs in to your Pocketprep account, navigates to your missed NREMT questions,
and exports them to a Markdown study plan with mnemonics.

## Setup (one-time)

```bash
pip install playwright
python -m playwright install chromium
```

## Run

```bash
# Option A — env vars (recommended, avoids typing password in terminal history)
export POCKETPREP_EMAIL="you@example.com"
export POCKETPREP_PASSWORD="yourpassword"
python3 pocketprep_scraper.py

# Option B — interactive prompt
python3 pocketprep_scraper.py
```

## Output

| File | Contents |
|------|----------|
| `missed_questions.json` | Raw question data (question text, choices, correct answer, explanation) |
| `learning_plan.md` | Formatted study plan organized by topic with NREMT mnemonics |

## Troubleshooting

**Nothing captured / stuck at login:**
- Check `debug_page.html` — the scraper saves it whenever it gets stuck
- Verify your email/password work on `app.pocketprep.com` manually
- Make sure your account has missed questions (take a quiz first, miss some)

**Only a few questions captured:**
- Pocketprep may limit quiz sessions — run the scraper multiple times
- Try taking a "Missed Questions" quiz manually in your browser while the
  API interceptor runs (the scraper captures all network traffic)

**SSL errors:**
- The `ignore_https_errors=True` flag handles most cases; if you still see
  SSL errors, try running with `--ignore-certificate-errors` in the Chrome
  launch args (already included)
