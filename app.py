"""
=========================================================
Label QC Checker Pro
Flask Web Application
Version 6.1
=========================================================
"""

import os
import uuid
import traceback

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_from_directory,
    flash,
    jsonify
)

from werkzeug.utils import secure_filename

from config import *

from label_compare import compare_labels

# ---------------------------------------------------------
# Flask Application
# ---------------------------------------------------------

app = Flask(__name__)

app.secret_key = "labelqc"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE

os.makedirs(

    UPLOAD_FOLDER,

    exist_ok=True

)

# ---------------------------------------------------------
# Allowed File Types
# ---------------------------------------------------------

def allowed_file(filename):

    if "." not in filename:

        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ---------------------------------------------------------
# Generate Unique Filename
# ---------------------------------------------------------

def unique_filename(filename):

    filename = secure_filename(filename)

    extension = filename.rsplit(".", 1)[1]

    unique = uuid.uuid4().hex

    return f"{unique}.{extension}"


# ---------------------------------------------------------
# Home Page
# ---------------------------------------------------------

@app.route("/")
def index():

    return render_template(

        "index.html"

    )
    # ---------------------------------------------------------
# Compare Labels
# ---------------------------------------------------------

@app.route("/compare", methods=["POST"])
def compare():

    try:

        # -------------------------------------------------
        # Validate Request
        # -------------------------------------------------

        if "approval" not in request.files:

            flash("Approval label is missing.")

            return redirect("/")

        if "sample" not in request.files:

            flash("Sample label is missing.")

            return redirect("/")

        approval = request.files["approval"]

        samples = request.files.getlist("sample")

        if approval.filename == "":

            flash("Please select an approval label.")

            return redirect("/")

        if not allowed_file(approval.filename):

            flash("Unsupported approval file type.")

            return redirect("/")

        if len(samples) == 0:

            flash("Please select at least one sample label.")

            return redirect("/")

        # -------------------------------------------------
        # Save Approval File
        # -------------------------------------------------

        approval_filename = unique_filename(

            approval.filename

        )

        approval_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            approval_filename

        )

        approval.save(

            approval_path

        )

        # -------------------------------------------------
        # Compare Sample Files
        # -------------------------------------------------

        all_results = []

        for sample in samples:

            if sample.filename == "":

                continue

            if not allowed_file(sample.filename):

                all_results.append({

                    "sample_filename": sample.filename,

                    "status": "Failed",

                    "error": "Unsupported file type"

                })

                continue

            sample_filename = unique_filename(

                sample.filename

            )

            sample_path = os.path.join(

                app.config["UPLOAD_FOLDER"],

                sample_filename

            )

            sample.save(

                sample_path

            )

            try:

                result = compare_labels(

                    approval_path,

                    sample_path

                )

                result["sample_filename"] = sample.filename

                result["sample_saved"] = sample_filename

                result["status"] = "Success"

            except Exception as e:

                result = {

                    "sample_filename": sample.filename,

                    "status": "Failed",

                    "error": str(e),

                    "traceback": traceback.format_exc()

                }

            all_results.append(

                result

            )

        return render_template(

            "results.html",

            approval_filename=approval_filename,

            results=all_results

        )

    except Exception as e:

        flash(

            f"Unexpected Error: {str(e)}"

        )

        return redirect("/")
    # ---------------------------------------------------------
# Uploaded Files
# ---------------------------------------------------------

@app.route("/uploads/<path:filename>")
def uploads(filename):

    return send_from_directory(

        app.config["UPLOAD_FOLDER"],

        filename

    )


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.route("/health")
def health():

    return jsonify({

        "status": "Running",

        "application": APP_NAME,

        "version": APP_VERSION

    })


# ---------------------------------------------------------
# File Too Large
# ---------------------------------------------------------

@app.errorhandler(413)
def file_too_large(error):

    flash(

        f"File is too large. Maximum allowed size is {MAX_UPLOAD_SIZE // (1024 * 1024)} MB."

    )

    return redirect("/")


# ---------------------------------------------------------
# Page Not Found
# ---------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):

    return render_template(

        "404.html"

    ), 404
    # ---------------------------------------------------------
# Internal Server Error
# ---------------------------------------------------------

@app.errorhandler(500)
def internal_server_error(error):

    traceback.print_exc()

    try:

        return render_template(

            "500.html",

            error=str(error)

        ), 500

    except Exception:

        return (

            f"Internal Server Error\n\n{str(error)}",

            500

        )


# ---------------------------------------------------------
# Startup Message
# ---------------------------------------------------------

def startup_message():

    print("=" * 60)

    print(APP_NAME)

    print(f"Version : {APP_VERSION}")

    print(f"Upload Folder : {UPLOAD_FOLDER}")

    print(f"Report Folder : {REPORT_FOLDER}")

    print("=" * 60)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    startup_message()

app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    debug=False
)