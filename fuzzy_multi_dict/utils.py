from typing import Optional, Dict


def validate_symbol_weights(symbol_weights: Optional[Dict[str, float]]) -> None:
    """
    Validates the symbol weights dictionary.

    Ensures that all keys in the `symbol_weights` dictionary are single-character strings
    and that all weights are in the range [0, 1].

    Args:
        symbol_weights (Optional[Dict[str, float]]): A dictionary where keys are symbols (strings of length 1)
            and values are weights (floats in the range [0, 1]).

    Raises:
        ValueError: If any key is not a single-character string.
        ValueError: If any weight is not a float in the range [0, 1].
    """
    if symbol_weights is None:
        return

    invalid_keys = [key for key in symbol_weights if len(key) != 1]
    if invalid_keys:
        raise ValueError(
            f"Invalid keys in `symbol_weights`: {invalid_keys}. "
            "All keys must be single-character symbols (e.g., 'a', 'b', 'c')."
        )

    invalid_weights = {key: weight for key, weight in symbol_weights.items() if not (0.0 <= weight <= 1.0)}
    if invalid_weights:
        raise ValueError(
            f"Invalid weights in `symbol_weights`: {invalid_weights}. "
            "All weights must be floats in the range [0, 1]."
        )
