"""
Approach inspired by https://github.com/pytest-dev/pytest-django/pull/223.
"""
from django.test import TestCase, TransactionTestCase
from pytest_django.plugin import validate_django_db


def pytest_collection_modifyitems(items):
    def get_marker_transaction(test):
        marker = test.get_marker('django_db')
        if marker:
            validate_django_db(marker)
            # As of pytest 3.6.1 or maybe 3.6 'transaction' is not longer a property of
            # the MarkInfo at this execution point anyway, so if we are in that context
            # then fallback to checking the kwargs for the presence of a transaction test case.
            return getattr(marker, 'transaction',  'transaction' in marker.kwargs)

        return None

    def has_fixture(test, fixture):
        funcargnames = getattr(test, 'funcargnames', None)
        return funcargnames and fixture in funcargnames

    def weight_test_case(test):
        """
        Key function for ordering test cases like the Django test runner.
        """
        is_test_case_subclass = test.cls and issubclass(test.cls, TestCase)
        is_transaction_test_case_subclass = test.cls and issubclass(test.cls, TransactionTestCase)

        if is_test_case_subclass or get_marker_transaction(test) is False:
            return 0
        elif has_fixture(test, 'db'):
            return 0

        if is_transaction_test_case_subclass or get_marker_transaction(test) is True:
            return 1
        elif has_fixture(test, 'transactional_db'):
            return 1

        return 0

    items.sort(key=weight_test_case)
