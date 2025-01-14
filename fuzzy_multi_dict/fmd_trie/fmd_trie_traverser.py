from typing import List, Tuple, Dict
from collections import deque

from .fmd_trie import FMDTrieNode

from fuzzy_multi_dict.config import DEFAULT_TOPN_LEAVES


class FMDTrieTraverser:
    """
    A class responsible for traversing the prefix tree and applying a string to the tree.

    Methods:
        apply_string(node, s, position): Applies a string to the prefix tree and traverses from the given node.
    """

    @staticmethod
    def apply_string(node: FMDTrieNode, s: str) -> List[FMDTrieNode]:

        path_nodes: List[FMDTrieNode] = []

        for char in s:
            current_node = node.get(char)
            if not current_node:
                return path_nodes

            path_nodes.append(current_node)
            node = current_node

        return path_nodes

    @staticmethod
    def get_node_leaves(node: FMDTrieNode, topn: int = DEFAULT_TOPN_LEAVES) -> List[int]:

        queue = deque(list(node.children.values()))
        leaves = []

        while queue and len(leaves) < topn:
            current_node = queue.popleft()

            if current_node.values:
                leaves.extend(current_node.values)
                if len(leaves) >= topn:
                    return leaves[:topn]

            queue.extend(current_node.children.values())

        return leaves[:topn]

