from pyseq.opt import Opt
from pyseq.seq import Seq


def test_seq():
    assert Seq.range(3).to_list() == [0, 1, 2]
    assert Seq.zip(range(5), [9, 8, 7]).to_list() == [(0, 9), (1, 8), (2, 7)]
    assert Seq.repeat(6, 3).to_list() == [6, 6, 6]
    assert Seq.once(6).to_list() == [6]
    assert Seq.once(None).to_list() == []
    assert Seq.range(4).map(lambda x: x ** 2).to_list() == [0, 1, 4, 9]
    assert Seq.range(10).take_if(lambda x: x % 3 == 0).to_list() == [0, 3, 6, 9]
    assert Seq.range(10).drop_if(lambda x: x % 3 == 0).to_list() == [1, 2, 4, 5, 7, 8]
    assert Seq.range(10).take_while(lambda x: x < 4).to_list() == [0, 1, 2, 3]
    assert Seq.range(10).take_until(lambda x: x == 4).to_list() == [0, 1, 2, 3]
    assert Seq.range(10).drop_while(lambda x: x < 4).to_list() == [4, 5, 6, 7, 8, 9]
    assert Seq.range(10).drop_until(lambda x: x == 4).to_list() == [4, 5, 6, 7, 8, 9]
    assert Seq.range(10).take(5).to_list() == [0, 1, 2, 3, 4]
    assert Seq.range(10).drop(5).to_list() == [5, 6, 7, 8, 9]
    assert Seq.range(10).slice(2, 6).to_list() == [2, 3, 4, 5]
    assert Seq(['x', 'y', 'z']).enumerate(start=1).to_list() == [(1, 'x'), (2, 'y'), (3, 'z')]
    assert Seq.range(5).reverse().to_list() == [4, 3, 2, 1, 0]
    assert Seq([9, 3, 2, 8]).sort().to_list() == [2, 3, 8, 9]
    assert Seq([9, 3, 2, 8]).sort_desc().to_list() == [9, 8, 3, 2]
    assert Seq([5, 1, 2, 1, 3, 1, 4]).unique().to_list() == [5, 1, 2, 3, 4]
    assert Seq.range(4).zip_with([9, 8, 7, 6, 5]).to_list() == [(0, 9), (1, 8), (2, 7), (3, 6)]
    assert Seq.range(4).chain([-2, -1]).to_list() == [0, 1, 2, 3, -2, -1]
    assert Seq(['Alpha', 'Beta', 'Gamma']).flatten().to_str() == 'AlphaBetaGamma'
    assert Seq.range(3).flat_map(lambda x: range(10, 11 + x)).to_list() == [10, 10, 11, 10, 11, 12]
    assert Seq.range(3).all(lambda x: x < 10)
    assert Seq.range(3).any(lambda x: x < 10)
    assert not Seq.range(3).none(lambda x: x < 10)
    assert Seq.range(3).join() == '012'
    assert Seq.range(1, 101).sum() == 5050
    assert not Seq([]).first()
    assert Seq([]).first().value_or(-1) == -1
    assert Seq([]).first().value_or_eval(lambda: -2) == -2
    assert Seq([1, 2, 3]).first().value() == 1
    assert Seq([1, 2, 3]).nth(4).value_or(-1) == -1
    assert Seq([1, 2, 3]).nth(4) == Opt.none()
    assert Seq([1, 2, 3]).nth(1) == Opt.of(2)
    assert Seq.range(10).to_dict(lambda x: x % 2) == {0: 8, 1: 9}
    assert Seq.range(10).to_multidict(lambda x: x % 2) == {0: [0, 2, 4, 6, 8], 1: [1, 3, 5, 7, 9]}
    assert Seq.zip([1, 2, 3, 4], ['a', 'b', 'c', 'd']).to_dict() == {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
    assert Seq([1, 2, 3, 4]).min() == 1
    assert Seq([0, 1, 2, 3, 4]).min(lambda x: abs(x - 3)) == 3
    assert Seq([1, 2, 3, 4]).max() == 4
    assert Seq([0, 1, 2, 3, 4]).max(lambda x: abs(x - 3)) == 0
    assert Seq([0, 1, 2, 3, 4]).minmax() == (0, 4)
    assert Seq([0, 1, 2, 3, 4]).minmax(lambda x: abs(x - 3)) == (3, 0)
