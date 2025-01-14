from typing import List, Optional
from dataclasses import dataclass


@dataclass
class CorrectionDetail:
    """
    Represents detailed information about a correction.

    Attributes:
        description (str): Correction description (e.g., for logging).
        position (Optional[int]): Position of the correction in the string (if applicable).
        price (Optional[float]): The "cost" or score of the correction.
    """
    correction_name: str
    parameters: List[str]
    position: Optional[int]
    price: Optional[float]


def get_total_corrections_price(corrections: Optional[List[CorrectionDetail]]) -> float:
    """
    Calculates the total "price" (score) of all corrections.

    Args:
        corrections (Optional[List[CorrectionDetail]]): A list of corrections applied to the query.

    Returns:
        float: The sum of correction scores. Returns 0.0 if no corrections are provided.
    """
    if not corrections:
        return 0.0

    return sum(correction.price for correction in corrections if correction.price is not None)
