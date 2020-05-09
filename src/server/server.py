import datetime
from werkzeug.utils import secure_filename
import os
import flask
from flask import Flask, render_template, request, make_response, jsonify, Response, send_from_directory, redirect, send_file
import subprocess
from time import sleep
from shelljob import proc
import pandas as pd


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../data/raw'
app.config['PROCED_VIDEO_PATH'] = '../data/processed/scenes'
app.config['PROCED_IMG_PATH'] = '../data/processed/images'

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
def homepage():
    if request.method == "POST":

        file = request.files["file"]
        temp_file = file.filename.split(".")
        file.save(os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(temp_file[0] + str(datetime.datetime.now().isoformat()) + "." + temp_file[1])))
        print("File uploaded")
        print(file)

        res = make_response(jsonify({"message": "File uploaded"}), 200)

        return res
    return render_template("public/home.html")


@app.route("/upload", methods=["GET", "POST"])
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
        # host="docker.for.mac.host.internal",
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
    # print(sql_query)
    mycursor.execute(sql_query)
    rows = mycursor.fetchall()
    # print(type(rows))
    for row in rows:
        result_list.append(list(row))
    # print(result_list)
    df_list = pd.DataFrame.from_records(result_list)

    def prepend(list, str):
        str += '% s'
        list = [str % i for i in list]
        return(list)
    # print(df_list)
    vid_list = df_list[1].tolist()
    str = '/video/'
    vid_link_list = prepend(vid_list, str)
    img_list = df_list[2].tolist()
    str = '/cdn/image/'
    img_link_list = prepend(img_list, str)
    desc_list = df_list[3].tolist()
    acc_list = df_list[4].tolist()
    # print(vid_list)
    return render_template('public/results.html', img_link_list=img_link_list, vid_link_list=vid_link_list, desc_list=desc_list)
    # return Response(rows, mimetype='text/event-stream')


@app.route('/cdn/image/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.config['PROCED_IMG_PATH'], filename)


@app.route('/video/<path:filename>')
def custom_static2(filename):
    # filelink = os.path.abspath(os.getcwd())[
    #     :-10]+'src/data/processed/scenes/'+filename
    # return send_file(filelink)
    # send_file("scenes/"+filename)
    # return send_from_directory(app.config['PROCED_VIDEO_PATH'], filename, mimetype="video/mp4")
    # def serve_video(vid_name):
    # vid_path = os.path.abspath(os.getcwd())[
    #     :-6]+'data/processed/scenes/'+filename
    # resp = make_response(
    #     send_file(vid_path, 'video/mp4'))
    # resp.headers['Content-Disposition'] = 'inline'
    # return resp

    return send_from_directory(app.config['PROCED_VIDEO_PATH'], filename)


if __name__ == "__main__":
    # import sys
    app.run(host="0.0.0.0", debug=True, threaded=False)
