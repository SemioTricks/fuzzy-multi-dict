# Fuzzy Multi Dict

[![Coverage Status](https://img.shields.io/badge/%20Python%20Versions-%3E%3D3.9-informational)](https://pypi.org/project/fuzzy_multi_dict/)
[![Coverage Status](https://coveralls.io/repos/github/SemioTricks/fuzzy-multi-dict/badge.svg?branch=feature/initial)](https://coveralls.io/github/SemioTricks/fuzzy-multi-dict?branch=feature/initial)

[![Coverage Status](https://img.shields.io/badge/Version-0.0.1-informational)](https://pypi.org/project/fuzzy_multi_dict/)
[![Coverage Status](https://img.shields.io/badge/Docs-passed-green)](https://github.com/SemioTricks/fuzzy-multi-dict/tree/main/docs)

**fuzzy-multi-dict** is a module that provides a hight-flexible structure for storing 
and accessing information by a string key.

**Fuzzy**: access by key is carried out even if there are mistakes 
(missing/extra/incorrect character) in the string representation of the key.

**Multi**: flexible functionality for updating data on an existing key.


### Installation

> pip install fuzzy_multi_dict

## Examples

Module can be used as a fast enough (due to the tree structure of data storage)
spell-checker.

```python
import re
from fuzzy_multi_dict import FuzzyMultiDict

with open('big_text.txt', 'r') as f:
    words = list(set(re.findall(r'[a-z]+', f.read().lower())))
    
vocab = FuzzyMultiDict(max_mistakes_number=3)
for word in words:
    vocab[word] = word
    
vocab['responsibilities']
# 'responsibilities'

vocab['espansibillities']
# 'responsibilities'

vocab.get('espansibillities')
# [{'value': 'responsibilities',
#   'key': 'responsibilities',
#   'mistakes': [{'mistake_type': 'missing symbol "r"', 'position': 0},
#    {'mistake_type': 'wrong symbol "a": replaced on "o"', 'position': 3},
#    {'mistake_type': 'extra symbol "l"', 'position': 10}]}]
```

It can also be used as a flexible structure to store and access semi-structured data.

```python
from fuzzy_multi_dict import FuzzyMultiDict

def update_value(x, y):
    
    if x is None: return y
    
    if not isinstance(x, dict) or not isinstance(y, dict):
        raise TypeError(f'Invalid value type; expect dict; got {type(x)} and {type(y)}')
        
    for k, v in y.items():
        if x.get(k) is None: x[k] = v
        elif isinstance(x[k], list):
            if v not in x[k]: x[k].append(v)
        elif x[k] != v: x[k] = [x[k], v]
            
    return x

phone_book = FuzzyMultiDict(
    max_mistakes_number=3, 
    update_value_func=update_value
)

phone_book['Mom'] = {'phone': '123-4567', 'organization': 'family'}
phone_book['Adam'] = {'phone': '890-1234', 'organization': 'work'}
phone_book['Lisa'] = {'phone': '567-8901', 'organization': 'family'}
phone_book['Adam'] = {'address': 'baker street 221b'}
phone_book['Adam'] = {'phone': '234-5678', 'organization': 'work'}

phone_book['Adam']
# {'phone': ['890-1234', '234-5678'],
#  'organization': 'work',
#  'address': 'baker street 221b'}
```