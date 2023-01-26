from typing import List, Any, Dict, Optional, Callable


class FuzzyMultiDict:

    def __init__(self,
                 max_mistakes_number: int = 2,
                 update_value_func: Optional[Callable] = None):
        """
        :param max_mistakes_number: the maximum number of mistakes in the key
        :param update_value_func: value merge function when writing a new value by key

        """
        self.__prefix_tree = {
            'parent': 'ROOT',
            'children': dict(),
            'data': None,
            'path': ''
        }
        self.__max_mistakes_number = max_mistakes_number
        self.__update_value = (
            lambda x, y: y) if update_value_func is None else update_value_func

    def __setitem__(self, key: str, value: Any):

        if not isinstance(key, str):
            raise TypeError(f'Invalid key type: expect str, got {type(key)}')

        __node = self.__prefix_tree
        for i, c in enumerate(key):
            if __node['children'].get(c) is None:
                __node['children'][c] = {
                    'parent': __node,
                    'children': dict(),
                    'data': None,
                    'path': key[:i + 1]
                }
            __node = __node['children'][c]

        __node['value'] = self.__update_value(__node.get('value'), value)

    def get(self, key: str) -> list:

        key_length = len(key)
        max_mistakes_number = self.__max_mistakes_number

        # if its correct number title
        node, position = self.__apply_string(node=self.__prefix_tree, s=key, position=0)
        if position == key_length and node.get('value'):
            return [{'value': node['value'], 'key': key, 'mistakes': list()}, ]

        result = dict()
        rows_to_process = [(position, node, list()), (0, self.__prefix_tree, list())]
        processed = {(pos, node['path']): 0 for (pos, node, _) in rows_to_process}

        while True:
            rows_to_process__ = list()
            for (position, node, mistakes) in rows_to_process:
                processed[(position, node['path'])] = len(mistakes)

                if position == key_length and node.get('value'):
                    __result_row = result.get(node['path'])
                    if __result_row is None \
                            or len(__result_row['mistakes'] > len(mistakes)):
                        result[node['path']] = {
                            'value': node['value'],
                            'key': node['path'],
                            'mistakes': mistakes
                        }
                        if len(mistakes) < max_mistakes_number:
                            max_mistakes_number = len(mistakes)
                    continue

                __node_children = node['children'].keys()
                __has_children = len(__node_children) > 0

                # no mistake
                if position + 1 < key_length and __has_children:
                    __node = node['children'].get(key[position])
                    if __node:
                        __processed = processed.get((position + 1, __node['path']))
                        if __processed is None or __processed > len(mistakes):
                            rows_to_process__.append((position + 1, __node, mistakes))
                            processed[(position + 1, __node['path'])] = len(mistakes)

                            __node, __position = self.__apply_string(
                                node=node, s=key, position=position
                            )
                            __processed = processed.get((__position, __node['path']))
                            if __processed is None or __processed > len(mistakes):
                                rows_to_process__.append((__position, __node, mistakes))
                                processed[(__position, __node['path'])] = len(mistakes)

                if len(mistakes) >= max_mistakes_number:
                    continue

                # mistake: missing symbol
                if __has_children:
                    for __c in __node_children:
                        __node = node['children'][__c]
                        __mistakes = mistakes + [{
                            'mistake_type': f'missing symbol "{__c}"',
                            'position': position},
                        ]
                        __processed = processed.get((position, __node['path']))
                        if __processed is None or __processed > len(__mistakes):
                            rows_to_process__.append((position, __node, __mistakes))
                            processed[(position, __node['path'])] = len(__mistakes)

                        __node, __position = self.__apply_string(node=__node, s=key,
                                                                 position=position)
                        __processed = processed.get((__position, __node['path']))
                        if __processed is None or __processed > len(__mistakes):
                            rows_to_process__.append((__position, __node, __mistakes))
                            processed[(__position, __node['path'])] = len(__mistakes)

                if position < key_length:

                    # mistake: extra symbol
                    __mistakes = mistakes + [{
                        'mistake_type': f'extra symbol "{key[position]}"',
                        'position': position},
                    ]
                    __processed = processed.get((position + 1, node['path']))
                    if __processed is None or __processed > len(__mistakes):
                        rows_to_process__.append((position + 1, node, __mistakes))
                        processed[(position + 1, node['path'])] = len(__mistakes)

                    __node, __position = self.__apply_string(
                        node=node, s=key, position=position + 1)
                    __processed = processed.get((__position, __node['path']))
                    if __processed is None or __processed > len(__mistakes):
                        rows_to_process__.append((__position, __node, __mistakes))
                        processed[(__position, __node['path'])] = len(__mistakes)

                    # mistake: wrong symbol
                    for __c in __node_children:
                        __mistakes = mistakes + [{
                            'mistake_type': f'wrong symbol "{key[position]}": '
                                            f'replaced on "{__c}"',
                            'position': position},
                        ]
                        __node = node['children'][__c]
                        __processed = processed.get((position + 1, __node['path']))
                        if __processed is None or __processed > len(__mistakes):
                            rows_to_process__.append((position + 1, __node, __mistakes))
                            processed[(position + 1, __node['path'])] = len(__mistakes)

                        __node, __position = self.__apply_string(
                            node=__node, s=key, position=position + 1)
                        __processed = processed.get((__position, __node['path']))
                        if __processed is None or __processed > len(__mistakes):
                            rows_to_process__.append((__position, __node, __mistakes))
                            processed[(__position, __node['path'])] = len(__mistakes)

            if not len(rows_to_process__):
                break

            rows_to_process = rows_to_process__

        if not len(result):
            return result

        __min_n_mistakes = min([len(x['mistakes']) for x in result.values()])
        return sorted(
            [x for x in result.values() if len(x['mistakes']) == __min_n_mistakes],
            key=lambda x: x['key']
        )

    def __getitem__(self, key: str) -> List[Dict[str, Any]]:

        if not isinstance(key, str):
            raise TypeError(f'Invalid key type: expect str; got {type(key)}')

        value = self.get(key)

        if len(value):
            return value[0]['value']

        raise KeyError(key)

    @staticmethod
    def __apply_string(node: dict, s: str, position: int):

        sub_position = 0

        for c in s[position:]:

            __node = node['children'].get(c)
            if not __node:
                return node, position + sub_position

            node = __node
            sub_position += 1

        return node, position + sub_position
