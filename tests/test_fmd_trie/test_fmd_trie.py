from fuzzy_multi_dict.fmd_trie import FMDTrie, FMDTrieNode


def test_init():
    trie = FMDTrie()
    trie.add('abc', 1)
    assert trie.node_count == 4
    assert trie.find('abc') == {1, }
    assert trie.find('xyz') is None


def test_init_multiple_values():
    trie = FMDTrie()
    trie.add('abc', 1)
    trie.add('abc', 2)
    assert trie.node_count == 4
    assert trie.find('abc') == {1, 2}


def test_init_values_inside_trie():
    trie = FMDTrie()
    trie.add('a', 1)
    trie.add('ab', 2)
    trie.add('abc', 3)
    assert trie.node_count == 4
    assert trie.find('a') == {1, }
    assert trie.find('ab') == {2, }
    assert trie.find('abc') == {3, }


def test_init_structured():
    trie = FMDTrie()
    trie.add('abc', 1)
    trie.add('abd', 2)
    trie.add('ae', 3)
    assert trie.node_count == 6

    a_node = trie._root['a']
    assert not a_node.values
    assert len(a_node.children) == 2


def test_init_with_symbol_weight():
    trie = FMDTrie()
    trie.add('a', 1)
    trie.add('b', 2)
    trie.add('c', 3)
    trie.add('d', 4)
    assert list(trie._root.children.keys()) == ['a', 'b', 'c', 'd']

    trie = FMDTrie()
    trie.add('a', 1, symbol_weights={'a': .1, 'b': .2, 'c': .3})
    trie.add('b', 2, symbol_weights={'a': .1, 'b': .2, 'c': .3})
    trie.add('c', 3, symbol_weights={'a': .1, 'b': .2, 'c': .3})
    trie.add('d', 4, symbol_weights={'a': .1, 'b': .2, 'c': .3})
    assert list(trie._root.children.keys()) == ['c', 'b', 'a', 'd']
