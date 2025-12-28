#!/usr/bin/env python3

from . import detect_silence
from . import place_markers
import os
import argparse
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote

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

    asset1 = root.find(".//asset[@id='r2']")
    media_rep1 = asset1.find(".//media-rep[@kind='original-media']")
    output1 = media_rep1.get('src')
    output1 = urlparse(output1)
    output1 = unquote(output1.path) # video

    asset2 = root.find(".//asset[@id='r3']")
    media_rep2 = asset2.find(".//media-rep[@kind='original-media']")
    output2 = media_rep2.get('src')
    output2 = urlparse(output2)
    output2 = unquote(output2.path) # audio

    return output1, output2

def main():

    parser = argparse.ArgumentParser(description="Detect silences in audio and add FCP Markers")
    parser.add_argument("fcpxml_filepath", help="Absolute filepath to fcpxml (required)")
    parser.add_argument("--db", type=float, default=-40.0, help="Silence threshold in dB")
    parser.add_argument("--duration", type=float, default=3.5, help="Minimum silence duration in seconds")
    parser.add_argument("--polish_duration", type=float, default=0.7, help="Maximum non-silence duration in seconds")
    parser.add_argument("--buffer_duration", type=float, default=1.5, help="Amount to reduce silence duration in seconds. (Should be greater than duration)")
    parser.add_argument("--sync", type=float, default=0, help="(experimental) synched clip.")
    args = parser.parse_args()

    xf = clean_filepath(args.fcpxml_filepath)
    vf = clean_filepath(parse_fcpxml_filepath(xf))
    if args.sync == 1:
        dummy, vf = parse_fcpxml_filepath_sync(xf)
        dummy = clean_filepath(dummy)
        vf = clean_filepath(vf)
    print(f"fcpxml file: {xf}")
    print(f"video file: {vf}")
    ffmpeg_silences = detect_silence.detect(vf, args.db, args.duration)
    silences = detect_silence.parse(ffmpeg_silences)
    silences = detect_silence.polish(silences, args.polish_duration)
    silences = detect_silence.buffer(silences, args.buffer_duration)
    if args.sync == 1:
        place_markers.place_sync(xf, silences)
    else:
        place_markers.place(xf, silences)

if __name__ == "__main__":
    main()
