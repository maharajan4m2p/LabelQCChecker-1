import os

from flask import (
    Flask,
    render_template,
    request
)

from werkzeug.utils import secure_filename

from label_compare import compare_labels


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tif",
    "tiff",
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "csv",
    "txt"
}


def allowed_file(filename):

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    approval = request.files.get(
        "approval"
    )

    samples = request.files.getlist(
        "samples"
    )

    if not approval:
        return "Approval file missing"

    if not allowed_file(
        approval.filename
    ):
        return "Unsupported approval file type"

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

        if not sample.filename:
            continue

        if not allowed_file(
            sample.filename
        ):
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

        result[
            "sample_file"
        ] = sample.filename

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
        debug=False
    )