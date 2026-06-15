import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from label_compare import compare_labels

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():

    approval = request.files.get("approval")

    if not approval:
        return "Approval image is required"

    samples = request.files.getlist("samples")

    if len(samples) == 0:
        return "Please upload at least one sample image"

    approval_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(approval.filename)
    )

    approval.save(approval_path)

    all_results = []

    for sample in samples:

        if sample.filename == "":
            continue

        sample_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            secure_filename(sample.filename)
        )

        sample.save(sample_path)

        result = compare_labels(
            approval_path,
            sample_path
        )

        result["sample_name"] = sample.filename

        all_results.append(result)

    return render_template(
        "results.html",
        results=all_results
    )


@app.errorhandler(413)
def file_too_large(error):
    return "File too large. Maximum size is 10 MB."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port
    )