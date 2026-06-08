import os
import uuid
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from label_compare import compare_label_images

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {
    "png", "jpg", "jpeg", "bmp", "tif", "tiff"
}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/test")
def test():
    return "Flask is working"


@app.route("/compare", methods=["POST"])
def compare():

    approval_path = None
    sample_path = None

    try:

        if "approval" not in request.files:
            return render_template(
                "results.html",
                error="Approval image missing"
            )

        if "sample" not in request.files:
            return render_template(
                "results.html",
                error="Sample image missing"
            )

        approval_file = request.files["approval"]
        sample_file = request.files["sample"]

        if approval_file.filename == "":
            return render_template(
                "results.html",
                error="Select approval image"
            )

        if sample_file.filename == "":
            return render_template(
                "results.html",
                error="Select sample image"
            )

        if not allowed_file(approval_file.filename):
            return render_template(
                "results.html",
                error="Invalid approval image format"
            )

        if not allowed_file(sample_file.filename):
            return render_template(
                "results.html",
                error="Invalid sample image format"
            )

        approval_filename = (
            str(uuid.uuid4())
            + "_"
            + secure_filename(approval_file.filename)
        )

        sample_filename = (
            str(uuid.uuid4())
            + "_"
            + secure_filename(sample_file.filename)
        )

        approval_path = os.path.join(
            UPLOAD_FOLDER,
            approval_filename
        )

        sample_path = os.path.join(
            UPLOAD_FOLDER,
            sample_filename
        )

        approval_file.save(approval_path)
        sample_file.save(sample_path)

        results = compare_label_images(
            approval_path,
            sample_path
        )

        return render_template(
            "results.html",
            results=results,
            error=None
        )

    except Exception as e:

        import traceback
        traceback.print_exc()

        return (
            f"<h2>Server Error</h2>"
            f"<pre>{str(e)}</pre>",
            500
        )

    finally:

        for path in [approval_path, sample_path]:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except:
                pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port
    )