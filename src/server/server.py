import datetime
from werkzeug.utils import secure_filename
import os
import flask
from flask import Flask, render_template, request, make_response, jsonify, Response
import subprocess
from time import sleep
from shelljob import proc

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../data/raw'

input_video_paths = list()
input_video_names = list()
PROCESSED_PATH = '../data/processed/'
STATS_FILE_PATH = f'{PROCESSED_PATH}stats.csv'
RAW_PATH = '../data/raw/'
with os.scandir(RAW_PATH) as entries:
    for entry in entries:
        input_video_names.append(entry.name)
        input_video_paths.append(f'../data/raw/{entry.name}')

processed_images_path = f'{PROCESSED_PATH}images'
processed_scenes_path = f'{PROCESSED_PATH}scenes'


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


# @app.route('/yield')
# def index():
#     return render_template('public/process.html')


# @app.route('/stream')
# def stream():
#     # process_cli = f'scenedetect --input {input_video_paths[0]} --output {PROCESSED_PATH} --stats {STATS_FILE_PATH} detect-content --min-scene-len 30 --threshold 27 list-scenes save-images --output {processed_images_path} --num-images 1 split-video --output {processed_scenes_path}'
#     # g = proc.Group()
#     # p = g.run(process_cli)

#     # def read_process():
#     #     while g.is_pending():
#     #         lines = g.readlines()
#     #         for proc, line in lines:
#     #             yield line

#     return Response(read_process(), mimetype='text/event-stream')


@app.route("/search-page")
def search_page_return():
    return render_template("public/search-page.html")


@app.route("/search", methods=["POST"])
def search_sql():
    search_query = request.form['search_query']
    result_list = list()
    import mysql.connector
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="UVSE"
    )
    mycursor = mydb.cursor()

    # SELECT * FROM articles
    # WHERE MATCH(title, body)
    # AGAINST('database' IN NATURAL LANGUAGE MODE)
    # SELECT id, caption, MATCH(caption) AGAINST('man roof' IN NATURAL LANGUAGE MODE) AS score FROM captions ORDER BY `score`  DESC

    # sql_query = f"select * from captions where MATCH ('{search_query}')"
    sql_query = f"SELECT id, vid_name, img_name, caption, MATCH(caption) AGAINST('{search_query}' IN NATURAL LANGUAGE MODE) AS score FROM captions ORDER BY `score` DESC LIMIT 10"
    print(sql_query)
    mycursor.execute(sql_query)
    rows = mycursor.fetchall()
    # print(type(rows))
    for row in rows:
        result_list.append(list(row))
    return render_template('public/results.html', rows=result_list)
    # return Response(rows, mimetype='text/event-stream')


if __name__ == "__main__":
    # import sys
    app.run(host="0.0.0.0", debug=True, threaded=False)
