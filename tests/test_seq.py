from pyseq.functions import identity
from pyseq.opt import Opt
from pyseq.seq import Seq


def _test_seq(seq, expected):
    assert list(seq) == expected


def test_seq():
    _test_seq(Seq.range(3), [0, 1, 2])
    _test_seq(Seq.zip(range(5), [9, 8, 7]), [(0, 9), (1, 8), (2, 7)])
    _test_seq(Seq.repeat(6, 3), [6, 6, 6])
    _test_seq(Seq.once(6), [6])
    _test_seq(Seq.empty(), [])
    _test_seq(Seq.as_iterable(None), [])
    _test_seq(Seq.as_iterable(6), [6])
    _test_seq(Seq.as_iterable('abc'), ['abc'])
    _test_seq(Seq.range(4).map(lambda x: x ** 2), [0, 1, 4, 9])
    _test_seq(Seq.range(10).take_if(lambda x: x % 3 == 0), [0, 3, 6, 9])
    _test_seq(Seq.range(10).drop_if(lambda x: x % 3 == 0), [1, 2, 4, 5, 7, 8])
    _test_seq(Seq.range(10).take_while(lambda x: x < 4), [0, 1, 2, 3])
    _test_seq(Seq.range(10).take_until(lambda x: x == 4), [0, 1, 2, 3])
    _test_seq(Seq.range(10).drop_while(lambda x: x < 4), [4, 5, 6, 7, 8, 9])
    _test_seq(Seq.range(10).drop_until(lambda x: x == 4), [4, 5, 6, 7, 8, 9])
    _test_seq(Seq.range(10).take(5), [0, 1, 2, 3, 4])
    _test_seq(Seq.range(10).drop(5), [5, 6, 7, 8, 9])
    _test_seq(Seq.range(10).slice(2, 6), [2, 3, 4, 5])
    _test_seq(Seq(['x', 'y', 'z']).enumerate(start=1), [(1, 'x'), (2, 'y'), (3, 'z')])
    _test_seq(Seq.range(5).reverse(), [4, 3, 2, 1, 0])
    _test_seq(Seq([9, 3, 2, 8]).sort(), [2, 3, 8, 9])
    _test_seq(Seq([9, 3, 2, 8]).sort_desc(), [9, 8, 3, 2])
    _test_seq(Seq([5, 1, 2, 1, 3, 1, 4]).unique(), [5, 1, 2, 3, 4])
    _test_seq(Seq.range(4).zip_with([9, 8, 7, 6, 5]), [(0, 9), (1, 8), (2, 7), (3, 6)])
    _test_seq(Seq.range(4).chain([-2, -1]).extend([9]).append(-42), [0, 1, 2, 3, -2, -1, 9, -42])
    Seq(['Alpha', 'Beta', 'Gamma']).flatten().to_str() == 'AlphaBetaGamma'
    _test_seq(Seq.range(3).flat_map(lambda x: range(10, 11 + x)), [10, 10, 11, 10, 11, 12])
    _test_seq(Seq.range(10, 16).replace_if(lambda x: x % 3 == 0, -888), [10, 11, -888, 13, 14, -888])
    _test_seq(Seq.range(10, 13).replace(10, -888), [-888, 11, 12])
    assert Seq.range(3).all(lambda x: x < 10)
    assert Seq.range(3).any(lambda x: x < 10)
    assert not Seq.range(3).none(lambda x: x < 10)
    assert Seq.range(3).join() == '012'
    assert Seq.range(1, 101).sum() == 5050
    assert not Seq([]).first()
    assert Seq([]).first().get_or(-1) == -1
    assert Seq([]).first().get_or_else(lambda: -2) == -2
    assert Seq([1, 2, 3]).first() == Opt.some(1)
    assert Seq([]).last() == Opt.none()
    assert Seq([1, 2, 3]).last() == Opt.some(3)
    assert Seq([1, 2, 3]).nth(1) == Opt.some(2)
    assert Seq([1, 2, 3]).nth(4) == Opt.none()
    assert Seq.range(10).to_dict(lambda x: x % 2) == {0: 8, 1: 9}
    assert Seq.range(10).to_multidict(lambda x: x % 2) == {0: [0, 2, 4, 6, 8], 1: [1, 3, 5, 7, 9]}
    assert Seq.zip([1, 2, 3, 4], ['a', 'b', 'c', 'd']).to_dict() == {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
    assert Seq([1, 2, 3, 4]).min() == Opt.some(1)
    assert Seq([0, 1, 2, 3, 4]).min(lambda x: abs(x - 3)) == Opt.some(3)
    assert Seq([]).min() == Opt.none()
    assert Seq([1, 2, 3, 4]).max() == Opt.some(4)
    assert Seq([0, 1, 2, 3, 4]).max(lambda x: abs(x - 3)) == Opt.some(0)
    assert Seq([]).max() == Opt.none()
    assert Seq([8, 9, 10, 11, 12]).find(lambda x: x > 10) == Opt.some(11)
    assert Seq([8, 9, 10, 11, 12]).find(lambda x: x > 100) == Opt.none()
    assert Seq([8]).single() == Opt.some(8)
    assert Seq([]).single() == Opt.none()
    assert Seq([8, 9]).single() == Opt.none()
    _test_seq(Seq([0, None, 1, None, 2, None]).filter_map(Opt), [0, 1, 2])
    _test_seq(Seq([Opt.some(1), Opt.none(), Opt.some(2), Opt.none()]).filter_map(identity), [1, 2])
    _test_seq(Seq.range(8).map(lambda x: x ** 2).chunk(3), [[0, 1, 4], [9, 16, 25], [36, 49]])
    _test_seq(Seq('x,y,z').split_after(lambda x: x == ','), [['x', ','], ['y', ','], ['z']])
    _test_seq(Seq('x,y,z').split_before(lambda x: x == ','), [['x'], [',', 'y'], [',', 'z']])
    _test_seq(Seq('xy,,yz,,zz,,').split_at(lambda x: x == ','), [['x', 'y'], ['y', 'z'], ['z', 'z']])
    assert Seq.range(10).take_if(lambda x: x % 3 == 0).len() == 4
    _test_seq(Seq([1, 2, 2, 3, 7]).intersection([2, 9, 3, 7, 7]), [2, 3, 7])
    _test_seq(Seq([1, 2, 2, 3, 7]).union([2, 9, 3, 7, 7]), [1, 2, 3, 7, 9])
    _test_seq(Seq([7, 2, 2, 3, 1]).difference([3]), [1, 2, 7])
    _test_seq(Seq([9, 1, 6, 2, 7]).exclude([7, 1]), [9, 6, 2])
    assert Seq([1, 2, 3]).contains(3)
    assert not Seq([1, 2, 3]).contains(8)
    assert tuple(x.to_list() for x in Seq([1, 2, 3, 4, 5]).partition(lambda x: x % 2 == 0)) == ([2, 4], [1, 3, 5])
    _test_seq(Seq([3, 0, 9, 8, 7]).adjacent(), [(3, 0), (0, 9), (9, 8), (8, 7)])
    _test_seq(Seq([3, 0, 9, 8]).adjacent_difference(None), [-3, 9, -1])
    _test_seq(Seq(['A', 'B', 'C']).intersperse(','), ['A', ',', 'B', ',', 'C'])
