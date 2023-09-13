from fuzzy_multi_dict import FuzzyMultiDict


def update_value(x, y):

    if x is None:
        return y

    if not isinstance(x, dict) or not isinstance(y, dict):
        raise TypeError(f"Invalid value type; expect dict; got {type(x)} and {type(y)}")

    for k, v in y.items():

        if x.get(k) is None:
            x[k] = v
        elif isinstance(x[k], list):
            if v not in x[k]:
                x[k].append(v)
        elif x[k] != v:
            x[k] = [x[k], v]

    return x


phone_book = FuzzyMultiDict(
    max_corrections_relative=2 / 3, update_value_func=update_value
)

phone_book["Mom"] = {"phone": "123-4567", "organization": "family"}
phone_book["Adam"] = {"phone": "890-1234", "organization": "work"}
phone_book["Lisa"] = {"phone": "567-8901", "organization": "family"}
phone_book["Adam"] = {"address": "baker street 221b"}
phone_book["Adam"] = {"phone": "234-5678", "organization": "work"}

print(phone_book["Adam"])
# {'phone': ['890-1234', '234-5678'],
#  'organization': 'work',
#  'address': 'baker street 221b'}
