# fuzzy-multi-dict

[![Coverage Status](https://img.shields.io/badge/%20Python%20Versions-%3E%3D3.9-informational)](https://pypi.org/project/fuzzy_multi_dict/)
[![Coverage Status](https://coveralls.io/repos/github/SemioTricks/fuzzy-multi-dict/badge.svg?branch=feature/initial)](https://coveralls.io/github/SemioTricks/fuzzy-multi-dict?branch=feature/initial)

[![Coverage Status](https://img.shields.io/badge/Version-0.0.7-informational)](https://pypi.org/project/fuzzy_multi_dict/)
[![Coverage Status](https://img.shields.io/badge/Docs-passed-green)](https://github.com/SemioTricks/fuzzy-multi-dict/tree/main/docs)

**fuzzy-multi-dict** is a module that provides a hight-flexible structure for storing 
and accessing information by a string key.

**Fuzzy**: access by key is carried out even if there are mistakes 
(missing/extra/incorrect character) in the string representation of the key.

**Multi**: flexible functionality for updating data on an existing key.


# Installation

> pip install fuzzy_multi_dict

# Quickstart

Module can be used as a fast enough (due to the tree structure of data storage)
spell-checker.

```python
from fuzzy_multi_dict import FuzzyMultiDict
from fuzzy_multi_dict.search_engine import (
    SearchEngine,
    SymbolInsertion,
    SymbolsTransposition,
    SymbolsDeletion,
    SymbolSubstitution
)

symbol_weights = {'a': 1, 'p': .5, 'l': .6, 'e': .7}
symbols_distances = {('a', 's'): .1, ('a', 'l'): .7}

corrections = [
    SymbolInsertion(price=1., symbol_weights=symbol_weights),
    SymbolsTransposition(price=1., symbols_distances=symbols_distances),
    SymbolsDeletion(price=1., symbol_weights=symbol_weights),
    SymbolSubstitution(price=1., symbols_distances=symbols_distances)
]
search_engine = SearchEngine(corrections)


d = FuzzyMultiDict(
    search_engine=search_engine,
    symbol_weights=symbol_weights,
)

d["apple golden delicious"] = 1
d["apple red delicious"] = 2
d["apple granny smith"] = 3
d["apple honeycrisp"] = 4
d["apple pink lady"] = 5
d["apple fuji"] = 6

print(d.get("apple"))
# [6, 5, 4, 3, 2, 1]

print(d.get("apel"))
# [6, 5, 4, 3, 2, 1]

print(d.get("apple g"))
# [3, 1]

print(d.get("apple f"))
# [6]

print(d.get("apple gol"))
# [1]

print(d.get("ppl pnk ld"))
# [5]

print(d.get("juice"))
# []

```
