
from fcp_silence_detector import detect_silence

def test_detect():
    cases = [
                {
                'args': {
                    #filepath, dB=-40, duration=3, track=1
                    },
                #
                'expected': ,
                },
            ]

    for case in cases:
        assert detect_silence.detect(case['args']) == case['expected']

def test_parse():
    cases = [
                {
                'args': {
                    #stderr
                    },
                #
                'expected': ,
                },
            ]

    for case in cases:
        assert detect_silence.parse(case['args']) == case['expected']

def test_polish():
    cases = [
                {
                'args': {
                    #silences, polish_duration=1
                    },
                #
                'expected': ,
                },
            ]

    for case in cases:
        assert detect_silence.polish(case['args']) == case['expected']

def test_buffer():
    cases = [
                {
                'args': {
                    #silences, buffer_duration=1
                    },
                #
                'expected': ,
                },
            ]

    for case in cases:
        assert detect_silence.buffer(case['args']) == case['expected']

def test_detect_silences():
    cases = [
                {
                'args': {
                    #file_path, db, duration, polish_duration, buffer_duration, track
                    },
                #
                'expected': ,
                },
            ]

    for case in cases:
        assert detect_silence.detect_silences(case['args']) == case['expected']

