import pytest

from aws_croniter.utils import DateUtils


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
