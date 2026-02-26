
Writing functions are fun, writing test files for those functions are boring. This helps that.
om fcp_silence_detect import detect_silence

def test_detect():
    cases = [
                {
                'args': {
                    'filepath': fuck,
                    'dB': -40,
                    'duration': 3,
                    'track': 1
                    },
                'expected': fuck
                },
            ]
    
    for case in cases:
        # make sure to double-check the function name
        assert detect_silence.detect(case['args']) == case['expected']

def test_parse():
    cases = [
                {
                'args': {
                    'stderr': fuck,
                    },
                'expected': fuck
                },
            ]
    
    for case in cases:
        # make sure to double-check the function name
        assert detect_silence.parse(case['args']) == case['expected']

def test_polish():
    cases = [
                {
                'args': {
                    'silences': fuck,
                    'polish_duration': 1
                    },
                'expected': 'sth'
                },
            ]
    
    for case in cases:
        # make sure to double-check the function name
        assert detect_silence.polish(case['args']) == case['expected']

def test_buffer():
    cases = [
                {
                'args': {
                    'silences': fuck,
                    'buffer_duration': 1
                    },
                'expected': fuck
                },
            ]
    
    for case in cases:
        # make sure to double-check the function name
        assert detect_silence.buffer(case['args']) == case['expected']

def test_detect_silences():
    cases = [
                {
                'args': {
                    'file_path': fuck,
                    'db': fuck,
                    'duration': fuck,
                    'polish_duration': fuck,
                    'buffer_duration': fuck,
                    'track': fuck,
                    },
                'expected': fuck
                },
            ]
    
    for case in cases:
        # make sure to double-check the function name
        assert detect_silence.detect_silences(case['args']) == case['expected']
