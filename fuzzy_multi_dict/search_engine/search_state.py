from typing import List
from dataclasses import dataclass

from fuzzy_multi_dict.fmd_trie import FMDTrieNode

from .correction_detail import CorrectionDetail


@dataclass
class SearchState:
    position: int
    path: str
    node: FMDTrieNode
    corrections: List[CorrectionDetail]
