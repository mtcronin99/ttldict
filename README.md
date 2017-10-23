TTLDict
=======

Python dictionary with key expiry time

`OrderedTTLDict` - behaves like an ordered dict you know.
The methods `items` and `values` return a list of objects after purging expired
objects. The method `keys` returns `odict_keys` as the parent class, but it does
so after purging expired keys.
Python's own OrderedDict and other dictionaries return a [dictionary views][1]
whereas the methods here do not.

Expired keys are not removed, instead they are expired. You can remove expired
keys by calling `keys()` or any other method that iterates over the dictionary
instance. Expired keys will be removed when you try to access them.

Demo:

```
In [1]: from ttldict import  TTLOrderedDict

In [2]: mydict = TTLOrderedDict(default_ttl=3)  # expire keys after 3 second

In [3]: mydict['foo'] = 'bar'

In [4]: mydict.is_expired('foo')  # not yet expired

In [5]: mydict.is_expired('foo')  # not yet expired

In [6]: mydict.is_expired('foo')  # expired !!!
Out[6]: 'foo'


In [7]: mydict['foo']
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
<ipython-input-55-ed0618fdfbab> in <module>()
----> 1 mydict['foo']

/..../ttldict/__init__.py in __getitem__(self, key)
     95             if self.is_expired(key):
     96                 self.__delitem__(key)
---> 97                 raise KeyError
     98             item = super().__getitem__(key)[1]
     99             return item

KeyError:

In [8]: mydict.is_expired('foo')  # not available anymore
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
<ipython-input-56-351121feac66> in <module>()
----> 1 mydict.is_expired('foo')  # not available anymore

.../ttldict/__init__.py in is_expired(self, key, now)
     59                 now = time.time()
     60
---> 61             expire, _value = super().__getitem__(key)
     62
     63             if expire:

KeyError: 'foo'

```


Testing
-------

Use pytest to run the tests:

```
make test
```

Credits and Thanks:
-------------------

- mailgun for expiringdict

- Thomas Kemmer for
  https://github.com/tkem/cachetools

and for Jyrki Muukkonen for ttldict
published in https://github.com/jvtm/ttldict.

This library contains fixes for his TTLDict class
and my own OrderedTTLDict.

Without all those this work would not have been possible.

[1]: https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects
