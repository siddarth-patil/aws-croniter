class AWSCronExpressionError(ValueError):
    """Base exception for errors in AWS cron expressions."""

    pass


class AWSCronExpressionMinuteError(AWSCronExpressionError):
    """Exception raised for invalid minute values in an AWS cron expression."""

    pass


class AWSCronExpressionHourError(AWSCronExpressionError):
    """Exception raised for invalid hour values in an AWS cron expression."""

    pass


class AWSCronExpressionMonthError(AWSCronExpressionError):
    """Exception raised for invalid month values in an AWS cron expression."""

    pass


class AWSCronExpressionYearError(AWSCronExpressionError):
    """Exception raised for invalid year values in an AWS cron expression."""

    pass


class AWSCronExpressionDayOfMonthError(AWSCronExpressionError):
    """Exception raised for invalid day-of-month values in an AWS cron expression."""

    pass


class AWSCronExpressionDayOfWeekError(AWSCronExpressionError):
    """Exception raised for invalid day-of-week values in an AWS cron expression."""

    pass
