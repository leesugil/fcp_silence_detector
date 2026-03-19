
import subprocess
import re
from fcp_io import fcpxml_io
from fcp_math import arithmetic

def detect(filepath, dB=-40, duration=3, track=1, debug=False):
    """
    This runs the ffmpeg command to detect silence and returns the ffmpeg output so that later functions can parse relevant information from there.
    """

    cmd = [
            'ffmpeg', '-hide_banner', '-loglevel', 'info', '-i',
            f'{filepath}',
            '-map',
            f'0:{track}',
            '-af',
            f'silencedetect=n={dB}dB:d={duration}',
            '-f', 'null', '-',
            ]

    """
    cmd = [
            'ffmpeg', '-hide_banner', '-loglevel', 'info', '-i',
            f'{filepath}',
            '-map',
            f'0:a:{track}',
            '-af',
            f'silencedetect=n={dB}dB:d={duration}',
            '-f', 'null', '-',
            ]
    """

    if debug:
        print(f"detect-silence command to run: {cmd}")

    process = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True
            )
    output = process.stderr
    return output

def parse(stderr, debug=False):
    """
    Given the ffmpeg output message, this parses the silent region info,
    returns the info as a list of dictionaries.
    [{'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz}, {...}, ...]
    """
    silences = []

    for line in stderr.splitlines():
        if 'silence_start' in line:
            #t = float(re.search(r'silence_start: ([0-9.]+)', line).group(1))
            t = float(re.search(r'silence_start: (-?[0-9.]+)', line).group(1))
            silences.append({'start': t})
            if debug:
                print(line)
        elif 'silence_end' in line:
            matchs = re.search(r'silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)', line
                            )
            silences[-1]['end'] = float(matchs.group(1))
            silences[-1]['duration'] = float(matchs.group(2))
            assert silences[-1]['duration'] > 0

    if debug:
        print(f"parse silences: {silences}")

    return silences

def polish(silences, polish_duration=1, debug=False):
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

    if debug:
        print(f"polished silences: {output}")

    return output

def buffer(silences, buffer_duration=1, debug=False):
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

    if debug:
        print(f"buffered polished silences: {output}")

    return output

def start_time_adjustment(silences, start_time_threshold: float=0.0, debug=False):
    """
    When silence practically starts from the beginning of the audio, but the first silence region
    { 'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz },
    has 0.0 < xx.xxx <= start_time_threshold,
    then we set 'start': 0.0

    silences = [
            { 'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz },
            ...
        ]
    """
    assert start_time_threshold >= 0.0
    output = silences
    start = output[0]['start']
    if debug:
        print(f"start {start}")
    if start <= start_time_threshold:
        if debug:
            print(f"adjusting start {start} to 0.0")
        output[0]['start'] = 0.0
        output[0]['duration'] = output[0]['end'] - output[0]['start']

    return output

def end_time_adjustment(silences, audio_length, end_time_threshold: float=0.0, debug=False):
    """
    When the audio practically ends in silence, but the last silence region
    { 'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz },
    has audio_length - end_time_threshold <= yy.yyy < audio_length,
    then we set 'end': audio_length

    silences = [
            { 'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz },
            ...
        ]
    """
    assert end_time_threshold >= 0.0
    assert audio_length > 0.0
    output = silences
    end = output[-1]['end']
    if debug:
        print(f"end {end}")
    #if (audio_length - end_time_threshold <= output[-1]['end']) and (output[-1]['end'] < audio_length):
    if (audio_length - end_time_threshold <= end):
        if debug:
            print(f"adjusting end {end} to {audio_length}")
        output[-1]['end'] = audio_length
        output[-1]['duration'] = output[-1]['end'] - output[-1]['start']

    return output


# detect silences
def detect_silences(file_path, db, duration, polish_duration, buffer_duration, track, debug=False):
    ffmpeg_silences = detect(file_path, db, duration, track, debug=debug)
    silences = parse(ffmpeg_silences, debug=debug)
    silences = polish(silences, polish_duration, debug=debug)
    silences = buffer(silences, buffer_duration, debug=debug)
    return silences

# adjust to fcpxml timeline
def adjust_to_fcpxml_timeline(silences, root, start_time_threshold: float=0.0, end_time_threshold: float=0.0, debug=False):
    if debug:
        print(f"adjust_to_fcpxml_timeline start_time_threshold: {start_time_threshold}, end_time_threhold: {end_time_threshold}")
    if start_time_threshold > 0.0:
        silences = start_time_adjustment(silences=silences, start_time_threshold=start_time_threshold, debug=debug)

    if end_time_threshold > 0.0:
        asset_clip = fcpxml_io.get_spine_asset_clip(root)
        audio_length = arithmetic.fcpsec2frac(asset_clip.get('duration'))
        if debug:
            print(f"adjust_to_fcpxml_timeline source audio_length: {audio_length}")
        silences = end_time_adjustment(silences=silences, audio_length=audio_length, end_time_threshold=end_time_threshold, debug=debug)

    return silences
