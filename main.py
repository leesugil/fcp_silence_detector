#!/usr/bin/env python3

import detect_silence
import place_markers
import os
import argparse

parser = argparse.ArgumentParser(description="Detect silences in audio")
parser.add_argument("--dB", type=float, default=-40, help="Silence threshold in dB")
parser.add_argument("--duration", type=float, default=3, help="Minimum silence duration in seconds")
parser.add_argument("--polish_duration", type=float, default=1, help="Maximum non-silence duration in seconds")
args = parser.parse_args()
dB = args.dB
duration = args.duration
polish_duration = args.polish_duration

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
        silences = detect_silence.parse(ffmpeg_silences)
        silences = detect_silence.polish(silences, polish_duration)
        place_markers.place(xf, silences)

if __name__ == "__main__":
    main()
