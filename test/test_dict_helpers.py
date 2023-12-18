import unittest

from libs.helpers.dict import diff_dict, apply_diff


class DictDiffTest(unittest.TestCase):
    def test_equal(self):
        """ test to make sure that if the dicts are the same it will return an empty dict.
            this function will test the diff_dict and the apply_diff function."""
        a = {'a': 1, 'b': 2, 'c': 3}
        b = {'a': 1, 'b': 2, 'c': 3}
        diff = diff_dict(a, b)
        self.assertEqual(diff, {})
        self.assertEqual(apply_diff(a, diff), b)

    def test_simple_difference(self):
        """ test with a simple top level change. will test the diff_dict and the apply_diff function."""
        a = {'a': 1, 'b': 2, 'c': 3}
        b = {'a': 1, 'b': 3, 'd': 4}

        diff = diff_dict(a, b)
        self.assertEqual(diff, {'b': (2, 3), 'c': (0, 3), 'd': (1, 4)})
        self.assertEqual(apply_diff(a, diff), b)

    def test_array_difference(self):
        """ test with a change in an array. will test the diff_dict and the apply_diff function."""
        a = {'a': 1, 'b': [1, 2, 3], 'c': 3}
        b = {'a': 1, 'b': [1, 3, 4], 'd': 4}

        diff = diff_dict(a, b)
        self.assertEqual(diff, {'b': ((0, [2]), (1, [4])), 'c': (0, 3), 'd': (1, 4)})
        self.assertEqual(apply_diff(a, diff), b)

    def test_nested_dict_difference(self):
        a = {'a': 1, 'b': {'a': 1, 'b': 2}, 'c': 3}
        b = {'a': 1, 'b': {'a': 1, 'b': 3}, 'd': 4}

        diff = diff_dict(a, b)
        self.assertEqual(diff, {'b': {'b': (2, 3)}, 'c': (0, 3), 'd': (1, 4)})
        self.assertEqual(apply_diff(a, diff), b)

    def test_nested_array_difference(self):
        a = {'a': 1, 'b': {'a': 1, 'b': [1, 2, 3]}, 'c': 3}
        b = {'a': 1, 'b': {'a': 1, 'b': [1, 3, 4]}, 'd': 4}

        diff = diff_dict(a, b)
        self.assertEqual(diff, {'b': {'b': ((0, [2]), (1, [4]))}, 'c': (0, 3), 'd': (1, 4)})
        self.assertEqual(apply_diff(a, diff), b)
