"""Script writing for ClipForge.

Two modes:
- Gemini mode (best quality): if a GEMINI_API_KEY is available, a real
  narration script is written by the model.
- Offline mode (always works): starter templates built around the topic,
  so the pipeline runs with no key, no account, and no cost.
"""

import json
import os
import urllib.request

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)


def _offline_script(topic: str) -> list[str]:
    """Template scenes used when no API key is available."""
    t = topic.strip().rstrip(".")
    cap = t[0].upper() + t[1:] if t else t
    return [
        f"{cap}. You have heard the name - but do you know the real story?",
        f"It starts in a place most people walk past without looking twice: the world of {t}.",
        f"Here is what makes {t} different. It was not built in a day, and it was not built by accident.",
        f"Every detail of {t} exists for a reason - and once you see it, you cannot unsee it.",
        f"So next time someone mentions {t}, remember: the story is always bigger than it looks.",
        "Follow for more stories like this.",
    ]


def _gemini_script(topic: str, api_key: str) -> list[str]:
    prompt = (
        "Write a narration script for a 40-second vertical short video about: "
        f"{topic}\n"
        "Rules: exactly 6 short lines, one idea per line, spoken style, "
        "strong hook in line 1, no hashtags, no emojis, no stage directions. "
        "Reply with ONLY a JSON list of strings."
    )
    body = json.dumps(
        {"contents": [{"parts": [{"text": prompt}]}]}
    ).encode("utf-8")
    req = urllib.request.Request(
        GEMINI_URL.format(model=GEMINI_MODEL, key=api_key),
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("["):]
    scenes = json.loads(text)
    scenes = [str(s).strip() for s in scenes if str(s).strip()]
    if len(scenes) < 3:
        raise ValueError("script too short")
    return scenes


def build_script(topic: str, api_key: str | None = None) -> list[str]:
    """Return a list of narration lines (one per scene)."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if key:
        try:
            return _gemini_script(topic, key)
        except Exception:
            pass  # fall through to the offline script
    return _offline_script(topic)
