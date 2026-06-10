# ============================================================
# app.py — Flask Application
# ============================================================

import os
import uuid
from flask          import Flask, render_template, request
from werkzeug.utils import secure_filename
from label_compare  import compare_label_images

# ── Config ────────────────────────────────────────────────
BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER      = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tif", "tiff"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Helper ────────────────────────────────────────────────
def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# ── Routes ────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():
    try:
        # ── Check both files exist in request ──────────────
        if ("approval" not in request.files or
                "sample" not in request.files):
            return render_template(
                "results.html",
                results=None,
                error="Both images are required."
            )

        approval_file = request.files["approval"]
        sample_file   = request.files["sample"]

        # ── Check filenames not empty ──────────────────────
        if (approval_file.filename == "" or
                sample_file.filename == ""):
            return render_template(
                "results.html",
                results=None,
                error="Please select both images."
            )

        # ── Check file types allowed ───────────────────────
        if not allowed_file(approval_file.filename):
            return render_template(
                "results.html",
                results=None,
                error="Approval file type not allowed. "
                      "Use PNG, JPG, BMP, TIF."
            )

        if not allowed_file(sample_file.filename):
            return render_template(
                "results.html",
                results=None,
                error="Sample file type not allowed. "
                      "Use PNG, JPG, BMP, TIF."
            )

        # ── Save files with unique names ───────────────────
        approval_filename = (
            str(uuid.uuid4()) + "_" +
            secure_filename(approval_file.filename)
        )
        sample_filename = (
            str(uuid.uuid4()) + "_" +
            secure_filename(sample_file.filename)
        )

        approval_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            approval_filename
        )
        sample_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            sample_filename
        )

        approval_file.save(approval_path)
        sample_file.save(sample_path)

        # ── Run comparison ─────────────────────────────────
        results = compare_label_images(
            approval_path, sample_path
        )

        # ── Clean up uploaded files ────────────────────────
        try:
            os.remove(approval_path)
            os.remove(sample_path)
        except Exception:
            pass

        # ── Check if compare returned an error ────────────
        if results.get("verdict") == "ERROR":
            return render_template(
                "results.html",
                results=None,
                error=results.get(
                    "error", "Unknown comparison error"
                )
            )

        return render_template(
            "results.html",
            results=results,
            error=None
        )

    except Exception as e:
        return render_template(
            "results.html",
            results=None,
            error=f"Server error: {str(e)}"
        )


# ── Error handlers ────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template(
        "results.html",
        results=None,
        error="Page not found."
    ), 404


@app.errorhandler(413)
def too_large(e):
    return render_template(
        "results.html",
        results=None,
        error="File too large. Maximum size is 16MB."
    ), 413


@app.errorhandler(500)
def server_error(e):
    return render_template(
        "results.html",
        results=None,
        error=f"Internal server error: {str(e)}"
    ), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )