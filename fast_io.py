#!/usr/bin/env python3
# Copyright (c) 2026 Niraj Mallik (@nirajmallik143-hub) | MIT License
import sys
import os
import json
import urllib.request

SYS_RULE = "Direct input = output mode. Return only the exact solution, command, or code. No greetings, no filler."
LOCAL_URL = "http://127.0.0.1:8080/v1/chat/completions"
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")


def stream_online(prompt: str) -> bool:
    if not GEMINI_KEY:
        return False
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:streamGenerateContent?alt=sse&key={GEMINI_KEY}"
    payload = {
        "systemInstruction": {"parts": [{"text": SYS_RULE}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            for raw in resp:
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line.startswith("data: "):
                    continue
                chunk = json.loads(line[6:])
                parts = chunk.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "text" in p:
                        sys.stdout.write(p["text"])
                        sys.stdout.flush()
        print()
        return True
    except Exception:
        return False


def stream_offline(prompt: str) -> None:
    payload = {
        "model": "qwen2.5-local",
        "messages": [
            {"role": "system", "content": SYS_RULE},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 256,
        "stream": True,
    }
    req = urllib.request.Request(
        LOCAL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        for raw in resp:
            line = raw.decode("utf-8", errors="ignore").strip()
            if not line.startswith("data: ") or line == "data: [DONE]":
                continue
            chunk = json.loads(line[6:])
            delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
            if delta:
                sys.stdout.write(delta)
                sys.stdout.flush()
    print()


if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:]).strip() or sys.stdin.read().strip()
    if not user_input:
        sys.exit(1)
    if not stream_online(user_input):
        stream_offline(user_input)
