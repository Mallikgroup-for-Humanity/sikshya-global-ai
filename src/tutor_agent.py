import os, json, urllib.request

STATE_FILE = "data/student_state.json"
API_KEY = os.getenv("GEMINI_API_KEY", "")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"student": "Student", "history": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def ask_tutor(prompt, state):
    if not API_KEY:
        return "Set GEMINI_API_KEY first: export GEMINI_API_KEY='your_key'"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    system_msg = (
        "You are Sikshya Global AI, a bilingual (English + Nepali) tutor built by Mallik Group. "
        "Remember previous questions and adapt explanations to the student's level."
    )
    context = "\n".join(state["history"][-6:])
    payload = {
        "contents": [{"parts": [{"text": f"{system_msg}\n\nRecent Context:\n{context}\n\nStudent: {prompt}"}]}]
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        return data["candidates"][0]["content"]["parts"][0]["text"]

if __name__ == "__main__":
    state = load_state()
    print("=== Sikshya Global AI Agent (Type 'exit' to suspend state) ===")
    while True:
        q = input("\nYou: ").strip()
        if q.lower() in ("exit", "quit"):
            save_state(state)
            print("Agent state suspended to disk.")
            break
        ans = ask_tutor(q, state)
        print(f"\nSikshya AI: {ans}")
        state["history"].append(f"User: {q}\nAI: {ans}")
        save_state(state)
