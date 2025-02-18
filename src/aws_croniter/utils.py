import calendar
import datetime

from dateutil.relativedelta import relativedelta


class RegexUtils:
    MINUTE_VALUES = r"(0?[0-9]|[1-5][0-9])"  # [0]0-59
    HOUR_VALUES = r"(0?[0-9]|1[0-9]|2[0-3])"  # [0]0-23
    MONTH_OF_DAY_VALUES = r"(0?[1-9]|[1-2][0-9]|3[0-1])"  # [0]1-31
    MONTH_OF_DAY_VALUES_WITH_L = r"(0?[1-9]|[1-2][0-9]|30)"  # [0]1-30
    MONTH_VALUES = r"(?i:0?[1-9]|1[0-2]|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)"  # [0]1-12 or JAN-DEC
    DAY_OF_WEEK_VALUES = r"(?i:[1-7]|SUN|MON|TUE|WED|THU|FRI|SAT)"  # 1-7 or SAT-SUN
    DAY_OF_WEEK_HASH = rf"({DAY_OF_WEEK_VALUES}#[1-5])"  # Day of the week in the Nth week of the month
    YEAR_VALUES = r"((19[7-9][0-9])|(2[0-1][0-9][0-9]))"  # 1970-2199

    @classmethod
    def range_regex(cls, values: str) -> str:
        return rf"({values}|(\*\-{values})|({values}\-{values})|({values}\-\*))"  # v , *-v , v-v or v-*

    @classmethod
    def list_range_regex(cls, values: str) -> str:
        range_ = cls.range_regex(values)
        return rf"({range_}(\,{range_})*)"  # One or more ranges separated by a comma

    @classmethod
    def slash_regex(cls, values: str) -> str:
        range_ = cls.range_regex(values)
        return rf"((\*|{range_}|{values})\/{values})"
        # Slash can be preceded by *, range, or a valid value and must be followed by a natural
        # number as the increment.

    @classmethod
    def list_slash_regex(cls, values: str) -> str:
        slash = cls.slash_regex(values)
        slash_or_range = rf"({slash}|{cls.range_regex(values)})"
        return rf"({slash_or_range}(\,{slash_or_range})*)"  # One or more separated by a comma

    @classmethod
    def common_regex(cls, values: str) -> str:
        return rf"({cls.list_range_regex(values)}|\*|{cls.list_slash_regex(values)})"  # values , - * /

    @classmethod
    def minute_regex(cls) -> str:
        return rf"^({cls.common_regex(cls.MINUTE_VALUES)})$"  # values , - * /

    @classmethod
    def hour_regex(cls) -> str:
        return rf"^({cls.common_regex(cls.HOUR_VALUES)})$"  # values , - * /

    @classmethod
    def day_of_month_regex(cls) -> str:
        return (
            rf"^({cls.common_regex(cls.MONTH_OF_DAY_VALUES)}|\?|L|L-({cls.MONTH_OF_DAY_VALUES_WITH_L})|LW|{cls.MONTH_OF_DAY_VALUES}W)$"
            # values , - * / ? L W
        )

    @classmethod
    def month_regex(cls):
        return rf"^({cls.common_regex(cls.MONTH_VALUES)})$"  # values , - * /

    @classmethod
    def day_of_week_regex(cls):
        range_list = cls.list_range_regex(cls.DAY_OF_WEEK_VALUES)
        return rf"^({range_list}|\*|\?|{cls.DAY_OF_WEEK_VALUES}L|L|L-[1-7]|{cls.DAY_OF_WEEK_HASH})$"
        # values , - * ? L #

    @classmethod
    def year_regex(cls):
        return rf"^({cls.common_regex(cls.YEAR_VALUES)})$"  # values , - * /


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
