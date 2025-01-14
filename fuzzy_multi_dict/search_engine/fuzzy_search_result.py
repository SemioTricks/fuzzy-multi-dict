from typing import Optional, List, Any
from dataclasses import dataclass, field

from .correction_detail import CorrectionDetail, get_total_corrections_price


@dataclass
class FuzzySearchResult:
    """
    Represents the result of a fuzzy search.

    Attributes:
        value (Optional[int]): The found value.
        key (str): The key corresponding to the result.
        path (str): The full path to the result in the prefix tree.
        corrections (Optional[List[CorrectionDetail]]): A list of corrections made during the search.
        total_corrections_price (float): The total "price" or score of all corrections.
    """
    value: Optional[int] = None
    key: str = ""
    path: str = ""
    corrections: Optional[List[CorrectionDetail]] = field(default_factory=list)
    total_corrections_price: float = 0.0

    def __post_init__(self):
        """
        Calculates the total correction price after the object is initialized.
        """
        self.total_corrections_price = get_total_corrections_price(self.corrections)
