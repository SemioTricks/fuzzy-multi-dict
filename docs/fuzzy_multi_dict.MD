# Module `fuzzy_multi_dict.py`
> Path: `fuzzy_multi_dict/fuzzy_multi_dict.py`
## Class `FuzzyMultiDict`
### SubElement(s)
 > ## Function  `__init__`
 > ### Argument(s)
 > + `max_mistakes_number`: int - the maximum number of mistakes in the key
 > + `update_value_func`: Optional[Callable] - value merge function when writing a new value by key
 > ## Function  `__setitem__`
 > ### Argument(s)
 > + `key`: str - empty doc string
 > + `value`: Any - empty doc string
 > ## Function  `get`
 > ### Argument(s)
 > + `key`: str - empty doc string
 > #### Declared returns: `List[Dict[Any, Any]]`
 > ## Function  `__getitem__`
 > ### Argument(s)
 > + `key`: str - empty doc string
 > #### Declared returns: `Dict[str, Any]`
 > ## Function  `__apply_string`
 > ### Decorator(s)
 > + staticmethod
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `s`: str - empty doc string
 > + `position`: int - empty doc string
 > #### Declared returns: `Tuple[Dict[Any, Any], int]`