"""
=========================================================
Label QC Checker Pro
APP.py
=========================================================
"""

import os
import traceback

from flask import (

    Flask,

    render_template,

    request,

    redirect,

    url_for,

    flash,

    send_from_directory

)

from werkzeug.utils import secure_filename

from label_compare import compare_labels

# ---------------------------------------------------------
# Flask App
# ---------------------------------------------------------

app = Flask(__name__)

app.secret_key = "label_qc_checker"

UPLOAD_FOLDER = "uploads"

os.makedirs(

    UPLOAD_FOLDER,

    exist_ok=True

)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------------------------------------------------
# Allowed Files
# ---------------------------------------------------------

ALLOWED_EXTENSIONS = {

    "png",

    "jpg",

    "jpeg",

    "bmp",

    "tif",

    "tiff",

    "pdf"

}

# ---------------------------------------------------------
# File Validation
# ---------------------------------------------------------

def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(

            ".",

            1

        )[1].lower()

        in ALLOWED_EXTENSIONS

    )

# ---------------------------------------------------------
# Uploaded Images
# ---------------------------------------------------------

@app.route(

    "/uploads/<path:filename>"

)

def uploaded_file(filename):

    return send_from_directory(

        app.config["UPLOAD_FOLDER"],

        filename

    )

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

@app.route(

    "/compare",

    methods=["POST"]

)

def compare():

    try:

        print("=" * 80)
        print("LABEL QC CHECK STARTED")
        print("=" * 80)

        if "approval_file" not in request.files:

            flash("Please upload approval label.")

            return redirect(
                url_for("index")
            )

        approval_file = request.files[
            "approval_file"
        ]

        sample_files = request.files.getlist(
            "samples_file"
        )

        if approval_file.filename == "":

            flash("Approval label missing.")

            return redirect(
                url_for("index")
            )

        if len(sample_files) == 0:

            flash("Please upload sample labels.")

            return redirect(
                url_for("index")
            )

        if not allowed_file(
            approval_file.filename
        ):

            flash("Unsupported approval file.")

            return redirect(
                url_for("index")
            )

        approval_filename = secure_filename(
            approval_file.filename
        )

        approval_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            approval_filename

        )

        approval_file.save(
            approval_path
        )

        all_results = []

        for sample_file in sample_files:

            if sample_file.filename == "":

                continue

            if not allowed_file(
                sample_file.filename
            ):

                continue

            sample_filename = secure_filename(
                sample_file.filename
            )

            sample_path = os.path.join(

                app.config["UPLOAD_FOLDER"],

                sample_filename

            )

            sample_file.save(
                sample_path
            )

            print()

            print("=" * 80)
            print("Comparing :", sample_filename)
            print("=" * 80)

            result = compare_labels(

                approval_path,

                sample_path

            )

            result["sample_file"] = sample_filename

            all_results.append(result)
            # -------------------------------------------------
        # Prepare Dashboard Data
        # -------------------------------------------------

        for result in all_results:

            comparison = result.get("comparison", {})

            matched = comparison.get("matched", [])
            missing = comparison.get("missing", [])
            modified = comparison.get("modified", [])
            extra = comparison.get("extra", [])

            result["matched_constraints"] = matched
            result["missing_constraints"] = missing
            result["modified_items"] = modified
            result["extra_constraints"] = extra

            result["matched_constraints_count"] = len(matched)
            result["missing_constraints_count"] = len(missing)
            result["modified_count"] = len(modified)
            result["extra_constraints_count"] = len(extra)

            result["matched_count"] = len(matched)
            result["missing_count"] = len(missing)
            result["extra_count"] = len(extra)

            comparison_summary = result.get("summary", {})

            result["similarity"] = round(
                comparison_summary.get("similarity", 0),
                2
            )

            result["qc_score"] = comparison_summary.get(
                "qc_score",
                0
            )

            if "logo" in result:

                result["logo_status"] = result["logo"].get(
                    "status",
                    "FAIL"
                )

            else:

                result["logo_status"] = "FAIL"
                
            if "barcode" in result:

                result["barcode_status"] = result["barcode"].get(
                    "status",
                    "FAIL"
                )

            else:

                result["barcode_status"] = "FAIL"

            if (
                result["similarity"] >= 95
                and
                result["logo_status"] == "PASS"
                and
                result["barcode_status"] =="PASS"
                and
                result["missing_constraints_count"] == 0
            ):

                result["verdict"] = "APPROVED"

            elif result["similarity"] >= 80:

                result["verdict"] = "REVIEW REQUIRED"

            else:

                result["verdict"] = "REJECTED"

        print("=" * 80)
        print("QC COMPLETED")
        print("=" * 80)
        
        if len(all_results) == 0:

            flash("No valid sample files were uploaded.")

            return redirect(
                url_for("index")
            )

        return render_template(

            "results.html",

            all_results=all_results

        )
        # ---------------------------------------------------------
# Exception Handling
# ---------------------------------------------------------

    except Exception as e:

        print()

        print("=" * 80)
        print("APPLICATION ERROR")
        print("=" * 80)

        traceback.print_exc()

        flash(str(e))

        return redirect(

            url_for("index")

        )


# ---------------------------------------------------------
# Run Flask
# ---------------------------------------------------------

if __name__ == "__main__":

    print()

    print("=" * 80)
    print("LABEL QC CHECKER PRO")
    print("=" * 80)
    print("Server Started")
    print("Open Browser:")
    print("http://127.0.0.1:5000")
    print("=" * 80)

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )