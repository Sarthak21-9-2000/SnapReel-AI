# 🎬 SnapReel AI

Generate Instagram-style **vertical reels** (1080×1920) from text + images using **Flask**, **FFmpeg**, and **ElevenLabs TTS**.

---

## ✨ Features
- Upload images + a description
- Description → speech using **ElevenLabs**
- Images + audio stitched into a Reel via **FFmpeg**
- Responsive **Gallery** shows all generated reels
- Background **worker** processes uploads continuously

---

## 🧰 Tech Stack
- Backend: Flask (Python)
- Media: FFmpeg (external binary)
- TTS: ElevenLabs Python SDK
- Frontend: HTML + CSS
- Storage:
  - `user_uploads/<uuid>/` → `desc.txt`, images, `input.txt`, `audio.mp3`
  - `static/reels/` → final `.mp4` reels
  - `done.txt` → processed jobs tracker

---
SnapReel AI/
├── main.py
├── generate_process.py
├── text_to_audio.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│ ├── base.html
│ ├── index.html
│ ├── create.html
│ └── gallery.html
└── static/
├── css/
│ ├── style.css
│ ├── create.css
│ └── gallery.css
└── reels/ # (generated)


---

## ⚡ Quick Start

### 1) Clone
```bash
git clone https://github.com/Sarthak21-9-2000/SnapReel-AI.git
cd "SnapReel AI"

2) Python env + deps
python -m venv venv
# Windows (Git Bash / PowerShell)
source venv/Scripts/activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt

3) Install FFmpeg

Download from https://ffmpeg.org/download.html

Add to PATH

Verify:

ffmpeg -version

4) ElevenLabs API key

Create a .env file in the project root:

ELEVEN_API_KEY="your_api_key_here"


Load it in text_to_audio.py (example):

import os
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))
# ... generate() and write audio.mp3 into user_uploads/<uuid>/

5) Run

Terminal 1 – Flask

python main.py
# -> http://127.0.0.1:5000


Terminal 2 – Worker

python generate_process.py


Go to:

http://127.0.0.1:5000/create → upload images + description

http://127.0.0.1:5000/gallery → watch reels 🎥

🖼️ Screenshots (optional)

Create a docs/ folder and add:

docs/create.png
docs/gallery.png


Then reference them in the README:

| Create | Gallery |
|-------|---------|
| ![Create](docs/create.png) | ![Gallery](docs/gallery.png) |

🧪 Tips

Keep Flask (server) and worker in separate terminals during development.

Use url_for('static', filename=...) and add ?v={{ mtime }} to bust cache on updated MP4s.

Generate poster frames for faster previews (optional):

ffmpeg -y -ss 1 -i static/reels/<name>.mp4 -frames:v 1 static/reels/<name>.jpg

🚀 Roadmap

Background music selection

Support short video clips

Auth + user accounts

Deploy to Render/Heroku/VPS (Flask + worker as separate processes)

📝 License

MIT © 2025 SnapReel AI


---

# `requirements.txt`

```txt
# Core Web Framework
Flask==2.3.2
Werkzeug==2.3.6

# ElevenLabs TTS SDK
elevenlabs==0.2.27

# NOTE: FFmpeg is required but must be installed separately:
# https://ffmpeg.org/download.html

