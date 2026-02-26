import xml.etree.ElementTree as ET
from tqdm import tqdm
from fcp_io import fcpxml_io
from fcp_math import arithmetic

def place(root, silences: list[dict], fps: str, keyword: str, in_event: bool=False):
    """
    silences: [{'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz}, {...}, ...]
    """
    asset_clip = fcpxml_io.get_event_asset_clip(root) if in_event else fcpxml_io.get_spine_asset_clip(root)

    # Place silence Markers
    for i, s in tqdm(enumerate(silences, start=1)):
        start = arithmetic.float2fcpsec(s['start'], fps)
        start_marker = ET.SubElement(asset_clip, "marker")
        start_marker.set("start", start)
        start_marker.set("value", f"{keyword} start {i}")
        start_marker.set("duration", fps)
        start_marker.set("completed", "0")

        end = arithmetic.float2fcpsec(s['end'], fps)
        end_marker = ET.SubElement(asset_clip, "marker")
        end_marker.set("start", end)
        end_marker.set("value", f"{keyword} end {i}")
        end_marker.set("duration", fps)
        end_marker.set("completed", "0")
