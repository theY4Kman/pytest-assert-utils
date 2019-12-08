from datetime import datetime

import pytest

from pytest_assert_utils import util


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
    def it_compares_true_to_values_of_other_type(self, expected, actual):
        assert expected != actual
