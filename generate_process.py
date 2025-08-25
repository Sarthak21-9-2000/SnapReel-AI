# generate_process.py
# Watches user_uploads/* and renders reels into static/reels/*
from pathlib import Path
import time
import subprocess
from text_to_audio import text_to_speech_file

ROOT = Path("user_uploads").resolve()
OUT  = Path("static/reels").resolve()
DONE_FILE = Path("done.txt").resolve()

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

ROOT.mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
if not DONE_FILE.exists():
    DONE_FILE.write_text("", encoding="utf-8")

def _log(*a): print("[worker]", *a)

def text_to_audio(folder_name: str):
    folder = ROOT / folder_name
    desc = (folder / "desc.txt").read_text(encoding="utf-8") if (folder / "desc.txt").exists() else ""
    _log("TTA -", folder_name)
    text_to_speech_file(desc, folder_name)  # your function must write audio.mp3 in the folder

def create_reel(folder_name: str):
    folder = ROOT / folder_name
    list_file = folder / "input.txt"
    audio     = folder / "audio.mp3"
    out_path  = OUT / f"{folder_name}.mp4"

    # Use absolute paths + no shell
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_file.resolve()),
        "-i", str(audio.resolve()),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", "-r", "30", "-pix_fmt", "yuv420p",
        str(out_path.resolve())
    ]
    _log("FFmpeg start ->", out_path.name)
    subprocess.run(cmd, check=True)
    _log("FFmpeg done  ->", out_path.name)

def _read_done() -> set[str]:
    return {line.strip() for line in DONE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()}

def _append_done(folder_name: str):
    with DONE_FILE.open("a", encoding="utf-8") as f:
        f.write(folder_name + "\n")

def process_once():
    """Run a single scan/pass (useful for testing)."""
    done = _read_done()
    for folder in sorted(p.name for p in ROOT.iterdir() if p.is_dir()):
        if folder in done:
            continue
        try:
            # Minimal sanity: need input.txt and at least one image
            if not (ROOT / folder / "input.txt").exists():
                continue
            if not any((ROOT / folder).glob("*")):
                continue
            text_to_audio(folder)
            create_reel(folder)
            _append_done(folder)
        except Exception as e:
            (ROOT / folder / "error.txt").write_text(str(e), encoding="utf-8")
            _log("ERROR", folder, "->", e)

def run_loop(poll_seconds: float = 2.0):
    _log("Watching", ROOT)
    while True:
        process_once()
        time.sleep(poll_seconds)

if __name__ == "__main__":
    # Standalone mode: run the loop if you execute this file directly
    run_loop()
