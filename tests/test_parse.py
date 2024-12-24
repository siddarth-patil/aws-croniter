import datetime

import pytest

from aws_croniter.awscron import AWSCron


def print_cron_results(cron_str, cron_obj):
    print(f"Input: {cron_str}")
    print("Result:")
    print(f"\t{cron_obj}")
    print(f"\tcron.minutes: {cron_obj.minutes}")
    print(f"\tcron.hours: {cron_obj.hours}")
    print(f"\tcron.days_of_month: {cron_obj.days_of_month}")
    print(f"\tcron.months: {cron_obj.months}")
    print(f"\tcron.days_of_week: {cron_obj.days_of_week}")
    print(f"\tcron.years: {cron_obj.years}")


def test_cron_expressions1():
    expected = {
        "minutes": [6],
        "hours": [4, 7, 10, 13, 16, 19, 22],
        "daysOfMonth": [8, 18, 19, 20, 26, 27, 28],
        "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "daysOfWeek": [],
        "years": [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
    }
    cron_str = "6 4/3 8,18-20,26-28 * ? 2020-2030"
    cron_obj = AWSCron(cron_str)
    print_cron_results(cron_str, cron_obj)
    assert expected["minutes"] == cron_obj.minutes
    assert expected["hours"] == cron_obj.hours
    assert expected["daysOfMonth"] == cron_obj.days_of_month
    assert expected["months"] == cron_obj.months
    assert expected["daysOfWeek"] == cron_obj.days_of_week
    assert expected["years"] == cron_obj.years


@pytest.mark.parametrize(
    "cron_str,expected",
    [
        (
            "15 10 ? * 6L 2002-2025",
            {
                "minutes": [15],
                "hours": [10],
                "daysOfMonth": [],
                "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "daysOfWeek": ["L", 6],
                "years": [x for x in range(2002, 2025 + 1)],
            },
        ),
        (
            "*/5 10 ? * MON-FRI *",
            {
                "minutes": [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
                "hours": [10],
                "daysOfMonth": [],
                "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "daysOfWeek": [2, 3, 4, 5, 6],
                "years": [x for x in range(1970, 2199 + 1)],
            },
        ),
        (
            "0 */3 */1 * ? *",
            {
                "minutes": [0],
                "hours": list(range(0, 22, 3)),
                "daysOfMonth": list(range(1, 32)),
                "months": list(range(1, 13)),
                "daysOfWeek": [],
                "years": [x for x in range(1970, 2199 + 1)],
            },
        ),
        (
            "15 12 ? * sun,mon *",
            {
                "minutes": [15],
                "hours": [12],
                "daysOfMonth": [],
                "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "daysOfWeek": [1, 2],
                "years": [x for x in range(1970, 2199 + 1)],
            },
        ),
        (
            "10 7/5 7 * ? 2020",
            {
                "minutes": [10],
                "hours": [7, 12, 17, 22],
                "daysOfMonth": [7],
                "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "daysOfWeek": [],
                "years": [2020],
            },
        ),
        (
            "0-29/5 22 09 05 ? 2020,2021,2022",
            {
                "minutes": [0, 5, 10, 15, 20, 25],
                "hours": [22],
                "daysOfMonth": [9],
                "months": [5],
                "daysOfWeek": [],
                "years": [2020, 2021, 2022],
            },
        ),
        (
            "30 9 L-2 * ? *",
            {
                "minutes": [30],
                "hours": [9],
                "daysOfMonth": ["L", 2],
                "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "daysOfWeek": [],
                "years": [x for x in range(1970, 2199 + 1)],
            },
        ),
        (
            "30 9 3W * ? *",
            {
                "minutes": [30],
                "hours": [9],
                "daysOfMonth": ["W", 3],
                "months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "daysOfWeek": [],
                "years": [x for x in range(1970, 2199 + 1)],
            },
        ),
    ],
)
def test_cron_expressions_parametrized(cron_str, expected):
    cron_obj = AWSCron(cron_str)
    print_cron_results(cron_str, cron_obj)
    assert expected["minutes"] == cron_obj.minutes
    assert expected["hours"] == cron_obj.hours
    assert expected["daysOfMonth"] == cron_obj.days_of_month
    assert expected["months"] == cron_obj.months
    assert expected["daysOfWeek"] == cron_obj.days_of_week
    assert expected["years"] == cron_obj.years


def test_cron_expressions10():
    cron_str = "0 9 ? * 2 *"
    expected_list = [
        "2022-01-03 09:00:00+00:00",
        "2022-01-10 09:00:00+00:00",
        "2022-01-17 09:00:00+00:00",
        "2022-01-24 09:00:00+00:00",
        "2022-01-31 09:00:00+00:00",
        "2022-02-07 09:00:00+00:00",
        "2022-02-14 09:00:00+00:00",
        "2022-02-21 09:00:00+00:00",
        "2022-02-28 09:00:00+00:00",
        "2022-03-07 09:00:00+00:00",
    ]
    cron = AWSCron(cron_str)
    dt = datetime.datetime(2021, 12, 31, 21, 0, 0, tzinfo=datetime.timezone.utc)
    print_cron_results(cron_str, cron)
    results = []
    for expected in expected_list:
        dt = cron.occurrence(dt).next()
        assert expected == str(dt)
