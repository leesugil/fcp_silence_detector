import xml.etree.ElementTree as ET
import os
import shutil

def place(filepath):
    d, b = os.path.split(filepath)
    fcpxml_filename = 'Info.fcpxml'
    filepath = os.path.join(filepath, fcpxml_filename)

    tree = ET.parse(filepath)
    root = tree.getroot()

    asset_clip = root.find(".//asset-clip")

    silences = [
            {"start": 2879.412708, "end": 2882.479625, "duration": 3.066917}
            ]

    for i, s in enumerate(silences, start=1):
        start_marker = ET.SubElement(asset_clip, "marker")
        start_marker.set("start", f"{s['start']}s")
        start_marker.set("value", f"Silence start {i}")

        end_marker = ET.SubElement(asset_clip, "marker")
        end_marker.set("start", f"{s['end']}s")
        end_marker.set("value", f"Silence end {i}")

    # Save the new FCPXML file
    src_filepath = os.path.join(d, b)
    new_filepath = os.path.join(d, 'silence_marked_'+b)
    shutil.copytree(src_filepath, new_filepath, dirs_exist_ok=True)
    destination_filepath = os.path.join(new_filepath, fcpxml_filename)
    ET.indent(tree, space="\t", level=0)
    tree.write(destination_filepath, encoding='UTF-8', xml_declaration=True)

with open('data_fcpxml') as f:
    for line in f:
        if '\n' in line:
            line = line[:-1]

        filepath = os.path.abspath(line)
        place(filepath)
