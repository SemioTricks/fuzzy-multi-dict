from collections import namedtuple
from typing import Any, Callable, Dict, List, Optional, Tuple

import dill as pickle

CorrectionPrice = namedtuple(  # type: ignore
    "CorrectionScore", "transposition deletion substitution insertion"
)


class FuzzyMultiDict:

    __prefix_tree: Dict[str, Any]
    __update_value: Callable
    __max_corrections_value: float
    __correction_price: CorrectionPrice
    __symbol_probability: Dict[str, float]
    __symbols_distance: Dict[Tuple[str, str], float]
    __default_symbol_probability: float
    __default_symbols_distance: float

    def __init__(
        self,
        max_corrections_value: float = 0.0,
        update_value: Optional[Callable] = None,
        correction_price: CorrectionPrice = CorrectionPrice(1.0, 1.0, 1.0, 1.0),
        symbol_probability: Optional[Dict[str, float]] = None,
        default_symbol_probability: float = 1e-5,
        symbols_distance: Optional[Dict[Tuple[str, str], float]] = None,
        default_symbols_distance: float = 1.0,
    ):
        """
        Initialize Fuzzy Multi Dict object with input parameters

        ::Parameters::

        :param float max_corrections_value: max relative number of corrections in
               the query to find the matching key; default = 1.
        :param Optional[Callable] update_value: function to update data by key
        :param CorrectionPrice correction_price: correction price depending on type;
               default = CorrectionPrice(1., 1., 1., 1.)
        :param Optional[Dict[str, float]] symbol_probability: probability for each
               character to rank output and sort result; default is None
        :param float default_symbol_probability: default symbol probability value
               (between 0 and 1); default = 1e-5
        :param Optional[Dict[Tuple[str, str], float]] symbols_distance: distance
               between characters (between 0 and 1) to rank output and sort result;
               default is None
        :param float default_symbols_distance: defaut value of distance between
               characters; default = 1.

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict, CorrectionPrice
        >>> d = FuzzyMultiDict(
        ...   max_corrections_value=2/3,
        ...   correction_price=CorrectionPrice(
        ...      deletion=.2, insertion=1., transposition=.1, substitution=.3),
        ...   symbol_probability={'a': 1., 'b': .5, 'c': .3},
        ...   default_symbol_probability=1e-5,
        ...   symbols_distance={('a', 'b'): .3, ('b', 'c'): .1},
        ...   default_symbols_distance=1.
        ... )

        """
        self.__prefix_tree = {"parent": "ROOT", "children": dict(), "value": None}
        self.__update_value = (lambda x, y: y) if update_value is None else update_value  # type: ignore # noqa
        self.set_correction_price(correction_price)
        self.set_symbols_probability_distances(
            symbol_probability=symbol_probability,
            symbols_distance=symbols_distance,
            default_symbol_probability=default_symbol_probability,
            default_symbols_distance=default_symbols_distance,
        )
        self.set_max_corrections_value(max_corrections_value)

    def set_correction_price(self, correction_price: CorrectionPrice):
        """
        Sets correction prices for all correction types

        ::Parameters::

        :param CorrectionPrice correction_price: correction price depending on type;
               default = CorrectionPrice(1., 1., 1., 1.)

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict(correction_price=CorrectionPrice(
        ...   deletion=.2, insertion=1., transposition=.1, substitution=.3),
        ... )
        >>> d.correction_price
        ... # CorrectionScore(
        ... #    transposition=0.1, deletion=0.2, substitution=0.3, insertion=0.1)
        >>> d.correction_price.insertion
        ... # 0.1

        """
        if not isinstance(correction_price, CorrectionPrice):
            raise TypeError(f"expect CorrectionPrice; got {type(correction_price)}")

        if not all(
            [
                0.0 <= price <= 1.0
                for price in (
                    correction_price.deletion,
                    correction_price.substitution,
                    correction_price.transposition,
                    correction_price.insertion,
                )
            ]
        ):
            raise ValueError("expect float value between .0 and 1.")

        self.__correction_price = correction_price

    def set_symbols_probability_distances(
        self,
        symbol_probability: Optional[Dict[str, float]],
        default_symbol_probability: float,
        symbols_distance: Optional[Dict[Tuple[str, str], float]],
        default_symbols_distance: float,
    ):
        """
        Sets symbols probabilities and distances

        ::Parameters::

        :param Optional[Dict[str, float]] symbol_probability: probability for each
               character to rank output and sort result; default is None
        :param float default_symbol_probability: default symbol probability value
               (between 0 and 1); default = 1e-5
        :param Optional[Dict[Tuple[str, str], float]] symbols_distance: distance
               between characters (between 0 and 1) to rank output and
               sort result; default is None
        :param float default_symbols_distance: default value of distance between
               characters; default = 1.

        ::Example::

        >>> d = FuzzyMultiDict()

        >>> d.set_symbols_probability_distances(
        ...    symbol_probability={'a': 1., 'b': .5, 'c': 1.},
        ...    default_symbol_probability=.1,
        ...    symbols_distance={('a', 'b'): .5, ('b', 'c'): .1},
        ...    default_symbols_distance=1.)

        >>> d.default_symbol_probability
        ... # .1
        >>> d.default_symbols_distance
        ... # 1.

        >>> d.get_symbol_probability('b')
        ... # .5
        >>> d.get_symbol_probability('e')
        ... # .1

        >>> d.get_symbols_distance('a', 'b')
        ... # .5
        >>> d.get_symbols_distance('b', 'a')
        ... # .5
        >>> d.get_symbols_distance('d', 'e')
        ... # 1.
        >>> d.get_symbols_distance('c', 'c')
        ... # .0

        """
        if not 0.0 <= default_symbol_probability <= 1.0:
            raise ValueError("expect float value between .0 and 1.")

        if not 0.0 <= default_symbols_distance <= 1.0:
            raise ValueError("expect float value between .0 and 1.")

        if not all(
            [
                (0.0 <= prob <= 1.0) and isinstance(c, str) and len(c) == 1
                for c, prob in (symbol_probability or dict()).items()
            ]
        ):
            raise ValueError(
                "expect probability float value between .0 and 1. " "and char key value"
            )

        if not all(
            [
                (0.0 <= dist <= 1.0)
                and isinstance(x, str)
                and len(x) == 1
                and isinstance(y, str)
                and len(y) == 1
                for (x, y), dist in (symbols_distance or dict()).items()
            ]
        ):
            raise ValueError(
                "expect probability float value between .0 and 1. " "and char key value"
            )

        self.__default_symbol_probability = default_symbol_probability
        self.__default_symbols_distance = default_symbols_distance

        self.__symbol_probability = {
            c: prob for c, prob in (symbol_probability or dict()).items()
        }

        self.__symbols_distance = {
            (x, y): dist for (x, y), dist in (symbols_distance or dict()).items()
        }
        for (x, y) in (symbols_distance or dict()).keys():
            if self.__symbols_distance.get((y, x)) is None:
                self.__symbols_distance[(y, x)] = self.__symbols_distance[(x, y)]

    def set_max_corrections_value(self, max_corrections_value: float):
        """
        Sets max corrections value

        ::Parameters::

        :param float max_corrections_value: max relative number of corrections in
               the query to find the matching key; default = 1.

        ::Example::

        >>> from fuzzy_multi_dict import fuzzy_multi_dict
        >>> d = FuzzyMultiDict(max_corrections_value=1/3)
        >>> d.set_max_corrections_value(.5)
        >>> d.max_corrections_value
        ... # .5

        """
        if not 0 <= max_corrections_value <= 1:
            raise ValueError("expect float between .0 and 1.")

        self.__max_corrections_value = max_corrections_value

    def save(self, filename: str):
        """
        Saves prefix tree data to binary file

        ::Parameters::

        :param str filename: filename to save prefix tree data

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict(
        ...    max_corrections_value=2/3,
        ...    correction_price=CorrectionPrice(1., 1., 1., 1.),
        ...    symbol_probability={'a': 1., 'c': .5},
        ...    default_symbol_probability=.1,
        ...    symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
        ...    default_symbols_distance=1.)

        >>> d["first"] = 1
        >>> d["second"] = 2
        >>> d["third"] = 3
        >>> d.save('dict.bin')

        """
        with open(filename, "wb") as f:
            pickle.dump(
                file=f,
                obj={
                    "prefix_tree": self.__prefix_tree,
                    "update_value": self.__update_value,
                    "max_corrections_value": self.__max_corrections_value,
                    "correction_price": self.__correction_price,
                    "symbol_probability": self.__symbol_probability,
                    "default_symbol_probability": self.__default_symbol_probability,
                    "symbols_distance": self.__symbols_distance,
                    "default_symbols_distance": self.__default_symbols_distance,
                },
                recurse=True,
            )

    def load(self, filename: str):
        """
        Loads prefix tree data from binary file

        ::Parameters::

        :param str filename: filename to load prefix tree data

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict()
        >>> d.load('dict.bin')

        """
        with open(filename, "rb") as f:

            obj = pickle.load(file=f)  # type: Dict[str, Any]

            self.__prefix_tree = obj["prefix_tree"]
            self.__update_value = obj["update_value"]  # type: ignore
            self.__max_corrections_value = obj["max_corrections_value"]
            self.__correction_price = obj["correction_price"]
            self.__symbol_probability = obj["symbol_probability"]
            self.__default_symbol_probability = obj["default_symbol_probability"]
            self.__symbols_distance = obj["symbols_distance"]
            self.__default_symbols_distance = obj["default_symbols_distance"]

    def __setitem__(self, key: str, value: Any):
        """
        Storing the `value` with the `key`

        ::Parameters::

        :param key: input key
        :param value: input value

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict(max_corrections_value=1.)
        >>> d["first"] = 1

        """
        if not isinstance(key, str):
            raise TypeError(f"Invalid key type: expect str, got {type(key)}")

        __node = self.__prefix_tree

        for i, c in enumerate(key):
            if __node["children"].get(c) is None:
                __node["children"][c] = {"children": dict(), "value": None}
            __node = __node["children"][c]

        __node["value"] = self.__update_value(__node["value"], value)  # noqa

    def get(self, query: str, topn: Optional[int] = None) -> List[Dict[Any, Any]]:
        """
        Extracting the value given the `query`

        ::Parameters::

        :param query: query to search for dictionary key
        :param int topn: only topn results will be returned

        :return List[Dict[Any, Any]]:
            [
                {
                    "value": <dictionary value>,
                    "key": <dictionary key; may differ from the query key>,
                    "correction": [
                        {
                            'correction': <correction type, str>,
                            'score': <correction score>,
                            'position': <position in query>
                        },
                        ...
                    ],
                    "leaves": <empty list>
                },
                ...
            ]

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict(max_corrections_value=1.)
        >>> d["first"] = 1
        >>> d["second"] = 2
        >>> d["third"] = 3

        >>> d.get("frst")
        ... # [{
        ... #    'value': 1, 'key': 'first',
        ... #    'correction': [{'correction': 'insertion of "i"',
        ... #                    'score': 0.9999949999875, 'position': 1}],
        ... #    'leaves': []}]

        >>> d.get('fird')
        ... # [{
        ... #    'value': 1, 'key': 'first',
        ... #    'correction': [{'correction': 'insertion of "s"',
        ... #                    'score': 0.9999949999875, 'position': 3},
        ... #                   {'correction': 'substitution "d" for "t"',
        ... #                    'score': 1.0, 'position': 3}],
        ... #     'leaves': []},
        ... #    {'value': 3, 'key': 'third',
        ... #     'correction': [{'correction': 'insertion of "t"',
        ... #                     'score': 0.9999949999875, 'position': 0},
        ... #                    {'correction': 'substitution "f" for "h"',
        ... #                     'score': 1.0, 'position': 0}],
        ... #     'leaves': []}]

        """
        return self.__get(query=query, topn=topn, topn_leaves=None)

    def search(self, query: str, topn: int = 10) -> List[Any]:
        """
        Searching the values starts as given the `query`

        ::Parameters::

        :param query: query to search
        :param topn: only to n search results will be returned

        :return List[Any]: list of values in format
            [
                {
                    "value": <dictionary value>,
                    "key": <dictionary key; may differ from the query key>
                    "correction": [
                        {
                            'correction': <correction type, str>,
                            'score': <correction score>,
                            'position': <position in query>
                        },
                        ...
                    ],
                    "is_leaf": <True if result found in leaves>
                },
                ...
            ]

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict(max_corrections_value=2/3)
        >>> d["apple"] = "apple"
        >>> d["apple red delicious"] = "apple red delicious"
        >>> d["apple fuji"] = "apple fuji"
        >>> d["apple granny smith"] = "apple granny smith"
        >>> d["apple honeycrisp"] = "apple honeycrisp"
        >>> d["apple golden delicious"] = "apple golden delicious"
        >>> d["apple pink lady"] = "apple pink lady"

        >>> d.search("apl")
        ... # [{
        ... #    'value': 'apple',
        ... #    'key': 'apple',
        ... #    'correction': [{'correction': 'insertion of "p"',
        ... #                    'score': 0.9999949999875, 'position': 2}
        ... #      ],
        ... #     'is_leaf': True},
        ... #  {
        ... #    'value': 'apple fuji',
        ... #    'key': 'apple fuji',
        ... #    'correction': [{'correction': 'insertion of "p"',
        ... #                    'score': 0.9999949999875, 'position': 2}],
        ... #    'is_leaf': True},
        ... #  ...
        ... # ]

        """
        __result = self.__get(query=query, topn=topn, topn_leaves=topn)

        top = list()
        __processed_keys = dict()  # type: Dict[Any, Any]

        for item in __result:

            if item.get("value") is None or __processed_keys.get(item["key"]):
                continue

            top.append(
                {
                    "value": item["value"],
                    "key": item["key"],
                    "correction": item["correction"],
                    "is_leaf": False,
                }
            )
            __processed_keys[item["key"]] = True

            if len(top) >= topn:
                return top

        for item in __result:

            if not item.get("leaves"):
                continue

            for leaf_item in item["leaves"]:

                if __processed_keys.get(leaf_item["key"]):
                    continue

                top.append(
                    {
                        "value": leaf_item["value"],
                        "key": leaf_item["key"],
                        "correction": item["correction"],
                        "is_leaf": True,
                    }
                )
                __processed_keys[leaf_item["key"]] = True

                if len(top) >= topn:
                    return top

        return top

    def __get(  # noqa
        self, query: str, topn: Optional[int] = None, topn_leaves: Optional[int] = None
    ) -> List[Dict[Any, Any]]:
        """
        Extracting the value and search result given the `query`

        ::Parameters::

        :param query: query to search for dictionary key
        :param int topn: only topn results will be returned
        :param Optional[int] topn_leaves: only topn leaves from found will
               be returned; used for searching

        :return List[Dict[Any, Any]]:
            [
                {
                    "value": <dictionary value>,
                    "key": <dictionary key; may differ from the query key>
                    "correction": <list of correction in the query key>
                    "leaves": <list of result nodes leaves values>
                },
                ...
            ]

        """
        node, position = self.__apply_string(
            node=self.__prefix_tree, s=query, position=0
        )

        result = dict()  # type: Dict[Any, Any]
        if position == len(query) and (node.get("value") is not None or topn_leaves):

            result = {
                query: {
                    "value": None,
                    "key": query,
                    "correction": list(),
                    "leaves": list(),
                }
            }

            if node.get("value"):
                result[query]["value"] = node["value"]

            if topn_leaves:
                result[query]["leaves"] = self.__get_node_leaves(
                    node=node, path=query, topn=topn_leaves
                )

            return self.__prepare_result(
                result=result, topn=topn, topn_leaves=topn_leaves
            )

        rows_to_process = [
            (position, query[:position], node, list()),
            (0, "", self.__prefix_tree, list()),
        ]  # type: List[Tuple[int, str, Dict[Any,Any], List[Any]]]
        processed = {(pos, path): 0 for (pos, path, _, __) in rows_to_process}

        while True:

            rows_to_process__ = list()

            for (position, path, node, correction) in rows_to_process:

                res_row__ = self.__check_value(
                    node=node,
                    path=path,
                    query=query,
                    position=position,
                    correction=correction,
                    result=result,
                    topn_leaves=topn_leaves,
                )

                if res_row__:
                    result[path] = res_row__

                rows_to_process__.extend(
                    self.__apply_as_is(
                        node, path, query, position, processed, correction
                    )
                )

                current_corrections_rel = (len(correction) + 1) / len(query)

                if current_corrections_rel <= self.__max_corrections_value:
                    if (topn_leaves and position < len(query)) or topn_leaves is None:
                        rows_to_process__.extend(
                            self.__apply_insertion(
                                node=node,
                                path=path,
                                query=query,
                                position=position,
                                processed=processed,
                                correction=correction,
                            )
                        )

                if (
                    position < len(query)
                    and current_corrections_rel <= self.__max_corrections_value
                ):
                    rows_to_process__.extend(
                        self.__apply_substitution(
                            node=node,
                            path=path,
                            query=query,
                            position=position,
                            processed=processed,
                            correction=correction,
                        )
                    )

                    rows_to_process__.extend(
                        self.__apply_deletion(
                            node=node,
                            path=path,
                            query=query,
                            position=position,
                            processed=processed,
                            correction=correction,
                        )
                    )

                if (
                    position + 1 < len(query)
                    and query[position] != query[position + 1]
                    and current_corrections_rel <= self.__max_corrections_value
                ):
                    rows_to_process__.extend(
                        self.__apply_transposition(
                            node=node,
                            path=path,
                            query=query,
                            position=position,
                            processed=processed,
                            correction=correction,
                        )
                    )

            if not len(rows_to_process__):
                break

            rows_to_process = rows_to_process__

        return self.__prepare_result(result=result, topn=topn, topn_leaves=topn_leaves)

    def __getitem__(self, query: str) -> Dict[str, Any]:
        """
        Extracting the value given the `query`

        ::Parameters::

        :param query: query to search for dictionary key
        :return Any: first found by `query` dictionary value

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict(max_corrections_value=1.)
        >>> d["first"] = 1
        >>> d["second"] = 2
        >>> d["third"] = 3

        >>> d["first"]
        ... # 1
        >>> d["frst"]
        ... # 1
        >>> d["forst"]
        ... # 1
        >>> d["fiirst"]
        ... # 1
        >>> d["frsd"]
        ... # 1
        >>> d["tirsf"]
        ... # 1
        >>> d["rsd"]
        ... # 1

        """
        if not isinstance(query, str):
            raise TypeError(f"Invalid key type: expect str; got {type(query)}")

        value = self.get(query)

        if len(value):
            return value[0]["value"]

        raise KeyError(query)

    @staticmethod
    def __apply_string(node: dict, s: str, position: int) -> Tuple[Dict[Any, Any], int]:

        sub_position = 0

        for c in s[position:]:

            __node = node["children"].get(c)
            if not __node:
                return node, position + sub_position

            node = __node
            sub_position += 1

        return node, position + sub_position

    def __apply_as_is(
        self,
        node: dict,
        path: str,
        key: str,
        position: int,
        processed: dict,
        correction: list,
    ) -> list:

        __node_children = node["children"].keys()
        __has_children = len(__node_children) > 0

        rows_to_process__ = list()

        if position + 1 < len(key) and __has_children:
            __node = node["children"].get(key[position])
            if __node:
                __path = path + key[position]
                __processed = processed.get((position + 1, __path))
                if __processed is None or __processed > len(correction):
                    rows_to_process__.append((position + 1, __path, __node, correction))
                    processed[(position + 1, __path)] = len(correction)

                __node, __position = self.__apply_string(
                    node=node, s=key, position=position
                )
                __path = path + key[position:__position]
                __processed = processed.get((__position, __path))
                if __processed is None or __processed > len(correction):
                    rows_to_process__.append((__position, __path, __node, correction))
                    processed[(__position, __path)] = len(correction)

        return rows_to_process__

    def __apply_transposition(
        self,
        node: dict,
        path: str,
        query: str,
        position: int,
        processed: dict,
        correction: list,
    ) -> list:

        rows_to_process__: List[tuple] = list()

        if position + 1 >= len(query):
            return rows_to_process__

        if (
            query[position + 1] in node["children"].keys()
            and query[position]
            in node["children"][query[position + 1]]["children"].keys()
        ):
            __node = node["children"][query[position + 1]]["children"][query[position]]
            __path = path + query[position + 1] + query[position]
            __processed = processed.get((position + 2, __path))
            __score = (
                self.__correction_price.transposition
                * self.get_symbols_distance(query[position], query[position + 1])
            ) ** 0.5

            __correction = correction + [
                {
                    "correction": f"transposition of symbols "
                    f'"{query[position: position + 2]}"',
                    "score": __score,
                    "position": position,
                },
            ]

            if __processed is None or __processed > len(__correction):
                rows_to_process__.append((position + 2, __path, __node, __correction))
                processed[(position + 2, __path)] = len(__correction)

            __node, __position = self.__apply_string(
                node=__node, s=query, position=position + 2
            )
            __path = (
                path
                + path
                + query[position + 1]
                + query[position]
                + query[position + 2 : __position]
            )
            __processed = processed.get((__position, __path))
            if __processed is None or __processed > len(__correction):
                rows_to_process__.append((__position, __path, __node, __correction))
                processed[(__position, __path)] = len(__correction)

        return rows_to_process__

    def __apply_insertion(
        self,
        node: dict,
        path: str,
        query: str,
        position: int,
        processed: dict,
        correction: list,
    ) -> list:

        rows_to_process__: List[Tuple[int, str, dict, list]] = list()

        __node_children = node["children"].keys()
        __has_children = len(__node_children) > 0

        if __has_children:
            __node_children = sorted(
                __node_children,
                key=lambda x: -self.__symbol_probability.get(
                    x, self.__default_symbol_probability
                ),
            )

        if not __has_children:
            return rows_to_process__

        for __c in __node_children:
            __node = node["children"][__c]
            __path = path + __c
            __score = (
                self.__correction_price.insertion
                * (
                    1
                    - self.__symbol_probability.get(
                        __c, self.__default_symbol_probability
                    )
                )
            ) ** 0.5
            __correction = correction + [
                {
                    "correction": f'insertion of "{__c}"',
                    "score": __score,
                    "position": position,
                },
            ]
            __processed = processed.get((position, __path))
            if __processed is None or __processed > len(__correction):
                rows_to_process__.append((position, __path, __node, __correction))
                processed[(position, __path)] = len(__correction)

            __node, __position = self.__apply_string(
                node=__node, s=query, position=position
            )
            __path = path + __c + query[position:__position]
            __processed = processed.get((__position, __path))
            if __processed is None or __processed > len(__correction):
                rows_to_process__.append((__position, __path, __node, __correction))
                processed[(__position, __path)] = len(__correction)

        return rows_to_process__

    def __apply_deletion(
        self,
        node: dict,
        path: str,
        query: str,
        position: int,
        processed: dict,
        correction: list,
    ) -> list:

        rows_to_process__ = list()
        __score = (
            self.__correction_price.deletion
            * (
                1
                - self.__symbol_probability.get(
                    query[position], self.__default_symbol_probability
                )
            )
        ) ** 0.5
        __correction = correction + [
            {
                "correction": f'deletion of "{query[position]}"',
                "score": __score,
                "position": position,
            },
        ]

        __processed = processed.get((position + 1, path))
        if __processed is None or __processed > len(__correction):
            rows_to_process__.append((position + 1, path, node, __correction))
            processed[(position + 1, path)] = len(__correction)

        __node, __position = self.__apply_string(
            node=node, s=query, position=position + 1
        )
        __path = path + query[position + 1 : __position]

        __processed = processed.get((__position, __path))
        if __processed is None or __processed > len(__correction):
            rows_to_process__.append((__position, __path, __node, __correction))
            processed[(__position, __path)] = len(__correction)
        return rows_to_process__

    def __apply_substitution(
        self,
        node: dict,
        path: str,
        query: str,
        position: int,
        processed: dict,
        correction: list,
    ) -> list:

        rows_to_process__ = list()

        __node_children = node["children"].keys()

        if len(__node_children) > 0:
            __node_children = sorted(
                sorted(__node_children),
                key=lambda x: self.get_symbols_distance(x, query[position]),
            )

        for __c in __node_children:
            if __c == query[position]:
                continue

            __score = (
                self.__correction_price.substitution
                * self.get_symbols_distance(query[position], __c)
            ) ** 0.5
            __correction = correction + [
                {
                    "correction": f'substitution "{query[position]}" for "{__c}"',
                    "score": __score,
                    "position": position,
                },
            ]
            __node = node["children"][__c]
            __path = path + __c

            __processed = processed.get((position + 1, __path))
            if __processed is None or __processed > len(__correction):
                rows_to_process__.append((position + 1, __path, __node, __correction))
                processed[(position + 1, __path)] = len(__correction)

            __node, __position = self.__apply_string(
                node=__node, s=query, position=position + 1
            )
            __path = path + __c + query[position + 1 : __position]

            __processed = processed.get((__position, __path))
            if __processed is None or __processed > len(__correction):
                rows_to_process__.append((__position, __path, __node, __correction))
                processed[(__position, __path)] = len(__correction)

        return rows_to_process__

    def __prepare_result(
        self, result: dict, topn: Optional[int], topn_leaves: Optional[int]
    ) -> list:

        if not topn_leaves:
            result = {k: v for k, v in result.items() if v["value"] is not None}

        if not len(result):
            return list()

        prepeared_result = sorted(
            result.values(),
            key=lambda x: self.__get_total_corrections_score(x["correction"]),
        )

        if topn:
            prepeared_result = prepeared_result[:topn]

        return prepeared_result

    def __check_value(
        self,
        node: dict,
        path: str,
        query: str,
        position: int,
        correction: list,
        result: dict,
        topn_leaves: Optional[int],
    ) -> Optional[dict]:

        if position != len(query):
            return None

        result_value = {
            "value": None,
            "key": path,
            "correction": correction,
            "leaves": list(),
        }  # type: Dict[str, Any]

        if node.get("value") is not None:
            __result_row = result.get(path)
            if __result_row is None or len(__result_row["correction"]) > len(
                correction
            ):
                result_value["value"] = node["value"]
                result_value["correction"] = correction

        if topn_leaves:
            result_value["leaves"] = self.__get_node_leaves(node, path, topn_leaves)

        return result_value

    def __get_node_leaves(
        self, node: dict, path: str = "", topn: Optional[int] = 10
    ) -> List[Dict[str, Any]]:
        """
        Returns top node leaves

        :param dict node: current position in prefix tree
        :param str path: path to node
        :param int topn: only topn leaves will be returned

        :return List[Dict[str, Any]]: list of leaves in format:
                [
                    {
                        'key': <search key>,
                        'value': <leaf value>
                    },
                    ...
                ]

        """
        leaves = list()  # type: List[Any]

        if topn <= 0:
            return leaves

        for x in sorted(node["children"].keys()):
            __node, __path, __value = node["children"][x], x, None

            while True:

                __value = __node.get("value")

                if __value is not None:

                    leaves.append({"key": path + __path, "value": __node["value"]})

                    topn -= 1
                    if topn <= 0:
                        return leaves

                    break

                if len(__node["children"]) != 1:
                    break

                __x, __node = list(__node["children"].items())[0]
                __path += __x

            leaves.extend(self.__get_node_leaves(__node, path + __path, topn))

        return leaves

    @staticmethod
    def __get_total_corrections_score(corrections: List[Dict[str, Any]]) -> float:
        """
        Returns sum of corrections prices

        ::Parameters::

        :param corrections: list of corrections in query
        :return float: sum of corrections prices

        """
        return sum([_["score"] for _ in corrections])

    @property
    def correction_price(self) -> CorrectionPrice:
        """
        Returns corretions prices

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict()
        >>> d.correction_price
        ... # CorrectionScore(
        ... #    transposition=0.1, deletion=0.2, substitution=0.3, insertion=0.1)

        """
        return self.__correction_price

    @property
    def max_corrections_value(self) -> float:
        """
        Returns max correction value

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict(max_corrections_value=.1)
        >>> d.max_corrections_value
        ... # .1

        """
        return self.__max_corrections_value

    @property
    def default_symbols_distance(self) -> float:
        """
        Returns default symbols distance

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict(
        ... symbols_distance={('а', 'b'): .5, ('b', 'c'): .1},
        ... default_symbols_distance=1.)
        >>> d.default_symbols_distance
        ... # 1.

        """
        return self.__default_symbols_distance

    @property
    def default_symbol_probability(self):
        """
        Returns default symbol probability

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict(
        ... symbol_probability={'a': 1., 'b': .5},
        ... default_symbol_probability=.1)
        >>> d.default_symbol_probability
        ... # .1

        """
        return self.__default_symbol_probability

    def get_symbols_distance(self, x: str, y: str) -> float:
        """
        Returns distance between symbols `x` and `y`

        ::Parameters::

        :param str x: first char
        :param str y: second char

        :return float: distance between symbols `x` and `y` (between 0. and 1.)

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict()
        >>> d.set_symbols_probability_distances(
        ... symbol_probability={'a': 1., 'b': .5},
        ... default_symbol_probability=.1,
        ... symbols_distance={('а', 'b'): .5, ('b', 'c'): .1},
        ... default_symbols_distance=1.)

        >>> d.get_symbols_distance('а', 'b')
        ... # .5
        >>> d.get_symbols_distance('b', 'a')
        ... # .5
        >>> d.get_symbols_distance('c', 'd')
        ... # 1.
        >>> d.get_symbols_distance('c', 'с')
        ... # .0

        """
        if x == y:
            return 0.0

        return self.__symbols_distance.get((x, y), self.__default_symbols_distance)

    def get_symbol_probability(self, c: str):
        """
        Returns symbol probability

        ::Parameters::

        :param str c: input char
        :return float: symbol `c` probability

        ::Example::

        >>> from fuzzy_multi_dict import FuzzyMultiDict
        >>> d = FuzzyMultiDict()
        >>> d.set_symbols_probability_distances(
        ... symbol_probability={'a': 1., 'b': .5},
        ... default_symbol_probability=.1,
        ... symbols_distance={('a', 'b'): .5, ('b', 'c'): .1},
        ... default_symbols_distance=1.)

        >>> d.get_symbol_probability('b')
        ... # .5
        >>> d.get_symbol_probability('e')
        ... # .1

        """
        return self.__symbol_probability.get(c, self.__default_symbol_probability)
