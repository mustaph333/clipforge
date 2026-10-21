# ClipForge

**A free, local AI video studio. Topic in — finished vertical video out.**

Online AI video tools charge per video, lock you into subscriptions, and
upload your work to someone else's cloud. ClipForge runs entirely on your
own machine, costs nothing per video, and needs no account.

Give it a topic. It writes the script, records the voiceover, draws the
slides, burns in the subtitles, and hands you one finished 9:16 MP4 —
ready for Reels, Shorts and TikTok.

## Demo flow

```
$ python -m clipforge "the old medina of Tangier"

[1/4] writing the script: the old medina of Tangier
      - The old medina of Tangier. You have heard the name - but do you know the real story?
      - ...
[2/4] recording the voiceover
[3/4] drawing the slides
[4/4] assembling the video
done: out/clip.mp4 (38.2s, 6 scenes)
```

## Install

You need Python 3.10+ and [ffmpeg](https://ffmpeg.org/download.html) on
your PATH.

```bash
git clone https://github.com/mustaph333/clipforge.git
cd clipforge
pip install -r requirements.txt
```

## Use

```bash
python -m clipforge "how volcanoes work"
python -m clipforge "the history of coffee" --out out/coffee.mp4
python -m clipforge "space facts" --voice en-GB-RyanNeural
```

### Better scripts (optional)

Without any key, ClipForge uses built-in starter templates so it always
works offline. For real AI-written scripts, bring a free
[Google AI Studio](https://aistudio.google.com) key:

```bash
export GEMINI_API_KEY="your-key"
python -m clipforge "the old medina of Tangier"
```

If the key fails or is missing, ClipForge quietly falls back to the
offline script — a run never dies because of the network.

## How it works

| Step | Module | What happens |
|------|--------|--------------|
| 1 | `script.py` | Gemini writes a 6-line narration, or offline templates step in |
| 2 | `tts.py` | Free Edge neural voices read each line (edge-tts), timed with ffprobe |
| 3 | `slides.py` | Pillow draws a 1080×1920 title card per line, colours shifting per scene |
| 4 | `subtitles.py` | Scene timings become an SRT subtitle track |
| 5 | `assemble.py` | ffmpeg zooms each slide (Ken Burns), joins the scenes, burns the subtitles in |

## Design rules

- **Free means free.** No paid API is required for a full run.
- **Local means local.** Your topics and videos never leave your machine
  (except the optional Gemini script call, with your own key).
- **Fail soft.** Every stage degrades gracefully instead of crashing the run.

## Roadmap

- [ ] Real image generation per scene (Stable Diffusion / API pluggable)
- [ ] Background music track mixing
- [ ] Arabic and French voice presets
- [ ] Horizontal (16:9) output mode
- [ ] One-command Windows installer

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE). Built by [Mustapha Rais](https://github.com/mustaph333).
