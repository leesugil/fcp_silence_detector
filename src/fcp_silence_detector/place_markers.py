import xml.etree.ElementTree as ET
from tqdm import tqdm
#from . import fcpxml_io
from fcp_io import fcpxml_io

def place(filepath: str, silences: list[dict], affix: str, sync=False):
    """
    silences: [{'start': xx.xxx, 'end': yy.yyy, 'duration': zz.zzz}, {...}, ...]
    """
    tree, root = fcpxml_io.get_fcpxml(filepath)
    asset_clip = fcpxml_io.get_clip(root, sync)
    offset = fcpxml_io.get_offset(asset_clip, sync)

    # Place silence Markers
    for i, s in tqdm(enumerate(silences, start=1)):
        start_marker = ET.SubElement(asset_clip, "marker")
        start_marker.set("start", f"{s['start']+offset}s")
        start_marker.set("value", f"Silence start {i}")
        start_marker.set("duration", "100/6000s")
        start_marker.set("completed", "0")

        end_marker = ET.SubElement(asset_clip, "marker")
        end_marker.set("start", f"{s['end']+offset}s")
        end_marker.set("value", f"Silence end {i}")
        end_marker.set("duration", "100/6000s")
        end_marker.set("completed", "0")

    #fcpxml_io.save(tree, filepath, affix)
    fcpxml_io.save_with_affix(tree, filepath, affix)

