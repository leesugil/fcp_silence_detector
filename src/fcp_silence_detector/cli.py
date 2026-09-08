#!/usr/bin/env python3

import argparse
import xml.etree.ElementTree as ET

from . import detect_silence
from . import place_markers
from fcp_io import fcpxml_io

def main():
    # Define possible arguments
    # fcp-detect-silence --db=-40 --duration=0.75 --polish-duration=0.5 --buffer-duration=0.4 --track=0 --affix='silence_marked_' <file_path>
    parser = argparse.ArgumentParser(description="Detect silences in audio in video, place FCP Markers")
    parser.add_argument("fcpxml_filepath", help="Absolute filepath to fcpxml (required)")
    parser.add_argument("--event", action="store_true", help="Add this if the fcpxml file is exported from an Event item, not a Project in FCP.")
    parser.add_argument("--keyword", type=str, default='silence', help="Keyword to be used in Marker description")
    # audio related
    """
    Audio arguments explained:

    _____..::...::..___.:.______.:::._______
    0   1   2   3   4   5   6   7   8   9

    --db=-5 vs -50
    |-----|  |-|  |----| |------|   |------|
    |---|           |-|   |----|     |-----|

    --duration=0 vs 1
    |---|           |-|   |----|     |-----|
    |---|                 |----|     |-----|

    --polish-duration=0 vs 1
    |---|           |-|   |----|     |-----|
    |---|           |----------|     |-----|

    --buffer-duration=0 vs 1
    |---|           |-|   |----|     |-----|
    |-|                     ||         |---|
    """
    parser.add_argument("--db", type=float, default=-35.0, help="Silence threshold in dB")
    parser.add_argument("--duration", type=float, default=1.0, help="Minimum silence duration in seconds.")
    parser.add_argument("--polish-duration", type=float, default=0.5, help="Miminum non-silence duration in seconds. Any sound lasting less than this time window will be considered as silence. (Popping noise filtering based on time interval)")
    parser.add_argument("--buffer-duration", type=float, default=0.3, help="Amount to reduce silence duration in seconds. That is, this is the gap time between consecutive loud sound blocks. Should not be greater than '--duration' because '--duration' is the theoretical shortest time interval between consecutive sound blocks, so it is possible to have a back-to-back sound blocks with the '--duration' distance, and adding a buffer length longer than this distance will push these blocks away ruining the timeline.")
    parser.add_argument("--buffer-start-duration", type=float, help="The usual '--buffer-duration' adds half the duration to both the start and end of a sound block (equal buffer length). This option is just to add a single buffer to the start only.")
    parser.add_argument("--buffer-end-duration", type=float, help="The usual '--buffer-duration' adds half the duration to both the start and end of a sound block (equal buffer length). This option is just to add a single buffer to the end only.")
    # silence detection from the beginning to the end
    parser.add_argument("--start-time-threshold", type=float, default=0.0, help="When ffmpeg detects silence, it might not capture silence from 0.0s of the audio. This ensures 'If silence starts within the first x seconds, assume the silence started from the beginning.")
    parser.add_argument("--end-time-threshold", type=float, default=0.0, help="When ffmpeg detects silence, it might not capture silence from 0.0s of the audio. This ensures 'If silence starts within the first x seconds, assume the silence started from the beginning.")
    # audio track if multitrack
    parser.add_argument("--track", type=int, default=1, help="aduio track to scan if multitrack")
    # source file change when working with proxy media
    parser.add_argument("--proxy-media", action="store_true", help="Read from proxy media file instead of the source media file. Useful when the source media is externally stored and not available at the moment.")
    # output
    parser.add_argument("--affix", type=str, default='silence_marked_', help="affix to modify the output filename")
    # debug
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    xf = fcpxml_io.clean_filepath(args.fcpxml_filepath)
    tree, root = fcpxml_io.get_fcpxml(xf)
    fps = fcpxml_io.get_fps(root)
    asset_clips = fcpxml_io.get_all_spine_asset_clips(root=root)
    print(f"fcpxml file: {xf}")

    if (args.buffer_start_duration is None) or (args.buffer_end_duration is None):
        args.buffer_start_duration = args.buffer_duration / 2
        args.buffer_end_duration = args.buffer_duration / 2

    # Detect silence in <asset-clip>s in the Project Timeline
    for asset_clip in asset_clips:
        # Silence detection using ffmpeg
        silences = detect_silence.detect_silences_from_fcpxml_asset_clip(asset_clip=asset_clip, root=root, db=args.db, duration=args.duration, polish_duration=args.polish_duration, buffer_start_duration=args.buffer_start_duration, buffer_end_duration=args.buffer_end_duration, track=args.track, proxy_media=args.proxy_media, debug=args.debug)

        # Adjust first and last silent regions to fit to FCPXML Project Timeline.
        silences = detect_silence.adjust_to_fcpxml_timeline(silences=silences, asset_clip=asset_clip, start_time_threshold=args.start_time_threshold, end_time_threshold=args.end_time_threshold, fps=fps, debug=args.debug)

        # Place Markers
        place_markers.place_in_asset_clip(asset_clip=asset_clip, silences=silences, fps=fps, keyword=args.keyword, in_event=args.event, debug=args.debug)

    fcpxml_io.save_with_affix(tree=tree, src_filepath=xf, affix=args.affix)

if __name__ == "__main__":
    main()
