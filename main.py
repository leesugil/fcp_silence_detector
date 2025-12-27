#!/usr/bin/env python3

import detect_silence
import place_markers
import os
import argparse

parser = argparse.ArgumentParser(description="Detect silences in audio")
parser.add_argument("--dB", type=float, default=-35, help="Silence threshold in dB")
parser.add_argument("--duration", type=float, default=3, help="Minimum silence duration in seconds")
args = parser.parse_args()
dB = args.dB
duration = args.duration

def clean_filepath(line):
    if '\n' in line:
        line = line[:-1]
    output = os.path.abspath(line)
    return output

def main():
    video_filepaths = open('data_video', 'r', encoding='utf-8')
    fcpxml_filepaths = open('data_fcpxml', 'r', encoding='utf-8')

    for vf, xf in zip(video_filepaths, fcpxml_filepaths):
        vf = clean_filepath(vf)
        xf = clean_filepath(xf) 
        ffmpeg_silences = detect_silence.detect(vf, dB, duration)
        ffmpeg_silences = detect_silence.detect(vf)
        silences = detect_silence.parse(ffmpeg_silences)
        place_markers.place(xf, silences)

if __name__ == "__main__":
    main()
