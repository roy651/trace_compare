import importlib.util

import pytest

from trace_compare.align import get_nested_from_dict
from trace_compare.modes import (
    both_or_none,
    deep_equal,
    fuzzy_similar,
    numeric_similar,
    same_type_and_length,
    semantic_similar,
)


class TestExactMatch:
    def test_strings_ignore_surrounding_whitespace(self):
        assert deep_equal("  flights.book \n", "flights.book")
        assert not deep_equal("flights book", "flightsbook")

    def test_lists_ignore_order_but_count_duplicates(self):
        assert deep_equal(["a", "b", "c"], ["c", "a", "b"])
        assert not deep_equal([1, 2, 2], [1, 2, 1])
        assert not deep_equal([1, 2], [1, 2, 3])

    def test_nested_lists_and_dicts(self):
        assert deep_equal([{"app": "x", "tags": [1, 2]}], [{"tags": [2, 1], "app": " x"}])
        assert not deep_equal([{"app": "x"}], [{"app": "x", "extra": 1}])

    def test_numbers_compare_by_value_and_bool_falls_back_to_python_equality(self):
        assert deep_equal(1, 1.0)
        assert deep_equal(True, 1)
        assert not deep_equal(True, 2)

    def test_none_equals_only_none(self):
        assert deep_equal(None, None)
        assert not deep_equal(None, "")


class TestFuzzyMatch:
    def test_reworded_string_passes(self):
        assert fuzzy_similar("Book a flight from London to Tokyo", "Book a flight London to Tokyo")

    def test_different_string_fails(self):
        assert not fuzzy_similar("New York", "Washington")

    def test_string_lists_are_joined(self):
        assert fuzzy_similar(["search flights", "book flight"], ["search flights", "book the flight"])

    def test_mixed_types_fail(self):
        assert not fuzzy_similar("a b", ["a", "b"])


class TestApproximateNumeric:
    def test_scalars_within_absolute_tolerance(self):
        assert numeric_similar(356.00, 356.02)
        assert not numeric_similar(689.0, 289.0)

    def test_sequences_use_average_difference(self):
        assert numeric_similar([1.0, 2.0], [1.04, 2.04])
        assert not numeric_similar([1.0, 2.0], [1.0])
        assert numeric_similar([], [])


class TestListLength:
    def test_same_type_and_length(self):
        assert same_type_and_length([1, 2, 3], ["a", "b", "c"])
        assert not same_type_and_length([1, 2], [1, 2, 3])

    def test_different_types_fail(self):
        assert not same_type_and_length([1], (1,))

    def test_unsized_values_of_same_type_pass(self):
        assert same_type_and_length(3, 7)


class TestFieldExists:
    def test_one_sided_presence_fails(self):
        assert not both_or_none(["late"], None)
        assert both_or_none(None, None)
        assert both_or_none("x", "y")


@pytest.mark.skipif(importlib.util.find_spec("sentence_transformers") is not None, reason="extra installed")
def test_semantic_without_extra_names_the_extra():
    with pytest.raises(ImportError, match=r"trace-compare\[semantic\]"):
        semantic_similar("a", "b")


class TestFieldPaths:
    def test_dot_path(self):
        assert get_nested_from_dict({"a": {"b": 1}}, "a.b") == 1

    def test_list_fan_out_with_brackets(self):
        output = {"steps": [{"app": "flights"}, {"app": "payments"}, {"other": 1}]}
        assert get_nested_from_dict(output, "steps[].app") == ["flights", "payments", None]

    def test_missing_key_and_non_dict_root(self):
        assert get_nested_from_dict({"a": 1}, "b") is None
        assert get_nested_from_dict(["a"], "a") is None
