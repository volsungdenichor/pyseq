from pyseq.match import create_matcher, when, __


def test_matcher_11():
    matcher = create_matcher(
        when(lambda x: x < 10).then(lambda x: 100 * x),
        when(lambda x: 10 <= x < 20) >> 881,
        when(__) >> (lambda: 991))

    assert matcher(5) == 500
    assert matcher(10) == 881
    assert matcher(999) == 991


def test_matcher_2():
    matcher = create_matcher(
        when(lambda x: x is None) >> 'None',
        when(lambda x: x.startswith('X')) >> str.lower,
        when(lambda x: x.startswith('Y')) >> (lambda x: '_' + x.upper()),
        when(lambda x: x == '?') >> (lambda: '@'),
        when('!') >> '%',
        when(__) >> (lambda x: x))

    assert matcher(None) == 'None'
    assert matcher('Abc') == 'Abc'
    assert matcher('Xyphos') == 'xyphos'
    assert matcher('Ydaspes') == '_YDASPES'
    assert matcher('?') == '@'
    assert matcher('!') == '%'
