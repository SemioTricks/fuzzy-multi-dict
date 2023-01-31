# Module `fuzzy_multi_dict.py`
> Path: `fuzzy_multi_dict/fuzzy_multi_dict.py`
## Class `FuzzyMultiDict`
### SubElement(s)
 > ## Function  `__init__`
 > ### Argument(s)
 > + `max_mistakes_number`: int - default value of maximum number of corrections
 > in the query key when searching for a matching dictionary key
 > + `max_mistakes_number_part`: Optional[float] - default value to calculate
 > maximum number of corrections in the query key when searching
 > for a matching dictionary key;
 > calculated as round(max_mistakes_number_part * token_length)
 > + `update_value_func`: Optional[Callable] - merge function for value
 > when storing a new value with a key
 > ## Function  `__setitem__`
 > ```text
 > Storing the `value` with the `key`
 > ```
 > 
 > ### Argument(s)
 > + `key`: str - empty doc string
 > + `value`: Any - empty doc string
 > ## Function  `get`
 > ```text
 > Extracting the value given the `key`
 > ```
 > 
 > ### Argument(s)
 > + `key`: str - dictionary key
 > + `max_mistakes_number`: Optional[int] - maximum number of corrections in the query key
 > when searching for a matching dictionary key
 > + `max_mistakes_number_part`: Optional[float] - value to calculate maximum number
 > of corrections in the query key when searching for a matching
 > dictionary key;  if not None - `max_mistakes_number` will be ignored;
 > calculated as round(max_mistakes_number_part * token_length);
 > + `extract_all`: bool - if True - all existing keys that can be obtained
 > from the request by fixing no more than `max_mistakes_number` mistakes
 > will be returned
 > #### Declared returns: `List[Dict[Any, Any]]`
 > ## Function  `__getitem__`
 > ```text
 > Extracting the value given the `key`
 > ```
 > 
 > ### Argument(s)
 > + `key`: str - dictionary key
 > #### Declared returns: `Dict[str, Any]`
 > ## Function  `__apply_string`
 > ### Decorator(s)
 > + staticmethod
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `s`: str - empty doc string
 > + `position`: int - empty doc string
 > #### Declared returns: `Tuple[Dict[Any, Any], int]`
 > ## Function  `__no_mistakes`
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `path`: str - empty doc string
 > + `key`: str - empty doc string
 > + `position`: int - empty doc string
 > + `processed`: dict - empty doc string
 > + `mistakes`: list - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__missing_symbol`
 > ### Argument(s)
 > + `node` - empty doc string
 > + `path` - empty doc string
 > + `key` - empty doc string
 > + `position` - empty doc string
 > + `processed` - empty doc string
 > + `mistakes` - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__extra_symbol`
 > ### Argument(s)
 > + `node` - empty doc string
 > + `path` - empty doc string
 > + `key` - empty doc string
 > + `position` - empty doc string
 > + `processed` - empty doc string
 > + `mistakes` - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__wrong_symbol`
 > ### Argument(s)
 > + `node` - empty doc string
 > + `path` - empty doc string
 > + `key` - empty doc string
 > + `position` - empty doc string
 > + `processed` - empty doc string
 > + `mistakes` - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__prepare_result`
 > ### Decorator(s)
 > + staticmethod
 > ### Argument(s)
 > + `result`: Dict[str, Dict[Any, Any]] - empty doc string
 > + `extract_all`: bool - empty doc string
 > #### Declared returns: `List[Dict[Any, Any]]`
 > ## Function  `__check_value`
 > ### Decorator(s)
 > + staticmethod
 > ### Argument(s)
 > + `node` - empty doc string
 > + `path` - empty doc string
 > + `key` - empty doc string
 > + `position` - empty doc string
 > + `mistakes` - empty doc string
 > + `result` - empty doc string
 > + `extract_all` - empty doc string
 > #### Declared returns: `Optional[dict]`