# Module `fuzzy_multi_dict.py`
> Path: `fuzzy_multi_dict/fuzzy_multi_dict.py`
## Class `FuzzyMultiDict`
### SubElement(s)
 > ## Function  `__init__`
 > ### Argument(s)
 > + `max_corrections`: Optional[int] - default value of maximum number of corrections
 > in the query key when searching for a matching dictionary key;
 > default = 2
 > + `max_corrections_relative`: Optional[float] - default value to calculate
 > maximum number of corrections in the query key when searching
 > for a matching dictionary key; default = None
 > calculated as round(max_corrections_relative * token_length)
 > + `update_value_func`: Optional[Callable] - merge function for value
 > when storing a new value with a key; default = None
 > + `sort_key`: Optional[Callable] - key for sorting values founded by query;
 > default = None
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
 > Extracting the value given the `query`
 > ```
 > 
 > ### Argument(s)
 > + `query`: str - query to search for dictionary key
 > + `max_corrections`: Optional[int] - maximum number of corrections in the query key
 > when searching for a matching dictionary key
 > + `max_corrections_relative`: Optional[float] - value to calculate maximum number
 > of corrections in the query key when searching for a matching
 > dictionary key;  if not None - `max_corrections` will be ignored;
 > calculated as round(max_corrections_relative * token_length);
 > + `extract_all`: bool - if True - all existing keys that can be obtained
 > from the request by fixing no more than `max_corrections` correction
 > will be returned
 > #### Declared returns: `List[Dict[Any, Any]]`
 > ## Function  `__getitem__`
 > ```text
 > Extracting the value given the `query`
 > ```
 > 
 > ### Argument(s)
 > + `query`: str - query to search for dictionary key
 > #### Declared returns: `Dict[str, Any]`
 > ## Function  `__apply_string`
 > ### Decorator(s)
 > + staticmethod
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `s`: str - empty doc string
 > + `position`: int - empty doc string
 > #### Declared returns: `Tuple[Dict[Any, Any], int]`
 > ## Function  `__apply_as_is`
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `path`: str - empty doc string
 > + `key`: str - empty doc string
 > + `position`: int - empty doc string
 > + `processed`: dict - empty doc string
 > + `correction`: list - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__apply_transposition`
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `path`: str - empty doc string
 > + `query`: str - empty doc string
 > + `position`: int - empty doc string
 > + `processed`: dict - empty doc string
 > + `correction`: list - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__apply_insertion`
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `path`: str - empty doc string
 > + `query`: str - empty doc string
 > + `position`: int - empty doc string
 > + `processed`: dict - empty doc string
 > + `correction`: list - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__apply_deletion`
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `path`: str - empty doc string
 > + `query`: str - empty doc string
 > + `position`: int - empty doc string
 > + `processed`: dict - empty doc string
 > + `correction`: list - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__apply_substitution`
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `path`: str - empty doc string
 > + `query`: str - empty doc string
 > + `position`: int - empty doc string
 > + `processed`: dict - empty doc string
 > + `correction`: list - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__prepare_result`
 > ### Argument(s)
 > + `result`: dict - empty doc string
 > + `extract_all`: bool - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__check_value`
 > ### Decorator(s)
 > + staticmethod
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `path`: str - empty doc string
 > + `query`: str - empty doc string
 > + `position`: int - empty doc string
 > + `correction`: list - empty doc string
 > + `result`: dict - empty doc string
 > + `extract_all`: bool - empty doc string
 > #### Declared returns: `Optional[dict]`
 > ## Function  `__get_max_corrections`
 > ### Argument(s)
 > + `n`: int - empty doc string
 > + `max_corrections`: Optional[int] - empty doc string
 > + `max_corrections_relative`: Optional[float] - empty doc string
 > #### Declared returns: `int`