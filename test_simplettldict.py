"""
Unit tests for TTLDict
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from builtins import zip
from builtins import range
from future import standard_library
standard_library.install_aliases()
from collections import OrderedDict
from unittest import TestCase
from simplettldict import SimpleTTLDict
import time


class SimpleTTLDictTest(TestCase):
    """ SimpleTTLDict tests """
    def test_update_no_ttl(self):
        """ Test update() call """
        ttl_dict = SimpleTTLDict(3)
        # order is not preserved for dicts before Python 3.6
        orig_dict = OrderedDict([('hello', 'world'), ('intval', 3)])
        ttl_dict.update(orig_dict)
        items = ttl_dict.items()
        for item in orig_dict.items():
            self.assertIn(item, items)

    def test_purge_clears_expired_items(self):
        """ Test that calling _purge() removes expired items """
        ttl_dict = SimpleTTLDict(1, a=1, b=2)
        self.assertEqual(sorted(ttl_dict.keys()), sorted(['a', 'b']))
        time.sleep(2)
        ttl_dict._purge()
        self.assertEqual(len(ttl_dict), 0)
        self.assertEqual(list(ttl_dict.keys()), [])

    def test_expire_at(self):
        """ Test expire_at """
        ttl_dict = SimpleTTLDict(60)
        ttl_dict['a'] = 100
        ttl_dict['b'] = 123
        self.assertEqual(ttl_dict['a'], 100)
        self.assertEqual(ttl_dict['b'], 123)
        self.assertEqual(len(ttl_dict), 2)
        self.assertRaises(NotImplementedError,ttl_dict.expire_at, 'a', time.time())

    def test_set_ttl(self):
        """ Test that set_ttl() raises NotImplementedError """
        ttl_dict = SimpleTTLDict(60)
        self.assertRaises(NotImplementedError, ttl_dict.set_ttl, 'test', 10)

    def test_get_ttl_key_error(self):
        """ Test that get_ttl() raises KeyError """
        ttl_dict = SimpleTTLDict(60)
        self.assertRaises(KeyError, ttl_dict.get_ttl, 'missing')

    def test_iter_empty(self):
        """ Test that empty SimpleTTLDict can be iterated """
        ttl_dict = SimpleTTLDict(60)
        for key in ttl_dict:
            self.fail("Iterating empty dictionary gave a key %r" % (key,))

    def test_iter(self):
        """ Test that SimpleTTLDict can be iterated """
        ttl_dict = SimpleTTLDict(60)
        ttl_dict.update(zip(range(10), range(10)))
        self.assertEqual(len(ttl_dict), 10)
        for key in ttl_dict:
            self.assertEqual(key, ttl_dict[key])

    def test_is_expired(self):
        """ Test is_expired() call """
        now = time.time()
        ttl_dict = SimpleTTLDict(60, a=1, b=2)
        self.assertFalse(ttl_dict.is_expired('a'))
        self.assertFalse(ttl_dict.is_expired('a', now=now))
        self.assertTrue(ttl_dict.is_expired('a', now=now+61))

        # remove=False, so nothing should be gone
        self.assertEqual(len(ttl_dict), 2)

    def test_values(self):
        ttl_dict = SimpleTTLDict(60)
        orig_dict = OrderedDict([('a', 1), ('b', 2)])
        ttl_dict.update(orig_dict)
        self.assertTrue(len(ttl_dict.values()), 2)
        self.assertEqual([1, 2], sorted(ttl_dict.values()))

    def test_len(self):
        """ Test len() gives real length """
        ttl_dict = SimpleTTLDict(1)
        self.assertEqual(len(ttl_dict), 0)
        ttl_dict['a'] = 1
        ttl_dict['b'] = 2
        self.assertEqual(len(ttl_dict), 2)
        time.sleep(2)
        self.assertEqual(len(ttl_dict), 0)

    def test_get(self):
        """ Test get() returns value if exists or default if not"""
        ttl_dict = SimpleTTLDict(1)
        ttl_dict['a'] = 1
        self.assertEqual(ttl_dict.get('a'), 1)
        self.assertEqual(ttl_dict.get('b', "default"), "default")
        time.sleep(2)
        self.assertEqual(ttl_dict.get('a', "default"), "default")

    def test_set_clears_expired_items(self):
        """ Test that setting item removes expired items """
        ttl_dict = SimpleTTLDict(2, a=1, b=2)
        self.assertEqual(sorted(ttl_dict.keys()), sorted(['a', 'b']))
        ttl_dict['c'] = 3
        self.assertEqual(len(ttl_dict), 3)
        time.sleep(4)
        ttl_dict['d'] = 4
        self.assertEqual(len(ttl_dict), 1)
        self.assertEqual(list(ttl_dict.keys()), ['d'])
