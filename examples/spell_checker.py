import re
from fuzzy_multi_dict import FuzzyMultiDict


with open('big.txt', 'r') as f:
    text = f.read()
    words = list(set(re.findall(r'[a-z]+', text.lower())))

vocab = FuzzyMultiDict(max_mistakes_number=3)
for word in words:
    vocab[word] = word

print(vocab['responsibilities'])
# 'responsibilities'

print(vocab['espansibillities'])
# 'responsibilities'

print(vocab.get('espansibillities'))
# [{'value': 'responsibilities',
#   'key': 'responsibilities',
#   'mistakes': [{'mistake_type': 'missing symbol "r"', 'position': 0},
#    {'mistake_type': 'wrong symbol "a": replaced on "o"', 'position': 3},
#    {'mistake_type': 'extra symbol "l"', 'position': 10}]}]