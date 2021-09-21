import functools
import inspect
import typing

from .assertions import assert_model_attrs

try:
    from collections.abc import Collection as BaseCollection
except ImportError:
    from collections import Collection as BaseCollection

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

__all__ = [
    'Any',
    'Optional',
    'Collection',
    'List',
    'Set',
    'Dict',
    'Str',
    'Model',
]


T = typing.TypeVar('T')

_CheckerType = typing.TypeVar('_CheckerType', bound=typing.Type['_BaseCollectionValuesChecker'])
_ItemType = typing.TypeVar('_ItemType')


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
        else:
            return f'<Any {", ".join(t.__name__ for t in self.allowed_types)}>'

    def __hash__(self):
        return hash(self.allowed_types)


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

    def __hash__(self):
        return hash(self.value)


class _CollectionValuesCheckerMeta(type(BaseCollection)):
    """Overloads isinstance() to enable truthiness based on values inside the collection
    """

    def __hash__(cls):
        return hash(id(cls))

    def __eq__(cls: typing.Type['_BaseCollectionValuesChecker'], instance) -> bool:
        return cls.__instancecheck__(instance)

    def __instancecheck__(cls: typing.Type['_BaseCollectionValuesChecker'], instance) -> bool:
        if cls._collection_type and not isinstance(instance, cls._collection_type):
            return False

        if cls._must_be_empty and not cls._collection_is_empty_(instance):
            return False

        if cls._must_not_be_empty and cls._collection_is_empty_(instance):
            return False

        if cls._must_contain and not all(cls._collection_contains_(instance, v) for v in cls._must_contain):
            return False

        if cls._must_contain_only and not all(v in cls._must_contain_only for v in cls._collection_iter_(instance)):
            return False

        if cls._must_contain_exactly:
            values = list(cls._collection_iter_(instance))
            if len(cls._must_contain_exactly) != len(values):
                return False
            for v in cls._must_contain_exactly:
                try:
                    values.remove(v)
                except ValueError:
                    return False

        if cls._must_not_contain and any(cls._collection_contains_(instance, v) for v in cls._must_not_contain):
            return False

        return True

    def __repr__(cls: typing.Type['_BaseCollectionValuesChecker']) -> str:
        parts = [cls.__name__]

        if cls._must_be_empty:
            parts.append('empty()')

        if cls._must_not_be_empty:
            parts.append('not_empty()')

        if cls._must_contain:
            parts.append(f'containing({cls._repr_containing_(cls._must_contain)})')

        if cls._must_contain_only:
            parts.append(f'containing_only({cls._repr_containing_only_(cls._must_contain_only)})')

        if cls._must_contain_exactly:
            parts.append(f'containing_exactly({cls._repr_containing_exactly_(cls._must_contain_exactly)})')

        if cls._must_not_contain:
            parts.append(f'not_containing({cls._repr_not_containing_(cls._must_not_contain)})')

        return '.'.join(parts)


class _GenerativeMethod(Protocol):
    def __call__(cls: _CheckerType, *args, **kwargs) -> _CheckerType: ...


def _generative(fn: _GenerativeMethod) -> _GenerativeMethod:

    @functools.wraps(fn)
    def wrapped(cls: _CheckerType, *args, **kwargs) -> _CheckerType:
        clone = typing.cast(_CheckerType, type(cls.__name__, (cls,), {}))
        fn(clone, *args, **kwargs)
        return clone

    return wrapped


class _BaseCollectionValuesChecker(typing.Generic[_ItemType]):
    _collection_type: typing.Type[BaseCollection] = None
    _must_contain: typing.Tuple[_ItemType, ...] = ()
    _must_contain_only: typing.Tuple[_ItemType, ...] = ()
    _must_contain_exactly: typing.Tuple[_ItemType, ...] = ()
    _must_not_contain: typing.Tuple[_ItemType, ...] = ()
    _must_be_empty: bool = False
    _must_not_be_empty: bool = False

    def __init_subclass__(cls, **kwargs):
        cls._collection_type = next((base for base in reversed(cls.__mro__) if issubclass(base, BaseCollection)), None)

    @classmethod
    def _process_items(cls, items) -> typing.Iterable[_ItemType]:
        return cls._unpack_generators(items)

    @classmethod
    def _unpack_generators(cls, items) -> typing.Iterable[_ItemType]:
        for item in items:
            if inspect.isgenerator(item):
                yield from item
            else:
                yield item

    @classmethod
    @_generative
    def containing(cls, *items):
        cls._must_contain += tuple(cls._process_items(items))

    @classmethod
    @_generative
    def containing_only(cls, *items):
        cls._must_contain_only += tuple(cls._process_items(items))

    @classmethod
    @_generative
    def containing_exactly(cls, *items):
        cls._must_contain_exactly += tuple(cls._process_items(items))

    @classmethod
    @_generative
    def not_containing(cls, *items):
        cls._must_not_contain += tuple(cls._process_items(items))

    @classmethod
    @_generative
    def empty(cls):
        cls._must_be_empty = True

    @classmethod
    @_generative
    def not_empty(cls):
        cls._must_not_be_empty = True

    @classmethod
    def _repr_containing_(cls, must_contain):
        return ', '.join(repr(item) for item in must_contain)

    @classmethod
    def _repr_containing_only_(cls, must_contain_only):
        return cls._repr_containing_(must_contain_only)

    @classmethod
    def _repr_containing_exactly_(cls, must_contain_exactly):
        return cls._repr_containing_(must_contain_exactly)

    @classmethod
    def _repr_not_containing_(cls, must_not_contain):
        return cls._repr_containing_(must_not_contain)

    @classmethod
    def _collection_is_empty_(cls, collection) -> bool:
        return len(collection) == 0

    @classmethod
    def _collection_contains_(cls, collection, v) -> bool:
        return v in collection

    @classmethod
    def _collection_iter_(cls, collection) -> typing.Iterable[_ItemType]:
        return collection


class _CollectionValuesChecker(_BaseCollectionValuesChecker[typing.Any]):
    pass


class _DictValuesChecker(_BaseCollectionValuesChecker[typing.Tuple[typing.Hashable, typing.Any]]):
    @classmethod
    def _process_items(
        cls,
        items: typing.Union[typing.Hashable, typing.Dict],
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
        return super().containing(*items, kwargs)

    @classmethod
    def containing_only(cls: T, *items, **kwargs) -> T:
        return super().containing_only(*items, kwargs)

    @classmethod
    def containing_exactly(cls: T, *items, **kwargs) -> T:
        return super().containing_exactly(*items, kwargs)

    @classmethod
    def not_containing(cls: T, *items, **kwargs) -> T:
        return super().not_containing(*items, kwargs)

    @classmethod
    def _repr_containing_(cls, must_contain):
        return dict(must_contain)

    @classmethod
    def _collection_contains_(cls, collection, v) -> bool:
        k, v = v
        return k in collection and collection[k] == v

    @classmethod
    def _collection_iter_(cls, collection) -> typing.Iterable[typing.Tuple[typing.Hashable, typing.Any]]:
        return collection.items()


class Collection(_CollectionValuesChecker, BaseCollection, metaclass=_CollectionValuesCheckerMeta):
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

    >>> List.containing_only(1, 2) == [1, 2, 3]
    False
    >>> List.containing_only(1, 2) == [1, 2, 2]
    True
    >>> List.containing_only(4, 5, 6) == [4, 5, 6]
    True
    >>> List.containing_only(4, 5, 6, 7) == [4, 5, 6]
    True

    >>> List.containing_exactly(1, 2) == [1, 2, 3]
    False
    >>> List.containing_exactly(4, 5, 6, 7) == [4, 5, 6]
    False
    >>> List.containing_exactly(5, 6, 4) == [4, 5, 6]
    True
    >>> List.containing_exactly(4, 5) == [4, 5, 5]
    False
    >>> List.containing_exactly(5, 4, 5) == [4, 5, 5]
    True

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
    """Special class enabling equality comparisons to check items in a dict

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


class Model:
    """Special class for comparing the equality of attrs of another object

    Examples of functionality:

    >>> from collections import namedtuple
    >>> Foo = namedtuple('Foo', 'id,key,other_key,parent', defaults=(None,)*4)

    >>> Foo() == Model()
    True

    >>> Foo(key='value') == Model(key='value')
    True
    >>> Foo(key='value') == Model(key='not the value')
    False
    >>> Foo(key='value', other_key='other_value') == Model(key='value')
    True
    >>> [Foo(key='value', other_key='other_value')] == List.containing(Model(key='value'))
    True

    """

    __slots__ = ('attrs',)

    def __init__(self, **attrs):
        self.attrs = attrs

    def __repr__(self):
        attrs_repr = ', '.join(f'{k}={v!r}' for k, v in self.attrs.items())
        return f'{self.__class__.__name__}({attrs_repr})'

    def __eq__(self, other):
        try:
            assert_model_attrs(other, self.attrs)
        except AssertionError:
            return False
        else:
            return True
