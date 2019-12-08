import collections.abc
import typing

__all__ = [
    'Any',
    'Optional',
    'Collection',
    'List',
    'Set',
]


T = typing.TypeVar('T')


class Any:
    """Meta-value which compares True to any object (of the specified type(s))

    Examples of functionality:

    >>> Any() == 'stuff'
    True
    >>> Any() == 1
    True
    >>> Any() == None
    True
    >>> Any() == object()
    True

    >>> Any(int) == 1
    True
    >>> Any(int) == '1'
    False
    """

    def __init__(self, *allowed_types):
        self.allowed_types = allowed_types

    def __eq__(self, other):
        if self.allowed_types:
            return isinstance(other, self.allowed_types)
        else:
            return True

    def __repr__(self):
        if not self.allowed_types:
            return '<Any>'
        elif len(self.allowed_types) == 1:
            return f'<Any {self.allowed_types[0]!r}>'
        else:
            return f'<Any {self.allowed_types!r}>'


class Optional:
    """Meta-value which compares True to None or the optionally specified value

    Examples of functionality:

    >>> Optional() == None
    True
    >>> Optional() is None  # this will not work!
    False
    >>> Optional(24) == 24
    True
    >>> Optional(24) == None
    True

    >>> Optional(Any(int)) == 1
    True
    >>> Optional(Any(int)) == None
    True
    >>> Optional(Any(int)) == '1'
    False
    """

    def __init__(self, value=None):
        self.value = value

    def __eq__(self, other):
        return other in (None, self.value)


class _CollectionValuesCheckerMeta(type(collections.abc.Collection)):
    """Overloads isinstance() to enable truthiness based on values inside the collection
    """
    def __instancecheck__(cls: typing.Type['_CollectionValuesChecker'], instance) -> bool:
        if cls._must_be_empty and len(instance) > 0:
            return False

        if cls._must_not_be_empty and len(instance) == 0:
            return False

        if cls._must_contain and not all(v in instance for v in cls._must_contain):
            return False

        if cls._must_not_contain and any(v in instance for v in cls._must_not_contain):
            return False

        return True

    def __repr__(cls: typing.Type['_CollectionValuesChecker']) -> str:
        parts = [cls.__name__]

        if cls._must_be_empty:
            parts.append('empty()')

        if cls._must_not_be_empty:
            parts.append('not_empty()')

        if cls._must_contain:
            items = [str(item) for item in cls._must_contain]
            parts.append(f'containing({", ".join(items)})')

        if cls._must_not_contain:
            items = [str(item) for item in cls._must_not_contain]
            parts.append(f'not_containing({", ".join(items)})')

        return '.'.join(parts)


class _CollectionValuesChecker:
    _must_contain: typing.Set = frozenset()
    _must_not_contain: typing.Set = frozenset()
    _must_be_empty: bool = False
    _must_not_be_empty: bool = False

    @classmethod
    def containing(cls: T, *items) -> T:
        _must_contain = {
            *cls._must_contain,
            *items,
        }
        return type(cls.__name__, (cls,), {'_must_contain': _must_contain})

    @classmethod
    def not_containing(cls: T, *items) -> T:
        _must_not_contain = {
            *cls._must_not_contain,
            *items,
        }
        return type(cls.__name__, (cls,), {'_must_not_contain': _must_not_contain})

    @classmethod
    def empty(cls: T) -> T:
        return type(cls.__name__, (cls,), {'_must_be_empty': True})

    @classmethod
    def not_empty(cls: T) -> T:
        return type(cls.__name__, (cls,), {'_must_not_be_empty': True})


class Collection(_CollectionValuesChecker, collections.abc.Collection, metaclass=_CollectionValuesCheckerMeta):
    """Special class allowing utils.Any to check items in any collection (list, set, tuple, etc)

    Examples of functionality:

    >>> Any(Collection.containing(1)) == [1, 2, 3]
    True
    >>> Any(Collection.containing(1)) == {1, 2, 3}
    True
    >>> Any(Collection.containing(1)) == (1, 2, 3)
    True

    >>> Any(Collection.containing(1)) == [4, 5, 6]
    False
    >>> Any(Collection.containing(1)) == {4, 5, 6}
    False
    >>> Any(Collection.containing(1)) == (4, 5, 6)
    False
    """


class List(_CollectionValuesChecker, list, metaclass=_CollectionValuesCheckerMeta):
    """Special class allowing utils.Any to check items in a list

    Examples of functionality:

    >>> Any(List.containing(1)) == [1, 2, 3]
    True
    >>> Any(List.containing(1)) == [4, 5, 6]
    False

    >>> Any(List.not_containing(1)) == [1, 2, 3]
    False
    >>> Any(List.not_containing(1)) == [4, 5, 6]
    True

    >>> Any(List.empty()) == [1, 2, 3]
    False
    >>> Any(List.empty()) == []
    True

    >>> Any(List.not_empty()) == [1, 2, 3]
    True
    >>> Any(List.not_empty()) == []
    False
    """


class Set(_CollectionValuesChecker, set, metaclass=_CollectionValuesCheckerMeta):
    """Special class allowing utils.Any to check items in a set

    Examples of functionality:

    >>> Any(Set.containing(1)) == {1, 2, 3}
    True
    >>> Any(Set.containing(1)) == {4, 5, 6}
    False

    >>> Any(Set.not_containing(1)) == {1, 2, 3}
    False
    >>> Any(Set.not_containing(1)) == {4, 5, 6}
    True

    >>> Any(Set.empty()) == {1, 2, 3}
    False
    >>> Any(Set.empty()) == set()
    True

    >>> Any(Set.not_empty()) == {1, 2, 3}
    True
    >>> Any(Set.not_empty()) == set()
    False
    """
