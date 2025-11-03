import datetime
import re

from aws_croniter.exceptions import AwsCroniterExpressionDayOfMonthError
from aws_croniter.exceptions import AwsCroniterExpressionDayOfWeekError
from aws_croniter.exceptions import AwsCroniterExpressionError
from aws_croniter.exceptions import AwsCroniterExpressionHourError
from aws_croniter.exceptions import AwsCroniterExpressionMinuteError
from aws_croniter.exceptions import AwsCroniterExpressionMonthError
from aws_croniter.exceptions import AwsCroniterExpressionYearError
from aws_croniter.occurrence import Occurrence
from aws_croniter.utils import RegexUtils


class AwsCroniter:
    MONTH_REPLACES = [
        ["JAN", "1"],
        ["FEB", "2"],
        ["MAR", "3"],
        ["APR", "4"],
        ["MAY", "5"],
        ["JUN", "6"],
        ["JUL", "7"],
        ["AUG", "8"],
        ["SEP", "9"],
        ["OCT", "10"],
        ["NOV", "11"],
        ["DEC", "12"],
    ]

    DAY_WEEK_REPLACES = [
        ["SUN", "1"],
        ["MON", "2"],
        ["TUE", "3"],
        ["WED", "4"],
        ["THU", "5"],
        ["FRI", "6"],
        ["SAT", "7"],
    ]

    def __init__(self, cron):
        self.cron = cron
        self.minutes = None
        self.hours = None
        self.days_of_month = None
        self.months = None
        self.days_of_week = None
        self.years = None
        self.rules = cron.split(" ")
        self.__validate()

    def __validate(self):
        """
        Validates these AWS EventBridge cron expressions, which are similar to, but not compatible with standard
        unix cron expressions:
        https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html#eb-cron-expressions

        | Field        | Values          | Wildcards     |
        | :----------: | :-------------: | :-----------: |
        | Minute       | 0-59            | , - * /       |
        | Hour         | 0-23            | , - * /       |
        | Day-of-month | 1-31            | , - * ? / L W |
        | Month        | 1-12 or JAN-DEC | , - * /       |
        | Day-of-week  | 1-7 or SUN-SAT  | , - * ? L #   |
        | Year         | 1970-2199       | , - * /       |
        """
        value_count = len(self.cron.split(" "))
        if value_count != 6:
            raise AwsCroniterExpressionError(
                f"Incorrect number of values in '{self.cron}'. 6 required, {value_count} provided."
            )

        minute, hour, day_of_month, month, day_of_week, year = self.cron.split(" ")

        if not ((day_of_month == "?" and day_of_week != "?") or (day_of_month != "?" and day_of_week == "?")):
            raise AwsCroniterExpressionError(
                f"Invalid combination of day-of-month '{day_of_month}' and day-of-week '{day_of_week}'."
                "One must be a question mark (?)"
            )

        if not re.fullmatch(RegexUtils.minute_regex(), minute):
            raise AwsCroniterExpressionMinuteError(f"Invalid minute value '{minute}'.")
        if not re.fullmatch(RegexUtils.hour_regex(), hour):
            raise AwsCroniterExpressionHourError(f"Invalid hour value '{hour}'.")
        if not re.fullmatch(RegexUtils.day_of_month_regex(), day_of_month):
            raise AwsCroniterExpressionDayOfMonthError(f"Invalid day-of-month value '{day_of_month}'.")
        if not re.fullmatch(RegexUtils.month_regex(), month):
            raise AwsCroniterExpressionMonthError(f"Invalid month value '{month}'.")
        if not re.fullmatch(RegexUtils.day_of_week_regex(), day_of_week):
            raise AwsCroniterExpressionDayOfWeekError(f"Invalid day-of-week value '{day_of_week}'.")
        if not re.fullmatch(RegexUtils.year_regex(), year):
            raise AwsCroniterExpressionYearError(f"Invalid year value '{year}'.")

        # If validation passes, then parse the cron expression
        self.__parse()

    def occurrence(self, utc_datetime):
        if utc_datetime.tzinfo is None or utc_datetime.tzinfo != datetime.timezone.utc:
            raise Exception("Occurrence utc_datetime must have tzinfo == datetime.timezone.utc")
        return Occurrence(self, utc_datetime)

    def __replace(self, s, rules):
        rs = str(s).upper()
        for rule in rules:
            rs = rs.replace(rule[0], rule[1])
        return rs

    def __parse(self):
        self.minutes = self.__parse_one_rule(self.rules[0], 0, 59)
        self.hours = self.__parse_one_rule(self.rules[1], 0, 23)
        self.days_of_month = self.__parse_one_rule(self.rules[2], 1, 31)
        self.months = self.__parse_one_rule(self.__replace(self.rules[3], AwsCroniter.MONTH_REPLACES), 1, 12)
        self.days_of_week = self.__parse_one_rule(self.__replace(self.rules[4], AwsCroniter.DAY_WEEK_REPLACES), 1, 7)
        self.years = self.__parse_one_rule(self.rules[5], 1970, 2199)

    @staticmethod
    def __parse_one_rule(rule, min_value, max_value):
        if rule == "?":
            return []
        if rule == "L":
            return ["L", 0]
        if rule.startswith("L-"):
            return ["L", int(rule[2:])]
        if rule.endswith("L"):
            return ["L", int(rule[0:-1])]
        if rule.endswith("W"):
            return ["W", int(rule[0:-1])]
        if "#" in rule:
            return ["#", int(rule.split("#")[0]), int(rule.split("#")[1])]

        allows = []
        for subrule in rule.split(","):
            if "/" in subrule:
                parts = subrule.split("/")
                start = None
                end = None
                if parts[0] == "*":
                    start = min_value
                    end = max_value
                elif "-" in parts[0]:
                    splits = parts[0].split("-")
                    start = int(splits[0])
                    end = int(splits[1])
                else:
                    start = int(parts[0])
                    end = max_value
                increment = int(parts[1])
                allows.extend(range(start, end + 1, increment))
            elif "-" in subrule:
                start, end = map(int, subrule.split("-"))
                allows.extend(range(start, end + 1))
            elif subrule == "*":
                allows.extend(range(min_value, max_value + 1))
            else:
                allows.append(int(subrule))

        allows.sort()
        return allows

    def get_next(self, from_date, n=1, inclusive=False):
        """
        Returns a list with the n next datetime(s) that match the aws cron expression from the provided start date.

        :param from_date: datetime with the start date
        :param n: Int of the n next datetime(s), defaults to 1
        :param inclusive: If True, include the from_date time if it matches a valid execution.
        :return: list of datetime objects
        """
        if not isinstance(from_date, datetime.datetime):
            raise ValueError(
                "Invalid from_date. Must be of type datetime.datetime and have tzinfo = datetime.timezone.utc"
            )
        else:
            schedule_list = [None] * n
            for i in range(n):
                from_date = self.occurrence(from_date).next(inclusive=(inclusive and i == 0))
                if from_date is None:
                    break
                schedule_list[i] = from_date

            return schedule_list

    def get_prev(self, from_date, n=1, inclusive=False):
        """
        Returns a list with the n prev datetime(s) that match the aws cron expression
        from the provided start date.

        :param from_date: datetime with the start date
        :param n: Int of the n next datetime(s), defaults to 1
        :param inclusive: If True, include the from_date time if it matches a valid execution.
        :return: list of datetime objects
        """
        if not isinstance(from_date, datetime.datetime):
            raise ValueError(
                "Invalid from_date. Must be of type datetime.datetime and have tzinfo = datetime.timezone.utc"
            )
        else:
            schedule_list = [None] * n
            for i in range(n):
                from_date = self.occurrence(from_date).prev(inclusive=(inclusive and i == 0))
                if from_date is None:
                    break
                schedule_list[i] = from_date

            return schedule_list

    def get_all_schedule_bw_dates(self, from_date, to_date, exclude_ends=False):
        """
        Get all datetime(s) from from_date to to_date matching the given cron expression.
        If the cron expression matches either 'from_date' and/or 'to_date',
        those times will be returned as well unless 'exclude_ends=True' is passed.

        :param from_date: datetime object from where the schedule will start with tzinfo in utc.
        :param to_date: datetime object to where the schedule will end with tzinfo in utc.
        :param exclude_ends: bool defaulted to False, to not exclude the end date
        :return: list of datetime objects
        """

        if type(from_date) != type(to_date) and not (
            isinstance(from_date, type(to_date)) or isinstance(to_date, type(from_date))
        ):
            raise ValueError(
                "The from_date and to_date must be same type. {0} != {1}".format(type(from_date), type(to_date))
            )

        elif not isinstance(from_date, datetime.datetime) or (from_date.tzinfo != datetime.timezone.utc):
            raise ValueError(
                "Invalid from_date and to_date. Must be of type datetime.datetime "
                "and have tzinfo = datetime.timezone.utc"
            )
        else:
            schedule_list = []
            start = from_date.replace(second=0, microsecond=0) - datetime.timedelta(seconds=1)
            stop = to_date.replace(second=0, microsecond=0)

            while start is not None and start <= stop:
                start = self.occurrence(start).next()
                if start is None or start > stop:
                    break
                schedule_list.append(start)

            # If exclude_ends=True ,
            # remove first & last element from the list if they match from_date & to_date
            if exclude_ends:
                if schedule_list[0] == from_date.replace(second=0, microsecond=0):
                    schedule_list.pop(0)
                if schedule_list[-1] == to_date.replace(second=0, microsecond=0):
                    schedule_list.pop()
            return schedule_list

    def get_final_execution_time(self, from_date, to_date):
        """
        Get the final execution datetime between from_date and to_date matching the given cron expression.
        This method efficiently finds the final execution without looping through all occurrences.
        The to_date is exclusive, meaning if to_date exactly matches the cron expression,
        it will not be included in the result. Only executions strictly before to_date will be returned.

        :param from_date: datetime object from where the schedule will start with tzinfo in utc.
        :param to_date: datetime object to where the schedule will end with tzinfo in utc (exclusive).
        :return: datetime object representing the final execution time, or None if no executions found
        """
        if type(from_date) != type(to_date) and not (
            isinstance(from_date, type(to_date)) or isinstance(to_date, type(from_date))
        ):
            raise ValueError(
                "The from_date and to_date must be same type. {0} != {1}".format(type(from_date), type(to_date))
            )

        elif not isinstance(from_date, datetime.datetime) or (from_date.tzinfo != datetime.timezone.utc):
            raise ValueError(
                "Invalid from_date and to_date. Must be of type datetime.datetime "
                "and have tzinfo = datetime.timezone.utc"
            )
        else:
            # Use the occurrence logic to find the final execution efficiently
            # Start from the end date and work backwards
            # Using inclusive=False to make to_date exclusive - if to_date matches an execution,
            # it will not be included, and we'll get the previous execution instead
            occurrence = self.occurrence(to_date)
            
            # Find the previous execution before to_date (to_date is exclusive)
            final_execution = occurrence.prev(inclusive=False)
            
            # If no execution found, or the execution is before from_date, return None
            if final_execution is None or final_execution < from_date:
                return None
            
            return final_execution
