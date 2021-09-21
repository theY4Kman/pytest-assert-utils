from dataclasses import make_dataclass
from datetime import datetime
from functools import partial
from typing import Type, TypeVar

import pytest
from pytest_lambda import lambda_fixture

from pytest_assert_utils import util
from pytest_assert_utils.util import decl


class DescribeAny:

    def it_compares_true_to_anything_with_no_args(self):
        example_values = [
            1,
            '2',
            3.0,
            b'4',
            object(),
            None,
            True,
            False,
        ]

        any_ = util.Any()
        inequal_values = [
            value
            for value in example_values
            if any_ != value
        ]

        assert not inequal_values, \
            'Unexpectedly found values which did not compare true to Any()'

    @pytest.mark.parametrize('expected,actual', [
        pytest.param(util.Any(int), 1, id='int'),
        pytest.param(util.Any(str), '1', id='str'),
        pytest.param(util.Any(datetime), datetime.today(), id='datetime'),
    ])
    def it_compares_true_to_values_of_same_type(self, expected, actual):
        assert expected == actual

    @pytest.mark.parametrize('expected,actual', [
        pytest.param(util.Any(int), '1', id='int'),
        pytest.param(util.Any(str), 1, id='str'),
        pytest.param(util.Any(datetime), None, id='datetime'),
    ])
    def it_compares_false_to_values_of_other_types(self, expected, actual):
        assert expected != actual

    def it_generates_string_repr_including_types(self):
        expected = {
            util.Any(): '<Any>',
            util.Any(int): '<Any int>',
            util.Any(int, str): '<Any int, str>',
        }
        actual = {
            instance: repr(instance)
            for instance in expected
        }
        assert expected == actual


CHECKER_CLASSES = (
    util.List,
    util.Set,
    util.Dict,
    util.Str,
)

CHECKER_COLLECTION_TYPES = {
    cls: cls.__bases__[1]
    for cls in CHECKER_CLASSES if cls is not util.Collection
}


_CT = TypeVar('_CT', bound=decl.BaseCollection)


def create_collection_of_type(collection_type: Type[_CT], *items) -> _CT:
    if issubclass(collection_type, dict):
        return {item: item for item in items}
    elif issubclass(collection_type, str):
        return ''.join(items)
    else:
        return collection_type(items)


class DescribeCollectionValuesChecker:

    checker_cls = lambda_fixture(params=[
        util.List,
        util.Set,
        util.Dict,
        util.Str,
    ])
    collection_type = lambda_fixture(lambda checker_cls: checker_cls._collection_type)
    create_collection = lambda_fixture(lambda collection_type: partial(create_collection_of_type, collection_type))


    class CaseType:
        checker_cls = lambda_fixture(params=CHECKER_CLASSES + (util.Collection,))

        compatible_collection_types = lambda_fixture(
            lambda checker_cls:
                set(CHECKER_COLLECTION_TYPES.values())
                if checker_cls is util.Collection
                else {CHECKER_COLLECTION_TYPES[checker_cls]}
        )

        incompatible_collection_types = lambda_fixture(
            lambda compatible_collection_types:
                set(CHECKER_COLLECTION_TYPES.values()) - compatible_collection_types)

        def it_compares_true_to_compatible_instances(self, checker_cls, compatible_collection_types):
            checker = checker_cls

            expected = compatible_collection_types
            actual = {cls for cls in CHECKER_COLLECTION_TYPES.values() if checker == cls()}
            assert expected == actual

        def it_doesnt_compare_true_to_incompatible_instances(self, checker_cls, incompatible_collection_types):
            checker = checker_cls

            expected = incompatible_collection_types
            actual = {cls for cls in CHECKER_COLLECTION_TYPES.values() if checker != cls()}
            assert expected == actual


    class DescribeEmpty:

        def it_compares_true_to_empty_collection(self, checker_cls, create_collection):
            collection = create_collection()
            assert len(collection) == 0  # sanity check

            expected = checker_cls.empty()
            actual = collection
            assert expected == actual

        def it_compares_false_to_nonempty_collection(self, checker_cls, create_collection):
            collection = create_collection('a')
            assert len(collection) > 0  # sanity check

            expected = checker_cls.empty()
            actual = collection
            assert expected != actual


    class DescribeNotEmpty:

        def it_compares_true_to_nonempty_collection(self, checker_cls, create_collection):
            collection = create_collection('a')
            assert len(collection) > 0  # sanity check

            expected = checker_cls.not_empty()
            actual = collection
            assert expected == actual

        def it_compares_false_to_empty_collection(self, checker_cls, create_collection):
            collection = create_collection()
            assert len(collection) == 0  # sanity check

            expected = checker_cls.not_empty()
            actual = collection
            assert expected != actual


    class DescribeContaining:

        def it_compares_true_to_collection_containing_values(self, checker_cls, create_collection):
            expected = checker_cls.containing('b', 'c')
            actual = create_collection(*'abcz')
            assert expected == actual

        def it_accepts_values_from_generator(self, checker_cls, create_collection):
            expected = checker_cls.containing(c for c in 'bc')
            actual = create_collection(*'abcz')
            assert expected == actual

        def it_compares_false_to_collection_not_containing_values(self, checker_cls, create_collection):
            expected = checker_cls.containing('b', 'c')
            actual = create_collection(*'acz')
            assert expected != actual


    class DescribeNotContaining:

        def it_compares_true_to_collection_not_containing_values(self, checker_cls, create_collection):
            expected = checker_cls.not_containing('b', 'd')
            actual = create_collection(*'acz')
            assert expected == actual

        def it_accepts_values_from_generator(self, checker_cls, create_collection):
            expected = checker_cls.not_containing(c for c in 'bd')
            actual = create_collection(*'acz')
            assert expected == actual

        def it_compares_false_to_collection_containing_values(self, checker_cls, create_collection):
            expected = checker_cls.not_containing('b', 'c')
            actual = create_collection(*'abcz')
            assert expected != actual


    class DescribeContainingOnly:

        def it_compares_true_to_collection_containing_only_values(self, checker_cls, create_collection):
            expected = checker_cls.containing_only('b', 'c')
            actual = create_collection(*'bc')
            assert expected == actual

        def it_accepts_values_from_generator(self, checker_cls, create_collection):
            expected = checker_cls.containing_only(c for c in 'bc')
            actual = create_collection(*'bc')
            assert expected == actual

        def it_compares_false_to_collection_containing_extra_values(self, checker_cls, create_collection):
            expected = checker_cls.containing_only('b', 'c')
            actual = create_collection(*'abcz')
            assert expected != actual

        def it_compares_false_to_collection_not_containing_values(self, checker_cls, create_collection):
            expected = checker_cls.containing_only('b', 'c')
            actual = create_collection(*'acz')
            assert expected != actual


    class DescribeContainingExactly:

        def it_compares_true_to_collection_containing_exactly_values(self, checker_cls, create_collection):
            expected = checker_cls.containing_exactly('a', 'b')
            actual = create_collection(*'ab')
            assert expected == actual

        def it_accepts_values_from_generator(self, checker_cls, create_collection):
            expected = checker_cls.containing_exactly(c for c in 'ab')
            actual = create_collection(*'ab')
            assert expected == actual

        def it_compares_false_to_collection_not_containing_values(self, checker_cls, create_collection):
            expected = checker_cls.containing_exactly('a', 'b')
            actual = create_collection(*'ac')
            assert expected != actual

        def it_compares_false_to_collection_containing_additional_values(self, checker_cls, create_collection):
            expected = checker_cls.containing_exactly('a', 'b')
            actual = create_collection(*'abc')
            assert expected != actual

        def it_compares_false_to_collection_containing_dupe_values(
            self, checker_cls, create_collection, collection_type
        ):
            if issubclass(collection_type, (dict, set)):
                pytest.xfail('dict and set do not support dupe values')

            expected = checker_cls.containing_exactly('a', 'b')
            actual = create_collection(*'aabb')
            assert expected != actual

        def it_compares_false_to_collection_containing_fewer_values(self, checker_cls, create_collection):
            expected = checker_cls.containing_exactly('a', 'b')
            actual = create_collection('a')
            assert expected != actual


    class DescribeRepr:

        def it_generates_string_repr_for_all_methods(self, checker_cls):
            checker = (
                checker_cls
                    .empty()
                    .not_empty()
                    .containing('uniq1')
                    .containing_only('uniq2')
                    .not_containing('uniq5')
            )
            if issubclass(checker_cls, dict):
                checker = checker.containing_exactly(uniq3='uniq4')
            else:
                checker = checker.containing_exactly('uniq3', 'uniq4')

            checker_repr = repr(checker)

            expected = {
                'empty',
                'not_empty',
                'containing',
                'containing_only',
                'containing_exactly',
                'not_containing',
                'uniq1',
                'uniq2',
                'uniq3',
                'uniq4',
                'uniq5',
            }
            actual = {s for s in expected if s in checker_repr}
            assert actual == expected


def create_object_with_attrs(**attrs):
    cls = make_dataclass('ExampleObject', attrs.keys())
    return cls(**attrs)


class DescribeModel:
    def it_compares_true_to_object_with_matching_attrs(self):
        expected = util.Model(a='alpha', b='beta')
        actual = create_object_with_attrs(a='alpha', b='beta')
        assert expected == actual

    def it_compares_false_to_object_with_differing_attr_values(self):
        expected = util.Model(a='alpha', b='beta')
        actual = create_object_with_attrs(a='agnes', b='bob')
        assert expected != actual

    def it_compares_false_to_object_with_missing_attr_values(self):
        expected = util.Model(a='alpha', b='beta')
        actual = create_object_with_attrs(a='alpha')
        assert expected != actual

    class DescribeRepr:
        def it_includes_attrs_and_values(self):
            checker = util.Model(uniq1='uniq2', uniq3='uniq4')
            checker_repr = repr(checker)

            expected = {
                'uniq1',
                'uniq2',
                'uniq3',
                'uniq4',
            }
            actual = {s for s in expected if s in checker_repr}
            assert actual == expected
