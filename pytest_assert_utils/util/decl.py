import collections
import inspect
import typing

__all__ = [
    'Any',
    'Optional',
    'Collection',
    'List',
    'Set',
    'Dict',
    'Str',
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


class _CollectionValuesCheckerMeta(type(collections.Collection)):
    """Overloads isinstance() to enable truthiness based on values inside the collection
    """
    def __eq__(cls: typing.Type['_CollectionValuesChecker'], instance) -> bool:
        return cls.__instancecheck__(instance)

    def __instancecheck__(cls: typing.Type['_CollectionValuesChecker'], instance) -> bool:
        if cls._must_be_empty and not cls._collection_is_empty_(instance):
            return False

        if cls._must_not_be_empty and cls._collection_is_empty_(instance):
            return False

        if cls._must_contain and not all(cls._collection_contains_(instance, v) for v in cls._must_contain):
            return False

        if cls._must_not_contain and any(cls._collection_contains_(instance, v) for v in cls._must_not_contain):
            return False

        return True

    def __repr__(cls: typing.Type['_CollectionValuesChecker']) -> str:
        parts = [cls.__name__]

        if cls._must_be_empty:
            parts.append('empty()')

        if cls._must_not_be_empty:
            parts.append('not_empty()')

        if cls._must_contain:
            parts.append(f'containing({cls._repr_containing_(cls._must_contain)})')

        if cls._must_not_contain:
            parts.append(f'not_containing({cls._repr_not_containing_(cls._must_not_contain)})')

        return '.'.join(parts)


class _CollectionValuesChecker:
    _must_contain: typing.Tuple = ()
    _must_not_contain: typing.Tuple = ()
    _must_be_empty: bool = False
    _must_not_be_empty: bool = False

    @classmethod
    def _unpack_generators(cls, items):
        for item in items:
            if inspect.isgenerator(item):
                yield from item
            else:
                yield item

    @classmethod
    def containing(cls: T, *items) -> T:
        _must_contain = (
            *cls._must_contain,
            *cls._unpack_generators(items),
        )
        return type(cls.__name__, (cls,), {'_must_contain': _must_contain})

    @classmethod
    def not_containing(cls: T, *items) -> T:
        _must_not_contain = (
            *cls._must_not_contain,
            *cls._unpack_generators(items),
        )
        return type(cls.__name__, (cls,), {'_must_not_contain': _must_not_contain})

    @classmethod
    def empty(cls: T) -> T:
        return type(cls.__name__, (cls,), {'_must_be_empty': True})

    @classmethod
    def not_empty(cls: T) -> T:
        return type(cls.__name__, (cls,), {'_must_not_be_empty': True})

    @classmethod
    def _repr_containing_(cls, must_contain):
        return ', '.join(repr(item) for item in must_contain)

    @classmethod
    def _repr_not_containing_(cls, must_not_contain):
        return cls._repr_containing_(must_not_contain)

    @classmethod
    def _collection_is_empty_(cls, collection) -> bool:
        return len(collection) == 0

    @classmethod
    def _collection_contains_(cls, collection, v) -> bool:
        return v in collection


class _DictValuesChecker(_CollectionValuesChecker):
    @classmethod
    def _process_items(
        cls,
        *items: typing.Union[typing.Hashable, typing.Dict],
    ) -> typing.List[typing.Tuple[typing.Hashable, typing.Any]]:
        processed = []
        for item in cls._unpack_generators(items):
            if isinstance(item, dict):
                processed.extend(item.items())
            else:
                processed.append((item, Any()))
        return processed

    @classmethod
    def containing(cls: T, *items, **kwargs) -> T:
        return super().containing(*cls._process_items(*items, kwargs))

    @classmethod
    def not_containing(cls: T, *items, **kwargs) -> T:
        return super().not_containing(*cls._process_items(*items, kwargs))

    @classmethod
    def _repr_containing_(cls, must_contain):
        return dict(must_contain)

    @classmethod
    def _collection_contains_(cls, collection, v) -> bool:
        k, v = v
        return k in collection and collection[k] == v


class Collection(_CollectionValuesChecker, collections.Collection, metaclass=_CollectionValuesCheckerMeta):
    """Special class enabling equality comparisons to check items in any collection (list, set, tuple, etc)

    Examples of functionality:

    >>> Collection.containing(1) == [1, 2, 3]
    True
    >>> Collection.containing(1) == {1, 2, 3}
    True
    >>> Collection.containing(1) == (1, 2, 3)
    True

    >>> Collection.containing(1) == [4, 5, 6]
    False
    >>> Collection.containing(1) == {4, 5, 6}
    False
    >>> Collection.containing(1) == (4, 5, 6)
    False
    """


class List(_CollectionValuesChecker, list, metaclass=_CollectionValuesCheckerMeta):
    """Special class enabling equality comparisons to check items in a list

    Examples of functionality:

    >>> List.containing(1) == [1, 2, 3]
    True
    >>> List.containing(1) == [4, 5, 6]
    False

    >>> List.not_containing(1) == [1, 2, 3]
    False
    >>> List.not_containing(1) == [4, 5, 6]
    True

    >>> List.empty() == [1, 2, 3]
    False
    >>> List.empty() == []
    True

    >>> List.not_empty() == [1, 2, 3]
    True
    >>> List.not_empty() == []
    False
    """


class Set(_CollectionValuesChecker, set, metaclass=_CollectionValuesCheckerMeta):
    """Special class enabling equality comparisons to check items in a set

    Examples of functionality:

    >>> Set.containing(1) == {1, 2, 3}
    True
    >>> Set.containing(1) == {4, 5, 6}
    False

    >>> Set.not_containing(1) == {1, 2, 3}
    False
    >>> Set.not_containing(1) == {4, 5, 6}
    True

    >>> Set.empty() == {1, 2, 3}
    False
    >>> Set.empty() == set()
    True

    >>> Set.not_empty() == {1, 2, 3}
    True
    >>> Set.not_empty() == set()
    False
    """


class Dict(_DictValuesChecker, dict, metaclass=_CollectionValuesCheckerMeta):
    """Special class allowing utils.Any to check items in a dict

    Examples of functionality:

    >>> Dict.containing('a') == {'a': 1, 'b': 2}
    True
    >>> Dict.containing(a=1) == {'a': 1, 'b': 2}
    True
    >>> Dict.containing({'a': 1}) == {'a': 1, 'b': 2}
    True
    >>> Dict.containing('a') == {'b': 2}
    False
    >>> Dict.containing(a=1) == {'b': 2}
    False
    >>> Dict.containing({'a': 1}) == {'b': 2}
    False

    >>> Dict.not_containing('a') == {'a': 1, 'b': 2}
    False
    >>> Dict.not_containing(a=1) == {'a': 1, 'b': 2}
    False
    >>> Dict.not_containing({'a': 1}) == {'a': 1, 'b': 2}
    False
    >>> Dict.not_containing('a') == {'b': 2}
    True
    >>> Dict.not_containing(a=1) == {'b': 2}
    True
    >>> Dict.not_containing({'a': 1}) == {'b': 2}
    True

    >>> Dict.empty() == {'a': 1, 'b': 2, 'c': 3}
    False
    >>> Dict.empty() == {}
    True

    >>> Dict.not_empty() == {'a': 1, 'b': 2, 'c': 3}
    True
    >>> Dict.not_empty() == {}
    False

    """


class Str(_CollectionValuesChecker, str, metaclass=_CollectionValuesCheckerMeta):
    """Special class enabling equality comparisons to check items in a string

    Examples of functionality:

    >>> Str.containing('app') == 'apple'
    True
    >>> Str.containing('app') == 'happy'
    True
    >>> Str.containing('app') == 'banana'
    False

    >>> Str.not_containing('app') == 'apple'
    False
    >>> Str.not_containing('app') == 'happy'
    False
    >>> Str.not_containing('app') == 'banana'
    True

    >>> Str.empty() == 'hamster'
    False
    >>> Str.empty() == ''
    True

    >>> Str.not_empty() == 'hamster'
    True
    >>> Str.not_empty() == ''
    False

    """
