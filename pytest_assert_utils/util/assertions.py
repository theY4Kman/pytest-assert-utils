import operator

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

__all__ = ['assert_dict_is_subset', 'assert_model_attrs']

UNSET = object()


def assert_dict_is_subset(subset, superset, recursive=True):
    """Assert `subset` is a non-strict subset of `superset`

    If this assertion fails, a pretty diff will be printed by pytest.

    >>> expected = {'a': 12}
    >>> actual = {'b': 20, 'a': 12}
    >>> assert_dict_is_subset(expected, actual)

    >>> expected = {'a': 12}
    >>> actual = {'b': 50000}
    >>> assert_dict_is_subset(expected, actual)
    Traceback (most recent call last):
     ...
    AssertionError
    """
    superset_slice = _slice_superset(subset, superset, recursive=recursive)

    expected = subset
    actual = superset_slice
    assert expected == actual


def assert_model_attrs(instance, _d=UNSET, **attrs):
    """Assert a model instance has the specified attr values
    """
    if _d is not UNSET:
        if attrs:
            attrs['_d'] = _d
        else:
            attrs = _d

    model_attrs_slice = _slice_superset(attrs, instance,
                                        getitem=getattr, hasitem=hasattr)

    expected = attrs
    actual = model_attrs_slice
    assert_dict_is_subset(expected, actual)


def _slice_superset(subset, superset,
                    recursive=True,
                    getitem=operator.getitem,
                    hasitem=operator.contains):
    superset_slice = {}

    for key, value in subset.items():
        if not hasitem(superset, key):
            continue

        superset_value = getitem(superset, key)
        if recursive and (isinstance(value, Mapping) and
                          _is_bare_mapping(superset_value)):
            # NOTE: value *must* have .items(), superset_value only needs
            #       `b in a` and `a[b]`
            superset_value = _slice_superset(value, superset_value)

        superset_slice[key] = superset_value

    return superset_slice


def _is_bare_mapping(o):
    """Whether the object supports __getitem__ and __contains__"""
    return (
        hasattr(o, '__contains__') and callable(o.__contains__) and
        hasattr(o, '__getitem__') and callable(o.__getitem__)
    )
