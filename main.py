#!/usr/bin/env python3

import detect_silence
import place_markers
import os
import argparse

parser = argparse.ArgumentParser(description="Detect silences in audio and add FCP Markers")
parser.add_argument("video_filepath", help="Absolute filepath to video (required)")
parser.add_argument("fcpxml_filepath", help="Absolute filepath to fcpxml (required)")
parser.add_argument("--db", type=float, default=-40.0, help="Silence threshold in dB")
parser.add_argument("--duration", type=float, default=3.0, help="Minimum silence duration in seconds")
parser.add_argument("--polish_duration", type=float, default=1.0, help="Maximum non-silence duration in seconds")

args = parser.parse_args()

def clean_filepath(line):
    if '\n' in line:
        line.replace('\n', '')
    output = os.path.abspath(line)
    return output

def main():
    vf = clean_filepath(args.video_filepath)
    xf = clean_filepath(args.fcpxml_filepath)
    ffmpeg_silences = detect_silence.detect(vf, args.db, args.duration)
    silences = detect_silence.parse(ffmpeg_silences)
    silences = detect_silence.polish(silences, args.polish_duration)
    place_markers.place(xf, silences)

if __name__ == "__main__":
    main()
