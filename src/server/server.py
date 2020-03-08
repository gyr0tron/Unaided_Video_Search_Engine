import datetime
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, request, make_response, jsonify, Response
from video_splitter import split_generate
import subprocess
from math import sqrt
from time import sleep

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../../data/raw'


@app.route("/", methods=["GET", "POST"])
def upload_video():

    if request.method == "POST":

        file = request.files["file"]
        temp_file = file.filename.split(".")
        file.save(os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(temp_file[0] + str(datetime.datetime.now().isoformat()) + "." + temp_file[1])))
        print("File uploaded")
        print(file)

        res = make_response(jsonify({"message": "File uploaded"}), 200)

        return res

    return render_template("public/upload_video.html")


@app.route('/yield')
# #show started
# #fuction call
# #function returns done
# #show done
# def index():
#     def inner():
#         with open('test.log', 'w') as f:
#             proc = subprocess.Popen(
#                 split_generate(),  # call something with a lot of output so we can see it
#                 shell=True,
#                 stdout=subprocess.PIPE
#             )
#             # for line in iter(lambda: proc.stdout.read(1), ''):
#             #     # Don't need this just shows the text streaming
#             #     # time.sleep(1)
#             #     yield line + '<br/>\n'
#             for c in iter(lambda: proc.stdout.read(1), ''):  # replace '' with b'' for Python 3
#                 sys.stdout.write(c)
#                 f.write(c)
#     # text/html is required for most browsers to show th$
#     return Response(inner(), mimetype='text/html')
def index():
    # render the template (below) that will use JavaScript to read the stream
    return render_template('public/process.html')


@app.route('/stream_sqrt')
def stream():
    def generate():
        proc = subprocess.Popen(
            split_generate(),  # call something with a lot of output so we can see it
            shell=True,
            stdout=subprocess.PIPE
        )

        # for i in range(500):
        for c in iter(proc.stdout.readlines()):
            yield '{}\n'.format(c.decode('utf-8').rstrip('\n'))
        # sleep(1)
    return app.response_class(generate(), mimetype='text/plain')


if __name__ == "__main__":
    # import sys
    app.run(threaded=False, debug=False)
