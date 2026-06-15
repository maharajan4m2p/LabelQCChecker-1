import os
import gc

from flask import Flask
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename

from label_compare import compare_labels

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():

    try:

        approval_file = request.files.get("approval")

        sample_files = request.files.getlist("sample")

        if not approval_file:
            return "Approval image not selected"

        if len(sample_files) == 0:
            return "Sample image not selected"

        approval_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            secure_filename(
                approval_file.filename
            )
        )

        approval_file.save(
            approval_path
        )

        all_results = []

        for sample in sample_files:

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

            result["sample_file"] = (
                sample.filename
            )

            all_results.append(
                result
            )

            try:
                os.remove(sample_path)
            except:
                pass

        try:
            os.remove(approval_path)
        except:
            pass

        gc.collect()

        return render_template(
            "results.html",
            results=all_results
        )

    except Exception as e:

        return f"""
        <h2>Error Occurred</h2>
        <pre>{str(e)}</pre>
        """


@app.errorhandler(413)
def file_too_large(error):

    return """
    <h2>File Too Large</h2>
    <p>Please upload images below 10 MB.</p>
    """, 413


@app.route("/health")
def health():

    return "OK"


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )