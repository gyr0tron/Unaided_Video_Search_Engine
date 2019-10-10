from __future__ import print_function
import os

import scenedetect
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_mkvmerge
from scenedetect.video_splitter import split_video_ffmpeg

import pandas as pd

input_video_paths = list()
input_video_names = list()
PROCESSED_PATH = '../../data/processed/'
STATS_FILE_PATH = f'{PROCESSED_PATH}stats.csv'
RAW_PATH = '../../data/raw/'
with os.scandir(RAW_PATH) as entries:
    for entry in entries:
        input_video_names.append(entry.name)
        input_video_paths.append(f'../../data/raw/{entry.name}')


def main():
    video_manager = VideoManager(input_video_paths)
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    scene_manager.add_detector(ContentDetector(min_scene_len=30))
    base_timecode = video_manager.get_base_timecode()

    try:
        # If stats file exists, load it.
        if os.path.exists(STATS_FILE_PATH):
            # Read stats from CSV file opened in read mode:
            with open(STATS_FILE_PATH, 'r') as stats_file:
                stats_manager.load_from_csv(stats_file, base_timecode)

        video_manager.set_downscale_factor()

        video_manager.start()

        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(base_timecode)
        processing_data = []
        print('List of scenes obtained:')
        for i, scene in enumerate(scene_list):
            print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i+1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),))
            processing_data.append([i, scene[0].get_timecode(), scene[0].get_frames(),
                                    scene[1].get_timecode(), scene[1].get_frames()])

        processing_data_df = pd.DataFrame(processing_data, columns=[
                                          'Scene', 'Start_time', 'Start_frame', 'End_time', 'End_frame'])
        # print(processing_data_df)
        processing_data_df.to_csv(f'{PROCESSED_PATH}/timecodes.csv')

        # We only write to the stats file if a save is required:
        if stats_manager.is_save_required():
            with open(STATS_FILE_PATH, 'w') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)

        # split_video_mkvmerge(
        #     input_video_paths[0], scene_list, output_file_prefix=f'{input_video_names[0]}', video_name=input_video_names[0], suppress_output=False)

        # split_video_ffmpeg(
        #     input_video_paths=input_video_paths[0], scene_list=scene_list, output_file_template=f'{input_video_names[0]}', video_name='vid', hide_progress=False, suppress_output=False)
        processed_images_path = f'{PROCESSED_PATH}images'
        processed_scenes_path = f'{PROCESSED_PATH}scenes'

        os.system(
            f'scenedetect --input {input_video_paths[0]} --output {PROCESSED_PATH} --stats {STATS_FILE_PATH} detect-content --min-scene-len 30 --threshold 27 list-scenes save-images --output {processed_images_path} --num-images 1 split-video --output {processed_scenes_path}')

    finally:
        video_manager.release()


if __name__ == "__main__":
    main()
