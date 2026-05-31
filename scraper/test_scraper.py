"""
End-to-end integration test.
Starts mock_server.py, patches pocketprep_scraper to point at localhost,
then runs the full scrape + plan generation and asserts correctness.
"""
import json
import sys
import time
import threading
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

import mock_server
import pocketprep_scraper as scraper

BASE_URL = f"http://127.0.0.1:{mock_server.PORT}"
CHROME_PATH = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# ---- patch the scraper's navigation targets ----------------------------

ORIGINAL_GOTO = scraper._goto
ORIGINAL_NAV = scraper._navigate_to_missed_questions


def patched_goto(page, url: str):
    """Redirect any pocketprep URL → local mock."""
    local = url.replace("https://app.pocketprep.com", BASE_URL)
    ORIGINAL_GOTO(page, local)


def patched_navigate(page, captured):
    """Walk the mock quiz pages directly."""
    from playwright.sync_api import sync_playwright

    print("[test] Navigating mock quiz …")
    # Hit the API endpoint first (tests API interception)
    patched_goto(page, "https://app.pocketprep.com/api/questions/missed")
    time.sleep(1)

    # Walk DOM quiz pages
    for i in range(len(mock_server.MOCK_QUESTIONS) + 1):
        patched_goto(page, f"https://app.pocketprep.com/quiz?mode=missed&q={i}")
        time.sleep(0.3)
        q = scraper._scrape_question_dom(page)
        if q:
            key = q["question_text"][:80]
            seen_keys = {c["question_text"][:80] for c in captured}
            if key not in seen_keys:
                captured.append(q)
                print(f"  [dom] captured: {key[:60]} …")


# ---- main test ---------------------------------------------------------

def run():
    print("=" * 60)
    print("  Integration Test — Pocketprep Scraper vs Mock Server")
    print("=" * 60)

    # 1. Start mock server
    mock_server.start()
    time.sleep(0.3)

    # 2. Patch scraper internals to use local server
    with (
        patch.object(scraper, "_goto", patched_goto),
        patch.object(scraper, "_navigate_to_missed_questions", patched_navigate),
    ):
        questions = scraper.scrape_missed_questions(
            email="test@example.com",
            password="testpass123",
        )

    questions = scraper.deduplicate(questions)

    # ---- Assertions -------------------------------------------------------
    failures = []

    def check(condition: bool, msg: str):
        if condition:
            print(f"  [PASS] {msg}")
        else:
            print(f"  [FAIL] {msg}")
            failures.append(msg)

    print("\n--- Assertions ---")
    check(len(questions) > 0, f"Captured at least 1 question (got {len(questions)})")
    check(len(questions) == len(mock_server.MOCK_QUESTIONS),
          f"Captured all {len(mock_server.MOCK_QUESTIONS)} questions (got {len(questions)})")

    for q in questions:
        check(bool(q.get("question_text")), f"question_text present: {q.get('question_text','')[:40]}")
        check(bool(q.get("correct_answer") or q.get("choices")),
              f"answer data present for: {q.get('question_text','')[:40]}")

    # Check a specific known question
    cardiac = next((q for q in questions if "unresponsive" in q["question_text"].lower()), None)
    check(cardiac is not None, "Found cardiac arrest question")
    if cardiac:
        check(
            "chest compressions" in (cardiac.get("correct_answer") or "").lower()
            or any("chest compressions" in c.lower() for c in cardiac.get("choices", [])),
            "Cardiac arrest question has 'chest compressions' in answer/choices"
        )

    # Learning plan generation
    print("\n--- Learning Plan ---")
    plan = scraper.generate_learning_plan(questions)
    check(len(plan) > 100, "Learning plan is non-empty")
    check("NREMT" in plan, "Learning plan mentions NREMT")
    check("Mnemonic" in plan or "mnemonic" in plan.lower() or "MOANS" in plan or "SAMPLE" in plan,
          "Learning plan includes mnemonics")
    check("Cardiac" in plan or "cardiac" in plan.lower(), "Learning plan includes cardiac topic")
    check("Trauma" in plan or "trauma" in plan.lower(), "Learning plan includes trauma topic")

    # Write outputs
    out_dir = Path(__file__).parent
    (out_dir / "missed_questions.json").write_text(json.dumps(questions, indent=2))
    (out_dir / "learning_plan.md").write_text(plan)
    print(f"\n[+] Outputs written to scraper/")

    # ---- Summary ----------------------------------------------------------
    print(f"\n{'='*60}")
    total = len(failures) + plan.count("[PASS]") + sum(
        1 for line in open(__file__).readlines() if "check(" in line
    )
    if failures:
        print(f"RESULT: {len(failures)} assertion(s) FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"RESULT: ALL ASSERTIONS PASSED ({len(questions)} questions captured)")
        print("The scraper works correctly end-to-end.")
    print("=" * 60)


if __name__ == "__main__":
    run()
