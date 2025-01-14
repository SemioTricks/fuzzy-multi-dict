from collections import OrderedDict
from typing import Optional, Set, Dict


class FMDTrie:
    """
    A prefix tree (trie) implementation that stores integer values and supports ordering of children keys.

    Attributes:
        _node_count (int): The total count of nodes in the trie.
        _root (FMDTrieNode): The root node of the trie.
    """

    def __init__(self):
        """Initializes the FMDTrie with a root node and a node counter."""
        self._node_count = 0
        self._root = FMDTrieNode(self)

    def __len__(self) -> int:
        """Returns the total number of nodes in the trie."""
        return self._node_count

    def __str__(self) -> str:
        """Returns a string representation of the trie structure."""
        def dfs(node: 'FMDTrieNode') -> str:
            children_s = ', '.join(
                [f'{k}⟶{list(child.values) or ""}{dfs(child)}' for k, child in node.children.items()]
            )
            return f'{{{children_s}}}' if children_s else ""

        return f'FMDTrie(node_count={self._node_count},trie={dfs(self._root)})'

    @property
    def node_count(self) -> int:
        """Returns the number of nodes in the trie."""
        return self._node_count

    def inc_node_count(self):
        """Increments the node count by 1."""
        self._node_count += 1

    def add(self, keys: str, value: int, symbol_weights: Optional[Dict[str, float]]=None):
        """
        Adds a value to the trie at the path specified by the sequence of keys.

        Args:
            keys (str): A string representing the sequence of keys.
            value (int): The value to store at the final node.
        """
        node = self._root
        for key in keys:
            node = node.add_child(key, symbol_weights)
        node.add_value(value)

    def find(self, keys: str) -> Optional[Set[int]]:
        """
        Finds the set of values stored at the node specified by the sequence of keys.

        Args:
            keys (str): A string representing the sequence of keys.

        Returns:
            Optional[Set[int]]: The set of values at the final node, or None if the path does not exist.
        """
        node = self._root
        for key in keys:
            node = node.get(key)
            if node is None:
                return None
        return node.values

    @property
    def root(self):
        return self._root


class FMDTrieNode:
    """
    A node in the FMDTrie.

    Attributes:
        _trie (FMDTrie): Reference to the parent trie.
        _idx (int): Unique index of the node.
        children (OrderedDict[str, FMDTrieNode]): Ordered dictionary of child nodes.
        values (Set[int]): Set of integer values stored at this node.
    """

    def __init__(self, trie: FMDTrie):
        """Initializes an FMDTrieNode with reference to the parent trie."""
        self._trie = trie
        self._idx = self._trie.node_count
        self._trie.inc_node_count()
        self.children: OrderedDict[str, 'FMDTrieNode'] = OrderedDict()
        self.values: Set[int] = set()

    def add_child(self, key: str, symbol_weights: Optional[Dict[str, float]]=None) -> 'FMDTrieNode':
        """
        Adds a child node for the given key if it does not exist.

        Args:
            key (str): The key for the child node.

        Returns:
            FMDTrieNode: The child node corresponding to the key.
        """
        if key not in self.children:
            self.children[key] = FMDTrieNode(self._trie)
            if symbol_weights:
                self.children = OrderedDict(
                    sorted(self.children.items(), key=lambda x: -symbol_weights.get(x[0], 0)))
        return self.children[key]

    def get(self, key: str) -> Optional['FMDTrieNode']:
        """
        Retrieves the child node for the given key.

        Args:
            key (str): The key to look for.

        Returns:
            Optional[FMDTrieNode]: The child node if it exists, or None otherwise.
        """
        return self.children.get(key)

    def __getitem__(self, key: str) -> 'FMDTrieNode':
        """
        Allows indexing to retrieve child nodes.

        Args:
            key (str): The key to retrieve.

        Returns:
            FMDTrieNode: The child node corresponding to the key.

        Raises:
            KeyError: If the key does not exist.
        """
        node = self.get(key)
        if node is None:
            raise KeyError(f"Key '{key}' not found.")
        return node

    def add_value(self, value: int):
        """
        Adds an integer value to the node.

        Args:
            value (int): The value to add.
        """
        self.values.add(value)

    def add_values(self, values: Set[int]):
        """
        Adds multiple integer values to the node.

        Args:
            values (Set[int]): The values to add.
        """
        self.values.update(values)

    def __str__(self) -> str:
        """Returns a string representation of the node."""
        return f'FMDTrieNode(idx={self._idx}, values={self.values}, children={list(self.children.keys())})'

    @property
    def idx(self):
        return self._idx

    @property
    def tree(self):
        return self._trie
