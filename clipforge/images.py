"""Scene images for ClipForge.

Each scene gets a real AI-painted picture (free Pollinations image API,
no key, no account) instead of a plain text slide. If the download fails
for any reason, ClipForge falls back to the drawn slide - a run never
dies because of the network.
"""

import os
import urllib.parse
import urllib.request

from . import slides

API = "https://image.pollinations.ai/prompt/{prompt}"
STYLE = (
    "cinematic digital painting, rich detail, atmospheric light, "
    "vertical composition, no text, no words"
)


def build_prompt(topic: str, index: int) -> str:
    """One visual prompt per scene; the seed changes so scenes differ."""
    return f"{topic} - scene {index + 1}, {STYLE}"


def _looks_like_image(path: str) -> bool:
    if not os.path.exists(path) or os.path.getsize(path) < 5000:
        return False
    with open(path, "rb") as fh:
        head = fh.read(12)
    return (
        head.startswith(b"\xff\xd8")          # JPEG
        or head.startswith(b"\x89PNG")        # PNG
        or head[:4] == b"RIFF"                # WebP
    )


def fetch_scene_image(topic: str, line: str, index: int, total: int,
                      out_path: str, timeout: int = 60) -> str:
    """Download the scene picture; fall back to a drawn slide."""
    prompt = urllib.parse.quote(build_prompt(topic, index))
    url = (
        f"{API.format(prompt=prompt)}"
        f"?width=1080&height=1920&seed={42 + index}&nologo=true"
    )
    for _attempt in range(2):  # one retry - the API can hang or queue
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "ClipForge/0.2"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            with open(out_path, "wb") as fh:
                fh.write(data)
            if _looks_like_image(out_path):
                return out_path
        except Exception:
            continue
    slides.render_slide(line, index, total, out_path)
    return out_path
