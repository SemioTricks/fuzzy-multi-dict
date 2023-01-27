from typing import Any, Callable, Dict, List, Optional, Tuple


class FuzzyMultiDict:
    def __init__(
        self, max_mistakes_number: int = 2, update_value_func: Optional[Callable] = None
    ):
        """
        :param max_mistakes_number: the maximum number of mistakes in the key
        :param update_value_func: value merge function when writing a new value by key

        """
        self.__prefix_tree = {
            "parent": "ROOT",
            "children": dict(),
            "data": None,
            "path": "",
        }
        self.__max_mistakes_number = max_mistakes_number
        self.__update_value = (
            (lambda x, y: y) if update_value_func is None else update_value_func
        )

    def __setitem__(self, key: str, value: Any):

        if not isinstance(key, str):
            raise TypeError(f"Invalid key type: expect str, got {type(key)}")

        __node = self.__prefix_tree
        for i, c in enumerate(key):
            if __node["children"].get(c) is None:  # type: ignore
                __node["children"][c] = {  # type: ignore
                    "parent": __node,
                    "children": dict(),
                    "data": None,
                    "path": key[: i + 1],
                }
            __node = __node["children"][c]  # type: ignore

        __node["value"] = self.__update_value(__node.get("value"), value)  # type: ignore  # noqa

    def get(self, key: str) -> List[Dict[Any, Any]]:

        max_mistakes_number = self.__max_mistakes_number

        node, position = self.__apply_string(node=self.__prefix_tree, s=key, position=0)
        if position == len(key) and node.get("value") is not None:
            return [
                {"value": node["value"], "key": key, "mistakes": list()},
            ]

        result = dict()  # type: Dict[Any, Any]
        rows_to_process = [
            (position, node, list()),
            (0, self.__prefix_tree, list()),
        ]  # type: List[Tuple[int, Dict[Any,Any], List[Any]]]
        processed = {(pos, node["path"]): 0 for (pos, node, _) in rows_to_process}

        while True:
            rows_to_process__ = list()
            for (position, node, mistakes) in rows_to_process:
                processed[(position, node["path"])] = len(mistakes)

                res_row__ = self.__check_value(node, key, position, mistakes, result)
                if res_row__:
                    result[node["path"]] = res_row__
                    if len(mistakes) < max_mistakes_number:
                        max_mistakes_number = len(mistakes)
                    continue

                rows_to_process__.extend(
                    self.__no_mistakes(node, key, position, processed, mistakes)
                )

                if len(mistakes) >= max_mistakes_number:
                    continue

                rows_to_process__.extend(
                    self.__missing_symbol(node, key, position, processed, mistakes)
                )

                if position < len(key):
                    rows_to_process__.extend(
                        self.__extra_symbol(node, key, position, processed, mistakes)
                    )
                    rows_to_process__.extend(
                        self.__wrong_symbol(node, key, position, processed, mistakes)
                    )

            if not len(rows_to_process__):
                break

            rows_to_process = rows_to_process__

        return self.__prepare_result(result)

    def __getitem__(self, key: str) -> Dict[str, Any]:

        if not isinstance(key, str):
            raise TypeError(f"Invalid key type: expect str; got {type(key)}")

        value = self.get(key)

        if len(value):
            return value[0]["value"]

        raise KeyError(key)

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

    def __no_mistakes(self, node, key, position, processed, mistakes) -> list:

        __node_children = node["children"].keys()
        __has_children = len(__node_children) > 0

        rows_to_process__ = list()

        if position + 1 < len(key) and __has_children:
            __node = node["children"].get(key[position])
            if __node:
                __processed = processed.get((position + 1, __node["path"]))
                if __processed is None or __processed > len(mistakes):
                    rows_to_process__.append((position + 1, __node, mistakes))
                    processed[(position + 1, __node["path"])] = len(mistakes)

                    __node, __position = self.__apply_string(
                        node=node, s=key, position=position
                    )
                    __processed = processed.get((__position, __node["path"]))
                    if __processed is None or __processed > len(mistakes):
                        rows_to_process__.append((__position, __node, mistakes))
                        processed[(__position, __node["path"])] = len(mistakes)

        return rows_to_process__

    def __missing_symbol(self, node, key, position, processed, mistakes) -> list:

        rows_to_process__: List[Tuple[int, dict, list]] = list()

        __node_children = node["children"].keys()
        __has_children = len(__node_children) > 0

        if not __has_children:
            return rows_to_process__

        for __c in __node_children:
            __node = node["children"][__c]
            __mistakes = mistakes + [
                {
                    "mistake_type": f'missing symbol "{__c}"',
                    "position": position,
                },
            ]
            __processed = processed.get((position, __node["path"]))
            if __processed is None or __processed > len(__mistakes):
                rows_to_process__.append((position, __node, __mistakes))
                processed[(position, __node["path"])] = len(__mistakes)

            __node, __position = self.__apply_string(
                node=__node, s=key, position=position
            )
            __processed = processed.get((__position, __node["path"]))
            if __processed is None or __processed > len(__mistakes):
                rows_to_process__.append((__position, __node, __mistakes))
                processed[(__position, __node["path"])] = len(__mistakes)

        return rows_to_process__

    def __extra_symbol(self, node, key, position, processed, mistakes) -> list:
        rows_to_process__ = list()
        __mistakes = mistakes + [
            {
                "mistake_type": f'extra symbol "{key[position]}"',
                "position": position,
            },
        ]

        __processed = processed.get((position + 1, node["path"]))
        if __processed is None or __processed > len(__mistakes):
            rows_to_process__.append((position + 1, node, __mistakes))
            processed[(position + 1, node["path"])] = len(__mistakes)

        __node, __position = self.__apply_string(
            node=node, s=key, position=position + 1
        )
        __processed = processed.get((__position, __node["path"]))
        if __processed is None or __processed > len(__mistakes):
            rows_to_process__.append((__position, __node, __mistakes))
            processed[(__position, __node["path"])] = len(__mistakes)

        return rows_to_process__

    def __wrong_symbol(self, node, key, position, processed, mistakes) -> list:
        rows_to_process__ = list()

        __node_children = node["children"].keys()

        for __c in __node_children:
            __mistakes = mistakes + [
                {
                    "mistake_type": f'wrong symbol "{key[position]}": '
                    f'replaced on "{__c}"',
                    "position": position,
                },
            ]
            __node = node["children"][__c]
            __processed = processed.get((position + 1, __node["path"]))
            if __processed is None or __processed > len(__mistakes):
                rows_to_process__.append((position + 1, __node, __mistakes))
                processed[(position + 1, __node["path"])] = len(__mistakes)

            __node, __position = self.__apply_string(
                node=__node, s=key, position=position + 1
            )
            __processed = processed.get((__position, __node["path"]))
            if __processed is None or __processed > len(__mistakes):
                rows_to_process__.append((__position, __node, __mistakes))
                processed[(__position, __node["path"])] = len(__mistakes)

        return rows_to_process__

    @staticmethod
    def __prepare_result(result: Dict[str, Dict[Any, Any]]) -> List[Dict[Any, Any]]:

        if not len(result):
            return list()

        __min_n_mistakes = min([len(x["mistakes"]) for x in result.values()])
        return [x for x in result.values() if len(x["mistakes"]) == __min_n_mistakes]

    def __check_value(self, node, key, position, mistakes, result) -> Optional[dict]:
        if position == len(key) and node.get("value") is not None:
            __result_row = result.get(node["path"])
            if __result_row is None or len(__result_row["mistakes"] > len(mistakes)):
                return {
                    "value": node["value"],
                    "key": node["path"],
                    "mistakes": mistakes,
                }
        return None
