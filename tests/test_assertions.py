from collections import namedtuple

import pytest

from pytest_assert_utils import assert_dict_is_subset, assert_model_attrs


class DescribeAssertDictIsSubset:

    @pytest.mark.parametrize('expected, actual', [
        pytest.param(
            {},
            {},
            id='empty',
        ),
        pytest.param(
            {'key': 'value'},
            {'key': 'value'},
            id='non-strict-superset',
        ),
        pytest.param(
            {'key': 'value'},
            {'key': 'value',
             'other_key': 'other_value'},
            id='strict-superset',
        ),
        pytest.param(
            {'parent': {'key': 'value'}},
            {'parent': {'key': 'value',
                        'other_key': 'other_value'}},
            id='nested-strict-superset',
        ),
    ])
    def it_evaluates_equal_subsets_truthily(self, expected, actual):
        try:
            assert_dict_is_subset(expected, actual)
        except AssertionError as e:
            raise AssertionError('dict was unexpectedly not a subset') from e


    @pytest.mark.parametrize('expected, actual', [
        pytest.param(
            {'key': 'value'},
            {},
            id='empty',
        ),
        pytest.param(
            {'key': 'value',
             'other_key': 'other_value'},
            {'key': 'value'},
            id='expected-more',
        ),
        pytest.param(
            {'parent': {'key': 'value',
                        'other_key': 'other_value'}},
            {'parent': {'key': 'value'}},
            id='expected-more-nested',
        ),
    ])
    def it_evaluates_unequal_subsets_falsily(self, expected, actual):
        with pytest.raises(AssertionError):
            assert_dict_is_subset(expected, actual)

            # Assertion above should fail. If not, manually fail it.
            pytest.fail('dict was unexpectedly a subset')


class DescribeAssertModelAttrs:

    Model = namedtuple('Model',
                       ('id', 'key', 'other_key', 'parent'),
                       defaults=(None, None, None, None))

    @pytest.mark.parametrize('expected,actual', [
        pytest.param(
            {},
            Model(),
            id='empty',
        ),
        pytest.param(
            {'key': 'value'},
            Model(key='value'),
            id='non-strict-superset',
        ),
        pytest.param(
            {'key': 'value'},
            Model(key='value', other_key='other_value'),
            id='strict-superset',
        ),
    ])
    @pytest.mark.parametrize('as_kwargs', [
        pytest.param(False, id='passing-dict'),
        pytest.param(True, id='passing-kwargs'),
    ])
    def it_evaluates_equivalent_item_subsets_truthily(self, expected, actual, as_kwargs):
        if as_kwargs:
            assert_model_attrs(actual, **expected)
        else:
            assert_model_attrs(actual, expected)
