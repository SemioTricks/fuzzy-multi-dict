import logging
from typing import List, Dict
from dataclasses import dataclass

from fuzzy_multi_dict.config import DEFAULT_TOPN_LEAVES, MAX_CORRECTION_RATE
from fuzzy_multi_dict.fmd_trie import FMDTrie, FMDTrieNode, FMDTrieTraverser

from .fuzzy_search_result import FuzzySearchResult
from .correction_detail import CorrectionDetail
from .correction import Correction


logger = logging.getLogger(__name__)


@dataclass
class SearchState:
    position: int
    path: str
    node: FMDTrieNode
    corrections: List[CorrectionDetail]


class SearchEngine:
    """
    Search engine for performing fuzzy searches within an FMDTrie.

    Attributes:
        _trie_traverser (FMDTrieTraverser): Helper class to traverse the trie.
        _corrections (List[Correction]): List of correction strategies to apply during the search.
    """

    def __init__(self, corrections: List[Correction]):
        """
        Initializes the SearchEngine with a list of corrections.

        Args:
            corrections (List[Correction]): List of correction strategies.
        """
        self._trie_traverser = FMDTrieTraverser()
        self._corrections = corrections

    def search(
            self, trie: FMDTrie, query: str,
            topn_leaves: int = DEFAULT_TOPN_LEAVES,
            max_correction_rate: float = MAX_CORRECTION_RATE) -> List[FuzzySearchResult]:
        """
        Perform a fuzzy search in the trie based on the query.

        Args:
            trie (FMDTrie): Trie structure to search.
            query (str): Query string.
            topn_leaves (int): Number of leaves to consider in results.
            max_correction_rate (float): Maximum allowed correction rate.

        Returns:
            List[FuzzySearchResult]: List of search results.
        """
        logger.info(f"Starting search for query: '{query}'")
        path_nodes = self._trie_traverser.apply_string(node=trie.root, s=query)

        if len(path_nodes) == len(query):
            logger.info("Exact match found.")
            return self._generate_search_result_from_node(
                node=path_nodes[-1], path=query, key=query, topn_leaves=topn_leaves, corrections=[])

        queue = [SearchState(position + 1, query[:position + 1], node, []) for position, node in enumerate(path_nodes)]
        queue.append(SearchState(0, "", trie.root, []))

        search_result: List[FuzzySearchResult] = []
        visited_status: Dict[int, int] = {}
        added = set()

        iteration = 0
        while queue:
            iteration += 1
            logger.info(f"Iteration {iteration}: {len(queue)} states in the queue.")
            updated_queue = []

            for step in queue:
                logger.debug(f"Processing node ID {step.node.idx} at position {step.position}, path='{step.path}', corrections={[c.correction_name for c in step.corrections]}")

                if step.position == len(query):
                    node_result = self._generate_search_result_from_node(
                        step.node, query[:step.position], step.path, topn_leaves, step.corrections)
                    for item in node_result:
                        if item.value not in added:
                            search_result.append(item)
                            added.add(item.value)
                            logger.info(f"Added result: path='{item.path}', value='{item.value}'")
                    continue

                if visited_status.get(step.node.idx) == 1:
                    logger.debug(f"Node ID {step.node.idx} already visited.")
                    continue

                visited_status[step.node.idx] = 1

                nodes_ids_path = self._trie_traverser.apply_string(step.node, query[step.position:])
                for i, node in enumerate(nodes_ids_path):
                    updated_queue.append(SearchState(
                        position=step.position + i + 1,
                        path=step.path + query[step.position: step.position + i + 1],
                        node=node,
                        corrections=step.corrections))

                current_correction_rate = (len(step.corrections) + 1) / len(query)
                if current_correction_rate <= max_correction_rate:
                    for correction in self._corrections:
                        corrections_states = correction.apply(query=query, search_state=step)
                        for correction_state in corrections_states:
                            if correction_state.node.idx == step.node.idx:
                                visited_status[step.node.idx] = 0
                                logger.debug(f"Correction loopback detected for node ID {step.node.idx}. Marked for revisit.")
                        updated_queue.extend(corrections_states)

            if not updated_queue:
                logger.info("No items left in queue. Search completed.")
                break

            queue = updated_queue

        logger.info(f"Search completed. Found {len(search_result)} results.")

        return sorted(search_result, key=lambda x: x.total_corrections_price)

    def _generate_search_result_from_node(self, node: FMDTrieNode, key: str, path: str, topn_leaves: int, corrections: List[CorrectionDetail]) -> List[FuzzySearchResult]:
        """
        Generate search results from a trie node and its leaves.

        Args:
            node (FMDTrieNode): Current node in the trie.
            key (str): Key string associated with the result.
            path (str): Path taken to reach this node.
            topn_leaves (int): Number of leaves to consider.
            corrections (List[CorrectionDetail]): List of corrections applied.

        Returns:
            List[FuzzySearchResult]: List of fuzzy search results.
        """
        logger.debug(f"Generating search result for node ID {node.idx} with path '{path}'")
        result = [
            FuzzySearchResult(value=value, key=key, path=path, corrections=corrections)
            for value in node.values
        ]
        leaves = self._trie_traverser.get_node_leaves(node, topn=topn_leaves)

        result.extend(
            FuzzySearchResult(value=value, key=key, path=path, corrections=corrections)
            for value in leaves
        )

        logger.debug(f"Generated {len(result)} results for node ID {node.idx}.")
        return result
