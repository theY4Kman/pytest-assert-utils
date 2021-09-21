# pytest-assert-utils

Handy assertion utilities for use with pytest


# Installation

```bash
pip install pytest-assert-utils
```


# Usage

## assert_dict_is_subset
```python
def assert_dict_is_subset(subset, superset, recursive=True)
```

Assert `subset` is a non-strict subset of `superset`

If this assertion fails, a pretty diff will be printed by pytest.

```pycon
>>> from pytest_assert_utils import assert_dict_is_subset

>>> expected = {'a': 12}
>>> actual = {'b': 20, 'a': 12}
>>> assert_dict_is_subset(expected, actual)

>>> expected = {'a': 12}
>>> actual = {'b': 50000}
>>> assert_dict_is_subset(expected, actual)
Traceback (most recent call last):
 ...
AssertionError
```

## assert_model_attrs
```python
def assert_model_attrs(instance, _d=UNSET, **attrs)
```

Assert a model instance has the specified attr values

May be passed a dict of attrs, or kwargs as attrs

```pycon
>>> from pytest_assert_utils import assert_model_attrs

>>> from collections import namedtuple
>>> Model = namedtuple('Model', 'id,key,other_key,parent', defaults=(None,)*4)

>>> assert_model_attrs(Model(), {})

>>> assert_model_attrs(Model(key='value'), {'key': 'value'})
>>> assert_model_attrs(Model(key='value'), key='value')
>>> assert_model_attrs(Model(key='value'), key='not the value')
Traceback (most recent call last):
 ...
AssertionError

>>> assert_model_attrs(Model(key='value', other_key='other_value'), key='value')
```

## Any
Meta-value which compares True to any object (of the specified type(s))

```pycon
>>> from pytest_assert_utils import util

>>> util.Any() == 'stuff'
True
>>> util.Any() == 1
True
>>> util.Any() == None
True
>>> util.Any() == object()
True

>>> util.Any(int) == 1
True
>>> util.Any(int) == '1'
False
```

## Optional
Meta-value which compares True to None or the optionally specified value

```pycon
>>> from pytest_assert_utils import util

>>> util.Optional() == None
True
>>> util.Optional() is None  # this will not work!
False
>>> util.Optional(24) == 24
True
>>> util.Optional(24) == None
True

>>> util.Optional(Any(int)) == 1
True
>>> util.Optional(Any(int)) == None
True
>>> util.Optional(Any(int)) == '1'
False
```

## Collection
Special class enabling equality comparisons to check items in any collection (list, set, tuple, etc)

```pycon
>>> from pytest_assert_utils import util

>>> util.Collection.containing(1) == [1, 2, 3]
True
>>> util.Collection.containing(1) == {1, 2, 3}
True
>>> util.Collection.containing(1) == (1, 2, 3)
True

>>> util.Collection.containing(1) == [4, 5, 6]
False
>>> util.Collection.containing(1) == {4, 5, 6}
False
>>> util.Collection.containing(1) == (4, 5, 6)
False
```

## List
Special class enabling equality comparisons to check items in a list

```pycon
>>> from pytest_assert_utils import util

>>> util.List.containing(1) == [1, 2, 3]
True
>>> util.List.containing(1) == [4, 5, 6]
False

>>> util.List.containing_only(1, 2) == [1, 2, 3]
False
>>> util.List.containing_only(1, 2) == [1, 2, 2]
True
>>> util.List.containing_only(4, 5, 6) == [4, 5, 6]
True
>>> util.List.containing_only(4, 5, 6, 7) == [4, 5, 6]
True

>>> util.List.containing_exactly(1, 2) == [1, 2, 3]
False
>>> util.List.containing_exactly(4, 5, 6, 7) == [4, 5, 6]
False
>>> util.List.containing_exactly(5, 6, 4) == [4, 5, 6]
True
>>> util.List.containing_exactly(4, 5) == [4, 5, 5]
False
>>> util.List.containing_exactly(5, 4, 5) == [4, 5, 5]
True

>>> util.List.not_containing(1) == [1, 2, 3]
False
>>> util.List.not_containing(1) == [4, 5, 6]
True

>>> util.List.empty() == [1, 2, 3]
False
>>> util.List.empty() == []
True

>>> util.List.not_empty() == [1, 2, 3]
True
>>> util.List.not_empty() == []
False
```

## Set
Special class enabling equality comparisons to check items in a set

```pycon
>>> from pytest_assert_utils import util

>>> util.Set.containing(1) == {1, 2, 3}
True
>>> util.Set.containing(1) == {4, 5, 6}
False

>>> util.Set.not_containing(1) == {1, 2, 3}
False
>>> util.Set.not_containing(1) == {4, 5, 6}
True

>>> util.Set.empty() == {1, 2, 3}
False
>>> util.Set.empty() == set()
True

>>> util.Set.not_empty() == {1, 2, 3}
True
>>> util.Set.not_empty() == set()
False
```

## Dict
Special class enabling equality comparisons to check items in a dict

```pycon
>>> from pytest_assert_utils import util

>>> util.Dict.containing('a') == {'a': 1, 'b': 2}
True
>>> util.Dict.containing(a=1) == {'a': 1, 'b': 2}
True
>>> util.Dict.containing({'a': 1}) == {'a': 1, 'b': 2}
True
>>> util.Dict.containing('a') == {'b': 2}
False
>>> util.Dict.containing(a=1) == {'b': 2}
False
>>> util.Dict.containing({'a': 1}) == {'b': 2}
False

>>> util.Dict.not_containing('a') == {'a': 1, 'b': 2}
False
>>> util.Dict.not_containing(a=1) == {'a': 1, 'b': 2}
False
>>> util.Dict.not_containing({'a': 1}) == {'a': 1, 'b': 2}
False
>>> util.Dict.not_containing('a') == {'b': 2}
True
>>> util.Dict.not_containing(a=1) == {'b': 2}
True
>>> util.Dict.not_containing({'a': 1}) == {'b': 2}
True

>>> util.Dict.empty() == {'a': 1, 'b': 2, 'c': 3}
False
>>> util.Dict.empty() == {}
True

>>> util.Dict.not_empty() == {'a': 1, 'b': 2, 'c': 3}
True
>>> util.Dict.not_empty() == {}
False
```

## Str
Special class enabling equality comparisons to check items in a string

```pycon
>>> from pytest_assert_utils import util

>>> util.Str.containing('app') == 'apple'
True
>>> util.Str.containing('app') == 'happy'
True
>>> util.Str.containing('app') == 'banana'
False

>>> util.Str.not_containing('app') == 'apple'
False
>>> util.Str.not_containing('app') == 'happy'
False
>>> util.Str.not_containing('app') == 'banana'
True

>>> util.Str.empty() == 'hamster'
False
>>> util.Str.empty() == ''
True

>>> util.Str.not_empty() == 'hamster'
True
>>> util.Str.not_empty() == ''
False
```

## Model
Special class enabling equality comparisons to check attrs of another object


```pycon
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
```
