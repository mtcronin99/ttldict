from collections import MutableMapping
from collections import OrderedDict
from threading import RLock
import time

__all__ = ['TTLDict', 'TTLOrderedDict']
__version__ = '0.1.0'


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
        return '<TTLDict@%#08x; ttl=%r, v=%r;>' % (
            id(self), self._default_ttl, self._values)

    def set_ttl(self, key, ttl, now=None):
        """ Set TTL for the given key """
        if now is None:
            now = time.time()
        with self._lock:
            _expire, value = self._values[key]
            self._values[key] = (now + ttl, value)

    def get_ttl(self, key, now=None):
        """ Return remaining TTL for a key """
        if now is None:
            now = time.time()
        with self._lock:
            expire, _value = self._values[key]
            return expire - now

    def expire_at(self, key, timestamp):
        """ Set the key expire timestamp """
        with self._lock:
            _expire, value = self._values[key]
            self._values[key] = (timestamp, value)

    def is_expired(self, key, now=None, remove=False):
        """ Check if key has expired """
        with self._lock:
            if now is None:
                now = time.time()
            expire, _value = self._values[key]
            if expire is None:
                return False
            expired = expire < now
            if expired and remove:
                self.__delitem__(key)
            return expired

    def __len__(self):
        with self._lock:
            for key in self._values.keys():
                self.is_expired(key, remove=True)
            return len(self._values)

    def __iter__(self):
        with self._lock:
            for key in self._values.keys():
                if not self.is_expired(key, remove=True):
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
            self.is_expired(key, remove=True)
            return self._values[key][1]


class TTLOrderedDict(OrderedDict):
    """
    OrderedDict with TTL
    Extra args and kwargs are passed to initial .update() call
    """
    def __init__(self, default_ttl, *args, **kwargs):
        self._default_ttl = default_ttl
        self._lock = RLock()
        super().__init__()
        self.update(*args, **kwargs)

    def __repr__(self):
        self._purge()
        return '<TTLDict@%#08x; ttl=%r, v=%r;>' % (
            id(self), self._default_ttl, super().__repr__())

    def set_ttl(self, key, ttl, now=None):
        """Set TTL for the given key"""
        if now is None:
            now = time.time()
        with self._lock:
            value = self[key]
            super().__setitem__(key, (now + ttl, value))

    def get_ttl(self, key, now=None):
        """Return remaining TTL for a key"""
        if now is None:
            now = time.time()
        with self._lock:
            expire, _value = super().__getitem__(key)
            return expire - now

    def expire_at(self, key, timestamp):
        """Set the key expire timestamp"""
        with self._lock:
            value = self.__getitem__(key)
            super().__setitem__(key,  (timestamp, value))

    def is_expired(self, key, now=None):
        """ Check if key has expired, and return it if so"""
        with self._lock:
            if now is None:
                now = time.time()

            expire, _value = super().__getitem__(key)

            if expire:
                if expire < now:
                    return key

    def _purge(self):
        _keys = list(super().__iter__())
        _remove = [key for key in _keys if self.is_expired(key)]  # noqa
        [self.__delitem__(key) for key in _remove]

    def __iter__(self):
        """make a snapshot iterator of keys.
        If you use this iterator it does not purge keys while you
        iterate.
        """
        with self._lock:
            for key in super().__iter__():
                if not self.is_expired(key):
                    yield key

    def __setitem__(self, key, value):
        with self._lock:
            if self._default_ttl is None:
                expire = None
            else:
                expire = time.time() + self._default_ttl
            super().__setitem__(key,  (expire, value))

    def __delitem__(self, key):
        with self._lock:
            super().__delitem__(key)

    def __getitem__(self, key, default=None):
        with self._lock:
            if self.is_expired(key):
                self.__delitem__(key)
            else:
                return super().__getitem__(key)[1]

    def keys(self):
        with self._lock:
            self._purge()
            return super().keys()

    def items(self):
        with self._lock:
            self._purge()
            return [(k, v[1]) for (k, v) in super().items()]

    def values(self):
        with self._lock:
            self._purge()
            return [v for (t, v) in list(super().values())]
