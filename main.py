import detect_silence
import place_markers
import os

video_filepaths = open('data_video', 'r', encoding='utf-8')
fcpxml_filepaths = open('data_fcpxml', 'r', encoding='utf-8')

def clean_filepath(line):
    if '\n' in line:
        line = line[:-1]
    output = os.path.abspath(line)
    return output

for vf, xf in zip(video_filepaths, fcpxml_filepaths):
    vf = clean_filepath(vf)
    xf = clean_filepath(xf)
    ffmpeg_silences = detect_silence.detect(vf)
    silences = detect_silence.parse(ffmpeg_silences)
    place_markers.place(xf, silences)
