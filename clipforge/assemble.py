"""Video assembly for ClipForge - all heavy lifting is done by ffmpeg.

Each scene becomes a segment: the slide slowly zooms (Ken Burns effect)
while its voice line plays. Segments are concatenated, then subtitles are
burned in. If the local ffmpeg has no subtitle filter, the SRT is muxed
as a soft subtitle track instead.
"""

import os
import subprocess

FPS = 30


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, capture_output=True, text=True, check=True)


def _segment(slide: str, audio: str, dur: float, out_path: str) -> None:
    frames = max(1, int(dur * FPS))
    filt = (
        "[0:v]scale=2160:3840:flags=lanczos,"
        f"zoompan=z='min(zoom+0.0007,1.12)':d={frames}:"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s=1080x1920:fps={FPS},format=yuv420p[v]"
    )
    _run([
        "ffmpeg", "-y", "-i", slide, "-i", audio,
        "-filter_complex", filt,
        "-map", "[v]", "-map", "1:a",
        "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k",
        out_path,
    ])


def assemble(slides: list[str], audios: list[str], durations: list[float],
             ass_text: str, srt_text: str, workdir: str, out_path: str) -> str:
    segments = []
    for i, (slide, audio, dur) in enumerate(zip(slides, audios, durations)):
        seg = os.path.join(workdir, f"seg_{i:02d}.mp4")
        _segment(slide, audio, dur, seg)
        segments.append(seg)

    list_file = os.path.join(workdir, "segments.txt")
    with open(list_file, "w") as fh:
        for seg in segments:
            fh.write(f"file '{seg}'\n")
    joined = os.path.join(workdir, "joined.mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
          "-c", "copy", joined])

    ass_path = os.path.join(workdir, "subs.ass")
    with open(ass_path, "w") as fh:
        fh.write(ass_text)
    srt_path = os.path.join(workdir, "subs.srt")
    with open(srt_path, "w") as fh:
        fh.write(srt_text)

    try:
        _run([
            "ffmpeg", "-y", "-i", joined,
            "-vf", f"ass={ass_path}",
            "-c:a", "copy", out_path,
        ])
    except subprocess.CalledProcessError:
        # No libass in this ffmpeg build: mux subtitles as a soft track.
        _run([
            "ffmpeg", "-y", "-i", joined, "-i", srt_path,
            "-c", "copy", "-c:s", "mov_text", out_path,
        ])
    return out_path
