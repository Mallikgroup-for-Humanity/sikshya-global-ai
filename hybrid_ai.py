# Copyright (c) 2026 Niraj Mallik (@nirajmallikhub) | MIT License
import os
import json
import urllib.request
import urllib.error

LOCAL_SERVER_URL = os.getenv("LOCAL_AI_URL", "http://127.0.0.1:8080/v1/chat/completions")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")


def _call_online_gemini(prompt: str, system_prompt: str = "You are a helpful AI assistant.") -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_offline_local(prompt: str, system_prompt: str = "You are a helpful AI assistant.") -> str:
    payload = {
        "model": "qwen2.5-local",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        LOCAL_SERVER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def generate_reply(prompt: str, system_prompt: str = "You are a helpful AI assistant.", force_offline: bool = False) -> dict:
    """
    Routes to Online Gemini first; automatically falls back to Offline llama.cpp (127.0.0.1:8080)
    on network failure, missing API key, or HTTP 429/503 rate limits.
    """
    if not force_offline:
        try:
            text = _call_online_gemini(prompt, system_prompt)
            return {"mode": "ONLINE (Gemini)", "reply": text}
        except Exception as online_err:
            print(f"[Hybrid Router] Online unavailable ({online_err}) -> Switching to Offline Local AI...")

    try:
        text = _call_offline_local(prompt, system_prompt)
        return {"mode": "OFFLINE (Local llama.cpp)", "reply": text}
    except Exception as offline_err:
        return {
            "mode": "ERROR",
            "reply": f"Both Online and Offline engines failed. Start local server with 'localai'. Details: {offline_err}",
        }


if __name__ == "__main__":
    result = generate_reply("Explain what Sikshya Global AI does in two sentences.")
    print(f"\n[{result['mode']}]\n{result['reply']}\n")
