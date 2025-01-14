import pytest
from unittest.mock import Mock

from fuzzy_multi_dict.fuzzy_multi_dict import FuzzyMultiDict
from fuzzy_multi_dict.fmd_trie.fmd_trie_traverser import FMDTrieTraverser

from fuzzy_multi_dict.search_engine.search_engine import SearchEngine
from fuzzy_multi_dict.search_engine.correction import SymbolInsertion


@pytest.fixture
def search_engine():
    return Mock()


@pytest.fixture
def trie_traverser():
    return FMDTrieTraverser()


def test_apply_string(search_engine, trie_traverser):
    d = FuzzyMultiDict(search_engine)
    d['abcd'] = 1

    path_nodes = trie_traverser.apply_string(d.trie.root, 'a')
    assert len(path_nodes) == 1

    path_nodes = trie_traverser.apply_string(d.trie.root, 'abcd')
    assert len(path_nodes) == 4

    path_nodes = trie_traverser.apply_string(d.trie.root, 'ax')
    assert len(path_nodes) == 1

    d = FuzzyMultiDict(search_engine)
    d['ab'] = 1
    d['abc'] = 2
    d['abcd'] = 3

    path_nodes = trie_traverser.apply_string(d.trie.root, 'abcd')
    assert len(path_nodes) == 4


def test_get_node_leaves(trie_traverser, search_engine):
    d = FuzzyMultiDict(search_engine)
    d['abcd'] = 1
    d['ade'] = 2
    d['ae'] = 3
    assert trie_traverser.get_node_leaves(d.trie.root) == [3, 2, 1]

    d = FuzzyMultiDict(search_engine)
    d['abcd'] = 3
    d['ade'] = 2
    d['ae'] = 1
    assert trie_traverser.get_node_leaves(d.trie.root) == [1, 2, 3]

    d = FuzzyMultiDict(search_engine)
    d['abcd'] = 1
    d['abc'] = 2
    d['ab'] = 3
    assert trie_traverser.get_node_leaves(d.trie.root) == [3, 2, 1]


def test_get_n_node_leaves(trie_traverser, search_engine):
    d = FuzzyMultiDict(search_engine)
    d['abcd'] = 1
    d['ade'] = 2
    d['ae'] = 3
    assert trie_traverser.get_node_leaves(d.trie.root) == [3, 2, 1]
    assert trie_traverser.get_node_leaves(d.trie.root, 2) == [3, 2]
    assert trie_traverser.get_node_leaves(d.trie.root, 1) == [3, ]
