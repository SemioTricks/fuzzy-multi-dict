import pytest
from unittest.mock import Mock
from fuzzy_multi_dict import FuzzyMultiDict
from fuzzy_multi_dict.search_engine.search_engine import SearchEngine
from fuzzy_multi_dict.search_engine.correction import (
    SymbolInsertion,
    SymbolsTransposition,
    SymbolsDeletion,
    SymbolSubstitution
)


@pytest.fixture
def search_engine():
    corrections = [
        SymbolInsertion(price=1.),
        SymbolsTransposition(price=1.),
        SymbolsDeletion(price=1.),
        SymbolSubstitution(price=1.)
    ]
    return SearchEngine(corrections)


def test_init():
    search_engine = Mock()
    d = FuzzyMultiDict(search_engine)
    d['abc'] = 2

    assert d.trie.root.idx == 0
    assert d.trie.root['a'].idx == 1
    assert d.trie.root['a']['b'].idx == 2
    assert d.trie.root['a']['b']['c'].idx == 3


def test_setitem():

    search_engine = Mock()

    d = FuzzyMultiDict(search_engine)
    d['x'] = 1

    d = FuzzyMultiDict(search_engine)
    d['a'] = 1
    d['ab'] = 2
    d['abc'] = 3

    d = FuzzyMultiDict(search_engine)
    d['abc'] = 1
    d['ab'] = 2
    d['a'] = 3


def test_setitem_with_symbol_weights():

    search_engine = Mock()
    d = FuzzyMultiDict(search_engine)
    d['a'] = 1
    d['b'] = 1
    assert list(d.trie.root.children.keys()) == ['a', 'b']

    d = FuzzyMultiDict(symbol_weights={'a': 0, 'b': 1}, search_engine=search_engine)
    d['a'] = 1
    d['b'] = 1
    assert list(d.trie.root.children.keys()) == ['b', 'a']


def test_getitem():

    search_engine = Mock()
    d = FuzzyMultiDict(search_engine)
    d['x'] = 1

    assert d['x'] == 1
    #
    # with pytest.raises(KeyError):
    #     assert d['y']


def test_get(search_engine):
    d = FuzzyMultiDict(search_engine)
    d['a'] = 1

    assert d.get('a') == [1, ]

    d = FuzzyMultiDict(search_engine)
    d['ab'] = 1
    d['acc'] = 2
    d['addd'] = 3

    assert d.get('a') == [1, 2, 3]

    d = FuzzyMultiDict(search_engine)
    d['ab'] = 3
    d['acc'] = 2
    d['addd'] = 1

    assert d.get('a') == [3, 2, 1]

    d = FuzzyMultiDict(search_engine)
    d['abc'] = 2
    d['abcd'] = 3

    assert d.get('ab') == [2, 3]


def test_get_with_insertion(search_engine):
    corrections = [
        SymbolInsertion(price=1.),
    ]
    search_engine = SearchEngine(corrections)
    d = FuzzyMultiDict(search_engine)

    d['abcd'] = 1
    assert d.get('bcd') == [1, ]
    assert d.get('acd') == [1, ]
    assert d.get('abd') == [1, ]
    assert d.get('abc') == [1, ]
    assert d.get('ac') == [1, ]
    assert d.get('ab') == [1, ]
    assert d.get('bc') == [1, ]

    d['ac'] = 2
    assert d.get('ac') == [2, ]

    d['bc'] = 3
    assert d.get('bc') == [3, ]


def test_get_with_transposition():
    corrections = [
        SymbolsTransposition(price=1.),
    ]
    search_engine = SearchEngine(corrections)
    d = FuzzyMultiDict(search_engine)

    d['abcd'] = 1
    assert d.get('bacd') == [1, ]
    assert d.get('acbd') == [1, ]
    assert d.get('abdc') == [1, ]


def test_get_with_deletion():

    corrections = [
        SymbolsDeletion(price=1.),
    ]
    search_engine = SearchEngine(corrections)

    d = FuzzyMultiDict(search_engine)
    d['abcd'] = 1

    assert d.get('aabcd') == [1, ]
    assert d.get('abcdd') == [1, ]
    assert d.get('aabcdd') == [1, ]

    assert d['xyz'] is None


def test_get_with_substitution():
    corrections = [
        SymbolSubstitution(price=1.)
    ]
    search_engine = SearchEngine(corrections)
    d = FuzzyMultiDict(search_engine)
    d['abcd'] = 1

    assert d.get('xbcd') == [1, ]
    assert d.get('axcd') == [1, ]
    assert d.get('abxd') == [1, ]
    assert d.get('abcx') == [1, ]

    assert d['xyz'] is None


def test_get_with_corrections(search_engine):

    d = FuzzyMultiDict(search_engine)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert d["first"] == 1
    assert d["frst"] == 1  # missing symbol
    assert d["irst"] == 1  # missing symbol
    assert d["firs"] == 1  # missing symbol

    assert d["ifrst"] == 1  # symbols transposition
    assert d["firts"] == 1  # symbols transposition

    assert d["fits"] == 1  # symbols transposition + missing symbol

    assert d["forst"] == 1  # wrong symbol
    assert d["fiirst"] == 1  # extra symbol

    assert d['xyz'] is None


def test_get_with_mylt_corrections(search_engine):
    d = FuzzyMultiDict(search_engine)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert d["fiirs"] == 1  # extra symbol + missing symbol

    assert d["frsd"] == 1  # 2 mistakes
    assert d["tirsf"] == 1  # 2 mistakes
    assert d["frsd"] == 1  # 2 mistakes


def test_get_with_mult_corrections_and_values(search_engine):
    d = FuzzyMultiDict(search_engine)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert d.get('tfirsd', max_correction_rate=.6) == [1, 3]
    assert d.get('tirsd') == [1, 3]


def test_max_corrections(search_engine):

    d = FuzzyMultiDict(search_engine)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert len(d.get("ffirst", max_correction_rate=.1)) == 0
    assert len(d.get("firstt", max_correction_rate=.1)) == 0
    assert len(d.get("firstt", max_correction_rate=1/3)) > 0

    assert len(d.get("firstttt", max_correction_rate=1/3)) == 0
    assert len(d.get("firstttt", max_correction_rate=.5)) > 0


def test_get_no_key(search_engine):
    d = FuzzyMultiDict(search_engine)

    d["first"] = 1
    d["second"] = 2

    r = d.get("third")
    assert len(r) == 0

    assert d["third"] is None


def test_get_key_with_sim(search_engine):

    d = FuzzyMultiDict(search_engine)

    d["on"] = 1
    d["one"] = 2
    d["ones"] = 3

    assert d.get("on")[0] == 1
    assert d.get("one")[0] == 2
    assert d.get("ones")[0] == 3


def test_unintuitive(search_engine):
    symbol_weights = {'a': 1., 'c': .5, 'ц': .1}
    symbols_distances = {
        ('а', 'с'): .01, ('с', 'а'): .01, ('ц', 'л'): 1, ('л', 'ц'): 1}

    corrections = [
        SymbolInsertion(price=1., symbol_weights=symbol_weights, symbols_distances=symbols_distances),
        SymbolsTransposition(price=1., symbol_weights=symbol_weights, symbols_distances=symbols_distances),
        SymbolsDeletion(price=1., symbol_weights=symbol_weights, symbols_distances=symbols_distances),
        SymbolSubstitution(price=1., symbol_weights=symbol_weights, symbols_distances=symbols_distances)
    ]
    search_engine = SearchEngine(corrections)

    d = FuzzyMultiDict(search_engine=search_engine, symbol_weights=symbol_weights)

    d["специи"] = 1
    d["апельсин"] = 2
    d["спицы"] = 3
    d["пила"] = 4
    d["опилки"] = 5
    d["слип"] = 6
    d["спальник"] = 7

    r = d.get('спел', max_correction_rate=2/3)
    assert len(r) > 0

    assert r[0] == 2


def test_search(search_engine):
    d = FuzzyMultiDict(search_engine)

    d["apple golden delicious"] = 1
    d["apple red delicious"] = 2
    d["apple granny smith"] = 3
    d["apple honeycrisp"] = 4
    d["apple pink lady"] = 5
    d["apple fuji"] = 6
    d["apple"] = 7

    assert d.get("apple") == [7, 6, 5, 4, 3, 2, 1]
    assert d.get("apl") == [7, 6, 5, 4, 3, 2, 1]
    assert d.get("apple g") == [3, 1]
    assert d.get("apple f") == [6, ]


def test_save_load(search_engine, tmp_path):
    d = FuzzyMultiDict(search_engine)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    d.save_trie(tmp_path / 'trie.bin')

    d_loaded = FuzzyMultiDict(search_engine)
    d_loaded.load_trie(tmp_path / 'trie.bin')
    assert d_loaded["first"] == 1

