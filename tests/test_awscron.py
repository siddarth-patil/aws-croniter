import datetime

import pytest

from aws_croniter.awscron import AWSCron


@pytest.mark.parametrize(
    "cron_str,expected",
    [
        (
            "6 4/3 8,18-20,26-28 * ? 2020-2030",
            {
                "minutes": [6],
                "hours": [4, 7, 10, 13, 16, 19, 22],
                "daysOfMonth": [8, 18, 19, 20, 26, 27, 28],
                "months": list(range(1, 13)),
                "daysOfWeek": [],
                "years": [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030],
            },
        ),
        (
            "15 10 ? * 6L 2002-2025",
            {
                "minutes": [15],
                "hours": [10],
                "daysOfMonth": [],
                "months": list(range(1, 13)),
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
                "months": list(range(1, 13)),
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
                "months": list(range(1, 13)),
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
                "months": list(range(1, 13)),
                "daysOfWeek": [],
                "years": [2020],
            },
        ),
        (
            "0-29/5 22 09 05 ? 2020,2021,2022",
            {
                "minutes": list(range(0, 26, 5)),
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
                "months": list(range(1, 13)),
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
                "months": list(range(1, 13)),
                "daysOfWeek": [],
                "years": [x for x in range(1970, 2199 + 1)],
            },
        ),
    ],
    ids=[
        "Every-3-hours-multiple-days-2020-2030",
        "Last-Friday-monthly-2002-2025",
        "Every-5-minutes-Mon-to-Fri",
        "Every-3-hours-daily",
        "Specific-hours-Sunday-Monday",
        "Every-5-hours-on-7th-2020",
        "Every-5-minutes-in-May-2020-2022",
        "Second-last-day-of-month",
        "Closest-weekday-to-3rd",
    ],
)
def test_cron_expressions(cron_str, expected):
    # Validation followed by Parsing of cron expression
    cron_obj = AWSCron(cron_str)
    assert expected["minutes"] == cron_obj.minutes
    assert expected["hours"] == cron_obj.hours
    assert expected["daysOfMonth"] == cron_obj.days_of_month
    assert expected["months"] == cron_obj.months
    assert expected["daysOfWeek"] == cron_obj.days_of_week
    assert expected["years"] == cron_obj.years


@pytest.mark.parametrize(
    "from_dt, to_date, cron_expression, exclude_ends, expected_list",
    [
        (
            datetime.datetime(2021, 8, 7, 8, 30, 57, tzinfo=datetime.timezone.utc),
            datetime.datetime(2021, 8, 7, 11, 30, 57, tzinfo=datetime.timezone.utc),
            "0/23 * * * ? *",
            False,
            [
                datetime.datetime(2021, 8, 7, 8, 46, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 9, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 9, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 9, 46, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 10, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 10, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 10, 46, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 11, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 11, 23, tzinfo=datetime.timezone.utc),
            ],
        ),
        (
            datetime.datetime(2021, 8, 7, 8, 30, 57, tzinfo=datetime.timezone.utc),
            datetime.datetime(2022, 8, 7, 11, 30, 57, tzinfo=datetime.timezone.utc),
            "1 2 3 4 ? 2022",
            False,
            [datetime.datetime(2022, 4, 3, 2, 1, tzinfo=datetime.timezone.utc)],
        ),
        (
            datetime.datetime(2021, 8, 7, 8, 46, 57, tzinfo=datetime.timezone.utc),
            datetime.datetime(2021, 8, 7, 11, 23, 57, tzinfo=datetime.timezone.utc),
            "0/23 * * * ? *",
            True,
            [
                datetime.datetime(2021, 8, 7, 9, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 9, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 9, 46, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 10, 0, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 10, 23, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 10, 46, tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 8, 7, 11, 0, tzinfo=datetime.timezone.utc),
            ],
        ),
    ],
    ids=[
        "test_regular_schedule_23_minutes",
        "test_specific_datetime_schedule",
        "test_exclude_bounds_schedule",
    ],
)
def test_get_all_schedule_bw_dates(from_dt, to_date, cron_expression, exclude_ends, expected_list):
    """
    Parameterized test for retrieving all schedule times between dates.
    """
    result = AWSCron.get_all_schedule_bw_dates(from_dt, to_date, cron_expression, exclude_ends)
    assert str(expected_list) == str(result)


def test_get_next_n_schedule():
    """Testing - retrieve n number of datetimes after start date when AWS cron expression is set to
    run every 23 minutes. cron(Minutes Hours Day-of-month Month Day-of-week Year)
    Where start datetime is 8/7/2021 8:30:57 UTC
    """
    expected_list = [
        datetime.datetime(2021, 8, 7, 8, 46, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 9, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 9, 23, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 9, 46, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 10, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 10, 23, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 10, 46, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 11, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 11, 23, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 11, 46, tzinfo=datetime.timezone.utc),
    ]
    from_dt = datetime.datetime(2021, 8, 7, 8, 30, 57, tzinfo=datetime.timezone.utc)
    result = AWSCron.get_next_n_schedule(10, from_dt, "0/23 * * * ? *")
    assert str(expected_list) == str(result)  # noqa: S101


def test_get_prev_n_schedule_1():
    """Testing - retrieve n number of datetimes before start date when AWS cron expression is set to
    run every 23 minutes. cron(Minutes Hours Day-of-month Month Day-of-week Year)
    Where start datetime is 8/7/2021 11:50:57 UTC
    """
    expected_list = [
        datetime.datetime(2021, 8, 7, 11, 46, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 11, 23, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 11, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 10, 46, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 10, 23, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 10, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 9, 46, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 9, 23, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 9, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 7, 8, 46, tzinfo=datetime.timezone.utc),
    ]
    from_dt = datetime.datetime(2021, 8, 7, 11, 50, 57, tzinfo=datetime.timezone.utc)
    result = AWSCron.get_prev_n_schedule(10, from_dt, "0/23 * * * ? *")
    assert str(expected_list) == str(result)


def test_get_prev_n_schedule_2():
    """Testing - retrieve n number of datetimes before start date when AWS cron expression is set to
    run every 5 minutes Monday through Friday between 8:00 am and 5:55 pm (UTC).
    cron(Minutes Hours Day-of-month Month Day-of-week Year)
    Where start datetime is 8/16/2021 8:50:57 UTC
    """
    expected_list = [
        datetime.datetime(2021, 8, 16, 8, 45, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 16, 8, 40, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 16, 8, 35, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 16, 8, 30, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 16, 8, 25, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 16, 8, 20, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 16, 8, 15, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 16, 8, 10, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 16, 8, 5, tzinfo=datetime.timezone.utc),
        datetime.datetime(2021, 8, 16, 8, 0, tzinfo=datetime.timezone.utc),
    ]
    from_dt = datetime.datetime(2021, 8, 16, 8, 50, 57, tzinfo=datetime.timezone.utc)
    result = AWSCron.get_prev_n_schedule(10, from_dt, "0/5 8-17 ? * MON-FRI *")
    assert str(expected_list) == str(result)
