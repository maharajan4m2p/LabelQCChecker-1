import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from label_compare import compare_labels

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():

    approval = request.files["approval"]
    sample = request.files["sample"]

    approval_path = os.path.join(
        UPLOAD_FOLDER,
        secure_filename(approval.filename)
    )

    sample_path = os.path.join(
        UPLOAD_FOLDER,
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
    app.run(host="0.0.0.0", port=5000)