# Global Nurse Academy — YouTube Shorts Autopilot

Android-friendly setup using GitHub Actions. This project generates a vertical educational Short using FFmpeg and offline eSpeak NG narration. Videos are initially **private only**.

## Setup
1. Open **Actions** and manually run **Build nursing Short** to test video rendering; download the `nursing-short` artifact from the run.
2. For YouTube uploads, configure repository Actions secrets `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN` (Google OAuth consent and YouTube Data API v3 required). Never commit secrets.
3. Run the workflow manually with `upload_private=true` to test a private YouTube upload.
4. Daily schedule is 12:30 UTC (6 PM IST), but GitHub scheduling may be delayed. To publish exactly at 6 PM, a separate YouTube scheduled-publish step is needed; this starter only uploads privately and does not publish publicly.

## Safety
Scripts are prewritten examples for general nursing education; review all clinical claims before use. No patient-specific medical advice. No automatic public posting. The voice is an offline synthesized female-variant eSpeak voice, not a natural human recording.

## Cost and limits
Uses standard GitHub-hosted Linux runners and free software. Check current GitHub Actions quotas and YouTube API quota; GitHub Actions may not execute at an exact minute. A public repository does not guarantee unlimited usage.
