import pytest

from fuzzy_multi_dict.utils import validate_symbol_weights


def test_validate_symbol_weights():

    validate_symbol_weights(None)
    validate_symbol_weights({})

    validate_symbol_weights({'a': .5})
    validate_symbol_weights({'a': 0})
    validate_symbol_weights({'a': 1})

    with pytest.raises(ValueError):
        validate_symbol_weights({'abc': 1})

    with pytest.raises(ValueError):
        validate_symbol_weights({'a': 10})
