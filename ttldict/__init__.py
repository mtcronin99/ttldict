"""
TTL dictionary

Tricks / features:
 - calling len() will remove expired keys
 - __repr__() might show expired values, doesn't remove expired ones
"""

__all__ = ['TTLDict']
__version__ = '0.0.4'

from collections import MutableMapping
from threading import RLock
import time


class TTLDict(MutableMapping):
    """
    Dictionary with TTL
    Extra args and kwargs are passed to initial .update() call
    """
    def __init__(self, default_ttl, *args, **kwargs):
        self._default_ttl = default_ttl
        self._values = {}
        self._lock = RLock()
        self.update(*args, **kwargs)

    def __repr__(self):
        self._purge()
        return '<TTLDict@%#08x; ttl=%r, v=%r;>' % (
            id(self), self._default_ttl, self._values)

    def set_ttl(self, key, ttl, now=None):
        """Set TTL for the given key"""
        if now is None:
            now = time.time()
        with self._lock:
            _expire, value = self._values[key]
            self._values[key] = (now + ttl, value)

    def get_ttl(self, key, now=None):
        """Return remaining TTL for a key"""
        if now is None:
            now = time.time()
        with self._lock:
            expire, _value = self._values[key]
            return expire - now

    def expire_at(self, key, timestamp):
        """Set the key expire timestamp"""
        with self._lock:
            _expire, value = self._values[key]
            self._values[key] = (timestamp, value)

    def is_expired(self, key, now=None):
        """ Check if key has expired, and return it if so"""
        with self._lock:
            if now is None:
                now = time.time()

            expire, _value = self._values[key]

            if expire:
                if expire < now:
                    return key

    def _purge(self):
        _remove = [key for key in self._values.keys() if self.is_expired(key)]  # noqa
        [self._values.pop(key) for key in _remove]

    def __len__(self):
        with self._lock:
            self._purge()
            return len(self._values)

    def __iter__(self):
        with self._lock:
            self._purge()
            for key in self._values.keys():
                yield key

    def __setitem__(self, key, value):
        with self._lock:
            if self._default_ttl is None:
                expire = None
            else:
                expire = time.time() + self._default_ttl
            self._values[key] = (expire, value)

    def __delitem__(self, key):
        with self._lock:
            del self._values[key]

    def __getitem__(self, key):
        with self._lock:
            if self.is_expired(key):
                self.__delitem__(key)
            else:
                return self._values[key][1]
