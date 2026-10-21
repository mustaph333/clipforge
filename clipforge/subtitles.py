"""Subtitle (SRT) generation for ClipForge."""


def _stamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def make_srt(scenes: list[str], durations: list[float]) -> str:
    """Build an SRT document from scene lines and their audio durations."""
    out, t = [], 0.0
    for i, (text, dur) in enumerate(zip(scenes, durations), start=1):
        out.append(f"{i}\n{_stamp(t)} --> {_stamp(t + dur)}\n{text}\n")
        t += dur
    return "\n".join(out)


def _ass_stamp(seconds: float) -> str:
    cs = int(round(seconds * 100))
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6_000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def make_ass(scenes: list[str], durations: list[float]) -> str:
    """Build an ASS document sized for the 1080x1920 canvas.

    Burning SRT directly leaves libass guessing the script resolution,
    which makes subtitles render at unpredictable sizes. An ASS file
    pins PlayRes to the real canvas, so FontSize means pixels.
    """
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Main,DejaVu Sans,54,&H00FFFFFF,&H000000FF,&H00000000,"
        "&H96000000,-1,0,0,0,100,100,0,0,1,3,1,2,60,60,150,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "MarginV, Effect, Text\n"
    )
    events, t = [], 0.0
    for text, dur in zip(scenes, durations):
        clean = text.replace("\n", " ")
        events.append(
            f"Dialogue: 0,{_ass_stamp(t)},{_ass_stamp(t + dur)},Main,,0,0,0,,{clean}"
        )
        t += dur
    return header + "\n".join(events) + "\n"

