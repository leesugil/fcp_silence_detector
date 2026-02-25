import xml.etree.ElementTree as ET
from tqdm import tqdm
from fcp_io import fcpxml_io
from fcp_math import arithmetic

def place(filepath: str, silences: list[dict], fps: str):
    """
    silences: [{'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz}, {...}, ...]
    """
    tree, root = fcpxml_io.get_fcpxml(filepath)
    asset_clip = fcpxml_io.get_event_asset_clip(root)

    # Place silence Markers
    for i, s in tqdm(enumerate(silences, start=1)):
        start = arithmetic.float2fcpsec(s['start'], fps)
        start_marker = ET.SubElement(asset_clip, "marker")
        start_marker.set("start", start)
        start_marker.set("value", f"Silence start {i}")
        start_marker.set("duration", fps)
        start_marker.set("completed", "0")

        end = arithmetic.float2fcpsec(s['end'], fps)
        end_marker = ET.SubElement(asset_clip, "marker")
        end_marker.set("start", end)
        end_marker.set("value", f"Silence end {i}")
        end_marker.set("duration", fps)
        end_marker.set("completed", "0")
