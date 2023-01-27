import pytest

from fuzzy_multi_dict import FuzzyMultiDict


def test_get_key_with_mistakes():

    d = FuzzyMultiDict(max_mistakes_number=3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    assert d["first"] == 1
    assert d["frs"] == 1
    assert d["rs"] == 1

    r = d.get("frst")
    assert len(r) == 1
    assert r[0]["value"] == 1
    assert len(r[0]["mistakes"]) == 1


def test_get_key_with_alts():
    d = FuzzyMultiDict(max_mistakes_number=3)

    d["first"] = 1
    d["second"] = 2
    d["third"] = 3

    r = d.get("fird")
    assert len(r) == 2
    values = [_["value"] for _ in r]
    assert 1 in values and 3 in values


def test_get_no_key():
    d = FuzzyMultiDict(max_mistakes_number=3)

    d["first"] = 1
    d["second"] = 2

    r = d.get("third")
    assert len(r) == 0

    with pytest.raises(KeyError):
        _ = d["third"]


def test_set_dict():
    d = FuzzyMultiDict(max_mistakes_number=3)

    d["first"] = {"x": 1, "y": 2, "z": 3}
    d["second"] = [1, 2, 3]
    d["third"] = 3
    print(d["first"].get("x"))
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

    d = FuzzyMultiDict(max_mistakes_number=3, update_value_func=update_value)

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
