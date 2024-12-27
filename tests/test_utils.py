import datetime

import pytest

from aws_croniter.utils import DateUtils
from aws_croniter.utils import SequenceUtils
from aws_croniter.utils import TimeUtils



@pytest.mark.parametrize(
    "year, month, days_of_week, expected",
    [
        (2023, 9, [2], [4, 11, 18, 25]),  # Mondays in September 2023
        (2023, 9, [7], [2, 9, 16, 23, 30]),  # Saturdays in September 2023
        (2024, 2, ["L", 2], [26]),  # Last Monday of February 2024 (Leap Year)
        (2023, 11, ["#", 4, 2], [8]),  # 2nd Wednesday of November 2023
        (2023, 11, ["#", 6, 3], [17]),  # 3rd Friday of November 2023
        (2023, 12, [2, 3], [4, 5, 11, 12, 18, 19, 25, 26]),  # Mondays and Tuesdays in December 2023
        (2023, 2, [1], [5, 12, 19, 26]),  # Sundays in February 2023 (Non-Leap Year)
        (2023, 4, ["L", 7], [29]),  # Last Saturday of April 2023
        (2023, 6, ["#", 3, 1], [6]),  # 1st Tuesday of June 2023
    ],
    ids=[
        "Mondays_September_2023",
        "Saturdays_September_2023",
        "Last_Monday_February_2024",
        "Second_Wednesday_November_2023",
        "Third_Friday_November_2023",
        "Mondays_Tuesdays_December_2023",
        "Sundays_February_2023",
        "Last_Saturday_April_2023",
        "First_Tuesday_June_2023",
    ],
)
def test_get_days_of_month_from_days_of_week(year, month, days_of_week, expected):
    """Test DateUtils.get_days_of_month_from_days_of_week with various inputs."""
    assert DateUtils.get_days_of_month_from_days_of_week(year, month, days_of_week) == expected

@pytest.mark.parametrize(
    "year, month, day, expected",
    [
        (2024, 2, 29, [29]),  # Leap year, valid weekday (Fri)
        (2023, 2, 28, [28]),  # Non-leap year, last valid day (Tue)
        (2023, 6, 3, [2]),  # Weekend (Sat), adjusts to nearest weekday (Fri)
        (2023, 6, 17, [16]),  # Weekend (Sat), adjusts backward (Fri)
        (2023, 4, 5, [5]),  # Valid weekday (Wed), no adjustment needed
        (2023, 12, 25, [25]),  # Valid weekday (Mon), no adjustment
        (2023, 12, 26, [26]),  # Valid weekday (Tue), no adjustment
        (2024, 2, 35, [])
    ],
    ids=[
        "Leap_Year_Valid",
        "Non_Leap_Year_Valid_Last_Day",
        "Weekend_Adjust_Backward",
        "Weekend_Adjust_Backward_Again",
        "Valid_Weekday",
        "Valid_Weekday_Christmas",
        "Valid_Weekday_Adjacent",
        "Invalid_Day_Beyond_Last"
    ],
)
def test_get_days_of_month_for_W(year, month, day, expected):
    """Test DateUtils.get_days_of_month_for_W with various inputs."""
    assert DateUtils.get_days_of_month_for_W(year, month, day) == expected

@pytest.mark.parametrize(
    "year, month, day, expected",
    [
        # Test for valid weekdays (Mon-Fri)
        (2023, 12, 25, True),  # Christmas 2023 (Monday)
        (2023, 12, 26, True),  # Tuesday
        (2023, 12, 27, True),  # Wednesday
        (2023, 12, 28, True),  # Thursday
        (2023, 12, 29, True),  # Friday
        # Test for weekends (Sat-Sun)
        (2023, 12, 30, False),  # Saturday
        (2023, 12, 31, False),  # Sunday
        # Test for invalid days
        (2023, 12, 32, False),  # Invalid day
        (2023, 2, 30, False),  # Invalid day for February in a non-leap year
        # Test for edge cases
        (2023, 2, 28, True),  # Last valid day of February in a non-leap year
        (2024, 2, 29, True),  # Leap year February 29
        # Test for different months and boundaries
        (2023, 1, 1, False),  # January 1st (Sunday)
        (2023, 1, 2, True),  # January 2nd (Monday)
    ],
    ids=[
        "Christmas_Monday_2023",
        "Tuesday_2023",
        "Wednesday_2023",
        "Thursday_2023",
        "Friday_2023",
        "Saturday_2023",
        "Sunday_2023",
        "Invalid_Day_32",
        "Invalid_February_30",
        "Last_February_Day_2023",
        "Leap_Year_February_29_2024",
        "New_Year_Sunday_2023",
        "Monday_January_2_2023",
    ],
)
def test_is_weekday(year, month, day, expected):
    """Test DateUtils.is_weekday with various inputs."""
    assert DateUtils.is_weekday(year, month, day) == expected


@pytest.mark.parametrize(
    "dt_obj, expected",
    [
        (datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc), 0),  # Epoch start
        (datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc), 946684800000),  # Y2K
        (datetime.datetime(2024, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc), 1704067200000),  # Future date
        (datetime.datetime(2023, 12, 25, 12, 0, 0, tzinfo=datetime.timezone.utc), 1703505600000),  # Christmas 2023
        (datetime.datetime(1900, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc), -2208988800000),  # Pre-epoch
    ],
    ids=[
        "Epoch_Start",
        "Y2K",
        "Future_2024",
        "Christmas_2023",
        "Pre_Epoch_1900",
    ],
)
def test_datetime_to_millisec(dt_obj, expected):
    """Test TimeUtils.datetime_to_millisec with various inputs."""
    assert TimeUtils.datetime_to_millisec(dt_obj) == expected

@pytest.mark.parametrize(
    "year, month, test_day, expected",
    [
        (2024, 2, 29, True),  # Leap year, valid date
        (2023, 2, 29, False),  # Non-leap year, invalid date
        (2023, 4, 30, True),  # Valid end-of-month date (April)
        (2023, 4, 31, False),  # Invalid end-of-month date (April)
        (2023, 12, 0, False),  # Invalid day (zero)
        (2023, 12, 32, False),  # Invalid day (over max day)
        (2023, 6, -1, False),  # Invalid negative day
    ],
    ids=[
        "Leap_Year_Valid",
        "Non_Leap_Year_Invalid",
        "Valid_End_Of_Month",
        "Invalid_End_Of_Month",
        "Invalid_Day_Zero",
        "Invalid_Day_Over_Max",
        "Invalid_Negative_Day",
    ]
)
def test_is_day_in_month(year, month, test_day, expected):
    """Test DateUtils.is_day_in_month with various inputs."""
    assert DateUtils.is_day_in_month(year, month, test_day) == expected


@pytest.mark.parametrize(
    "sequence, function, expected",
    [
        ([1, 2, 3, 4, 5], lambda x: x > 3, 4),  # First > 3
        ([10, 20, 30, 40], lambda x: x == 25, None),  # Not found
        ([0, -1, -2, -3], lambda x: x < 0, -1),  # First negative
        ([], lambda x: x == 1, None),  # Empty sequence
        ([100, 200, 300], lambda x: x > 50, 100),  # First > 50
    ],
    ids=[
        "First_Over_3",
        "Not_Found",
        "First_Negative",
        "Empty_Sequence",
        "First_Over_50",
    ],
)
def test_array_find_first(sequence, function, expected):
    """Test SequenceUtils.array_find_first with various inputs."""
    assert SequenceUtils.array_find_first(sequence, function) == expected


@pytest.mark.parametrize(
    "sequence, function, expected",
    [
        ([1, 2, 3, 4, 5], lambda x: x > 3, 5),  # Last > 3
        ([10, 20, 30, 40], lambda x: x == 25, None),  # Not found
        ([0, -1, -2, -3], lambda x: x < 0, -3),  # Last negative
        ([], lambda x: x == 1, None),  # Empty sequence
        ([100, 200, 300], lambda x: x > 50, 300),  # Last > 50
    ],
    ids=[
        "Last_Over_3",
        "Not_Found",
        "Last_Negative",
        "Empty_Sequence",
        "Last_Over_50",
    ],
)
def test_array_find_last(sequence, function, expected):
    """Test SequenceUtils.array_find_last with various inputs."""
    assert SequenceUtils.array_find_last(sequence, function) == expected
