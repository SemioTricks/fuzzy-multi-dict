# Module `fuzzy_multi_dict.py`
> Path: `fuzzy_multi_dict/fuzzy_multi_dict.py`
`CorrectionPrice` = namedtuple('CorrectionScore', 'transposition deletion substitution insertion')
## Class `FuzzyMultiDict`
### SubElement(s)
 > `__prefix_tree`: Dict[str, Any] = None
 > `__update_value`: Callable = None
 > `__max_corrections_value`: float = None
 > `__correction_price`: CorrectionPrice = None
 > `__symbol_probability`: Dict[str, float] = None
 > `__symbols_distance`: Dict[Tuple[str, str], float] = None
 > `__default_symbol_probability`: float = None
 > `__default_symbols_distance`: float = None
 > ## Function  `__init__`
 > ```text
 > Initialize Fuzzy Multi Dict object with input parameters
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `max_corrections_value`: float - max relative number of corrections in
 > the query to find the matching key; default = 1.
 > + `update_value`: Optional[Callable] - function to update data by key
 > + `correction_price`: CorrectionPrice - correction price depending on type;
 > default = CorrectionPrice(1., 1., 1., 1.)
 > + `symbol_probability`: Optional[Dict[str, float]] - probability for each
 > character to rank output and sort result; default is None
 > + `default_symbol_probability`: float - default symbol probability value
 > (between 0 and 1); default = 1e-5
 > + `symbols_distance`: Optional[Dict[Tuple[str, str], float]] - distance
 > between characters (between 0 and 1) to rank output and sort result;
 > default is None
 > + `default_symbols_distance`: float - defaut value of distance between
 > characters; default = 1.
 > ::Example::
 > >>> from fuzzy_multi_dict import FuzzyMultiDict, CorrectionPrice
 > >>> d = FuzzyMultiDict(
 > ...   max_corrections_value=2/3,
 > ...   correction_price=CorrectionPrice(
 > ...      deletion=.2, insertion=1., transposition=.1, substitution=.3),
 > ...   symbol_probability={'a': 1., 'b': .5, 'c': .3},
 > ...   default_symbol_probability=1e-5,
 > ...   symbols_distance={('a', 'b'): .3, ('b', 'c'): .1},
 > ...   default_symbols_distance=1.
 > ... )
 > ## Function  `set_correction_price`
 > ```text
 > Sets correction prices for all correction types
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `correction_price`: CorrectionPrice - correction price depending on type;
 > default = CorrectionPrice(1., 1., 1., 1.)
 > ::Example::
 > >>> from fuzzy_multi_dict import FuzzyMultiDict
 > >>> d = FuzzyMultiDict(correction_price=CorrectionPrice(
 > ...   deletion=.2, insertion=1., transposition=.1, substitution=.3),
 > ... )
 > >>> d.correction_price
 > ... # CorrectionScore(
 > ... #    transposition=0.1, deletion=0.2, substitution=0.3, insertion=0.1)
 > >>> d.correction_price.insertion
 > ... # 0.1
 > ## Function  `set_symbols_probability_distances`
 > ```text
 > Sets symbols probabilities and distances
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `symbol_probability`: Optional[Dict[str, float]] - probability for each
 > character to rank output and sort result; default is None
 > + `default_symbol_probability`: float - default symbol probability value
 > (between 0 and 1); default = 1e-5
 > + `symbols_distance`: Optional[Dict[Tuple[str, str], float]] - distance
 > between characters (between 0 and 1) to rank output and
 > sort result; default is None
 > + `default_symbols_distance`: float - default value of distance between
 > characters; default = 1.
 > ::Example::
 > >>> d = FuzzyMultiDict()
 > >>> d.set_symbols_probability_distances(
 > ...    symbol_probability={'a': 1., 'b': .5, 'c': 1.},
 > ...    default_symbol_probability=.1,
 > ...    symbols_distance={('a', 'b'): .5, ('b', 'c'): .1},
 > ...    default_symbols_distance=1.)
 > >>> d.default_symbol_probability
 > ... # .1
 > >>> d.default_symbols_distance
 > ... # 1.
 > >>> d.get_symbol_probability('b')
 > ... # .5
 > >>> d.get_symbol_probability('e')
 > ... # .1
 > >>> d.get_symbols_distance('a', 'b')
 > ... # .5
 > >>> d.get_symbols_distance('b', 'a')
 > ... # .5
 > >>> d.get_symbols_distance('d', 'e')
 > ... # 1.
 > >>> d.get_symbols_distance('c', 'c')
 > ... # .0
 > ## Function  `set_max_corrections_value`
 > ```text
 > Sets max corrections value
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `max_corrections_value`: float - max relative number of corrections in
 > the query to find the matching key; default = 1.
 > ::Example::
 > >>> from fuzzy_multi_dict import fuzzy_multi_dict
 > >>> d = FuzzyMultiDict(max_corrections_value=1/3)
 > >>> d.set_max_corrections_value(.5)
 > >>> d.max_corrections_value
 > ... # .5
 > ## Function  `save`
 > ```text
 > Saves prefix tree data to binary file
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `filename`: str - filename to save prefix tree data
 > ::Example::
 > >>> from fuzzy_multi_dict import FuzzyMultiDict
 > >>> d = FuzzyMultiDict(
 > ...    max_corrections_value=2/3,
 > ...    correction_price=CorrectionPrice(1., 1., 1., 1.),
 > ...    symbol_probability={'a': 1., 'c': .5},
 > ...    default_symbol_probability=.1,
 > ...    symbols_distance={('а', 'с'): .01, ('ц', 'л'): 1},
 > ...    default_symbols_distance=1.)
 > >>> d["first"] = 1
 > >>> d["second"] = 2
 > >>> d["third"] = 3
 > >>> d.save('dict.bin')
 > ## Function  `load`
 > ```text
 > Loads prefix tree data from binary file
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `filename`: str - filename to load prefix tree data
 > ::Example::
 > >>> from fuzzy_multi_dict import FuzzyMultiDict
 > >>> d = FuzzyMultiDict()
 > >>> d.load('dict.bin')
 > ## Function  `__setitem__`
 > ```text
 > Storing the `value` with the `key`
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `key`: str - input key
 > + `value`: Any - input value
 > ::Example::
 > >>> from fuzzy_multi_dict import FuzzyMultiDict
 > >>> d = FuzzyMultiDict(max_corrections_value=1.)
 > >>> d["first"] = 1
 > ## Function  `get`
 > ```text
 > Extracting the value given the `query`
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `query`: str - query to search for dictionary key
 > + `topn`: Optional[int] - only topn results will be returned
 > #### Declared returns: `List[Dict[Any, Any]]`
 > ## Function  `search`
 > ```text
 > Searching the values starts as given the `query`
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `query`: str - query to search
 > + `topn`: int - only to n search results will be returned
 > #### Declared returns: `List[Any]`
 > ## Function  `__get`
 > ```text
 > Extracting the value and search result given the `query`
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `query`: str - query to search for dictionary key
 > + `topn`: Optional[int] - only topn results will be returned
 > + `topn_leaves`: Optional[int] - only topn leaves from found will
 > be returned; used for searching
 > #### Declared returns: `List[Dict[Any, Any]]`
 > ## Function  `__getitem__`
 > ```text
 > Extracting the value given the `query`
 > ::Parameters::
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
 > + `topn`: Optional[int] - empty doc string
 > + `topn_leaves`: Optional[int] - empty doc string
 > #### Declared returns: `list`
 > ## Function  `__check_value`
 > ### Argument(s)
 > + `node`: dict - empty doc string
 > + `path`: str - empty doc string
 > + `query`: str - empty doc string
 > + `position`: int - empty doc string
 > + `correction`: list - empty doc string
 > + `result`: dict - empty doc string
 > + `topn_leaves`: Optional[int] - empty doc string
 > #### Declared returns: `Optional[dict]`
 > ## Function  `__get_node_leaves`
 > ```text
 > Returns top node leaves
 > ```
 > 
 > ### Argument(s)
 > + `node`: dict - current position in prefix tree
 > + `path`: str - path to node
 > + `topn`: Optional[int] - only topn leaves will be returned
 > #### Declared returns: `List[Dict[str, Any]]`
 > ## Function  `__get_total_corrections_score`
 > ```text
 > Returns sum of corrections prices
 > ::Parameters::
 > ```
 > 
 > ### Decorator(s)
 > + staticmethod
 > ### Argument(s)
 > + `corrections`: List[Dict[str, Any]] - list of corrections in query
 > #### Declared returns: `float`
 > ## Function  `correction_price`
 > ```text
 > Returns corretions prices
 > ::Example::
 > >>> from fuzzy_multi_dict import FuzzyMultiDict
 > >>> d = FuzzyMultiDict()
 > >>> d.correction_price
 > ... # CorrectionScore(
 > ... #    transposition=0.1, deletion=0.2, substitution=0.3, insertion=0.1)
 > ```
 > 
 > ### Decorator(s)
 > + property
 > #### Declared returns: `CorrectionPrice`
 > ## Function  `max_corrections_value`
 > ```text
 > Returns max correction value
 > ::Example::
 > >>> from fuzzy_multi_dict import FuzzyMultiDict
 > >>> d = FuzzyMultiDict(max_corrections_value=.1)
 > >>> d.max_corrections_value
 > ... # .1
 > ```
 > 
 > ### Decorator(s)
 > + property
 > #### Declared returns: `float`
 > ## Function  `default_symbols_distance`
 > ```text
 > Returns default symbols distance
 > ::Example::
 > >>> from fuzzy_multi_dict import FuzzyMultiDict
 > >>> d = FuzzyMultiDict(
 > ... symbols_distance={('а', 'b'): .5, ('b', 'c'): .1},
 > ... default_symbols_distance=1.)
 > >>> d.default_symbols_distance
 > ... # 1.
 > ```
 > 
 > ### Decorator(s)
 > + property
 > #### Declared returns: `float`
 > ## Function  `default_symbol_probability`
 > ```text
 > Returns default symbol probability
 > ::Example::
 > >>> from fuzzy_multi_dict import FuzzyMultiDict
 > >>> d = FuzzyMultiDict(
 > ... symbol_probability={'a': 1., 'b': .5},
 > ... default_symbol_probability=.1)
 > >>> d.default_symbol_probability
 > ... # .1
 > ```
 > 
 > ### Decorator(s)
 > + property
 > ## Function  `get_symbols_distance`
 > ```text
 > Returns distance between symbols `x` and `y`
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `x`: str - first char
 > + `y`: str - second char
 > #### Declared returns: `float`
 > ## Function  `get_symbol_probability`
 > ```text
 > Returns symbol probability
 > ::Parameters::
 > ```
 > 
 > ### Argument(s)
 > + `c`: str - input char