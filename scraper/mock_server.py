"""
Local mock server that mimics the Pocketprep app.
Serves: login page, dashboard, quiz page, and JSON API responses.
Run alongside pocketprep_scraper.py to prove the scraper works end-to-end.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import threading

PORT = 8765

MOCK_QUESTIONS = [
    {
        "id": 1,
        "questionBody": "A 34-year-old male is found unresponsive. Bystanders report he collapsed suddenly. You find no pulse and no breathing. What is your FIRST action?",
        "answers": [
            {"body": "Begin chest compressions", "correct": True},
            {"body": "Apply the AED immediately", "correct": False},
            {"body": "Open the airway with a head-tilt chin-lift", "correct": False},
            {"body": "Call for ALS backup", "correct": False},
        ],
        "explanation": "CPR starts with chest compressions (C-A-B sequence per AHA 2010+). High-quality compressions maintain perfusion pressure. Apply AED as soon as it arrives but do not delay compressions.",
        "category": "Cardiac Arrest",
    },
    {
        "id": 2,
        "questionBody": "You are assessing an adult patient with suspected tension pneumothorax. Which finding BEST confirms this diagnosis?",
        "answers": [
            {"body": "Absent breath sounds on one side with tracheal deviation away from the injury", "correct": True},
            {"body": "Bilateral crackles and SpO2 of 88%", "correct": False},
            {"body": "JVD with equal breath sounds bilaterally", "correct": False},
            {"body": "Subcutaneous emphysema with normal BP", "correct": False},
        ],
        "explanation": "Tension pneumothorax classically presents with absent unilateral breath sounds, tracheal deviation AWAY from the affected side, JVD, hypotension, and tachycardia. It is a clinical diagnosis — do not wait for imaging. Treat immediately with needle decompression.",
        "category": "Trauma",
    },
    {
        "id": 3,
        "questionBody": "A 6-year-old child is brought in with respiratory distress. Using the Pediatric Assessment Triangle, you note: limp muscle tone, no eye contact with you, inconsolable crying, and mottled skin. What does this PAT indicate?",
        "answers": [
            {"body": "Respiratory failure with circulatory failure", "correct": True},
            {"body": "Stable child with mild respiratory distress", "correct": False},
            {"body": "Isolated circulatory problem", "correct": False},
            {"body": "CNS/metabolic problem only", "correct": False},
        ],
        "explanation": "PAT = TICLS: Tone (limp), Interactivity (no eye contact), Consolability (inconsolable), Look/Gaze (poor), Speech/Cry (crying = air movement). Abnormal appearance + abnormal circulation = respiratory failure with circulatory compromise. Immediate intervention required.",
        "category": "Pediatric",
    },
    {
        "id": 4,
        "questionBody": "Which of the following BEST describes the correct sequence for managing a patient in hypovolemic shock?",
        "answers": [
            {"body": "Control hemorrhage → establish IV access → administer isotonic fluids → reassess", "correct": True},
            {"body": "Administer vasopressors → control hemorrhage → reassess", "correct": False},
            {"body": "Administer oxygen → administer fluids → control hemorrhage", "correct": False},
            {"body": "Establish airway → administer 2L NS bolus → transport", "correct": False},
        ],
        "explanation": "Hypovolemic shock management follows VIP: Ventilate, Irrigate (fluids), Pressors — but hemorrhage CONTROL comes first. Pouring fluids into an uncontrolled bleed is futile. Control the source, then resuscitate. Use isotonic crystalloids (NS or LR) for initial volume.",
        "category": "Shock",
    },
    {
        "id": 5,
        "questionBody": "A conscious adult patient is experiencing a severe allergic reaction with urticaria, bronchospasm, and hypotension. What is the drug of choice and route?",
        "answers": [
            {"body": "Epinephrine 0.3 mg IM into the lateral thigh", "correct": True},
            {"body": "Diphenhydramine 50 mg IV", "correct": False},
            {"body": "Epinephrine 1 mg IV push", "correct": False},
            {"body": "Albuterol nebulizer only", "correct": False},
        ],
        "explanation": "Anaphylaxis first-line = Epinephrine 0.3–0.5 mg (1:1000) IM lateral thigh. IM gives faster absorption than SQ. IV epinephrine (1:10,000) is reserved for cardiac arrest or refractory anaphylaxis with IV access in monitored setting. Antihistamines are adjuncts — they do NOT reverse anaphylaxis.",
        "category": "Pharmacology",
    },
]

LOGIN_PAGE = """<!DOCTYPE html>
<html>
<head><title>Pocket Prep</title></head>
<body>
  <h1>Sign In</h1>
  <form method="POST" action="/login">
    <input type="email" name="email" placeholder="Email address" /><br>
    <input type="password" name="password" placeholder="Password" /><br>
    <button type="submit">Log In</button>
  </form>
</body>
</html>"""

DASHBOARD_PAGE = """<!DOCTYPE html>
<html>
<head><title>Dashboard - Pocket Prep</title></head>
<body>
  <h1>Dashboard</h1>
  <p>Welcome back!</p>
  <a href="/quiz?mode=missed">NREMT</a>
  <a href="/quiz?mode=missed">Missed</a>
  <button onclick="location.href='/quiz?mode=missed'">Start</button>
</body>
</html>"""

def make_quiz_page(q_index: int) -> str:
    if q_index >= len(MOCK_QUESTIONS):
        return """<!DOCTYPE html><html><body><h1>Quiz Complete</h1><p>You have reviewed all missed questions.</p></body></html>"""
    q = MOCK_QUESTIONS[q_index]
    choices_html = "\n".join(
        f'<li class="answer-choice">{a["body"]}</li>' for a in q["answers"]
    )
    correct = next(a["body"] for a in q["answers"] if a["correct"])
    return f"""<!DOCTYPE html>
<html>
<head><title>Quiz - Pocket Prep</title></head>
<body>
  <div class="category">{q["category"]}</div>
  <div class="question-text">{q["questionBody"]}</div>
  <ul>{choices_html}</ul>
  <div class="correct-answer">{correct}</div>
  <div class="explanation">{q["explanation"]}</div>
  <button onclick="location.href='/quiz?mode=missed&q={q_index+1}'">Next Question</button>
</body>
</html>"""


class MockHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # Silence default request logging

    def _respond(self, status: int, content_type: str, body: str | bytes):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/" or path == "/login" or path == "/signin":
            self._respond(200, "text/html", LOGIN_PAGE)

        elif path == "/dashboard":
            self._respond(200, "text/html", DASHBOARD_PAGE)

        elif path == "/quiz":
            q_index = int(params.get("q", ["0"])[0])
            self._respond(200, "text/html", make_quiz_page(q_index))

        elif path == "/api/questions/missed":
            # Simulate an API endpoint that returns questions as JSON
            self._respond(200, "application/json", json.dumps({
                "data": {
                    "questions": MOCK_QUESTIONS
                }
            }))

        else:
            self._respond(404, "text/plain", "Not found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)
        email = params.get("email", [""])[0]
        password = params.get("password", [""])[0]

        if email and password:
            # Accept any non-empty credentials
            self.send_response(302)
            self.send_header("Location", "/dashboard")
            self.end_headers()
        else:
            self._respond(200, "text/html",
                LOGIN_PAGE.replace("</form>",
                    '<p style="color:red">Invalid credentials</p></form>'))


def start(port: int = PORT) -> threading.Thread:
    server = HTTPServer(("127.0.0.1", port), MockHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"[mock] Server running at http://127.0.0.1:{port}")
    return t


if __name__ == "__main__":
    import time
    start()
    print("[mock] Press Ctrl-C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
