import calendar
import datetime
import time

from dateutil.relativedelta import relativedelta


class Commons:
    @staticmethod
    def python_to_aws_day_of_week(python_day_of_week):
        # MON, TUE, WED, THU, FRI, SAT, SUN
        map = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 1}
        return map[python_day_of_week]

    @staticmethod
    def aws_to_python_day_of_week(aws_day_of_week):
        # MON, TUE, WED, THU, FRI, SAT, SUN
        map = {2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 1: 6}
        return map[aws_day_of_week]

    @staticmethod
    def array_find_first(sequence, function):
        """
        Static method c >= (current_minute if is_same_date and hour == current_hour else 0)
        """
        for i in sequence:
            if function(i) == True:
                return i
        return None

    @staticmethod
    def array_find_last(sequence, function):
        """
        Static method c <= (current_minute if is_same_date and hour == current_hour else 0)
        """
        # Using reversed as an iterator to give an iterator to iterate upon
        # instead of fully reversing the list that will utilize lot of space.
        for seq in reversed(sequence):
            if function(seq) == True:
                return seq
        return None

    @staticmethod
    def get_days_of_month_from_days_of_week(year, month, days_of_week):
        days_of_month = []
        index = 0  # only for "#" use case
        no_of_days_in_month = calendar.monthrange(year, month)[1]
        for i in range(1, no_of_days_in_month + 1, 1):
            this_date = datetime.datetime(year, month, i, tzinfo=datetime.timezone.utc)
            # already after last day of month
            if this_date.month != month:
                break
            if days_of_week[0] == "L":
                if days_of_week[1] == Commons.python_to_aws_day_of_week(this_date.weekday()):
                    same_day_next_week = datetime.datetime.fromtimestamp(
                        int(this_date.timestamp()) + 7 * 24 * 3600, tz=datetime.timezone.utc
                    )
                    if same_day_next_week.month != this_date.month:
                        return [i]
            elif days_of_week[0] == "#":
                if days_of_week[1] == Commons.python_to_aws_day_of_week(this_date.weekday()):
                    index += 1
                if days_of_week[2] == index:
                    return [i]
            elif Commons.python_to_aws_day_of_week(this_date.weekday()) in days_of_week:
                days_of_month.append(i)
        return days_of_month

    @staticmethod
    def get_days_of_month_for_L(year, month, days_before):
        for i in range(31, 28 - 1, -1):
            this_date = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc) + relativedelta(days=i - 1)
            if this_date.month == month:
                return [i - days_before]
        raise Exception("get_days_of_month_for_L - should not happen")

    @staticmethod
    def get_days_of_month_for_W(year, month, day):
        # offset = [0, 1, -1, 2, -2].find((c) => is_weekday(year, month, day + c))
        offset = Commons.array_find_first([0, 1, -1, 2, -2], lambda c: Commons.is_weekday(year, month, day + c))
        if offset is None:
            raise Exception("get_days_of_month_for_W, offset is None which should never happen")
        result = day + offset

        last_day_of_month = calendar.monthrange(year, month)[1]
        if result > last_day_of_month:
            return []
        return [result]

    @staticmethod
    def is_weekday(year, month, day):
        if day < 1 or day > 31:
            return False
        this_date = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc) + relativedelta(days=day - 1)
        if not (this_date.month == month and this_date.year == year):
            return False
        # pyhthon: Mon:0 Friday:4
        return this_date.weekday() >= 0 and this_date.weekday() <= 4

    @staticmethod
    def current_milli_time():
        return round(time.time() * 1000)

    @staticmethod
    def datetime_to_millisec(dt_obj):
        return dt_obj.timestamp() * 1000

    @staticmethod
    def is_day_in_month(year, month, test_day):
        try:
            this_date = datetime.datetime(year, month, test_day, tzinfo=datetime.timezone.utc)
            return True
        except ValueError as e:
            if str(e) == "day is out of range for month":
                return False
