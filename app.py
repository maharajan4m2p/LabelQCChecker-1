import os
import uuid

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from label_compare import compare_label_images

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tif", "tiff"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():
    try:
        approval = request.files.get("approval")
        samples = request.files.getlist("sample")

        if not approval or approval.filename == "":
            return "Approval file missing", 400

        if not samples or all(s.filename == "" for s in samples):
            return "Sample file missing", 400

        if not allowed_file(approval.filename):
            return "Unsupported approval file type", 400

        approval_filename = str(uuid.uuid4()) + "_" + secure_filename(approval.filename)
        approval_path = os.path.join(app.config["UPLOAD_FOLDER"], approval_filename)
        approval.save(approval_path)

        sample_results = []
    except Exception as e:
        return f"Error: {str(e)}", 500