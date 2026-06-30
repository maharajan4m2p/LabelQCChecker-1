"""
=========================================================
Label QC Checker Pro
Flask Web Application
Version 5.0
=========================================================
"""

import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_from_directory,
    flash
)

from werkzeug.utils import secure_filename

from config import *

from label_compare import compare_labels


app = Flask(__name__)

app.secret_key = "labelqc"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.route("/")
def index():

    return render_template("index.html")


# ---------------------------------------------------------
# Compare Labels
# ---------------------------------------------------------

@app.route("/compare", methods=["POST"])
def compare():

    if "approval" not in request.files:

        flash("Approval label missing")

        return redirect("/")

    if "sample" not in request.files:

        flash("Sample label missing")

        return redirect("/")

    approval = request.files["approval"]

    samples = request.files.getlist("sample")

    if approval.filename == "":

        flash("Please select approval label")

        return redirect("/")

    if len(samples) == 0:

        flash("Please select sample labels")

        return redirect("/")

    # -----------------------------------------
    # Save Approval Label
    # -----------------------------------------

    approval_name = secure_filename(
        approval.filename
    )

    approval_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        approval_name
    )

    approval.save(
        approval_path
    )

    # -----------------------------------------
    # Compare With Multiple Samples
    # -----------------------------------------

    all_results = []

    for sample in samples:

        if sample.filename == "":
            continue

        sample_name = secure_filename(
            sample.filename
        )

        sample_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            sample_name
        )

        sample.save(
            sample_path
        )

        result = compare_labels(
            approval_path,
            sample_path
        )

        result["sample_filename"] = sample_name

        all_results.append(result)

    return render_template(

        "results.html",

        approval_filename=approval_name,

        results=all_results

    )


# ---------------------------------------------------------
# Upload Folder
# ---------------------------------------------------------

@app.route("/uploads/<filename>")
def uploads(filename):

    return send_from_directory(

        app.config["UPLOAD_FOLDER"],

        filename

    )


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(

        debug=True

    )