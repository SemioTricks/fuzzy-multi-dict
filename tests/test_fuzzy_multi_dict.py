from unittest import TestCase

from fuzzy_multi_dict import FuzzyMultiDict


class TestFuzzyMultiDict(TestCase):

    def test_get_key_with_mistakes(self):

        d = FuzzyMultiDict(max_mistakes_number=3)

        d['first'] = 1
        d['second'] = 2
        d['third'] = 3

        self.assertEqual(d['first'], 1)
        self.assertEqual(d['frs'], 1)
        self.assertEqual(d['rs'], 1)

        r = d.get('frst')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['value'], 1)
        self.assertEqual(len(r[0]['mistakes']), 1)

    def test_get_key_with_alts(self):
        d = FuzzyMultiDict(max_mistakes_number=3)

        d['first'] = 1
        d['second'] = 2
        d['third'] = 3

        r = d.get('fird')
        self.assertEqual(len(r), 2)
        values = [_['value'] for _ in r]
        self.assertTrue(1 in values)
        self.assertTrue(3 in values)

    def test_get_no_key(self):
        d = FuzzyMultiDict(max_mistakes_number=3)

        d['first'] = 1
        d['second'] = 2

        r = d.get('third')
        self.assertEqual(len(r), 0)

        with self.assertRaises(KeyError):
            d['third']

    def test_set_dict(self):
        d = FuzzyMultiDict(max_mistakes_number=3)

        d['first'] = {'x': 1, 'y': 2, 'z': 3}
        d['second'] = [1, 2, 3]
        d['third'] = 3

        self.assertIsNotNone(d.get('first'))
        self.assertIsNotNone(d['first'].get('x'))
        self.assertEqual(d['first']['x'], 1)

    def test_custom_upd_value(self):

        def update_value(x, y):
            if x is None: return y

            if not isinstance(x, dict) or not isinstance(y, dict):
                raise TypeError(
                    f'Invalid value type; expect dict; got {type(x)} and {type(y)}')

            for k, v in y.items():
                if x.get(k) is None:
                    x[k] = v
                    continue

                if isinstance(x[k], list):
                    if v not in x[k]:
                        x[k].append(v)
                    continue

                if x[k] != v:
                    x[k] = [x[k], v]

            return x

        d = FuzzyMultiDict(max_mistakes_number=3, update_value_func=update_value)

        d['first'] = {'x': 1, 'y': 2}
        d['first'] = {'x': 1, 'y': 2, 'z': 3}
        self.assertEqual(d['first']['x'], 1)
        self.assertEqual(d['first']['y'], 2)

        d['first'] = {'x': 1, 'y': 2, 'z': 4}
        self.assertEqual(d['first']['x'], 1)
        self.assertEqual(d['first']['y'], 2)
        self.assertEqual(d['first']['z'], [3, 4])

        d['first'] = {'z': 5}
        self.assertEqual(d['first']['z'], [3, 4, 5])

        d['first'] = {'z': 5}
        self.assertEqual(d['first']['z'], [3, 4, 5])
