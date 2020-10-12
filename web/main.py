# Created by fw at 4/17/20

from flask import Flask, request, render_template, url_for, jsonify, abort
from werkzeug.utils import secure_filename

from rings import RingDetector
import hashlib

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOADS_DEFAULT_DEST"] = "/home/fw/Documents/rings/web/images/"

# image upload object
detector = RingDetector()


# rename and save the file based on md5 and its extension
def save_file(file, path=None):
    if path is None:
        path = app.config["UPLOADS_DEFAULT_DEST"]
    string = file.read()
    md5 = hashlib.md5(string).hexdigest()
    extension = secure_filename(file.filename).split(".")[-1]
    filename = f"{md5}.{extension}"
    with open(f"{path}/{filename}", "wb") as f:
        f.write(string)
    return path, filename


# convert array to json string
def process_response(filename, arr):
    md5 = filename
    arr = list(arr.reshape(-1))
    arr = [int(i) for i in arr]
    json = jsonify({'md5':md5,'array': arr})
    return json


# index route
@app.route("/")
def index():
    return render_template("index.html")


# process image route
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        parameters = request.form.to_dict()
        files = request.files
        if "file" in files:
            file = request.files["file"]
            path, filename = save_file(file)
            detector.update(path + filename, parameters, is_strip=True)
            arr = detector()
            json = process_response(filename, arr)
            return json
        else:
            return abort(400)
    else:
        return abort(400)


# fine tune image route
@app.route("/finetune", methods=["POST"])
def fine_tune():
    parameters = request.form.to_dict()
    if request.method == "POST":
        arr = detector(width=float(parameters['strip_width']),quantile=float(parameters['quantile'])/100)
        json = process_response(parameters['md5'], arr)
        return json
    else:
        return abort(400)
