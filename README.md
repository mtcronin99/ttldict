TTLDict
=======

Python dictionary with key expiry time

`OrderedTTLDict` - behaves like an ordered dict you know, for 3 methods

items, keys, and values return a list of objects after purging expired objects.
Python's own OrderedDict and other dictionaries return a [dictionary views][1]
whereas the methods here do not.


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
