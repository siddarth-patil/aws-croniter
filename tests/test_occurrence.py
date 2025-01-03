import datetime

import pytest

from aws_croniter.aws_croniter import AwsCroniter


def test_generate_next_occurrence_with_inclusive():
    cron = "23 17 25 7 ? 2020"
    expected_occurrence = "2020-07-25 17:23:00+00:00"
    cron = AwsCroniter(cron)
    dt = datetime.datetime(2020, 7, 25, 17, 23, 57, tzinfo=datetime.timezone.utc)
    dt = cron.occurrence(dt).next(inclusive=True)
    assert expected_occurrence == str(dt)


@pytest.mark.parametrize(
    "cron_expression, expected_list, start_datetime",
    [
        (
            "23,24,25 17,18 25 MAR/4 ? 2020,2021,2023,2028",
            [
                "2020-07-25 17:23:00+00:00",
                "2020-07-25 17:24:00+00:00",
                "2020-07-25 17:25:00+00:00",
                "2020-07-25 18:23:00+00:00",
                "2020-07-25 18:24:00+00:00",
                "2020-07-25 18:25:00+00:00",
                "2020-11-25 17:23:00+00:00",
                "2020-11-25 17:24:00+00:00",
                "2020-11-25 17:25:00+00:00",
                "2020-11-25 18:23:00+00:00",
            ],
            datetime.datetime(2020, 5, 9, 22, 30, 57, tzinfo=datetime.timezone.utc),
        ),
        (
            "15 10 ? * 6L 2002-2025",
            [
                "2020-05-29 10:15:00+00:00",
                "2020-06-26 10:15:00+00:00",
                "2020-07-31 10:15:00+00:00",
                "2020-08-28 10:15:00+00:00",
                "2020-09-25 10:15:00+00:00",
                "2020-10-30 10:15:00+00:00",
                "2020-11-27 10:15:00+00:00",
                "2020-12-25 10:15:00+00:00",
                "2021-01-29 10:15:00+00:00",
                "2021-02-26 10:15:00+00:00",
            ],
            datetime.datetime(2020, 5, 9, 22, 30, 57, tzinfo=datetime.timezone.utc),
        ),
        (
            "0 */3 */1 * ? *",
            [
                "2020-12-07 18:00:00+00:00",
                "2020-12-07 21:00:00+00:00",
                "2020-12-08 00:00:00+00:00",
                "2020-12-08 03:00:00+00:00",
            ],
            datetime.datetime(2020, 12, 7, 15, 57, 37, tzinfo=datetime.timezone.utc),
        ),
        (
            "15 12 ? * sun,mon *",
            [
                "2020-12-13 12:15:00+00:00",
                "2020-12-14 12:15:00+00:00",
                "2020-12-20 12:15:00+00:00",
                "2020-12-21 12:15:00+00:00",
            ],
            datetime.datetime(2020, 12, 7, 15, 57, 37, tzinfo=datetime.timezone.utc),
        ),
        (
            "10 7/5 7 * ? 2020,2021",
            [
                "2020-12-07 17:10:00+00:00",
                "2020-12-07 22:10:00+00:00",
                "2021-01-07 07:10:00+00:00",
                "2021-01-07 12:10:00+00:00",
            ],
            datetime.datetime(2020, 12, 7, 15, 57, 37, tzinfo=datetime.timezone.utc),
        ),
        (
            "0-29/5 22 09 05 ? 2020,2021,2022",
            [
                "2021-05-09 22:00:00+00:00",
                "2021-05-09 22:05:00+00:00",
                "2021-05-09 22:10:00+00:00",
                "2021-05-09 22:15:00+00:00",
                "2021-05-09 22:20:00+00:00",
                "2021-05-09 22:25:00+00:00",
                "2022-05-09 22:00:00+00:00",
                "2022-05-09 22:05:00+00:00",
                "2022-05-09 22:10:00+00:00",
                "2022-05-09 22:15:00+00:00",
                "2022-05-09 22:20:00+00:00",
                "2022-05-09 22:25:00+00:00",
            ],
            datetime.datetime(2020, 5, 9, 22, 30, 57, tzinfo=datetime.timezone.utc),
        ),
        (
            "30 9 L-2 * ? *",
            [
                "2020-05-29 09:30:00+00:00",
                "2020-06-28 09:30:00+00:00",
                "2020-07-29 09:30:00+00:00",
                "2020-08-29 09:30:00+00:00",
                "2020-09-28 09:30:00+00:00",
                "2020-10-29 09:30:00+00:00",
                "2020-11-28 09:30:00+00:00",
            ],
            datetime.datetime(2020, 5, 9, 22, 30, 57, tzinfo=datetime.timezone.utc),
        ),
        (
            "30 9 3W * ? *",
            [
                "2020-08-03 09:30:00+00:00",
                "2020-09-03 09:30:00+00:00",
                "2020-10-02 09:30:00+00:00",
            ],
            datetime.datetime(2020, 7, 31, 22, 30, 57, tzinfo=datetime.timezone.utc),
        ),
        (
            "0 0 31W * ? 2020",
            [
                "2020-05-29 00:00:00+00:00",
                "2020-07-31 00:00:00+00:00",
                "2020-08-31 00:00:00+00:00",
            ],
            datetime.datetime(2020, 4, 30, 22, 30, 57, tzinfo=datetime.timezone.utc),
        ),
        (
            "0 0 31W * ? *",
            [
                "2020-12-31 00:00:00+00:00",
                "2021-01-29 00:00:00+00:00",
            ],
            datetime.datetime(2020, 12, 30, 22, 30, 57, tzinfo=datetime.timezone.utc),
        ),
        (
            "5,4 * * * ? *",
            [
                "2020-04-30 23:04:00+00:00",
                "2020-04-30 23:05:00+00:00",
                "2020-05-01 00:04:00+00:00",
                "2020-05-01 00:05:00+00:00",
                "2020-05-01 01:04:00+00:00",
                "2020-05-01 01:05:00+00:00",
                "2020-05-01 02:04:00+00:00",
                "2020-05-01 02:05:00+00:00",
                "2020-05-01 03:04:00+00:00",
                "2020-05-01 03:05:00+00:00",
            ],
            datetime.datetime(2020, 4, 30, 22, 30, 57, tzinfo=datetime.timezone.utc),
        ),
        (
            "15 12 ? AUG,JUL mon,sun *",
            [
                "2021-07-04 12:15:00+00:00",
                "2021-07-05 12:15:00+00:00",
                "2021-07-11 12:15:00+00:00",
                "2021-07-12 12:15:00+00:00",
                "2021-07-18 12:15:00+00:00",
                "2021-07-19 12:15:00+00:00",
                "2021-07-25 12:15:00+00:00",
                "2021-07-26 12:15:00+00:00",
                "2021-08-01 12:15:00+00:00",
                "2021-08-02 12:15:00+00:00",
            ],
            datetime.datetime(2020, 12, 7, 15, 57, 37, tzinfo=datetime.timezone.utc),
        ),
    ],
)
def test_generate_next_occurrences(cron_expression, expected_list, start_datetime):
    cron = AwsCroniter(cron_expression)
    dt = start_datetime
    for expected in expected_list:
        dt = cron.occurrence(dt).next()
        assert expected == str(dt)


def test_generate_multiple_prev_occurrences1():
    """At 23, 24, and 25 minutes past the hour, at 05:00 PM and 06:00 PM,
    on day 25 of the month, every 4 months, March through December,
    only in 2019, 2020, 2021, 2023, and 2028
    cron(Minutes Hours Day-of-month Month Day-of-week Year)
    / ==>> This character is used to specify increments.
    """
    cron = "23,24,25 17,18 25 MAR/4 ? 2019,2020,2021,2023,2028"

    expected_list = [
        "2020-03-25 18:25:00+00:00",
        "2020-03-25 18:24:00+00:00",
        "2020-03-25 18:23:00+00:00",
        "2020-03-25 17:25:00+00:00",
        "2020-03-25 17:24:00+00:00",
        "2020-03-25 17:23:00+00:00",
        "2019-11-25 18:25:00+00:00",
        "2019-11-25 18:24:00+00:00",
        "2019-11-25 18:23:00+00:00",
        "2019-11-25 17:25:00+00:00",
    ]

    cron = AwsCroniter(cron)
    dt = datetime.datetime(2020, 5, 9, 22, 30, 57, tzinfo=datetime.timezone.utc)

    for expected in expected_list:
        dt = cron.occurrence(dt).prev()
        assert str(dt) == expected


def test_generate_prev_occurrence_with_inclusive():
    cron = "23 17 25 7 ? 2020"
    expected_occurrence = "2020-07-25 17:23:00+00:00"
    cron = AwsCroniter(cron)
    dt = datetime.datetime(2020, 7, 25, 17, 23, 57, tzinfo=datetime.timezone.utc)
    dt = cron.occurrence(dt).prev(inclusive=True)
    assert expected_occurrence == str(dt)
