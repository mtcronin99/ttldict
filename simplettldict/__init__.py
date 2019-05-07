from itertools import (islice, takewhile)

from ttldict import TTLOrderedDict

LOOK_AHEAD = 5

__all__ = ['SimpleTTLDict']


class SimpleTTLDict(TTLOrderedDict):
    def set_ttl(self, key, ttl, now=None):
        raise NotImplementedError

    def expire_at(self, key, timestamp):
        raise NotImplementedError

    def _quick_cleanup(self):
        ks = []
        for k in takewhile(lambda x: self.is_expired(x),
                           islice(super(SimpleTTLDict, self).__iter__(),
                                  None,
                                  LOOK_AHEAD)):
            ks.append(k)
        for k in ks:
            self.__delitem__(k)

    def __setitem__(self, key, value):
        with self._lock:
            self._quick_cleanup()
            super(SimpleTTLDict, self).__setitem__(key,  value)

    def __getitem__(self, key):
        with self._lock:
            self._quick_cleanup()
            if self.is_expired(key):
                self.__delitem__(key)
                raise KeyError
            item = super(SimpleTTLDict, self).__getitem__(key)
            return item





