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
    parser.add_argument("--duration", type=float, default=1.0, help="Minimum silence duration in seconds")
    parser.add_argument("--polish-duration", type=float, default=0.5, help="Miminum non-silence duration in seconds")
    parser.add_argument("--buffer-duration", type=float, default=0.4, help="Amount to reduce silence duration in seconds. (Should not be greater than duration)")
    # silence detection from the beginning to the end
    parser.add_argument("--start-time-threshold", type=float, default=0.0, help="When ffmpeg detects silence, it might not capture silence from 0.0s of the audio. This ensures 'If silence starts within the first x seconds, assume the silence started from the beginning.")
    parser.add_argument("--end-time-threshold", type=float, default=0.0, help="When ffmpeg detects silence, it might not capture silence from 0.0s of the audio. This ensures 'If silence starts within the first x seconds, assume the silence started from the beginning.")
    # audio track if multitrack
    parser.add_argument("--track", type=int, default=1, help="aduio track to scan if multitrack")
    # output
    parser.add_argument("--affix", type=str, default='silence_marked_', help="affix to modify the output filename")
    # debug
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    xf = fcpxml_io.clean_filepath(args.fcpxml_filepath)
    vf = fcpxml_io.clean_filepath(fcpxml_io.parse_fcpxml_filepath(xf))
    af = vf
    print(f"fcpxml file: {xf}")
    print(f"video file: {vf}")
    print(f"audio track: 0:{args.track}")

    # Detect silence
    silences = detect_silence.detect_silences(file_path=af, db=args.db, duration=args.duration, polish_duration=args.polish_duration, buffer_duration=args.buffer_duration, track=args.track, debug=args.debug)

    # Adjust first and last silent regions to fit to FCPXML Project Timeline.
    tree, root = fcpxml_io.get_fcpxml(xf)
    silences = detect_silence.adjust_to_fcpxml_timeline(silences=silences, root=root, start_time_threshold=args.start_time_threshold, end_time_threshold=args.end_time_threshold, debug=args.debug)

    # Place Markers
    tree, root = fcpxml_io.get_fcpxml(xf)
    fps = fcpxml_io.get_fps(root)
    place_markers.place(root=root, silences=silences, fps=fps, keyword=args.keyword, in_event=args.event, debug=args.debug)

    fcpxml_io.save_with_affix(tree=tree, src_filepath=xf, affix=args.affix)

if __name__ == "__main__":
    main()
