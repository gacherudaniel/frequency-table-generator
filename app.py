"""
app.py
------
Flask web app that lets a non-technical user:
  1. Upload a Stata (.dta) file
  2. Preview variables and choose analysis options
  3. Generate weighted/unweighted frequency tables
  4. Download a formatted Excel workbook

Run locally with:   python app.py
Deploy instructions are in README.md
"""
import os
import shutil
import time
import uuid
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, send_file, flash, abort
)
from werkzeug.utils import secure_filename

import core

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)

# SECRET_KEY is required for Flask sessions. In production, set this via an
# environment variable rather than hardcoding it (see README.md).
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_CONTENT_LENGTH_MB = int(os.environ.get("MAX_UPLOAD_MB", "300"))
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH_MB * 1024 * 1024

# How long (in seconds) an uploaded/generated file is kept before automatic cleanup
FILE_RETENTION_SECONDS = 60 * 60  # 1 hour


def cleanup_old_files():
    """Delete session folders under uploads/ older than FILE_RETENTION_SECONDS."""
    now = time.time()
    for folder in UPLOAD_DIR.iterdir():
        if folder.is_dir():
            try:
                age = now - folder.stat().st_mtime
                if age > FILE_RETENTION_SECONDS:
                    shutil.rmtree(folder, ignore_errors=True)
            except OSError:
                pass


def session_dir(session_id: str) -> Path:
    d = UPLOAD_DIR / session_id
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    cleanup_old_files()
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle the .dta file upload, read it, and show variable preview + options form."""
    uploaded_file = request.files.get("dataset")

    if not uploaded_file or uploaded_file.filename == "":
        flash("Please choose a .dta file to upload.", "error")
        return redirect(url_for("index"))

    filename = secure_filename(uploaded_file.filename)
    if not filename.lower().endswith(".dta"):
        flash("Only .dta (Stata) files are supported.", "error")
        return redirect(url_for("index"))

    # Create a unique session folder so multiple users don't collide
    session_id = uuid.uuid4().hex
    dest_dir = session_dir(session_id)
    dta_path = dest_dir / "dataset.dta"
    uploaded_file.save(dta_path)

    # Try to read it right away so we can show a friendly error if it's invalid
    try:
        df, meta = core.load_stata_dataset(dta_path)
    except RuntimeError as exc:
        shutil.rmtree(dest_dir, ignore_errors=True)
        flash(str(exc), "error")
        return redirect(url_for("index"))

    session["session_id"] = session_id
    session["original_filename"] = filename

    variable_overview = core.build_variable_overview(df, meta)
    column_names = list(df.columns)

    return render_template(
        "options.html",
        filename=filename,
        n_obs=len(df),
        n_vars=df.shape[1],
        variables=variable_overview,
        column_names=column_names,
    )


@app.route("/generate", methods=["POST"])
def generate():
    """Run the frequency table pipeline using the options submitted by the user."""
    session_id = session.get("session_id")
    original_filename = session.get("original_filename")

    if not session_id:
        flash("Your session expired. Please upload your dataset again.", "error")
        return redirect(url_for("index"))

    dest_dir = session_dir(session_id)
    dta_path = dest_dir / "dataset.dta"
    if not dta_path.exists():
        flash("Your uploaded file could not be found. Please upload it again.", "error")
        return redirect(url_for("index"))

    # --- Parse the submitted form ---
    weight_mode = request.form.get("weight_mode", "none")

    weight_var = None
    weight_value = None

    if weight_mode == "variable":
        weight_var = request.form.get("weight_var", "").strip()
        if weight_var.lower() in {"", "none", "no", "1"}:
            weight_var = None
    elif weight_mode == "value":
        raw_weight_value = request.form.get("weight_value", "").strip()
        try:
            weight_value = float(raw_weight_value)
        except ValueError:
            flash("Please enter a valid numeric weight value.", "error")
            return redirect(url_for("index"))
        if weight_value <= 0:
            flash("The weight value must be greater than 0.", "error")
            return redirect(url_for("index"))

    options = {
        "exclude_id_vars": request.form.get("exclude_id_vars") == "on",
        "exclude_continuous": request.form.get("exclude_continuous") == "on",
        "categorical_only": request.form.get("categorical_only") == "on",
        "max_categories": _safe_int(request.form.get("max_categories"), default=50),
    }

    output_path = dest_dir / "Frequency_Tables.xlsx"

    try:
        result = core.run_full_pipeline(
            dta_path=dta_path,
            output_path=output_path,
            dataset_name=original_filename,
            weight_var=weight_var,
            weight_value=weight_value,
            options=options,
        )
    except Exception as exc:
        flash(f"Something went wrong while generating the report: {exc}", "error")
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        filename=original_filename,
        summary=result["summary"],
        skipped=result["skipped"],
        n_processed=result["n_processed"],
        n_skipped=result["n_skipped"],
        elapsed=f"{result['elapsed']:.2f}",
        download_url=url_for("download", session_id=session_id),
    )


def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@app.route("/download/<session_id>", methods=["GET"])
def download(session_id):
    """Serve the generated Excel workbook for download."""
    # Basic protection: only allow downloading from the session that created it
    if session.get("session_id") != session_id:
        abort(403)

    file_path = session_dir(session_id) / "Frequency_Tables.xlsx"
    if not file_path.exists():
        abort(404)

    return send_file(
        file_path,
        as_attachment=True,
        download_name="Frequency_Tables.xlsx",
    )


@app.route("/start-over", methods=["GET"])
def start_over():
    """Clear the current session and its uploaded files."""
    session_id = session.pop("session_id", None)
    session.pop("original_filename", None)
    if session_id:
        shutil.rmtree(session_dir(session_id), ignore_errors=True)
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Error handlers (friendly pages instead of raw stack traces)
# ---------------------------------------------------------------------------
@app.errorhandler(413)
def too_large(e):
    flash(f"File is too large. The maximum allowed size is {MAX_CONTENT_LENGTH_MB} MB.", "error")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", message="Something went wrong on our end. Please try again."), 500


if __name__ == "__main__":
    # For local development only. In production, use gunicorn (see README.md).
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
