import xml.etree.ElementTree as ET
from tqdm import tqdm
from fcp_io import fcpxml_io
from fcp_math import arithmetic

def place(root, silences: list[dict], fps: str, keyword: str, in_event: bool=False):
    """
    silences: [{'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz}, {...}, ...]
    """
    asset_clip = fcpxml_io.get_event_asset_clip(root) if in_event else fcpxml_io.get_spine_asset_clip(root)
    audio_channel = asset_clip.find('audio-channel-source')
    if audio_channel is not None:
        print("🐝 audio-channel-source found!")

    previous_end = None

    # Place silence Markers
    for i, s in tqdm(enumerate(silences, start=1)):
        start = arithmetic.float2fcpsec(s['start'], fps)
        start_marker = ET.Element("marker")
        start_marker.set("start", start)
        start_marker.set("value", f"{keyword} start {i}")
        start_marker.set("duration", fps)
        start_marker.set("completed", "0")

        if audio_channel is not None:
            #print("🐝 audio-channel-source found!")
            index = list(asset_clip).index(audio_channel)
            asset_clip.insert(index, start_marker)
        else:
            #print("💀 NO audio-channel-source found!")
            #print(f"{list(asset_clip)[-5:]}")
            asset_clip.append(start_marker)

        end = arithmetic.float2fcpsec(s['end'], fps)
        end_marker = ET.Element("marker")
        end_marker.set("start", end)
        end_marker.set("value", f"{keyword} end {i}")
        end_marker.set("duration", fps)
        end_marker.set("completed", "0")

        # proof
        silence_duration = arithmetic.fcpsec2frac(end) - arithmetic.fcpsec2frac(start)
        assert silence_duration > arithmetic.Fraction(0, 1)
        if previous_end:
            silence_gap_from_previous = arithmetic.fcpsec2frac(start) - previous_end
            assert silence_gap_from_previous > 0

        if audio_channel is not None:
            asset_clip.insert(index+1, end_marker)
        else:
            asset_clip.append(end_marker)

        previous_end = arithmetic.fcpsec2frac(end)

