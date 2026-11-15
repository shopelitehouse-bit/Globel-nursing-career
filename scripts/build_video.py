#!/usr/bin/env python3
"""Produce a vertical educational video with locally installed free tools."""
import json
import pathlib
import subprocess
import tempfile
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
TOPICS = json.loads((ROOT / "content" / "topics.json").read_text(encoding="utf-8"))
# Rotate curated scripts daily. Add reviewed topics before using this in production.
topic = TOPICS[datetime.now(timezone.utc).date().toordinal() % len(TOPICS)]
(OUT / "metadata.json").write_text(json.dumps(topic, indent=2), encoding="utf-8")

def run(args):
    subprocess.run(args, check=True)

def escape_drawtext(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

with tempfile.TemporaryDirectory() as d:
    wav = pathlib.Path(d) / "voice.wav"
    run(["espeak-ng", "-v", "en-us+f3", "-s", "145", "-w", str(wav), topic["narration"]])
    duration = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(wav)], text=True).strip()) + 1.5
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    title = escape_drawtext(topic["title"])
    subtitle = escape_drawtext("GLOBAL NURSE ACADEMY")
    # Draw simple original graphic with no external copyrighted images.
    filters = (
        "drawbox=x=0:y=0:w=iw:h=ih:color=0x101e34:t=fill,"
        "drawbox=x=50:y=220:w=980:h=1350:color=0x193b59:t=fill,"
        f"drawtext=fontfile={font}:text='{subtitle}':fontcolor=0x6ce0df:fontsize=45:x=(w-text_w)/2:y=280,"
        f"drawtext=fontfile={font}:text='{title}':fontcolor=white:fontsize=52:"
        "x=(w-text_w)/2:y=620,"
        f"drawtext=fontfile={font}:text='NURSING EDUCATION':fontcolor=0xf9c96c:"
        "fontsize=46:x=(w-text_w)/2:y=1270"
    )
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=24",
         "-i", str(wav), "-vf", filters, "-t", str(duration),
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
         str(OUT / "nursing_short.mp4")])
print("Created", OUT / "nursing_short.mp4")
