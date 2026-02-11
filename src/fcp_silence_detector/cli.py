#!/usr/bin/env python3

import os
import argparse
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote

from . import detect_silence
from . import place_markers

def clean_filepath(line):
    output = os.path.abspath(line.strip())
    return output

def parse_fcpxml_filepath(xf):
    fcpxml_filename = 'Info.fcpxml'
    fcpxml_filepath = os.path.join(xf, fcpxml_filename)
    tree = ET.parse(fcpxml_filepath)
    root = tree.getroot()
    media_rep = root.find(".//media-rep[@kind='original-media']")
    output = media_rep.get('src')
    output = urlparse(output)
    output = unquote(output.path)
    return output

def parse_fcpxml_filepath_sync(xf):
    fcpxml_filename = 'Info.fcpxml'
    fcpxml_filepath = os.path.join(xf, fcpxml_filename)

    tree = ET.parse(fcpxml_filepath)
    root = tree.getroot()

    # video
    asset1 = root.find(".//asset[@id='r2']")
    media_rep1 = asset1.find(".//media-rep[@kind='original-media']")
    output1 = media_rep1.get('src')
    output1 = urlparse(output1)
    output1 = unquote(output1.path) # video

    # audio
    asset2 = root.find(".//asset[@id='r3']")
    media_rep2 = asset2.find(".//media-rep[@kind='original-media']")
    output2 = media_rep2.get('src')
    output2 = urlparse(output2)
    output2 = unquote(output2.path) # audio

    return output1, output2

def parse_numbers(string: str) -> list[int]:
    """
    "1,2,3,4" -> [1, 2, 3, 4]
    """
    output = [int(x.strip()) for x in string.split(',')]
    return output

def main():

    # Define possible arguments
    # ex)
    # fcp-detect-silence --db=-40 --duration=0.75 --polish_duration=0.5 --buffer_duration=0.4 --affix='silence_marked_' --sync=1 <file_path>
    parser = argparse.ArgumentParser(description="Detect silences in audio and texts in video, place FCP Markers")
    parser.add_argument("fcpxml_filepath", help="Absolute filepath to fcpxml (required)")
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

    --polish_duration=0 vs 1
    |---|           |-|   |----|     |-----|
    |---|           |----------|     |-----|

    --buffer_duration=0 vs 1
    |---|           |-|   |----|     |-----|
    |-|                     ||         |---|
    """
    parser.add_argument("--db", type=float, default=-35.0, help="Silence threshold in dB")
    parser.add_argument("--duration", type=float, default=1.0, help="Minimum silence duration in seconds")
    parser.add_argument("--polish_duration", type=float, default=0.5, help="Miminum non-silence duration in seconds")
    parser.add_argument("--buffer_duration", type=float, default=0.4, help="Amount to reduce silence duration in seconds. (Should not be greater than duration)")
    # output
    parser.add_argument("--affix", type=str, default='silence_marked_', help="affix to modify the output filename")
    # synched clip
    parser.add_argument("--sync", type=int, default=0, help="(experimental) synched clip.")

    args = parser.parse_args()

    xf = clean_filepath(args.fcpxml_filepath)
    vf = clean_filepath(parse_fcpxml_filepath(xf))
    af = vf
    if args.sync == 1:
        vf, af = parse_fcpxml_filepath_sync(xf)
        vf = clean_filepath(vf)
        af = clean_filepath(af)
    print(f"fcpxml file: {xf}")
    print(f"video file: {vf}")
    print(f"audio file: {af}")

    # detect silences
    def detect_silences(file_path, db, duration, polish_duration, buffer_duration):
        ffmpeg_silences = detect_silence.detect(file_path, db, duration)
        silences = detect_silence.parse(ffmpeg_silences)
        silences = detect_silence.polish(silences, polish_duration)
        silences = detect_silence.buffer(silences, buffer_duration)
        output = silences
        return output

    silences = detect_silences(file_path=af, db=args.db, duration=args.duration, polish_duration=args.polish_duration, buffer_duration=args.buffer_duration)

    sync = True if args.sync == 1 else False
    place_markers.place(filepath=xf, silences=silences, affix=args.affix, sync=sync)

if __name__ == "__main__":
    main()
