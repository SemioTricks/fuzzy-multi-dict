import pytest

from fuzzy_multi_dict import FuzzyMultiDict, CorrectionPrice


def test_get():

    d = FuzzyMultiDict(max_corrections_value=1.)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert d["first"] == 1
    assert d["frst"] == 1  # missing symbol
    assert d["forst"] == 1  # wrong symbol
    assert d["fiirst"] == 1  # extra symbol
    assert d["frsd"] == 1  # more than 1 mistake
    assert d["tirsf"] == 1  # more than 2 mistake
    assert d["rsd"] == 1  # more than 2 mistake

    r = d.get("frst")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_max_corrections():

    d = FuzzyMultiDict(max_corrections_value=1/3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert len(d.get("firstt")) > 0
    assert len(d.get("firstttt")) == 0

    d.set_max_corrections_value(.5)
    assert len(d.get("firstttt")) > 0

    d = FuzzyMultiDict()

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert len(d.get("firstt")) == 0

    d.set_max_corrections_value(1/3)
    assert len(d.get("firstt")) > 0

    d.set_max_corrections_value(1/2)
    assert len(d.get("firstt")) > 0


def test_transposition():

    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("ifrst")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_insertion():

    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("frst")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_substitution():
    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("ferst")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_deletion():

    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("firstt")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_get_key_with_alts():
    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("fird")
    assert len(r) == 2
    values = [_["value"] for _ in r]
    assert 1 in values and 3 in values


def test_get_no_key():
    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["first"] = 1
    d["second"] = 2

    r = d.get("third")
    assert len(r) == 0

    with pytest.raises(KeyError):
        _ = d["third"]


def test_set_dict():
    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["first"] = {"x": 1, "y": 2, "z": 3}
    d["second"] = [1, 2, 3]
    d["third"] = 3

    assert d.get("first") is not None
    assert d["first"].get("x") is not None
    assert d["first"]["x"] == 1


def test_custom_upd_value():
    def update_value(x, y):

        if x is None:
            return y

        if not isinstance(x, dict) or not isinstance(y, dict):
            raise TypeError(
                f"Invalid value type; expect dict; got {type(x)} and {type(y)}"
            )

        for k, v in y.items():

            if x.get(k) is None:
                x[k] = v
                continue

            if isinstance(x[k], list):
                if v not in x[k]:
                    x[k].append(v)
                continue

            if x[k] != v:
                x[k] = [x[k], v]

        return x

    d = FuzzyMultiDict(max_corrections_value=2/3, update_value=update_value)

    d["first"] = {"x": 1, "y": 2}
    d["first"] = {"x": 1, "y": 2, "z": 3}
    assert d["first"]["x"] == 1
    assert d["first"]["y"] == 2

    d["first"] = {"x": 1, "y": 2, "z": 4}
    assert d["first"]["z"] == [3, 4]

    d["first"] = {"z": 5}
    assert d["first"]["z"] == [3, 4, 5]

    d["first"] = {"z": 5}
    assert d["first"]["z"] == [3, 4, 5]


def test_get_key_with_sim():
    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["on"] = 1
    d["one"] = 2
    d["ones"] = 3

    r = d.get("on")
    assert len(r) == 1
    assert r[0]["value"] == 1

    r = d.get("one")
    assert len(r) == 1
    assert r[0]["value"] == 2

    r = d.get("ones")
    assert len(r) == 1
    assert r[0]["value"] == 3


def test_search():
    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["apple"] = "apple"
    d["apple red delicious"] = "apple red delicious"
    d["apple fuji"] = "apple fuji"
    d["apple granny smith"] = "apple granny smith"
    d["apple honeycrisp"] = "apple honeycrisp"
    d["apple golden delicious"] = "apple golden delicious"
    d["apple pink lady"] = "apple pink lady"

    assert len(d.get("apple")) == 1
    assert len(d.search("apple")) > 1
    assert len(d.search("apl")) > 1


def test_search_02():
    d = FuzzyMultiDict(max_corrections_value=2/3)

    d["apple"] = {'s': "apple", 'id': 1}
    d["apple red delicious"] = {'s': "apple red delicious", 'id': 2}
    d["apple fuji"] = {'s': "apple fuji", 'id': 3}
    d["apple granny smith"] = {'s': "apple granny smith", 'id': 4}
    d["apple honeycrisp"] = {'s': "apple honeycrisp", 'id': 5}
    d["apple golden delicious"] = {'s': "apple golden delicious", 'id': 6}
    d["apple pink lady"] = {'s': "apple pink lady", 'id': 7}

    assert len(d.get("apple")) == 1
    assert len(d.search("apple")) > 1
    assert len(d.search("apl")) > 1


def test_init():

    d = FuzzyMultiDict(
        max_corrections_value=2/3,
        correction_price=CorrectionPrice(1., 1., 1., 1.),
        symbol_probability={'a': 1., 'c': .5},
        default_symbol_probability=.1,
        symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
        default_symbols_distance=1.
    )

    d["специи"] = "специи"
    d["апельсин"] = "апельсин"
    d["спицы"] = "спицы"
    d["пила"] = "пила"
    d["опилки"] = "опилки"
    d["слип"] = "слип"
    d["спальник"] = "спальник"

    r = d.search('спел')
    assert len(r) > 0

    assert r[0]['value'] == 'апельсин'


def test_init_error_max_corr_value():

    with pytest.raises(ValueError):
        FuzzyMultiDict(
            max_corrections_value=5.,
            correction_price=CorrectionPrice(1., 1., 1., 1.),
            symbol_probability={'a': 1., 'c': .5},
            default_symbol_probability=.1,
            symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
            default_symbols_distance=1.
        )


def test_init_corr_price_type():
    with pytest.raises(TypeError):
        FuzzyMultiDict(
            max_corrections_value=2/3,
            correction_price=1.,
            symbol_probability={'a': 1., 'c': .5},
            default_symbol_probability=.1,
            symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
            default_symbols_distance=1.
        )


def test_init_corr_price():
    with pytest.raises(ValueError):
        FuzzyMultiDict(
            max_corrections_value=2/3,
            correction_price=CorrectionPrice(1., 1., 1., 10.),
            symbol_probability={'a': 1., 'c': .5},
            default_symbol_probability=.1,
            symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
            default_symbols_distance=1.
        )


def test_symb_prob_key():
    with pytest.raises(ValueError):
        FuzzyMultiDict(
            max_corrections_value=2/3,
            correction_price=CorrectionPrice(1., 1., 1., 1.),
            symbol_probability={'a': 1., 'c': .5, 'ас': .1},
            default_symbol_probability=.1,
            symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
            default_symbols_distance=1.
        )


def test_symb_prob():
    with pytest.raises(ValueError):
        FuzzyMultiDict(
            max_corrections_value=2/3,
            correction_price=CorrectionPrice(1., 1., 1., 1.),
            symbol_probability={'a': 1., 'c': .5, 'd': 10.},
            default_symbol_probability=.1,
            symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
            default_symbols_distance=1.
        )

    with pytest.raises(ValueError):
        FuzzyMultiDict(
            max_corrections_value=2/3,
            correction_price=CorrectionPrice(1., 1., 1., 1.),
            symbol_probability={'a': 1., 'c': .5, 'd': 1.},
            default_symbol_probability=5.1,
            symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
            default_symbols_distance=1.
        )


def test_symb_dist():

    with pytest.raises(ValueError):
        FuzzyMultiDict(
            max_corrections_value=2/3,
            correction_price=CorrectionPrice(1., 1., 1., 1.),
            symbol_probability={'a': 1., 'c': .5, 'd': 1.},
            default_symbol_probability=.1,
            symbols_distance={('а', 'с'): .01, ('ц', 'л'): 10.},
            default_symbols_distance=1.
        )
    with pytest.raises(ValueError):
        FuzzyMultiDict(
            max_corrections_value=2/3,
            correction_price=CorrectionPrice(1., 1., 1., 1.),
            symbol_probability={'a': 1., 'c': .5, 'd': 1.},
            default_symbol_probability=.1,
            symbols_distance={('а', 'с'): .01, ('ц', 'ло'): 1.},
            default_symbols_distance=1.
        )


def test_set_max_corr_value():
    d = FuzzyMultiDict(
        max_corrections_value=2/3,
        correction_price=CorrectionPrice(1., 1., 1., 1.),
        symbol_probability={'a': 1., 'c': .5, 'd': 1.},
        default_symbol_probability=.1,
        symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
        default_symbols_distance=1.
    )
    d.set_max_corrections_value(1/3)
    assert d.max_corrections_value == 1/3


def test_set_corr_price():
    d = FuzzyMultiDict(
        max_corrections_value=2/3,
        correction_price=CorrectionPrice(1., 1., 1., 1.),
        symbol_probability={'a': 1., 'c': .5, 'd': 1.},
        default_symbol_probability=.1,
        symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
        default_symbols_distance=1.
    )
    print(d.correction_price)
    d.set_correction_price(CorrectionPrice(deletion=1., substitution=.2, transposition=.3, insertion=.4),)
    assert d.correction_price.insertion == .4


def test_set_symb_prob_dist():
    d = FuzzyMultiDict()

    d.set_symbols_probability_distances(
        symbol_probability={'a': 1., 'b': .5, 'c': 1.},
        default_symbol_probability=.1,
        symbols_distance={('a', 'b'): .5, ('b', 'c'): .1},
        default_symbols_distance=1.)

    assert d.default_symbol_probability == .1
    assert d.default_symbols_distance == 1.

    assert d.get_symbol_probability('b') == .5
    assert d.get_symbol_probability('e') == .1

    assert d.get_symbols_distance('a', 'b') == .5
    assert d.get_symbols_distance('b', 'a') == .5
    assert d.get_symbols_distance('d', 'e') == 1.
    assert d.get_symbols_distance('c', 'c') == .0
