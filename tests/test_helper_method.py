import datetime

from aws_croniter.awscron import AWSCron


def test_get_all_schedule_bw_dates():
    """Testing - retrieve all datetimes between a start and end date when AWS cron expression is set to
    run every 23 minutes. cron(Minutes Hours Day-of-month Month Day-of-week Year)
    Where start datetime is 8/7/2021 8:30:57 UTC
    Where end datetime is 8/7/2021 11:30:57 UTC
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
    ]
    from_dt = datetime.datetime(2021, 8, 7, 8, 30, 57, tzinfo=datetime.timezone.utc)
    to_date = datetime.datetime(2021, 8, 7, 11, 30, 57, tzinfo=datetime.timezone.utc)
    result = AWSCron.get_all_schedule_bw_dates(from_dt, to_date, "0/23 * * * ? *")
    assert str(expected_list) == str(result)


def test_get_all_schedule_bw_dates_accept_datetime():
    """Testing - retrieve all datetimes between a start and end date when AWS cron expression is set to
    run on every 2:01, 3rd day, April, 2022 (specific datetime).
    Where start datetime is 8/7/2021 8:30:57 UTC
    Where end datetime is 8/7/2021 11:30:57 UTC
    """
    expected_list = [datetime.datetime(2022, 4, 3, 2, 1, tzinfo=datetime.timezone.utc)]
    from_dt = datetime.datetime(2021, 8, 7, 8, 30, 57, tzinfo=datetime.timezone.utc)
    to_date = datetime.datetime(2022, 8, 7, 11, 30, 57, tzinfo=datetime.timezone.utc)
    result = AWSCron.get_all_schedule_bw_dates(from_dt, to_date, "1 2 3 4 5 2022")
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
