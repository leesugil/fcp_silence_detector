import xml.etree.ElementTree as ET
import os
import shutil

def place(filepath, silences):
    filepath = os.path.abspath(filepath)
    d, b = os.path.split(filepath)
    fcpxml_filename = 'Info.fcpxml'
    filepath = os.path.join(filepath, fcpxml_filename)

    tree = ET.parse(filepath)
    root = tree.getroot()

    asset_clip = root.find(".//asset-clip")

    for i, s in enumerate(silences, start=1):
        start_marker = ET.SubElement(asset_clip, "marker")
        start_marker.set("start", f"{s['start']}s")
        start_marker.set("value", f"Silence start {i}")
        start_marker.set("duration", "100/6000s")
        start_marker.set("completed", "0")

        end_marker = ET.SubElement(asset_clip, "marker")
        end_marker.set("start", f"{s['end']}s")
        end_marker.set("value", f"Silence end {i}")
        end_marker.set("duration", "100/6000s")
        end_marker.set("completed", "0")

    # Save the new FCPXML file
    src_filepath = os.path.join(d, b)
    new_filepath = os.path.join(d, 'silence_marked_'+b)
    shutil.copytree(src_filepath, new_filepath, dirs_exist_ok=True)
    destination_filepath = os.path.join(new_filepath, fcpxml_filename)
    ET.indent(tree, space="\t", level=0)
    tree.write(destination_filepath, encoding='UTF-8', xml_declaration=True)

def place_sync(filepath, silences):
    filepath = os.path.abspath(filepath)
    d, b = os.path.split(filepath)
    fcpxml_filename = 'Info.fcpxml'
    filepath = os.path.join(filepath, fcpxml_filename)

    tree = ET.parse(filepath)
    root = tree.getroot()

    asset_clip = root.find(".//sync-clip[@format='r1']")
    asset_clip1 = asset_clip.find(".//asset-clip[@ref='r2']") # this is the source video
    asset_clip2 = asset_clip1.find(".//asset-clip[@ref='r3']") # this is the added audio "track"
    offset = asset_clip2.get('offset')
    offset = eval(offset.rstrip('s')) # as a float

    for i, s in enumerate(silences, start=1):
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

    # Save the new FCPXML file
    src_filepath = os.path.join(d, b)
    new_filepath = os.path.join(d, 'silence_marked_'+b)
    shutil.copytree(src_filepath, new_filepath, dirs_exist_ok=True)
    destination_filepath = os.path.join(new_filepath, fcpxml_filename)
    ET.indent(tree, space="\t", level=0)
    tree.write(destination_filepath, encoding='UTF-8', xml_declaration=True)

