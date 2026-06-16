import os

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from label_compare import compare_labels

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tif",
    "tiff",
    "webp",
    "gif",
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "csv",
    "txt"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():

    approval = request.files.get("approval")
    samples = request.files.getlist("samples")

    if not approval:
        return "Approval file missing"

    if not allowed_file(approval.filename):
        return "Unsupported approval file type"

    approval_filename = secure_filename(
        approval.filename
    )

    approval_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        approval_filename
    )

    approval.save(approval_path)

    all_results = []

    for sample in samples:

        if sample.filename == "":
            continue

        if not allowed_file(sample.filename):
            continue

        sample_filename = secure_filename(
            sample.filename
        )

        sample_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            sample_filename
        )

        sample.save(sample_path)

        try:

            result = compare_labels(
                approval_path,
                sample_path
            )

            result["sample_file"] = sample.filename

            all_results.append(result)

        except Exception as e:

            all_results.append({
                "sample_file": sample.filename,
                "verdict": "ERROR",
                "similarity": 0,
                "logo_status": "FAILED",
                "approval_text": "",
                "sample_text": "",
                "approval_brand": "",
                "sample_brand": "",
                "approval_product": "",
                "sample_product": "",
                "approval_barcode": "",
                "sample_barcode": "",
                "approval_weight": "",
                "sample_weight": "",
                "approval_mfg": "",
                "sample_mfg": "",
                "approval_exp": "",
                "sample_exp": "",
                "matched_words": [],
                "missing_words": [],
                "extra_words": [],
                "matched_count": 0,
                "missing_count": 0,
                "extra_count": 0,
                "error": str(e)
            })

    return render_template(
        "results.html",
        all_results=all_results
    )


@app.errorhandler(500)
def internal_error(error):
    return f"Server Error: {str(error)}", 500


@app.errorhandler(404)
def not_found(error):
    return "Page Not Found", 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )