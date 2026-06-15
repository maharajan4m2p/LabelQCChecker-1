import os

from flask import (
    Flask,
    render_template,
    request
)

from werkzeug.utils import secure_filename

from label_compare import compare_labels


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route(
    "/compare",
    methods=["POST"]
)
def compare():

    if "approval" not in request.files:

        return "Approval file missing"

    approval = request.files["approval"]

    samples = request.files.getlist(
        "samples"
    )

    if approval.filename == "":

        return "Approval file not selected"

    if len(samples) == 0:

        return "No sample files selected"

    approval_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        secure_filename(
            approval.filename
        )

    )

    approval.save(
        approval_path
    )

    all_results = []

    for sample in samples:

        if sample.filename == "":

            continue

        sample_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            secure_filename(
                sample.filename
            )

        )

        sample.save(
            sample_path
        )

        result = compare_labels(

            approval_path,

            sample_path

        )

        result["sample_name"] = (
            sample.filename
        )

        all_results.append(
            result
        )

    return render_template(

        "results.html",

        all_results=all_results

    )


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )