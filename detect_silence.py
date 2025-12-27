
import subprocess
import re

cmd1 = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel',
        'info',
        '-i',
        ]
cmd2 = [
        '-af',
        'silencedetect=n=-45dB:d=3',
        '-f',
        'null',
        '-',
#        '2>&1',
#        '|',
#        'grep',
#        'silence',
        ]

def detect(filepath):
    # Compile commands
    cmd = cmd1
    cmd.append(filepath)
    cmd = cmd + cmd2

    process = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True
            )
    output = process.stderr
    return output

def parse(stderr):
    silences = []

    for line in stderr.splitlines():
        if 'silence_start' in line:
            t = float(re.search(r'silence_start: ([0-9.]+)', line).group(1))
            silences.append({'start': t})
        elif 'silence_end' in line:
            matchs = re.search(r'silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)', line
                            )
            silences[-1]['end'] = float(matchs.group(1))
            silences[-1]['duration'] = float(matchs.group(2))

    return silences

with open('data_video') as f:
    # Reading filepaths
    for line in f:
        if '\n' in line:
            line = line[:-1]

        # Compile commands
        filepath = line
        silences_ffmpeg = detect(filepath)
        silences = parse(silences_ffmpeg)
        print(silences)
