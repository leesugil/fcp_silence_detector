"""
# Detect text in video (FCPXML)
(Once this module is implemented, maybe the whole 'fcp-silence-detector' should be upgraded to something else with multiple features including silence detection and text detection. Make the front-end your first)

## To make sure you don't place a marker every frame, set a time window parameter.
If the desired text is detected:
    Place '{text} start' and set state='detected'.
If state=='detected' and {text} is no longer detected for seconds=1:
    Place '{text} end' and set state='not detected'.

## Features
- Option to set a buffer range like buffer_seconds=0.5.

  If the pure detection gives
  ..........|--text---|..........,

  offer an option buffer_seconds=0.5 to place markers
  ......v.................v......

  because there could be other effects going on on screen before the desired text detectable clearly detectable by OCR.
- Should I use pyautogui OCR, or OpenCV image detection? Which one is more accurate? Which one is less expensive?
  Go with OCR first. This is a "Detect text" module.
- Allow multiple text detection maybe? Usually, my main use for this module is to remove the save or load screens in gaming videos. So the workflow is 'Open the menu' -> 'Click Save or Save As or Load or whatever' until the obvious text keyword "Saving..." appears on the screen. The pre-workflow can take more than the pre-determined time (like 0.5 seconds), I might just want to set multiple keywords for the detection condition and remove all of them by placing Markers.

## Optimization
- Sampling. Offer an option to perform OCR (expensive) at every n frames (or m milliseconds).
- Crop. Maybe first by declaring top-left and bottom-right pixels to scan. Add more user-friendly features later like declaring it with percentage.
"""

from tqdm import tqdm
import numpy as np
import pytesseract as tess
import cv2
import datetime

# Have OCR ready
tess.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# screen region to scan
def crop_frame(frame: np.ndarray, top: int, left: int, bottom: int, right: int) -> np.ndarray:
    assert top < bottom
    assert left < right

    output = frame[top:bottom, left:right]
    #print(f"Crop to top, left, bottom, right = {top, left, bottom, right}")

    return output

# OpenCV to go frame by frame

def detect_text_from_string(string: str, text: str):
    assert isinstance(text, str)
    assert text != ''

    x = string.find(text)
    if x != -1:
        # found the text in string
        return text
    return ''

def detect_texts_from_string(string: str, texts: list[str]):
    output = []

    for t in texts:
        d = detect_text_from_string(string, t)
        if d != '':
            output.append(d)

    return output

def format_timedelta(td: datetime.timedelta) -> str:
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    output = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return output

def seconds_to_frame(seconds: int, fps: int) -> int:
    assert seconds > -1
    assert fps > 0

    output = seconds * fps
    return output

def frame_to_seconds(frames: int, fps: int) -> int:
    assert frames > -1
    assert fps > 0

    output = round(frames / fps)
    return output

def filter_match(texts, detected, mode):
    """
    texts = ['a', 'bc', ...]
    detected: [{'time': 'hh:mm:ss', 'detected': ['ABC', 'XYZ', ...]}, {...}, ...]
    mode = 'and' or 'or'
    """
    output = []

    # OR
    if mode == 'or':
        output = detected
        return output

    # AND
    for d in detected:
        if set(texts) == set(d['detected']):
            output.append(d)

    return output

def detect_texts_from_video(file_path: str='', texts: list[str]=[], top: int=0, left: int=0, bottom: int=0, right: int=0, skip_frames: int=1, skip_seconds: int=0, mode='and'):
    """
    mode = 'and' or 'or'
    returns the info as a list of dictionaries.
    [{'timestamp': 'hh:mm:ss', 'detected': [a, b, c]}, {...}, ...]
    """
    assert file_path is not None
    assert isinstance(file_path, str)
    assert len(texts) > 0 #if args.texts = '', then texts = [], raising assertion.
    assert skip_frames > 0
    assert mode in {'and', 'or'}
    for s in texts:
        assert isinstance(s, str)
        assert s != ''
    print(f"DEBUG: texts: {texts}")

    video = cv2.VideoCapture(file_path)
    if not video.isOpened():
        raise RuntimeError("Could not open video file")

    # Determine cropping region
    height = round(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = round(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    if (top, left, bottom, right) == (0, 0, 0, 0):
        bottom = height
        right = width
    #print(f"top,left,bottom,right {top},{left},{bottom},{right}")

    output = []

    # Scan every skip_frames frames
    fps = video.get(cv2.CAP_PROP_FPS)
    if skip_seconds != 0:
        skip_frames = seconds_to_frame(skip_seconds, fps)
    frame_count = round(video.get(cv2.CAP_PROP_FRAME_COUNT))

    for i in tqdm(range(frame_count)):
        if (i % skip_frames) != 0:
            continue

        ret, frame = video.read()
        if not ret:
            break

        # frame is a NumPy array (H x W x 3)
        # Do something with frame
        d = {'time': '', 'detected': []}

        # Crop for OCR Scan
        img = crop_frame(frame=frame, top=top, left=left, bottom=bottom, right=right)
        #print(f"top,left,bottom,right {top},{left},{bottom},{right}")

        # Grayscale for OCR Scan
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Upscale for PyTesseract
        #scale = 2
        #img = cv2.resize(img, (img.shape[1]*scale, img.shape[0]*scale), interpolation=cv2.INTER_CUBIC)

        # OCR Scan
        captured_string = tess.image_to_string(img)
        #print(f"Captured string: {captured_string}")

        d['detected'] = detect_texts_from_string(string=captured_string, texts=texts)
        #print(f"Detected string: {d['detected']}")
        #cv2.imshow("debug frame", img)
        #cv2.waitKey(1)

        # Process the scanned data
        if d['detected']:
            td = datetime.timedelta(milliseconds=video.get(cv2.CAP_PROP_POS_MSEC))
            d['time'] = format_timedelta(td)
            output.append(d)
            print(f"detected from the current frame: {d['detected']}")
            print(f"OCR result so far: {output}")

    video.release()

    print(f"OCR result before filter_match: {output}")
    output = filter_match(texts=texts, detected=output, mode=mode)
    print(f"OCR result after filter_match: {output}")

    return output
