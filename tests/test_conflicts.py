import datetime

import pytest

from aws_croniter import ConflictCollectionMode
from aws_croniter import ConflictSearchOptions
from aws_croniter import find_conflicts
from aws_croniter.aws_croniter import AwsCroniter
from aws_croniter.exceptions import AwsCroniterConflictSearchLimitError
from aws_croniter.exceptions import AwsCroniterExpressionError

UTC = datetime.timezone.utc
FROM_DATE = datetime.datetime(2024, 1, 1, tzinfo=UTC)
TO_DATE = datetime.datetime(2024, 1, 31, 23, 59, tzinfo=UTC)
DENSE_RANGE_END = datetime.datetime(2024, 1, 2, tzinfo=UTC)

EXPR_SAME_DAY_NOON = "0 12 15 * ? 2024"
EXPR_SAME_DAY_NOON_PLUS_5 = "5 12 15 * ? 2024"
EXPR_SAME_DAY_1H15_LATER = "15 13 15 * ? 2024"
EXPR_SAME_DAY_1H_LATER = "0 13 15 * ? 2024"
EXPR_DENSE_EVERY_15 = "*/15 * * * ? 2024"
EXPR_DENSE_EVERY_10 = "*/10 * * * ? 2024"


def _pair(expr_a: str, expr_b: str, input_type: str) -> list:
    if input_type == "strings":
        return [expr_a, expr_b]
    if input_type == "croniter":
        return [AwsCroniter(expr_a), AwsCroniter(expr_b)]
    return [expr_a, AwsCroniter(expr_b)]


@pytest.mark.parametrize("input_type", ["strings", "croniter", "mixed"])
def test_exact_collision_with_string_or_croniter_inputs(input_type):
    expr_a = EXPR_SAME_DAY_NOON
    expr_b = EXPR_SAME_DAY_NOON
    result = find_conflicts(_pair(expr_a, expr_b, input_type), from_date=FROM_DATE, to_date=TO_DATE)

    assert result.has_conflict is True
    assert len(result.conflicts) == 1
    conflict = result.first_conflict
    assert conflict.separation == datetime.timedelta(0)
    assert {run.run_at for run in conflict.runs} == {datetime.datetime(2024, 1, 15, 12, 0, tzinfo=UTC)}
    assert {run.expression for run in conflict.runs} == {expr_a, expr_b}


@pytest.mark.parametrize(
    "second_expression,buffer,expected_has_conflict,expected_separation",
    [
        (EXPR_SAME_DAY_NOON_PLUS_5, datetime.timedelta(minutes=10), True, datetime.timedelta(minutes=5)),
        (
            EXPR_SAME_DAY_1H15_LATER,
            datetime.timedelta(hours=1, minutes=30),
            True,
            datetime.timedelta(hours=1, minutes=15),
        ),
        (EXPR_SAME_DAY_1H15_LATER, datetime.timedelta(hours=1), False, None),
        (EXPR_SAME_DAY_NOON_PLUS_5, datetime.timedelta(minutes=4), False, None),
    ],
    ids=["minutes_within_buffer", "hours_and_minutes_within_buffer", "hours_outside_buffer", "minutes_outside_buffer"],
)
def test_buffer_with_minutes_or_combined_hours_and_minutes(
    second_expression, buffer, expected_has_conflict, expected_separation
):
    result = find_conflicts(
        [EXPR_SAME_DAY_NOON, second_expression],
        from_date=FROM_DATE,
        to_date=TO_DATE,
        buffer=buffer,
    )

    assert result.has_conflict is expected_has_conflict
    if expected_has_conflict:
        assert result.first_conflict.separation == expected_separation
    else:
        assert result.conflicts == []


@pytest.mark.parametrize(
    "collection_mode,max_conflicts,expected_conflict_count",
    [
        (ConflictCollectionMode.FIRST, 1, 1),
        (ConflictCollectionMode.ALL, 3, 3),
    ],
)
def test_collection_mode_first_stops_early_and_all_collects_multiple(
    collection_mode, max_conflicts, expected_conflict_count
):
    result = find_conflicts(
        [EXPR_DENSE_EVERY_15, EXPR_DENSE_EVERY_10],
        from_date=FROM_DATE,
        to_date=DENSE_RANGE_END,
        buffer=datetime.timedelta(0),
        collection_mode=collection_mode,
        max_conflicts=max_conflicts,
    )

    assert result.has_conflict is True
    assert len(result.conflicts) == expected_conflict_count
    if collection_mode is ConflictCollectionMode.ALL:
        assert len({conflict.earliest for conflict in result.conflicts}) == expected_conflict_count
        assert all(conflict.separation == datetime.timedelta(0) for conflict in result.conflicts)


def test_sparse_schedules_report_no_conflict():
    result = find_conflicts(
        ["0 9 1 * ? 2024", "0 9 2 * ? 2024"],
        from_date=FROM_DATE,
        to_date=TO_DATE,
    )

    assert result.has_conflict is False
    assert result.conflicts == []


def test_invalid_expression_raises():
    with pytest.raises(AwsCroniterExpressionError):
        find_conflicts(["invalid cron", EXPR_SAME_DAY_NOON], from_date=FROM_DATE, to_date=TO_DATE)


@pytest.mark.parametrize(
    "expressions,match",
    [
        ([EXPR_SAME_DAY_NOON], "only one was provided"),
        ([], "none were provided"),
    ],
)
def test_rejects_too_few_expressions(expressions, match):
    with pytest.raises(ValueError, match=match):
        find_conflicts(expressions, from_date=FROM_DATE, to_date=TO_DATE)


def test_requires_utc_datetimes():
    with pytest.raises(ValueError, match="tzinfo"):
        find_conflicts(
            [EXPR_SAME_DAY_NOON, EXPR_SAME_DAY_1H_LATER],
            from_date=datetime.datetime(2024, 1, 1),
            to_date=TO_DATE,
        )


def test_max_expressions_limit():
    expressions = [f"0 {hour} 15 * ? 2024" for hour in range(5)]
    with pytest.raises(AwsCroniterConflictSearchLimitError, match="max_expressions"):
        find_conflicts(expressions, from_date=FROM_DATE, to_date=TO_DATE, max_expressions=3)


def test_max_total_occurrences_limit():
    with pytest.raises(AwsCroniterConflictSearchLimitError, match="max_total_occurrences"):
        find_conflicts(
            ["* * * * ? 2024", "30 * * * ? 2024"],
            from_date=FROM_DATE,
            to_date=datetime.datetime(2024, 1, 1, 6, 0, tzinfo=UTC),
            buffer=datetime.timedelta(0),
            max_total_occurrences=5,
        )


def test_conflict_search_options_object():
    options = ConflictSearchOptions.from_call(
        from_date=FROM_DATE,
        to_date=DENSE_RANGE_END,
        buffer=datetime.timedelta(0),
        collection_mode=ConflictCollectionMode.ALL,
        max_conflicts=2,
    )
    result = find_conflicts([EXPR_DENSE_EVERY_15, EXPR_DENSE_EVERY_10], options=options)

    assert result.has_conflict is True
    assert len(result.conflicts) == 2


def test_from_date_after_to_date_rejected():
    with pytest.raises(ValueError, match="from_date must be"):
        ConflictSearchOptions(from_date=TO_DATE, to_date=FROM_DATE)
