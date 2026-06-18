import os

from flask import (
    Flask,
    render_template,
    request
)

import werkzeug.utils

from label_compare import (
    compare_labels
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config[
    "UPLOAD_FOLDER"
] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {

    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tif",
    "tiff",
    "webp",

    "pdf",

    "docx",

    "xls",
    "xlsx",

    "csv",

    "txt"

}


def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(
            ".",
            1
        )[1].lower()

        in

        ALLOWED_EXTENSIONS

    )


@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route("/compare",methods=["POST"])
def compare():

    approval = request.files.get("approval_file")

    samples = request.files.getlist("samples_file")

    if not approval:
        return ("Approval file missing")
    
    print("Approval:",approval.filename)
    print("Samples:",len(samples))

    approval_name = werkzeug.utils.secure_filename(
        approval.filename
    )

    approval_path = os.path.join(
        app.config[
            "UPLOAD_FOLDER"
        ],
        approval_name
    )

    approval.save(
        approval_path
    )

    all_results = []

    for sample in samples:
        print("Sample File.",sample.filename)

        if (
            sample.filename == ""
        ):
            continue

        sample_name = werkzeug.utils.secure_filename(
            sample.filename
        )

        sample_path = os.path.join(
            app.config[
                "UPLOAD_FOLDER"
            ],
            sample_name
        )

        sample.save(
            sample_path
        )

        result = compare_labels(
            approval_path,
            sample_path
        )
        print(result)

        result[
            "sample_file"
        ] = sample.filename

        all_results.append(result)
        
    return render_template(
        "results.html",
        all_results=all_results)

    print("TOTAL RESULTS:",len(all_results))
    print(all_results)




if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )