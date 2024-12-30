class AwsCroniterExpressionError(ValueError):
    """Base exception for errors in AWS cron expressions."""

    pass


class AwsCroniterExpressionMinuteError(AwsCroniterExpressionError):
    """Exception raised for invalid minute values in an AWS cron expression."""

    pass


class AwsCroniterExpressionHourError(AwsCroniterExpressionError):
    """Exception raised for invalid hour values in an AWS cron expression."""

    pass


class AwsCroniterExpressionMonthError(AwsCroniterExpressionError):
    """Exception raised for invalid month values in an AWS cron expression."""

    pass


class AwsCroniterExpressionYearError(AwsCroniterExpressionError):
    """Exception raised for invalid year values in an AWS cron expression."""

    pass


class AwsCroniterExpressionDayOfMonthError(AwsCroniterExpressionError):
    """Exception raised for invalid day-of-month values in an AWS cron expression."""

    pass


class AwsCroniterExpressionDayOfWeekError(AwsCroniterExpressionError):
    """Exception raised for invalid day-of-week values in an AWS cron expression."""

    pass
