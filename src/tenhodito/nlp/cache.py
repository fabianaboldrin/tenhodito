from django.conf import settings
import shelve
import os


db = shelve.open(os.path.join(settings.BASE_DIR, 'cache.db'))


def load_from_cache(var_name, initial_value_method=None, force_update=False):
    """Loads a variable from cache.db. If this variable does not exist
    `initial_value_method` is called and the return is used to set a intial
    to the variable on cache.

    If the variable name isn't in cache and anyone  initial value method is
    provided, return None.
    """
    try:
        if force_update:
            raise KeyError
        else:
            return db[var_name]
    except KeyError:
        if callable(initial_value_method):
            db[var_name] = initial_value_method()
            db.sync()
            return db[var_name]
        else:
            return None


def update(var_name, value):
    """Update a variable with a new value or add a new variable to cache."""
    db[var_name] = value
    db.sync()
