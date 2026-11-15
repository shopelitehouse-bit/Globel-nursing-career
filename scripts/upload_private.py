#!/usr/bin/env python3
"""Private YouTube upload only. Never publishes or schedules a public video."""
import json
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

required = ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN")
missing = [name for name in required if not os.getenv(name)]
if missing:
    raise SystemExit("Missing GitHub Actions secrets: " + ", ".join(missing))
root = Path(__file__).resolve().parents[1]
metadata = json.loads((root / "output" / "metadata.json").read_text())
credentials = Credentials(
    token=None,
    refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["YOUTUBE_CLIENT_ID"],
    client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
    scopes=["https://www.googleapis.com/auth/youtube.upload"],
)
youtube = build("youtube", "v3", credentials=credentials)
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": metadata["title"] + " #Shorts",
            "description": metadata["description"],
            "categoryId": "27",
        },
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False},
    },
    media_body=MediaFileUpload(str(root / "output" / "nursing_short.mp4"),
                               mimetype="video/mp4", resumable=True),
)
response = None
while response is None:
    _, response = request.next_chunk()
print("PRIVATE upload complete. Video ID:", response["id"])
