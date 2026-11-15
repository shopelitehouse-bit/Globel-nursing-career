#!/usr/bin/env python3
"""Create original illustrated vertical nursing Shorts using free tools."""
import asyncio
import json
import math
import pathlib
import subprocess
import tempfile
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
topics = json.loads((ROOT / "content" / "topics.json").read_text(encoding="utf-8"))
topic = topics[datetime.now(timezone.utc).date().toordinal() % len(topics)]
(OUT / "metadata.json").write_text(json.dumps(topic, indent=2), encoding="utf-8")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1080, 1920

def run(cmd):
    subprocess.run(cmd, check=True)

def font(size, bold=True):
    return ImageFont.truetype(FONT if bold else REGULAR, size)

def wrap(draw, text, max_width, f):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=f)[2] > max_width and line:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines

def center_lines(draw, text, y, size, fill, width=890, spacing=18):
    f = font(size)
    for line in wrap(draw, text, width, f):
        bbox = draw.textbbox((0, 0), line, font=f)
        draw.text(((W - (bbox[2] - bbox[0])) / 2, y), line, font=f, fill=fill)
        y += size + spacing
    return y

def illustration(draw, kind, step):
    """Original vector-like medical illustrations, no downloaded stock images."""
    cx, cy = 540, 800
    draw.ellipse((190, 410, 890, 1110), fill="#163e63")
    if kind == "HAND HYGIENE":
        # Stylized hand with droplets and animated-scene variation
        draw.rounded_rectangle((420, 610, 670, 940), radius=95, fill="#f5b68d")
        for i in range(4):
            x = 415 + i * 66
            draw.rounded_rectangle((x, 510 - (i % 2) * 45, x + 55, 760), radius=27, fill="#ffd0a8")
        draw.ellipse((305, 735, 455, 860), fill="#f5b68d")
        for x, y in [(310, 570), (755, 660), (690, 980), (340, 1010)]:
            draw.ellipse((x, y, x + 35, y + 53), fill="#62e5ed")
        draw.arc((270, 490, 800, 1020), 35 + step * 18, 125 + step * 18, fill="#66e3e9", width=12)
    elif kind == "PATIENT ID CHECK":
        draw.rounded_rectangle((300, 510, 780, 1010), radius=48, fill="#f1f7ff")
        draw.rounded_rectangle((380, 460, 700, 545), radius=35, fill="#74d9e7")
        draw.ellipse((465, 595, 615, 745), fill="#f0b58e")
        draw.rounded_rectangle((390, 770, 690, 825), radius=15, fill="#1c5070")
        draw.rounded_rectangle((390, 855, 610, 895), radius=12, fill="#a1b7c7")
        draw.ellipse((640, 835, 745, 940), fill="#37d9aa")
        draw.line([(666, 882), (685, 902), (719, 855)], fill="#092d3b", width=13)
    else:
        for i, letter in enumerate(["S", "B", "A", "R"]):
            x = 230 + (i % 2) * 330
            y = 515 + (i // 2) * 255
            draw.rounded_rectangle((x, y, x + 290, y + 220), radius=38,
                                   fill=["#35d5d7", "#ffcc72", "#85a7ff", "#56e0aa"][i])
            f = font(120)
            bb = draw.textbbox((0, 0), letter, font=f)
            draw.text((x + (290 - (bb[2] - bb[0])) / 2, y + 30), letter, font=f, fill="#10253c")

def scene(path, idx):
    im = Image.new("RGB", (W, H), "#081729")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((55, 55, 1025, 1845), radius=65, fill="#10263f")
    d.rounded_rectangle((100, 100, 980, 205), radius=38, fill="#1c4960")
    center_lines(d, "GLOBAL NURSE ACADEMY", 130, 42, "#7de7e8")
    illustration(d, topic["title"], idx)
    d.rounded_rectangle((110, 1150, 970, 1650), radius=52, fill="#173a54")
    headings = [
        topic["title"],
        "REMEMBER THIS",
        "SAFE NURSING PRACTICE"
    ]
    center_lines(d, headings[idx], 1215, 68, "#ffffff", 750)
    chunks = topic["narration"].split(". ")
    details = [
        chunks[0].rstrip(".") + ".",
        (chunks[1] if len(chunks) > 1 else chunks[0]).rstrip(".") + ".",
        (". ".join(chunks[2:]) if len(chunks) > 2 else chunks[-1]).rstrip(".") + "."
    ]
    center_lines(d, details[idx], 1390, 40, "#c7eaf2", 740)
    d.rounded_rectangle((130, 1725, 950, 1739), radius=7, fill="#35566d")
    d.rounded_rectangle((130, 1725, 130 + int(820 * (idx + 1) / 3), 1739), radius=7, fill="#55e0d4")
    center_lines(d, "NURSING EDUCATION  •  " + str(idx + 1) + "/3", 1770, 27, "#8cb6c8")
    im.save(path)

async def make_voice(path):
    try:
        import edge_tts
        await edge_tts.Communicate(topic["narration"], "en-US-JennyNeural", rate="-5%").save(str(path))
        if path.stat().st_size < 1000:
            raise RuntimeError("Empty voice")
        print("Natural neural voice generated")
        return path
    except Exception as exc:
        print("Neural voice unavailable; using offline female voice:", str(exc)[:180])
        fallback = path.with_suffix(".wav")
        run(["espeak-ng", "-v", "en-us+f3", "-s", "145", "-w", str(fallback), topic["narration"]])
        return fallback

with tempfile.TemporaryDirectory() as tmp:
    d = pathlib.Path(tmp)
    audio = asyncio.run(make_voice(d / "voice.mp3"))
    duration = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio)
    ], text=True).strip()) + 1.0
    fps = 24
    frames = max(48, math.ceil(duration / 3 * fps))
    images = []
    for i in range(3):
        path = d / ("scene" + str(i) + ".png")
        scene(path, i)
        images.append(path)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for path in images:
        cmd += ["-loop", "1", "-framerate", str(fps), "-i", str(path)]
    cmd += ["-i", str(audio)]
    filters = []
    for i in range(3):
        # Subtle animated zoom creates motion without copyrighted stock footage.
        filters.append(
            f"[{i}:v]zoompan=z='min(zoom+0.00045,1.075)':d={frames}:"
            f"s=1080x1920:fps={fps},setsar=1,format=yuv420p[v{i}]"
        )
    filters.append("[v0][v1][v2]concat=n=3:v=1:a=0[v]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "3:a",
            "-t", str(duration), "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "25", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(OUT / "nursing_short.mp4")]
    run(cmd)
print("Created", OUT / "nursing_short.mp4")
