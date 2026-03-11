
from fcp_silence_detector import cli

def test_main():
    cases = [
                {
                'args': {
                    #
                    },
                #
                'expected': ,
                },
            ]

    for case in cases:
        assert cli.main(case['args']) == case['expected']

