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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():

    if "approval" not in request.files or "sample" not in request.files:
        return "Please upload both Approval and Sample images."

    approval = request.files["approval"]
    sample = request.files["sample"]

    if approval.filename == "" or sample.filename == "":
        return "Please select both files."

    approval_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(approval.filename)
    )

    sample_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(sample.filename)
    )

    approval.save(approval_path)
    sample.save(sample_path)

    results = compare_labels(
        approval_path,
        sample_path
    )

    return render_template(
        "results.html",
        results=results
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )