
import subprocess
import re

def detect(filepath, dB=-40, duration=3):
    """
    This runs the ffmpeg command to detect silence and returns the ffmpeg output so that later functions can parse relevant information from there.
    """
    cmd1 = [
            'ffmpeg',
            '-hide_banner',
            '-loglevel',
            'info',
            '-i',
            ]
    cmd2 = [
            '-af',
            f'silencedetect=n={dB}dB:d={duration}',
            '-f',
            'null',
            '-',
            ]

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
    """
    Given the ffmpeg output message, this parses the silent region info,
    returns the info as a list of dictionaries.
    [{'start': 'hh:mm:ss', 'end': 'hh:mm:ss', 'duration': 'hh:mm:ss'}, {...}, ...]
    """
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

def polish(silences, polish_duration=1):
    """
    silences = [
            { 'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz },
            ...
        ]
    """
    output = []
    interval = None
    for i in silences:
        if interval is None:
            interval = i
        else:
            gap = i['start'] - interval['end']
            if gap < polish_duration:
                # merge
                interval['end'] = i['end']
                interval['duration'] = interval['end'] - interval['start']
            else:
                # store interval and start a new interval
                output.append(interval)
                interval = i
    output.append(interval)
    return output

def buffer(silences, buffer_duration=1):
    """
    Gives more room for non-silence regions by shrinking the silent duration by buffer_duration.
    The buffer_duration should be shorter than the duration from detect().

    silences = [
            { 'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz },
            ...
        ]
    """
    output = []
    for i in silences:
        if i['duration'] > buffer_duration:
            i['start'] += buffer_duration/2
            i['end'] -= buffer_duration/2
            i['duration'] = i['end'] - i['start']
        output.append(i)
    return output

def offset(silences, offset=0):
    output = []
    for i in silences:
        i['start'] += offset
        i['end'] += offset
        output.append(i)
    return output
