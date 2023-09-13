import pickle
from typing import Any, Callable, Dict, List, Optional, Tuple


class FuzzyMultiDict:
    def __init__(
        self,
        max_corrections: Optional[int] = 2,
        max_corrections_relative: Optional[float] = None,
        update_value_func: Optional[Callable] = None,
        sort_key: Optional[Callable] = None,
    ):
        """
        :param int max_corrections: default value of maximum number of corrections
               in the query key when searching for a matching dictionary key;
               default = 2
        :param Optional[float] max_corrections_relative: default value to calculate
               maximum number of corrections in the query key when searching
               for a matching dictionary key; default = None
               calculated as round(max_corrections_relative * token_length)
        :param Optional[Callable] update_value_func: merge function for value
               when storing a new value with a key; default = None
        :param Optional[Callable] sort_key: key for sorting values founded by query;
               default = None

        """
        self.__prefix_tree = {
            "parent": "ROOT",
            "children": dict(),
            "data": None,
        }
        self.__max_corrections = max_corrections
        self.__max_corrections_relative = max_corrections_relative
        self.__update_value = (
            (lambda x, y: y) if update_value_func is None else update_value_func
        )
        self.__sort_key = (
            lambda x: len(x["correction"]) if sort_key is None else sort_key
        )

    def save(self, filename: str):
        with open(filename, "wb") as f:
            pickle.dump(file=f, obj=self.__prefix_tree)

    def load(self, filename: str):
        with open(filename, "rb") as f:
            self.__prefix_tree = pickle.load(file=f)

    def __setitem__(self, key: str, value: Any):
        """
        Storing the `value` with the `key`

        """
        if not isinstance(key, str):
            raise TypeError(f"Invalid key type: expect str, got {type(key)}")

        __node = self.__prefix_tree
        for i, c in enumerate(key):
            if __node["children"].get(c) is None:  # type: ignore
                __node["children"][c] = {  # type: ignore
                    "parent": __node,
                    "children": dict(),
                    "data": None,
                }
            __node = __node["children"][c]  # type: ignore

        __node["value"] = self.__update_value(
            __node.get("value"), value
        )  # type: ignore  # noqa

    def __get(
        self,
        query: str,
        max_corrections: Optional[int] = None,
        max_corrections_relative: Optional[float] = None,
        extract_all: bool = False,
        extract_leaves: bool = False,
    ) -> List[Dict[Any, Any]]:
        """
        Extracting the value and search result given the `query`

        :param query: query to search for dictionary key
        :param int max_corrections: maximum number of corrections in the query key
               when searching for a matching dictionary key
        :param max_corrections_relative: value to calculate maximum number
               of corrections in the query key when searching for a matching
               dictionary key;  if not None - `max_corrections` will be ignored;
               calculated as round(max_corrections_relative * token_length);
        :param bool extract_all: if True - all existing keys that can be obtained
               from the request by fixing no more than `max_corrections` correction
               will be returned
        :param bool extract_leaves: if True - all node leaves from found will
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
        max_corrections = self.__get_max_corrections(
            len(query), max_corrections, max_corrections_relative
        )

        node, position = self.__apply_string(
            node=self.__prefix_tree, s=query, position=0
        )

        result = dict()  # type: Dict[Any, Any]
        if position == len(query) and node.get("value") is not None:
            result = {
                query: {
                    "value": node["value"],
                    "key": query,
                    "correction": list(),
                    "leaves": list(),
                }
            }
            if extract_leaves:
                result[query]["leaves"] = self.__get_node_leaves(node, query)

            if not extract_all:
                return self.__prepare_result(
                    result=result,
                    extract_all=extract_all,
                    extract_leaves=extract_leaves,
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
                    node,
                    path,
                    query,
                    position,
                    correction,
                    result,
                    extract_all,
                    extract_leaves,
                )
                if res_row__:
                    result[path] = res_row__
                    if (
                        res_row__["value"] is not None
                        and len(correction) < max_corrections
                        and not extract_all
                    ):
                        max_corrections = len(correction)
                        continue

                rows_to_process__.extend(
                    self.__apply_as_is(
                        node, path, query, position, processed, correction
                    )
                )

                if len(correction) >= max_corrections:
                    continue

                rows_to_process__.extend(
                    self.__apply_insertion(
                        node, path, query, position, processed, correction
                    )
                )

                if position < len(query):
                    rows_to_process__.extend(
                        self.__apply_deletion(
                            node, path, query, position, processed, correction
                        )
                    )
                    rows_to_process__.extend(
                        self.__apply_substitution(
                            node, path, query, position, processed, correction
                        )
                    )

                if position + 1 < len(query):
                    rows_to_process__.extend(
                        self.__apply_transposition(
                            node, path, query, position, processed, correction
                        )
                    )

            if not len(rows_to_process__):
                break

            rows_to_process = rows_to_process__

        return self.__prepare_result(
            result=result, extract_all=extract_all, extract_leaves=extract_leaves
        )

    def get(
        self,
        query: str,
        max_corrections: Optional[int] = None,
        max_corrections_relative: Optional[float] = None,
        extract_all: bool = False,
    ) -> List[Dict[Any, Any]]:
        """
        Extracting the value given the `query`

        :param query: query to search for dictionary key
        :param int max_corrections: maximum number of corrections in the query key
               when searching for a matching dictionary key
        :param max_corrections_relative: value to calculate maximum number
               of corrections in the query key when searching for a matching
               dictionary key;  if not None - `max_corrections` will be ignored;
               calculated as round(max_corrections_relative * token_length);
        :param bool extract_all: if True - all existing keys that can be obtained
               from the request by fixing no more than `max_corrections` correction
               will be returned

        :return List[Dict[Any, Any]]:
            [
                {
                    "value": <dictionary value>,
                    "key": <dictionary key; may differ from the query key>
                    "correction": <list of correction in the query key>
                },
                ...
            ]

        """
        return self.__get(
            query=query,
            max_corrections=max_corrections,
            max_corrections_relative=max_corrections_relative,
            extract_all=extract_all,
            extract_leaves=False,
        )

    def search(self, query: str, topn: int = 10) -> List[Any]:
        """
        Searching the values starts as given the `query`

        :param query: query to search
        :param topn: only to n search results will be returned

        :return List[Any]: list of values

        """
        __result = self.__get(
            query=query,
            max_corrections_relative=1.0,
            extract_all=True,
            extract_leaves=True,
        )

        top = list()
        __processed = dict()  # type: Dict[Any, Any]
        for v in __result:
            if v.get('value') and not __processed.get(v['value']):
                top.append({'value': v['value'], 'key': v['key'], "correction": v["correction"], "is_leaf": False})
                __processed[v['value']] = True
                if len(top) >= topn:
                    return top
        for v in __result:
            if v["leaves"]:
                for k, x in v["leaves"]:
                    if not __processed.get(x):
                        top.append({'value': x, 'key': v['key'], "correction": v["correction"], "is_leaf": True})
                        __processed[x] = True
                        if len(top) >= topn:
                            return top

        return top

    def __getitem__(self, query: str) -> Dict[str, Any]:
        """
        Extracting the value given the `query`

        :param query: query to search for dictionary key
        :return Any: first found by `query` dictionary value

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
            __correction = correction + [
                {
                    "correction": f"transposition of symbols "
                    f'"{query[position: position + 2]}"',
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

        if not __has_children:
            return rows_to_process__

        for __c in __node_children:
            __node = node["children"][__c]
            __path = path + __c
            __correction = correction + [
                {
                    "correction": f'insertion of "{__c}"',
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
        __correction = correction + [
            {
                "correction": f'deletion of "{query[position]}"',
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

        for __c in __node_children:
            if __c == query[position]:
                continue
            __correction = correction + [
                {
                    "correction": f'substitution "{query[position]}" for "{__c}"',
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
        self, result: dict, extract_all: bool, extract_leaves: bool
    ) -> list:

        if not extract_leaves:
            result = {k: v for k, v in result.items() if v["value"] is not None}

        if not len(result):
            return list()

        if extract_all:
            return sorted(result.values(), key=self.__sort_key)  # type: ignore

        __min_n_correction = min([len(x["correction"]) for x in result.values()])

        return sorted(
            [x for x in result.values() if len(x["correction"]) == __min_n_correction],
            key=self.__sort_key,  # type: ignore
        )

    def __check_value(
        self,
        node: dict,
        path: str,
        query: str,
        position: int,
        correction: list,
        result: dict,
        extract_all: bool,
        extract_leaves: bool,
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
            if (
                __result_row is None
                or extract_all
                or len(__result_row["correction"]) > len(correction)
            ):
                result_value["value"] = node["value"]
                result_value["correction"] = correction

        if extract_leaves:
            result_value["leaves"] = self.__get_node_leaves(node, path)

        return result_value

    def __get_max_corrections(
        self,
        n: int,
        max_corrections: Optional[int],
        max_corrections_relative: Optional[float],
    ) -> int:
        if max_corrections_relative is not None:
            return round(max_corrections_relative * n)
        if max_corrections is not None:
            return max_corrections
        if self.__max_corrections_relative is not None:
            return round(self.__max_corrections_relative * n)
        if self.__max_corrections is not None:
            return self.__max_corrections
        return 0

    def __get_node_leaves(self, node: dict, path: str = "") -> List[Any]:

        leaves = list()
        for x, __node in node["children"].items():

            if __node.get("value"):
                leaves.append((path + x, __node["value"]))
            leaves.extend(self.__get_node_leaves(__node, path + x))

        return leaves
