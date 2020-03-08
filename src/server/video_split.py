from __future__ import print_function
import os

import pandas as pd
import scenedetect
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector
from scenedetect.detectors import ThresholdDetector

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
    # scene_manager.add_detector(ContentDetector(threshold=22, min_scene_len=90))
    scene_manager.add_detector(ThresholdDetector(
        threshold=50, min_percent=0.50, min_scene_len=30, fade_bias=0.0, add_final_scene=False, block_size=8))
    base_timecode = video_manager.get_base_timecode()

    try:
        if os.path.exists(STATS_FILE_PATH):
            with open(STATS_FILE_PATH, 'r') as stats_file:
                stats_manager.load_from_csv(stats_file, base_timecode)

        # start_time = base_timecode + 20     # 00:00:00.667
        # end_time = base_timecode + 20.0     # 00:00:20.000
        # # Set video_manager duration to read frames from 00:00:00 to 00:00:20.
        # video_manager.set_duration(start_time=start_time, end_time=end_time)

        video_manager.set_downscale_factor()

        video_manager.start()

        scene_manager.detect_scenes(frame_source=video_manager)

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

        if stats_manager.is_save_required():
            with open(STATS_FILE_PATH, 'w') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)

        # if (scenedetect.video_splitter.is_ffmpeg_available()):
        #     print('ffmpeg is available. Now loading ffmpeg!')
            # for vid_file in input_video_names:
            #     scenedetect.video_splitter.split_video_ffmpeg(
            #         input_video_paths, scene_list, vid_file, vid_file,
            #         arg_override='-c:v libx264 -preset fast -crf 21 -c:a copy', hide_progress=False, suppress_output=False)
        if (scenedetect.video_splitter.is_mkvmerge_available()):
            print('mkvmerge  is available. Now loading mkvmerge!')
            for vid_file in input_video_names:
                scenedetect.video_splitter.split_video_mkvmerge(
                    input_video_paths, scene_list, 'new/'+vid_file, vid_file, suppress_output=False)
        else:
            print('Install ffmpeg or mkvmerge for scene split')

    finally:
        video_manager.release()


if __name__ == "__main__":
    main()
