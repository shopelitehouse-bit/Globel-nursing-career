#!/usr/bin/env python3
"""Send a generated MP4 and metadata to a private Make custom webhook."""
import json
import mimetypes
import os
import uuid
from pathlib import Path
from urllib.request import Request, urlopen

root = Path(__file__).resolve().parents[1]
url = os.environ.get("MAKE_WEBHOOK_URL", "").strip()
if not url.startswith("https://"):
    raise SystemExit("MAKE_WEBHOOK_URL must be an HTTPS webhook URL")
video = root / "output" / "nursing_short.mp4"
meta = json.loads((root / "output" / "metadata.json").read_text())
content = video.read_bytes()
if len(content) > 5_000_000:
    raise SystemExit("Video exceeds the 5 MB Make webhook/free-plan transfer target")
boundary = "----nursing-" + uuid.uuid4().hex
parts = []
def add_field(name, value):
    parts.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n").encode())
add_field("title", meta.get("title", "Global Nurse Academy") + " #Shorts")
add_field("description", meta.get("description", "Global Nurse Academy nursing education"))
add_field("category", "27")
add_field("privacy", "private")
parts.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"nursing_short.mp4\"\r\nContent-Type: video/mp4\r\n\r\n").encode() + content + b"\r\n")
parts.append((f"--{boundary}--\r\n").encode())
headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
key = os.environ.get("MAKE_WEBHOOK_API_KEY", "").strip()
if key:
    headers["x-make-apikey"] = key
req = Request(url, data=b"".join(parts), headers=headers, method="POST")
with urlopen(req, timeout=90) as response:
    body = response.read(1024).decode("utf-8", "replace")
    print(f"Make webhook accepted request: HTTP {response.status}; response: {body}")
