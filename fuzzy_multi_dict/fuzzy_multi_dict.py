from typing import Any, Callable, Dict, List, Optional, Tuple


class FuzzyMultiDict:
    def __init__(
        self,
        max_mistakes_number: int = 2,
        max_mistakes_number_part: Optional[float] = None,
        update_value_func: Optional[Callable] = None,
    ):
        """
        :param int max_mistakes_number: default value of maximum number of corrections
               in the query key when searching for a matching dictionary key
        :param Optional[float] max_mistakes_number_part: default value to calculate
               maximum number of corrections in the query key when searching
               for a matching dictionary key;
               calculated as round(max_mistakes_number_part * token_length)
        :param update_value_func: merge function for value
               when storing a new value with a key

        """
        self.__prefix_tree = {
            "parent": "ROOT",
            "children": dict(),
            "data": None,
        }
        self.__max_mistakes_number = max_mistakes_number
        self.__max_mistakes_number_part = max_mistakes_number_part
        self.__update_value = (
            (lambda x, y: y) if update_value_func is None else update_value_func
        )

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

        __node["value"] = self.__update_value(__node.get("value"), value)  # type: ignore  # noqa

    def get(
        self,
        key: str,
        max_mistakes_number: Optional[int] = None,
        max_mistakes_number_part: Optional[float] = None,
        extract_all: bool = False,
    ) -> List[Dict[Any, Any]]:
        """
        Extracting the value given the `key`

        :param key: dictionary key
        :param int max_mistakes_number: maximum number of corrections in the query key
               when searching for a matching dictionary key
        :param max_mistakes_number_part: value to calculate maximum number
               of corrections in the query key when searching for a matching
               dictionary key;  if not None - `max_mistakes_number` will be ignored;
               calculated as round(max_mistakes_number_part * token_length);
        :param bool extract_all: if True - all existing keys that can be obtained
               from the request by fixing no more than `max_mistakes_number` mistakes
               will be returned

        :return List[Dict[Any, Any]]:
            [
                {
                    "value": <dictionary value>,
                    "key": <dictionary key; may differ from the query key>
                    "mistakes": <list of correction in the query key>
                },
                ...
            ]

        """
        max_mistakes_number_part = (
            max_mistakes_number_part or self.__max_mistakes_number_part
        )
        if max_mistakes_number_part:
            max_mistakes_number = round(len(key) * max_mistakes_number_part)
        else:
            max_mistakes_number = max_mistakes_number or self.__max_mistakes_number

        node, position = self.__apply_string(node=self.__prefix_tree, s=key, position=0)

        result = dict()  # type: Dict[Any, Any]
        if position == len(key) and node.get("value") is not None:
            result = {key: {"value": node["value"], "key": key, "mistakes": list()}}
            if not extract_all:
                return self.__prepare_result(result, extract_all=extract_all)

        rows_to_process = [
            (position, key[:position], node, list()),
            (0, "", self.__prefix_tree, list()),
        ]  # type: List[Tuple[int, str, Dict[Any,Any], List[Any]]]
        processed = {(pos, path): 0 for (pos, path, _, __) in rows_to_process}

        while True:
            rows_to_process__ = list()
            for (position, path, node, mistakes) in rows_to_process:

                res_row__ = self.__check_value(
                    node, path, key, position, mistakes, result, extract_all
                )
                if res_row__:
                    result[path] = res_row__
                    if len(mistakes) < max_mistakes_number and not extract_all:
                        max_mistakes_number = len(mistakes)
                    continue

                rows_to_process__.extend(
                    self.__no_mistakes(node, path, key, position, processed, mistakes)
                )

                if len(mistakes) >= max_mistakes_number:
                    continue

                rows_to_process__.extend(
                    self.__missing_symbol(
                        node, path, key, position, processed, mistakes
                    )
                )

                if position < len(key):
                    rows_to_process__.extend(
                        self.__extra_symbol(
                            node, path, key, position, processed, mistakes
                        )
                    )
                    rows_to_process__.extend(
                        self.__wrong_symbol(
                            node, path, key, position, processed, mistakes
                        )
                    )

            if not len(rows_to_process__):
                break

            rows_to_process = rows_to_process__

        return self.__prepare_result(result, extract_all=extract_all)

    def __getitem__(self, key: str) -> Dict[str, Any]:
        """
        Extracting the value given the `key`

        :param key: dictionary key
        :return Any: first found dictionary value

        """
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

    def __no_mistakes(
        self,
        node: dict,
        path: str,
        key: str,
        position: int,
        processed: dict,
        mistakes: list,
    ) -> list:
        __node_children = node["children"].keys()
        __has_children = len(__node_children) > 0

        rows_to_process__ = list()

        if position + 1 < len(key) and __has_children:
            __node = node["children"].get(key[position])
            if __node:
                __path = path + key[position]
                __processed = processed.get((position + 1, __path))
                if __processed is None or __processed > len(mistakes):
                    rows_to_process__.append((position + 1, __path, __node, mistakes))
                    processed[(position + 1, __path)] = len(mistakes)

                __node, __position = self.__apply_string(
                    node=node, s=key, position=position
                )
                __path = path + key[position:__position]
                __processed = processed.get((__position, __path))
                if __processed is None or __processed > len(mistakes):
                    rows_to_process__.append((__position, __path, __node, mistakes))
                    processed[(__position, __path)] = len(mistakes)

        return rows_to_process__

    def __missing_symbol(self, node, path, key, position, processed, mistakes) -> list:

        rows_to_process__: List[Tuple[int, str, dict, list]] = list()

        __node_children = node["children"].keys()
        __has_children = len(__node_children) > 0

        if not __has_children:
            return rows_to_process__

        for __c in __node_children:
            __node = node["children"][__c]
            __path = path + __c
            __mistakes = mistakes + [
                {
                    "mistake_type": f'missing symbol "{__c}"',
                    "position": position,
                },
            ]
            __processed = processed.get((position, __path))
            if __processed is None or __processed > len(__mistakes):
                rows_to_process__.append((position, __path, __node, __mistakes))
                processed[(position, __path)] = len(__mistakes)

            __node, __position = self.__apply_string(
                node=__node, s=key, position=position
            )
            __path = path + __c + key[position:__position]
            __processed = processed.get((__position, __path))
            if __processed is None or __processed > len(__mistakes):
                rows_to_process__.append((__position, __path, __node, __mistakes))
                processed[(__position, __path)] = len(__mistakes)

        return rows_to_process__

    def __extra_symbol(self, node, path, key, position, processed, mistakes) -> list:
        rows_to_process__ = list()
        __mistakes = mistakes + [
            {
                "mistake_type": f'extra symbol "{key[position]}"',
                "position": position,
            },
        ]

        __processed = processed.get((position + 1, path))
        if __processed is None or __processed > len(__mistakes):
            rows_to_process__.append((position + 1, path, node, __mistakes))
            processed[(position + 1, path)] = len(__mistakes)

        __node, __position = self.__apply_string(
            node=node, s=key, position=position + 1
        )
        __path = path + key[position + 1 : __position]

        __processed = processed.get((__position, __path))
        if __processed is None or __processed > len(__mistakes):
            rows_to_process__.append((__position, __path, __node, __mistakes))
            processed[(__position, __path)] = len(__mistakes)
        return rows_to_process__

    def __wrong_symbol(self, node, path, key, position, processed, mistakes) -> list:
        rows_to_process__ = list()

        __node_children = node["children"].keys()

        for __c in __node_children:
            if __c == key[position]:
                continue
            __mistakes = mistakes + [
                {
                    "mistake_type": f'wrong symbol "{key[position]}": '
                    f'replaced on "{__c}"',
                    "position": position,
                },
            ]
            __node = node["children"][__c]
            __path = path + __c

            __processed = processed.get((position + 1, __path))
            if __processed is None or __processed > len(__mistakes):
                rows_to_process__.append((position + 1, __path, __node, __mistakes))
                processed[(position + 1, __path)] = len(__mistakes)

            __node, __position = self.__apply_string(
                node=__node, s=key, position=position + 1
            )
            __path = path + __c + key[position + 1 : __position]

            __processed = processed.get((__position, __path))
            if __processed is None or __processed > len(__mistakes):
                rows_to_process__.append((__position, __path, __node, __mistakes))
                processed[(__position, __path)] = len(__mistakes)

        return rows_to_process__

    @staticmethod
    def __prepare_result(
        result: Dict[str, Dict[Any, Any]], extract_all: bool
    ) -> List[Dict[Any, Any]]:

        if not len(result):
            return list()

        if extract_all:
            return sorted(result.values(), key=lambda x: len(x["mistakes"]))

        __min_n_mistakes = min([len(x["mistakes"]) for x in result.values()])
        return [x for x in result.values() if len(x["mistakes"]) == __min_n_mistakes]

    @staticmethod
    def __check_value(
        node, path, key, position, mistakes, result, extract_all
    ) -> Optional[dict]:
        if position == len(key) and node.get("value") is not None:
            __result_row = result.get(path)
            if (
                __result_row is None
                or extract_all
                or len(__result_row["mistakes"]) > len(mistakes)
            ):
                return {
                    "value": node["value"],
                    "key": path,
                    "mistakes": mistakes,
                }
        return None
