"""
Pocketprep missed-question scraper + mnemonic learning plan generator.

Requires: pip install playwright && python -m playwright install chromium

Usage:
    # Set credentials as env vars (recommended):
    export POCKETPREP_EMAIL="you@email.com"
    export POCKETPREP_PASSWORD="yourpassword"
    python3 pocketprep_scraper.py

    # Or just run and it will prompt:
    python3 pocketprep_scraper.py

Output files (written next to this script):
    missed_questions.json   — raw captured question data
    learning_plan.md        — study plan with mnemonics
"""

import json
import os
import sys
import time
import getpass
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OUT_DIR = Path(__file__).parent
QUESTIONS_FILE = OUT_DIR / "missed_questions.json"
PLAN_FILE = OUT_DIR / "learning_plan.md"
DEBUG_FILE = OUT_DIR / "debug_page.html"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_credentials():
    email = os.environ.get("POCKETPREP_EMAIL") or input("Pocketprep email: ").strip()
    password = os.environ.get("POCKETPREP_PASSWORD") or getpass.getpass("Pocketprep password: ")
    if not email or not password:
        print("[!] Email and password are required.")
        sys.exit(1)
    return email, password


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------

def scrape_missed_questions(email: str, password: str) -> list[dict]:
    """
    Opens a headless browser, logs in to Pocketprep, navigates to missed
    questions, and captures question data from both DOM and API responses.
    """
    captured: list[dict] = []

    # Prefer the pre-installed Chromium if present (CI / remote sandboxes)
    _PREINSTALLED = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
    _exec = _PREINSTALLED if Path(_PREINSTALLED).exists() else None

    with sync_playwright() as pw:
        launch_kwargs: dict = dict(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        if _exec:
            launch_kwargs["executable_path"] = _exec
        browser = pw.chromium.launch(**launch_kwargs)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=True,
        )
        ctx.set_default_timeout(30_000)
        page = ctx.new_page()

        # Intercept API responses to capture question data directly
        page.on("response", lambda r: _intercept_response(r, captured))

        # ---- Login -------------------------------------------------------
        print("[*] Opening Pocketprep …")
        _goto(page, "https://app.pocketprep.com")

        # Wait for any input field (login form)
        try:
            page.wait_for_selector("input", timeout=15_000)
        except PWTimeout:
            # Try clicking a Login / Sign In button if the landing page shows one
            for label in ["Log In", "Sign In", "Login", "Get Started"]:
                try:
                    page.click(f"text={label}", timeout=3_000)
                    page.wait_for_selector("input", timeout=10_000)
                    break
                except PWTimeout:
                    continue
            else:
                _save_debug(page, "No input found on login page")
                browser.close()
                sys.exit(1)

        print("[*] Filling credentials …")
        # Email field
        for sel in [
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='email' i]",
            "input[placeholder*='username' i]",
            "input",
        ]:
            try:
                page.fill(sel, email, timeout=3_000)
                break
            except Exception:
                continue

        # Password field
        for sel in ["input[type='password']", "input[name='password']"]:
            try:
                page.fill(sel, password, timeout=3_000)
                break
            except Exception:
                continue

        # Submit
        try:
            page.click("button[type='submit']", timeout=3_000)
        except Exception:
            page.keyboard.press("Enter")

        # Wait for post-login page
        print("[*] Waiting for login to complete …")
        try:
            page.wait_for_url("**/dashboard**", timeout=20_000)
        except PWTimeout:
            try:
                # Accept any URL change away from login
                page.wait_for_function(
                    "() => !window.location.href.includes('login') && "
                    "!window.location.href.includes('signin')",
                    timeout=15_000,
                )
            except PWTimeout:
                # Check if there's an error message
                content = page.content().lower()
                if "incorrect" in content or "invalid" in content or "wrong" in content:
                    print("[!] Login failed — check your email/password.")
                else:
                    print("[!] Login timed out. URL:", page.url)
                    _save_debug(page, "Login timeout")
                browser.close()
                sys.exit(1)

        print(f"[+] Logged in! URL: {page.url}")
        time.sleep(2)

        # ---- Navigate to missed questions --------------------------------
        _navigate_to_missed_questions(page, captured)

        browser.close()

    return captured


def _goto(page, url: str):
    """Navigate with graceful fallback from networkidle to domcontentloaded."""
    try:
        page.goto(url, wait_until="networkidle", timeout=20_000)
    except PWTimeout:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15_000)
            time.sleep(3)
        except Exception as e:
            print(f"[!] Navigation error: {e}")
            sys.exit(1)


def _navigate_to_missed_questions(page, captured: list):
    """
    Strategy 1: Look for NREMT exam → Missed mode → start quiz.
    Strategy 2: Direct URL shortcuts.
    Strategy 3: API endpoint polling.
    """

    # --- Strategy 1: UI-based navigation ---------------------------------
    print("[*] Looking for NREMT exam …")

    # Click on NREMT / EMT exam
    for label in ["NREMT", "EMT", "Emergency Medical"]:
        try:
            page.click(f"text={label}", timeout=5_000)
            time.sleep(2)
            print(f"[*] Clicked '{label}'")
            break
        except PWTimeout:
            continue

    # Click Quiz or Study mode
    for label in ["Quiz", "Study", "Practice"]:
        try:
            page.click(f"text={label}", timeout=4_000)
            time.sleep(1.5)
            break
        except PWTimeout:
            continue

    # Click Missed mode
    for label in ["Missed", "missed", "Incorrect", "Wrong"]:
        try:
            page.click(f"text={label}", timeout=5_000)
            time.sleep(2)
            print(f"[*] Selected '{label}' mode")
            break
        except PWTimeout:
            continue

    # Click Start / Begin
    for label in ["Start", "Begin", "Start Quiz", "Take Quiz"]:
        try:
            page.click(f"text={label}", timeout=5_000)
            time.sleep(2)
            print(f"[*] Clicked '{label}'")
            break
        except PWTimeout:
            continue

    # --- Strategy 2: Direct URL shortcuts --------------------------------
    if not _looks_like_quiz(page):
        print("[*] UI nav didn't reach quiz — trying direct URLs …")
        quiz_urls = [
            "https://app.pocketprep.com/quiz?mode=missed",
            "https://app.pocketprep.com/quiz/missed",
            "https://app.pocketprep.com/study?mode=missed",
        ]
        for url in quiz_urls:
            _goto(page, url)
            time.sleep(3)
            if _looks_like_quiz(page):
                print(f"[*] Reached quiz via {url}")
                break

    # --- Walk through questions ------------------------------------------
    if _looks_like_quiz(page):
        _walk_quiz(page, captured)
    else:
        print("[!] Could not locate quiz. Saving debug page.")
        _save_debug(page, "Could not find quiz page")


def _looks_like_quiz(page) -> bool:
    try:
        content = page.content().lower()
        return any(k in content for k in ["question", "choice", "answer", "option"])
    except Exception:
        return False


def _walk_quiz(page, captured: list):
    """Iterate through every question in the quiz, scraping each one."""
    print("[*] Walking through questions …")
    max_q = 600
    seen: set[str] = set()
    no_new_streak = 0

    for _ in range(max_q):
        # First try to reveal the answer (click Submit / Check if needed)
        _try_submit_answer(page)

        q = _scrape_question_dom(page)
        if q:
            key = q["question_text"][:80]
            if key not in seen:
                seen.add(key)
                captured.append(q)
                no_new_streak = 0
                print(f"  [+] Q{len(captured)}: {key[:65]} …")
            else:
                no_new_streak += 1
        else:
            no_new_streak += 1

        if no_new_streak >= 5:
            print("[*] No new questions — quiz complete or stuck.")
            break

        # Advance to next question
        if not _advance_question(page):
            break

    print(f"[*] Walk complete. {len(captured)} questions via DOM.")


def _try_submit_answer(page):
    """Click Submit/Check to reveal the explanation if the question is unanswered."""
    for label in ["Submit", "Check", "Confirm"]:
        try:
            page.click(f"button:has-text('{label}')", timeout=1_500)
            time.sleep(1)
            return
        except Exception:
            continue


def _advance_question(page) -> bool:
    """Click next/continue to move to the next question."""
    for label in ["Next Question", "Next", "Continue", ">"]:
        try:
            page.click(f"button:has-text('{label}')", timeout=2_000)
            time.sleep(1.5)
            return True
        except Exception:
            continue

    # Fallback: arrow key
    try:
        page.keyboard.press("ArrowRight")
        time.sleep(1)
        return True
    except Exception:
        return False


def _scrape_question_dom(page) -> dict | None:
    """Extract question, choices, answer, explanation from the current DOM."""
    try:
        q_text = _first_text(page, [
            "[class*='question-text' i]",
            "[class*='questionText' i]",
            "[class*='question__body' i]",
            "[class*='question__stem' i]",
            "[data-testid*='question-stem']",
            "[data-testid*='question']",
            ".question p",
            "h2, h3",
        ], min_len=10)

        if not q_text:
            return None

        choices = []
        for sel in [
            "[class*='answer-choice' i]",
            "[class*='answerChoice' i]",
            "[class*='answer__text' i]",
            "[class*='choice__text' i]",
            "[class*='option__text' i]",
            "li[class*='answer' i]",
            "label[class*='answer' i]",
        ]:
            try:
                els = page.query_selector_all(sel)
                if els:
                    texts = [e.inner_text().strip() for e in els]
                    texts = [t for t in texts if t]
                    if texts:
                        choices = texts
                        break
            except Exception:
                continue

        correct = _first_text(page, [
            "[class*='correct-answer' i]",
            "[class*='correctAnswer' i]",
            "[aria-label*='correct' i]",
            "[class*='answer' i][class*='correct' i]",
        ])

        explanation = _first_text(page, [
            "[class*='explanation' i]",
            "[class*='rationale' i]",
            "[class*='feedback' i]",
            "[class*='answer-explanation' i]",
            "[data-testid*='explanation']",
        ], min_len=5)

        category = _first_text(page, [
            "[class*='category' i]",
            "[class*='topic' i]",
            "[class*='subject' i]",
            "[class*='section' i]",
            "[data-testid*='category']",
        ], min_len=2)

        return {
            "question_text": q_text,
            "choices": choices,
            "correct_answer": correct,
            "explanation": explanation,
            "category": category,
            "source": "dom",
        }
    except Exception:
        return None


def _first_text(page, selectors: list[str], min_len: int = 1) -> str | None:
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                if len(text) >= min_len:
                    return text
        except Exception:
            continue
    return None


# ---------------------------------------------------------------------------
# API response interception
# ---------------------------------------------------------------------------

def _intercept_response(response, captured: list):
    """Called for every HTTP response; extracts question data from API JSON."""
    try:
        url = response.url
        if response.status != 200:
            return
        ct = response.headers.get("content-type", "")
        if "json" not in ct:
            return
        if "pocketprep" not in url.lower():
            return

        data = response.json()
        _harvest(data, url, captured)
    except Exception:
        pass


def _harvest(data, url: str, captured: list):
    if isinstance(data, list):
        for item in data:
            _harvest(item, url, captured)
        return
    if not isinstance(data, dict):
        return

    # Detected a question object
    text_keys = {"questionBody", "question_body", "questionText", "question", "stem"}
    if text_keys & set(data.keys()):
        q = _normalize_api_q(data, url)
        if q:
            captured.append(q)
        return

    # Recurse into container keys
    for key in ("questions", "data", "results", "items", "payload", "content"):
        if key in data and isinstance(data[key], (list, dict)):
            _harvest(data[key], url, captured)


def _normalize_api_q(data: dict, url: str) -> dict | None:
    text = (
        data.get("questionBody")
        or data.get("question_body")
        or data.get("questionText")
        or data.get("stem")
        or data.get("question")
        or ""
    )
    if not text:
        return None

    raw_choices = data.get("answers") or data.get("choices") or data.get("options") or []
    choices = []
    correct = None
    for c in raw_choices:
        if isinstance(c, dict):
            label = c.get("body") or c.get("text") or c.get("answer") or ""
            choices.append(label)
            if c.get("correct") or c.get("isCorrect"):
                correct = label
        elif isinstance(c, str):
            choices.append(c)

    correct = correct or data.get("correctAnswer") or data.get("correct_answer")
    explanation = (
        data.get("explanation")
        or data.get("rationale")
        or data.get("feedback")
        or data.get("answerExplanation")
        or data.get("answer_explanation")
    )

    return {
        "question_text": str(text).strip(),
        "choices": choices,
        "correct_answer": correct,
        "explanation": explanation,
        "category": (
            data.get("category")
            or data.get("subject")
            or data.get("topic")
            or data.get("section")
        ),
        "source": "api",
        "source_url": url,
    }


def _save_debug(page, reason: str):
    DEBUG_FILE.write_text(page.content())
    try:
        page.screenshot(path=str(OUT_DIR / "debug_screenshot.png"))
    except Exception:
        pass
    print(f"[!] {reason}. Debug saved to {DEBUG_FILE}")


# ---------------------------------------------------------------------------
# Learning plan generator
# ---------------------------------------------------------------------------

NREMT_MNEMONICS = """\
## NREMT Core Mnemonics

| Mnemonic | Stands for | Use when |
|----------|-----------|----------|
| **PENMAN** | Personal safety / Environment / Number of pts / Mechanism / Additional resources / Nature of illness | Scene size-up |
| **MOANS** | Mask seal / Obese / Aged / No teeth / Stiff lungs | Predicting difficult BVM ventilation |
| **DOPE** | Displaced tube / Obstruction / Pneumothorax / Equipment failure | Intubated patient deteriorates |
| **H's & T's** | Hypovolemia, Hypoxia, H⁺ (acidosis), Hypo/Hyperkalemia, Hypothermia / Tension PTX, Tamponade, Toxins, Thrombosis (PE), Thrombosis (MI) | PEA / Asystole reversible causes |
| **DCAP-BTLS** | Deformity / Contusions / Abrasions / Punctures–Burns / Tenderness / Lacerations / Swelling | Trauma physical exam |
| **SAMPLE** | Signs & Symptoms / Allergies / Medications / Pertinent history / Last oral intake / Events | Patient history |
| **OPQRST** | Onset / Provocation / Quality / Radiation / Severity / Time | Pain assessment |
| **AEIOU-TIPS** | Alcohol / Epilepsy / Insulin / Opiates / Uremia // Trauma / Infection / Psychiatric / Stroke | Altered mental status |
| **TICLS** | Tone / Interactivity / Consolability / Look / Speech–cry | Pediatric Assessment Triangle |
| **MUDPILES** | Methanol / Uremia / DKA / Propylene glycol / Isoniazid–Iron / Lactic acidosis / Ethylene glycol / Salicylates | High anion-gap metabolic acidosis |
| **VIP** | Ventilation / Irrigation (fluids) / Pressors | Shock management order |
| **AVPU** | Alert / Verbal / Pain / Unresponsive | Rapid LOC scale |
"""

CATEGORY_MNEMONICS = {
    "airway": "**MOANS** — predicts difficult BVM; **DOPE** — intubated patient suddenly worse",
    "breathing": "**DOPE** (Displaced/Obstruction/Pneumothorax/Equipment) for any ventilated patient decline",
    "circulation": "Shockable rhythms → SHOCK them. PEA/Asystole → fix **H's & T's**",
    "cardiac": "**H's & T's** — the 10 reversible causes of cardiac arrest",
    "trauma": "**DCAP-BTLS** for head-to-toe exam; **PENMAN** for scene size-up",
    "neuro": "**AEIOU-TIPS** for altered LOC; **AVPU** for rapid neuro check",
    "medical": "**SAMPLE** history + **OPQRST** pain = complete medical assessment",
    "pediatric": "**TICLS** (PAT) → primary → secondary; weight = (age + 4) × 2 kg",
    "obstetric": "**HELLP** (Hemolysis / Elevated LFTs / Low Platelets) = severe preeclampsia",
    "pharmacology": "**MUDPILES** for anion gap; remember naloxone = 0.4–2 mg for opioid reversal",
    "respiratory": "**DOPE** for ventilated; for spontaneous → assess rate, depth, effort, SpO₂",
    "shock": "**VIP** — Ventilate, Irrigate (IVF), Pressors; classify: distributive/obstructive/cardiogenic/hypovolemic",
    "default": "**SAMPLE** + **OPQRST** for any patient encounter",
}


def generate_learning_plan(questions: list[dict]) -> str:
    if not questions:
        return "# No missed questions captured.\n\nTry running the scraper again after manually starting a Missed Questions quiz session.\n"

    by_cat: dict[str, list[dict]] = {}
    for q in questions:
        cat = (q.get("category") or "General").strip().lower()
        by_cat.setdefault(cat, []).append(q)

    lines = [
        "# NREMT Missed-Question Learning Plan",
        "",
        f"> **{len(questions)} missed questions** captured from Pocketprep",
        "> Work through these in priority order (most-missed topics first).",
        "",
        "---",
        "",
        NREMT_MNEMONICS,
        "",
        "---",
        "",
        "## Priority Study Order",
        "",
        "| Priority | Topic | Missed |",
        "|----------|-------|--------|",
    ]

    sorted_cats = sorted(by_cat.items(), key=lambda x: -len(x[1]))
    for i, (cat, qs) in enumerate(sorted_cats, 1):
        lines.append(f"| {i} | {cat.title()} | {len(qs)} |")

    lines += ["", "---", "", "## Questions by Topic", ""]

    for cat, qs in sorted_cats:
        mnemonic = _find_mnemonic(cat)
        lines.append(f"### {cat.title()} — {len(qs)} missed")
        lines.append(f"> Memory anchor: {mnemonic}")
        lines.append("")

        for i, q in enumerate(qs, 1):
            lines.append(f"#### Q{i}")
            lines.append(q["question_text"])
            lines.append("")
            if q.get("choices"):
                for ch in q["choices"]:
                    if ch:
                        lines.append(f"- {ch}")
                lines.append("")
            if q.get("correct_answer"):
                lines.append(f"**Correct answer:** {q['correct_answer']}")
                lines.append("")
            if q.get("explanation"):
                lines.append(f"**Explanation:** {q['explanation']}")
                lines.append("")
            lines.append("---")
            lines.append("")

    lines += [
        "## Spaced Repetition Schedule",
        "",
        "| Day | Action |",
        "|-----|--------|",
        "| Today | Read through all questions + explanations once |",
        "| +1 day | Re-test yourself on all — note which you miss again |",
        "| +3 days | Re-test missed-again subset |",
        "| +1 week | Full missed-questions re-test |",
        "| +2 weeks | Final sweep before exam |",
        "",
        "## Test-Taking Tips",
        "",
        "- Read the **last sentence** of the question first to know what's being asked",
        "- Eliminate answers that are **always wrong** (cruel, harmful, ignore the patient)",
        "- When two answers seem correct, pick the one done **first** (assessment before treatment)",
        "- For dosing questions: use **SAMPLE** to check for contraindications first",
        "- Suspected spinal injury → neutral inline stabilization **before** airway maneuvers",
        "",
    ]

    return "\n".join(lines)


def _find_mnemonic(cat: str) -> str:
    cat = cat.lower()
    for key, val in CATEGORY_MNEMONICS.items():
        if key in cat or cat in key:
            return val
    return CATEGORY_MNEMONICS["default"]


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate(questions: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for q in questions:
        key = re.sub(r"\s+", " ", q.get("question_text", ""))[:120].lower()
        if key and key not in seen:
            seen.add(key)
            out.append(q)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Pocketprep NREMT Missed-Question Scraper")
    print("=" * 60)
    print()

    email, password = get_credentials()
    print()

    questions = scrape_missed_questions(email, password)
    questions = deduplicate(questions)

    print(f"\n[+] {len(questions)} unique missed questions captured.")

    if not questions:
        print("\n[!] Nothing captured.")
        print("    Suggestions:")
        print("    1. Make sure you have missed questions in your Pocketprep account")
        print("    2. Check debug_page.html to see where the browser got stuck")
        print("    3. Run the scraper once, then manually start a Missed Quiz session")
        print("       and leave the browser open — the API interceptor will catch data")
        sys.exit(1)

    QUESTIONS_FILE.write_text(json.dumps(questions, indent=2, ensure_ascii=False))
    print(f"[+] Raw questions → {QUESTIONS_FILE}")

    plan = generate_learning_plan(questions)
    PLAN_FILE.write_text(plan)
    print(f"[+] Learning plan  → {PLAN_FILE}")

    print("\n[+] Done! Open learning_plan.md to start studying.")


if __name__ == "__main__":
    main()
