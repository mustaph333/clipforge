"""ClipForge command-line interface.

Usage:
    python -m clipforge "the medina of Tangier"
    python -m clipforge "how volcanoes work" --out out/volcano.mp4
"""

import argparse
import os
import tempfile

from . import assemble, script, slides, subtitles, tts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clipforge",
        description="A free, local AI video studio: topic in, video out.",
    )
    parser.add_argument("topic", nargs="+", help="what the video is about")
    parser.add_argument("--out", default="out/clip.mp4",
                        help="output mp4 path (default: out/clip.mp4)")
    parser.add_argument("--voice", default=tts.DEFAULT_VOICE,
                        help=f"edge-tts voice (default: {tts.DEFAULT_VOICE})")
    parser.add_argument("--workdir", default=None,
                        help="folder for intermediate files (default: temp)")
    args = parser.parse_args(argv)

    topic = " ".join(args.topic)
    workdir = args.workdir or tempfile.mkdtemp(prefix="clipforge-")
    os.makedirs(workdir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    print(f"[1/4] writing the script: {topic}")
    scenes = script.build_script(topic)
    for line in scenes:
        print(f"      - {line}")

    print("[2/4] recording the voiceover")
    audios, durations = [], []
    for i, line in enumerate(scenes):
        mp3 = os.path.join(workdir, f"scene_{i:02d}.mp3")
        tts.speak(line, mp3, voice=args.voice)
        audios.append(mp3)
        durations.append(tts.duration(mp3))

    print("[3/4] drawing the slides")
    slide_paths = []
    for i, line in enumerate(scenes):
        png = os.path.join(workdir, f"slide_{i:02d}.png")
        slides.render_slide(line, i, len(scenes), png)
        slide_paths.append(png)

    print("[4/4] assembling the video")
    ass = subtitles.make_ass(scenes, durations)
    srt = subtitles.make_srt(scenes, durations)
    assemble.assemble(slide_paths, audios, durations, ass, srt, workdir,
                      args.out)

    total = sum(durations)
    print(f"done: {args.out} ({total:.1f}s, {len(scenes)} scenes)")
    return 0
