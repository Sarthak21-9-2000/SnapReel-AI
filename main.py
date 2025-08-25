from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid, os
import threading
from generate_process import run_loop



app = Flask(__name__)

UPLOAD_ROOT = Path("user_uploads")
REELS_DIR   = Path("static/reels")
ALLOWED_EXT = {".png", ".jpg", ".jpeg"}

UPLOAD_ROOT.mkdir(exist_ok=True)
REELS_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    # id comes from form (hidden input named "uuid"); if missing, make one
    rec_id = request.form.get("uuid") or uuid.uuid4().hex
    job_dir = (UPLOAD_ROOT / rec_id)
    job_dir.mkdir(parents=True, exist_ok=True)

    if request.method == "POST":
        desc = (request.form.get("text") or "").strip()
        if desc:
            (job_dir / "desc.txt").write_text(desc, encoding="utf-8")

        saved = []
        for key, fs in request.files.items():
            if not fs or not fs.filename:
                continue
            name = secure_filename(fs.filename)
            ext = Path(name).suffix.lower()
            if ext not in ALLOWED_EXT:
                continue
            dst = job_dir / name
            fs.save(dst)
            saved.append(dst.resolve())  # absolute path

        # build concat list only if we saved any images
        if saved:
            txt = job_dir / "input.txt"
            with open(txt, "w", newline="\n", encoding="utf-8") as f:
                for p in saved:
                    f.write(f"file '{p.as_posix()}'\n")
                    f.write("duration 1\n")
                # repeat last file so the last duration is honored by ffmpeg
                f.write(f"file '{saved[-1].as_posix()}'\n")

        # hand off to your worker (it looks for job_dir and input.txt)
        return redirect(url_for("gallery"))

    # GET -> show create page with a fresh id
    myid = uuid.uuid4().hex
    return render_template("create.html", myid=myid)

REELS_DIR = Path("static/reels")

@app.route("/gallery")
def gallery():
    REELS_DIR.mkdir(exist_ok=True, parents=True)

    files = sorted(
        (p for p in REELS_DIR.glob("*.mp4")),
        key=os.path.getmtime,   # works with Path objects
        reverse=True
    )

    reel_urls = []
    for p in files:
        mtime = int(p.stat().st_mtime)                 # compute once
        url = url_for("static", filename=f"reels/{p.name}") + f"?v={mtime}"
        reel_urls.append(url)

    return render_template("gallery.html", reels=reel_urls)


if __name__ == "__main__":
    # Start worker in background
    t = threading.Thread(target=run_loop, kwargs={"poll_seconds": 2.0}, daemon=True)
    t.start()

    # Important: disable reloader so the worker doesn't start twice
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)