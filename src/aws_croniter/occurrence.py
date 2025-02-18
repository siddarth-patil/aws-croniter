import datetime
import math

from dateutil.relativedelta import relativedelta

from aws_croniter.utils import DateUtils
from aws_croniter.utils import SequenceUtils
from aws_croniter.utils import TimeUtils


class Occurrence:
    def __init__(self, AwsCroniter, utc_datetime):
        if utc_datetime.tzinfo is None or utc_datetime.tzinfo != datetime.timezone.utc:
            raise Exception("Occurrence utc_datetime must have tzinfo == datetime.timezone.utc")
        self.utc_datetime = utc_datetime
        self.cron = AwsCroniter
        self.iter = 0

    def __is_valid_date(self, year, month, day):
        try:
            datetime.datetime(year, month, day)
            return True
        except ValueError:
            return False

    def __find_once(self, parsed, datetime_from):
        if self.iter > 10:
            # This shouldn't happen, but iter > 10. This means that the method has been called recursively more than 10
            # times and still not found any valid date.
            # This is a safety check to prevent infinite loop. NONE is returned in this case. Example AWS cron
            # expression when this can occur is "30 9 L-30 2 ? *"
            return None
        self.iter += 1
        current_year = datetime_from.year
        current_month = datetime_from.month
        current_day_of_month = datetime_from.day
        current_hour = datetime_from.hour
        current_minute = datetime_from.minute

        year = SequenceUtils.array_find_first(parsed.years, lambda c: c >= current_year)
        if year is None:
            return None

        month = SequenceUtils.array_find_first(
            parsed.months, lambda c: c >= (current_month if year == current_year else 1)
        )
        if not month:
            return self.__find_once(parsed, datetime.datetime(year + 1, 1, 1, tzinfo=datetime.timezone.utc))

        is_same_month = True if year == current_year and month == current_month else False
        p_days_of_month = parsed.days_of_month
        is_w_in_current_month = None

        if len(p_days_of_month) == 0:
            p_days_of_month = DateUtils.get_days_of_month_from_days_of_week(year, month, parsed.days_of_week)
        elif p_days_of_month[0] == "L":
            p_days_of_month = DateUtils.get_days_of_month_for_L(year, month, int(p_days_of_month[1]))
        elif p_days_of_month[0] == "W":
            if DateUtils.is_day_in_month(year, month, int(p_days_of_month[1])):
                p_days_of_month = DateUtils.get_days_of_month_for_W(year, month, int(p_days_of_month[1]))
                is_w_in_current_month = True
            else:
                is_w_in_current_month = False
        if is_w_in_current_month is not None and not is_w_in_current_month:
            day_of_month = False
        else:
            day_of_month = SequenceUtils.array_find_first(
                p_days_of_month, lambda c: c >= (current_day_of_month if is_same_month else 1)
            )
        if not day_of_month or not self.__is_valid_date(year, month, day_of_month):
            dt = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc) + relativedelta(months=+1)
            return self.__find_once(parsed, dt)

        is_same_date = is_same_month and day_of_month == current_day_of_month

        hour = SequenceUtils.array_find_first(parsed.hours, lambda c: c >= (current_hour if is_same_date else 0))
        if hour is None:
            dt = datetime.datetime(year, month, day_of_month, tzinfo=datetime.timezone.utc) + relativedelta(days=+1)
            return self.__find_once(parsed, dt)

        minute = SequenceUtils.array_find_first(
            parsed.minutes, lambda c: c >= (current_minute if is_same_date and hour == current_hour else 0)
        )
        if minute is None:
            dt = datetime.datetime(year, month, day_of_month, hour, tzinfo=datetime.timezone.utc) + relativedelta(
                hours=+1
            )
            return self.__find_once(parsed, dt)

        return datetime.datetime(year, month, day_of_month, hour, minute, tzinfo=datetime.timezone.utc)

    def __find_prev_once(self, parsed, datetime_from: datetime):
        if self.iter > 10:
            # This shouldn't happen, but iter > 10. This means that the method has been called recursively more than 10
            # times and still not found any valid date.
            # This is a safety check to prevent infinite loop. NONE is returned in this case. Example AWS cron
            # expression when this can occur is "30 9 L-30 2 ? *"
            return None
        self.iter += 1
        current_year = datetime_from.year
        current_month = datetime_from.month
        current_day_of_month = datetime_from.day
        current_hour = datetime_from.hour
        current_minute = datetime_from.minute

        year = SequenceUtils.array_find_last(parsed.years, lambda c: c <= current_year)
        if year is None:
            return None

        month = SequenceUtils.array_find_last(
            parsed.months, lambda c: c <= (current_month if year == current_year else 12)
        )
        if not month:
            dt = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc) + relativedelta(seconds=-1)
            return self.__find_prev_once(parsed, dt)

        is_same_month = True if year == current_year and month == current_month else False
        p_days_of_month = parsed.days_of_month
        is_w_in_current_month = None

        if len(p_days_of_month) == 0:
            p_days_of_month = DateUtils.get_days_of_month_from_days_of_week(year, month, parsed.days_of_week)
        elif p_days_of_month[0] == "L":
            p_days_of_month = DateUtils.get_days_of_month_for_L(year, month, int(p_days_of_month[1]))
        elif p_days_of_month[0] == "W":
            if DateUtils.is_day_in_month(year, month, int(p_days_of_month[1])):
                p_days_of_month = DateUtils.get_days_of_month_for_W(year, month, int(p_days_of_month[1]))
                is_w_in_current_month = True
            else:
                is_w_in_current_month = False
        if is_w_in_current_month is not None and not is_w_in_current_month:
            day_of_month = False
        else:
            day_of_month = SequenceUtils.array_find_last(
                p_days_of_month, lambda c: c <= (current_day_of_month if is_same_month else 31)
            )

        if not day_of_month or not self.__is_valid_date(year, month, day_of_month):
            dt = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc) + relativedelta(seconds=-1)
            return self.__find_prev_once(parsed, dt)

        is_same_date = is_same_month and day_of_month == current_day_of_month

        hour = SequenceUtils.array_find_last(parsed.hours, lambda c: c <= (current_hour if is_same_date else 23))
        if hour is None:
            dt = datetime.datetime(year, month, day_of_month, tzinfo=datetime.timezone.utc) + relativedelta(seconds=-1)
            return self.__find_prev_once(parsed, dt)

        minute = SequenceUtils.array_find_last(
            parsed.minutes, lambda c: c <= (current_minute if is_same_date and hour == current_hour else 59)
        )
        if minute is None:
            dt = datetime.datetime(year, month, day_of_month, hour, tzinfo=datetime.timezone.utc) + relativedelta(
                seconds=-1
            )
            return self.__find_prev_once(parsed, dt)

        return datetime.datetime(year, month, day_of_month, hour, minute, tzinfo=datetime.timezone.utc)

    def next(self, inclusive=False):
        """
        Generate the next occurrence after the current time.

        :param inclusive: If True, include the current time if it matches a valid execution.
        :return: The next occurrence as a datetime object.
        """
        self.iter = 0
        from_epoch = (math.floor(TimeUtils.datetime_to_millisec(self.utc_datetime) / 60000.0) + 1) * 60000
        if inclusive:
            # Do not add extra minute, include current time
            from_epoch = math.floor(TimeUtils.datetime_to_millisec(self.utc_datetime) / 60000.0) * 60000
        dt = datetime.datetime.fromtimestamp(from_epoch / 1000.0, tz=datetime.timezone.utc)
        return self.__find_once(self.cron, dt)

    def prev(self, inclusive=False):
        """
        Generate the prev before the occurrence date value

        :param inclusive: If True, include the current time if it matches a valid execution.
        :return: The next occurrence as a datetime object.
        """
        self.iter = 0
        from_epoch = (math.floor(TimeUtils.datetime_to_millisec(self.utc_datetime) / 60000.0) - 1) * 60000
        if inclusive:
            # Do not subtract extra minute, include current time
            from_epoch = math.floor(TimeUtils.datetime_to_millisec(self.utc_datetime) / 60000.0) * 60000
        dt = datetime.datetime.fromtimestamp(from_epoch / 1000.0, tz=datetime.timezone.utc)
        return self.__find_prev_once(self.cron, dt)
