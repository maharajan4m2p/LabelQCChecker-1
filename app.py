import os

from flask import (
    Flask,
    render_template,
    request
)

from werkzeug.utils import secure_filename

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
@app.route(
    "/compare",
    methods=["POST"]
)
def compare():

    approval = request.files.get(
        "approval_file"
    )

    samples = request.files.getlist(
        "samples_file"
    )
    if not approval:

        return (
            "Approval file missing",
            400
        )

    if approval.filename == "":

        return (
            "Approval file missing",
            400
        )
    approval_name = secure_filename(
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
    all_results=[]
    for sample in samples:

        if sample.filename == "":

            continue
        sample_name = secure_filename(
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
        result[
            "sample_file"
        ] = sample.filename
        all_results.append(
            result
        )
        print(
        "TOTAL RESULTS:",
        len(all_results)
    )

    print(
        all_results
    )
    if len(all_results) == 0:

        return (
            "No sample files uploaded",
            400
        )
    return render_template(

        "results.html",

        all_results=all_results

    )
if __name__ == "__main__":

    app.run(
        
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
