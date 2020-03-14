import subprocess
import os
from shelljob import proc

input_video_paths = list()
input_video_names = list()
PROCESSED_PATH = './data/processed/'
STATS_FILE_PATH = f'stats.csv'
RAW_PATH = './data/raw/'
with os.scandir(RAW_PATH) as entries:
    for entry in entries:
        input_video_names.append(entry.name)
        input_video_paths.append(f'./data/raw/{entry.name}')

processed_images_path = f'{PROCESSED_PATH}images'
processed_scenes_path = f'{PROCESSED_PATH}scenes'

# process_cli = f'scenedetect --input {input_video_paths[0]} --output {PROCESSED_PATH} --stats {STATS_FILE_PATH} detect-content --min-scene-len 30 --threshold 27 list-scenes save-images --output {processed_images_path} --num-images 1 split-video --output {processed_scenes_path}'
# subprocess.Popen(process_cli, stdout=subprocess.PIPE).stdout.read()

process_cli = f'scenedetect --input {input_video_paths[0]} --output {PROCESSED_PATH} --stats {STATS_FILE_PATH} detect-content --min-scene-len 30 --threshold 27 list-scenes save-images --output {processed_images_path} --num-images 1 split-video --output {processed_scenes_path}'
# g = proc.Group()
# p = g.run(process_cli)

os.system(process_cli)
