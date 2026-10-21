"""Text-to-speech for ClipForge (Microsoft Edge voices via edge-tts).

Free to use, no account and no API key required.
"""

import asyncio
import os
import subprocess

DEFAULT_VOICE = "en-US-ChristopherNeural"


async def _save(text: str, voice: str, out_path: str) -> None:
    import edge_tts

    # Behind a proxy (office, school, some countries) the speech endpoint
    # is only reachable through it - honour the standard env variables.
    proxy = (
        os.environ.get("HTTPS_PROXY")
        or os.environ.get("https_proxy")
        or os.environ.get("HTTP_PROXY")
        or os.environ.get("http_proxy")
    )
    kwargs = {"proxy": proxy} if proxy else {}
    await edge_tts.Communicate(text, voice, **kwargs).save(out_path)


def speak(text: str, out_path: str, voice: str = DEFAULT_VOICE) -> str:
    """Turn one line of text into an mp3 file. Returns the file path."""
    asyncio.run(_save(text, voice, out_path))
    return out_path


def duration(path: str) -> float:
    """Audio length in seconds, read with ffprobe."""
    out = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())
