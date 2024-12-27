import calendar
import datetime

from dateutil.relativedelta import relativedelta


class DateUtils:
    @staticmethod
    def python_to_aws_day_of_week(python_day_of_week):
        """Convert Python day of week (Mon=0) to AWS day of week (Mon=2)."""
        mapping = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 1}
        return mapping[python_day_of_week]

    @staticmethod
    def get_days_of_month_from_days_of_week(year, month, days_of_week):
        """Get all days of the month that match the given days of the week."""
        days_of_month = []
        index = 0  # only for "#" use case
        no_of_days_in_month = calendar.monthrange(year, month)[1]
        for i in range(1, no_of_days_in_month + 1, 1):
            this_date = datetime.datetime(year, month, i, tzinfo=datetime.timezone.utc)
            if this_date.month != month:  # Skip if already out of month
                break
            if days_of_week[0] == "L":
                if days_of_week[1] == DateUtils.python_to_aws_day_of_week(this_date.weekday()):
                    same_day_next_week = datetime.datetime.fromtimestamp(
                        int(this_date.timestamp()) + 7 * 24 * 3600, tz=datetime.timezone.utc
                    )
                    if same_day_next_week.month != this_date.month:
                        return [i]
            elif days_of_week[0] == "#":
                if days_of_week[1] == DateUtils.python_to_aws_day_of_week(this_date.weekday()):
                    index += 1
                if days_of_week[2] == index:
                    return [i]
            elif DateUtils.python_to_aws_day_of_week(this_date.weekday()) in days_of_week:
                days_of_month.append(i)
        return days_of_month

    @staticmethod
    def get_days_of_month_for_L(year, month, days_before):
        """Get the last day of the month adjusted by a specific number of days."""
        for i in range(31, 28 - 1, -1):
            this_date = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc) + relativedelta(days=i - 1)
            if this_date.month == month:
                return [i - days_before]

    @staticmethod
    def get_days_of_month_for_W(year, month, day):
        """
        Get the closest weekday for the specified day of the month.
        Adjusts for weekends and ensures the date is within the month.
        """
        offset = SequenceUtils.array_find_first([0, 1, -1, 2, -2], lambda c: DateUtils.is_weekday(year, month, day + c))
        if offset is None:
            return []
        result = day + offset
        return [result]

    @staticmethod
    def is_weekday(year, month, day):
        """Check if a specific day is a weekday (Mon-Fri)."""
        if day < 1 or day > 31:
            return False
        this_date = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc) + relativedelta(days=day - 1)
        if this_date.month != month or this_date.year != year:
            return False
        return this_date.weekday() >= 0 and this_date.weekday() <= 4  # Mon=0, Fri=4

    @staticmethod
    def is_day_in_month(year, month, test_day):
        """Check if a specific day exists in a given month."""
        try:
            datetime.datetime(year, month, test_day, tzinfo=datetime.timezone.utc)
            return True
        except ValueError:
            return False


class TimeUtils:
    @staticmethod
    def datetime_to_millisec(dt_obj):
        """Convert a datetime object to milliseconds since epoch."""
        return round(dt_obj.timestamp() * 1000)


class SequenceUtils:
    @staticmethod
    def array_find_first(sequence, function):
        """Find the first element in a sequence that satisfies the given function."""
        for item in sequence:
            if function(item):
                return item
        return None

    @staticmethod
    def array_find_last(sequence, function):
        """Find the last element in a sequence that satisfies the given function."""
        for item in reversed(sequence):
            if function(item):
                return item
        return None
