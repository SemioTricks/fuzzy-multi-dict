import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple

from fuzzy_multi_dict.config import MIN_CORRECTION_PRICE

from .search_state import SearchState
from .correction_detail import CorrectionDetail

logger = logging.getLogger(__name__)


class Correction(ABC):
    """
    Abstract base class for describing query correction operations.

    Attributes:
        _name (str): The name of the correction.
        _price (float): The base cost of the correction.
    """

    _name: str
    _price: float = 1
    _symbols_distances: Optional[Dict[Tuple[str, str], float]] = None
    _symbol_weights: Optional[Dict[str, float]] = None

    def __init__(
            self, price: float = 1,
            symbol_weights: Optional[Dict[str, float]] = None,
            symbols_distances: Optional[Dict[Tuple[str, str], float]] = None):
        """
        Initializes the correction with the specified cost.

        Args:
            price (float): The base cost of the correction. Default is 1.
        """
        self.set_price(price)
        self._symbol_weights = symbol_weights
        self._symbols_distances = symbols_distances

    @abstractmethod
    def apply(self, query: str, search_state: SearchState) -> List[SearchState]:
        """
        Abstract method to apply the correction.

        Args:
            query (str): The input search query.
            search_state (SearchState): The current state of the search.

        Returns:
            List[SearchState]: A list of new search states after applying the correction.
        """
        pass

    def set_price(self, price: float):
        """
        Sets the base cost of the correction.

        Args:
            price (float): The new cost of the correction.
        """
        self._price = price

    @property
    def name(self):
        """
        Returns the name of the correction.

        Returns:
            str: The name of the correction.
        """
        return self._name


class SymbolInsertion(Correction):
    """
    Correction class for symbol insertion.
    """

    _name: str = 'insertion'

    def apply(self, query: str, search_state: SearchState) -> List[SearchState]:
        """
        Applies symbol insertion correction.

        Args:
            query (str): The input search query.
            search_state (SearchState): The current state of the search.

        Returns:
            List[SearchState]: A list of new search states after applying symbol insertion.
        """
        symbol_weights = self._symbol_weights or {}
        next_symbol = query[search_state.position]
        result_search_states = []

        for key in search_state.node.children:
            if key == next_symbol:
                continue

            symbol_weight = symbol_weights.get(key, 0)
            correction_price = (self._price * (1 - symbol_weight)) ** 0.5

            corrections = search_state.corrections + [
                CorrectionDetail(
                    correction_name=self._name,
                    parameters=[key],
                    position=search_state.position,
                    price=correction_price
                )
            ]

            result_search_states.append(SearchState(
                node=search_state.node.children[key],
                path=search_state.path + key,
                position=search_state.position,
                corrections=corrections
            ))

        logging.info(f'Apply {self._name}: {len(result_search_states)} corrections applied at position {search_state.position}')
        return result_search_states


class SymbolsTransposition(Correction):
    """
    Correction class for symbol transposition (swapping the positions of two symbols).
    """

    _name: str = 'transposition'

    def apply(self, query: str, search_state: SearchState) -> List[SearchState]:
        """
        Applies symbol transposition correction.

        Args:
            query (str): The input search query.
            search_state (SearchState): The current state of the search.

        Returns:
            List[SearchState]: A list of new search states after applying symbol transposition.
        """
        if len(query) <= search_state.position + 1:
            return []

        symbols_distances = self._symbols_distances or {}

        left_symbol, right_symbol = query[search_state.position], query[search_state.position + 1]

        if right_symbol not in search_state.node.children:
            return []

        sub_node = search_state.node.children[right_symbol]
        if left_symbol not in sub_node.children:
            return []

        node = sub_node.children[left_symbol]
        path = query[:search_state.position] + right_symbol + left_symbol
        symbols_distance = symbols_distances.get((left_symbol, right_symbol), 1)
        correction_price = (self._price * symbols_distance) ** 0.5

        corrections = search_state.corrections + [
            CorrectionDetail(
                correction_name=self._name,
                parameters=[left_symbol, right_symbol],
                price=correction_price,
                position=search_state.position
            )
        ]

        result_search_states = [
            SearchState(
                node=node,
                path=path,
                position=search_state.position + 2,
                corrections=corrections
            )
        ]

        logging.info(f'Apply {self._name}: correction applied at position {search_state.position}')
        return result_search_states


class SymbolsDeletion(Correction):
    """
    Correction class for symbol deletion.
    """

    _name: str = 'deletion'

    def apply(self, query: str, search_state: SearchState) -> List[SearchState]:
        """
        Applies symbol deletion correction.

        Args:
            query (str): The input search query.
            search_state (SearchState): The current state of the search.

        Returns:
            List[SearchState]: A list of new search states after applying symbol deletion.
        """
        if search_state.position > 0 and query[search_state.position - 1] == query[search_state.position]:
            correction_price = MIN_CORRECTION_PRICE
        else:
            symbol_weights = self._symbol_weights or {}
            symbol_weight = symbol_weights.get(query[search_state.position], 0)
            correction_price = (self._price * (1 - symbol_weight)) ** 0.5

        corrections = search_state.corrections + [
            CorrectionDetail(
                correction_name=self._name,
                parameters=[query[search_state.position]],
                price=correction_price,
                position=search_state.position
            )
        ]

        result_search_states = [
            SearchState(
                node=search_state.node,
                path=search_state.path,
                position=search_state.position + 1,
                corrections=corrections
            )
        ]

        logging.info(f'Apply {self._name}: deletion applied at position {search_state.position}')
        return result_search_states


class SymbolSubstitution(Correction):
    """
    Correction class for symbol substitution.
    """

    _name: str = 'substitution'

    def apply(self, query: str, search_state: SearchState) -> List[SearchState]:
        """
        Applies symbol substitution correction.

        Args:
            query (str): The input search query.
            search_state (SearchState): The current state of the search.

        Returns:
            List[SearchState]: A list of new search states after applying symbol substitution.
        """
        result_search_states = []

        for child_key in search_state.node.children:
            if child_key == query[search_state.position]:
                continue

            symbols_distances = self._symbols_distances or {}
            symbols_distance = symbols_distances.get((query[search_state.position], child_key), 1)

            correction_price = (self._price * symbols_distance) ** 0.5

            corrections = search_state.corrections + [
                CorrectionDetail(
                    correction_name=self._name,
                    parameters=[query[search_state.position], child_key],
                    price=correction_price,
                    position=search_state.position
                )
            ]

            result_search_states.append(
                SearchState(
                    node=search_state.node.children[child_key],
                    path=search_state.path + child_key,
                    position=search_state.position + 1,
                    corrections=corrections
                )
            )

        logging.info(f'Apply {self._name}: {len(result_search_states)} substitutions applied at position {search_state.position}')
        return result_search_states
