import pytest

from fuzzy_multi_dict import FuzzyMultiDict


def test_get():

    d = FuzzyMultiDict(max_corrections=3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert d["first"] == 1
    assert d["frst"] == 1  # missing symbol
    assert d["forst"] == 1  # wrong symbol
    assert d["fiirst"] == 1  # extra symbol
    assert d["frs"] == 1  # more than 1 mistake
    assert d["tirsf"] == 1  # more than 2 mistake
    assert d["rs"] == 1  # more than 2 mistake

    r = d.get("frst")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_max_corrections():

    d = FuzzyMultiDict(max_corrections=1)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert len(d.get("firstt")) > 0
    assert len(d.get("firstttt")) == 0
    assert len(d.get("firstttt", max_corrections=3)) > 0
    assert len(d.get("firstttt", max_corrections_relative=0.5)) > 0

    d = FuzzyMultiDict(max_corrections=None, max_corrections_relative=None)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert len(d.get("firstt")) == 0
    assert len(d.get("firstt", max_corrections=1)) > 0
    assert len(d.get("firstt", max_corrections_relative=0.5)) > 0


def test_transposition():

    d = FuzzyMultiDict(max_corrections=3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("ifrst")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_insertion():

    d = FuzzyMultiDict(max_corrections=3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("frst")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_substitution():
    d = FuzzyMultiDict(max_corrections=3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("ferst")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_deletion():

    d = FuzzyMultiDict(max_corrections=3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("firstt")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["correction"]) == 1


def test_get_key_with_alts():
    d = FuzzyMultiDict(max_corrections=3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("fird")
    assert len(r) == 2
    values = [_["value"] for _ in r]
    assert 1 in values and 3 in values


def test_get_no_key():
    d = FuzzyMultiDict(max_corrections=3)

    d["first"] = 1
    d["second"] = 2

    r = d.get("third")
    assert len(r) == 0

    with pytest.raises(KeyError):
        _ = d["third"]


def test_set_dict():
    d = FuzzyMultiDict(max_corrections=3)

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

    d = FuzzyMultiDict(max_corrections=3, update_value_func=update_value)

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
    d = FuzzyMultiDict(max_corrections=3)

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
