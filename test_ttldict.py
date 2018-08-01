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
from ttldict import TTLOrderedDict
import time


class TTLOrderedDictTest(TestCase):
    """ TTLOrderedDict tests """
    def test_update_no_ttl(self):
        """ Test update() call """
        ttl_dict = TTLOrderedDict(3)
        # order is not preserved for dicts before Python 3.6
        orig_dict = OrderedDict([('hello', 'world'), ('intval', 3)])
        ttl_dict.update(orig_dict)
        items = ttl_dict.items()
        for item in orig_dict.items():
            self.assertIn(item, items)

    def test_purge_clears_expired_items(self):
        """ Test that calling _purge() removes expired items """
        ttl_dict = TTLOrderedDict(1, a=1, b=2)
        self.assertEqual(sorted(ttl_dict.keys()), sorted(['a', 'b']))
        time.sleep(2)
        ttl_dict._purge()
        self.assertEqual(len(ttl_dict), 0)
        self.assertEqual(list(ttl_dict.keys()), [])

    def test_expire_at(self):
        """ Test expire_at """
        ttl_dict = TTLOrderedDict(60)
        ttl_dict['a'] = 100
        ttl_dict['b'] = 123
        self.assertEqual(ttl_dict['a'], 100)
        self.assertEqual(ttl_dict['b'], 123)
        self.assertEqual(len(ttl_dict), 2)
        ttl_dict.expire_at('a', time.time())
        self.assertRaises(KeyError, lambda: ttl_dict['a'])
        self.assertEqual(len(ttl_dict), 1)
        self.assertEqual(ttl_dict['b'], 123)

    def test_set_ttl_get_ttl(self):
        """ Test set_ttl() and get_ttl() """
        ttl_dict = TTLOrderedDict(120, foo=3, bar=None)
        self.assertEqual(sorted(ttl_dict), ['bar', 'foo'])
        self.assertEqual(ttl_dict['foo'], 3)
        self.assertEqual(ttl_dict['bar'], None)
        self.assertEqual(len(ttl_dict), 2)
        ttl_dict.set_ttl('foo', 3)
        ttl_foo = ttl_dict.get_ttl('foo')
        self.assertTrue(ttl_foo <= 3.0)
        ttl_bar = ttl_dict.get_ttl('bar')
        self.assertTrue(ttl_bar - ttl_foo > 100)

    def test_set_ttl_key_error(self):
        """ Test that set_ttl() raises KeyError """
        ttl_dict = TTLOrderedDict(60)
        self.assertRaises(KeyError, ttl_dict.set_ttl, 'missing', 10)

    def test_get_ttl_key_error(self):
        """ Test that get_ttl() raises KeyError """
        ttl_dict = TTLOrderedDict(60)
        self.assertRaises(KeyError, ttl_dict.get_ttl, 'missing')

    def test_iter_empty(self):
        """ Test that empty TTLOrderedDict can be iterated """
        ttl_dict = TTLOrderedDict(60)
        for key in ttl_dict:
            self.fail("Iterating empty dictionary gave a key %r" % (key,))

    def test_iter(self):
        """ Test that TTLOrderedDict can be iterated """
        ttl_dict = TTLOrderedDict(60)
        ttl_dict.update(zip(range(10), range(10)))
        self.assertEqual(len(ttl_dict), 10)
        for key in ttl_dict:
            self.assertEqual(key, ttl_dict[key])

    def test_is_expired(self):
        """ Test is_expired() call """
        now = time.time()
        ttl_dict = TTLOrderedDict(60, a=1, b=2)
        self.assertFalse(ttl_dict.is_expired('a'))
        self.assertFalse(ttl_dict.is_expired('a', now=now))
        self.assertTrue(ttl_dict.is_expired('a', now=now+61))

        # remove=False, so nothing should be gone
        self.assertEqual(len(ttl_dict), 2)

    def test_values(self):
        ttl_dict = TTLOrderedDict(60)
        orig_dict = OrderedDict([('a', 1), ('b', 2)])
        ttl_dict.update(orig_dict)
        self.assertTrue(len(ttl_dict.values()), 2)
        self.assertEqual([1, 2], sorted(ttl_dict.values()))

    def test_len(self):
        """ Test len() gives real length """
        ttl_dict = TTLOrderedDict(1)
        self.assertEqual(len(ttl_dict), 0)
        ttl_dict['a'] = 1
        ttl_dict['b'] = 2
        self.assertEqual(len(ttl_dict), 2)
        time.sleep(2)
        self.assertEqual(len(ttl_dict), 0)

    def test_get(self):
        """ Test get() returns value if exists or default if not"""
        ttl_dict = TTLOrderedDict(1)
        ttl_dict['a'] = 1
        self.assertEqual(ttl_dict.get('a'), 1)
        self.assertEqual(ttl_dict.get('b', "default"), "default")
        time.sleep(2)
        self.assertEqual(ttl_dict.get('a', "default"), "default")

