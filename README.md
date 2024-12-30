![PyPI](https://img.shields.io/pypi/v/aws-croniter)
![Tests](https://github.com/siddarth-patil/aws-croniter/actions/workflows/tests.yml/badge.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aws-croniter)
[![GitHub stars](https://img.shields.io/github/stars/siddarth-patil/aws-croniter)](https://github.com/siddarth-patil/aws-croniter/stargazers)

# AWS Croniter

AWS Croniter is a Python package for parsing, validating, and calculating occurrences of AWS EventBridge cron
expressions. AWS cron expressions are a powerful way to schedule events, but they differ from standard Unix cron syntax.
This library makes it easy to work with AWS-specific cron schedules programmatically.

## Features

- Validate AWS cron expressions against AWS EventBridge syntax.
- Parse and interpret cron rules with detailed validation error messages.
- Compute:
    - Next and previous occurrence times for a given schedule.
    - All occurrences of a schedule between two given dates.
- Handle special AWS cron syntax (e.g., `?`, `L`, `W`, `#`) and aliases for months (`JAN`, `FEB`, ...) and days of the
  week (`SUN`, `MON`, ...).

## Installation

Install the package via pip:

```bash
pip install aws-croniter
```

## Usage

Here is a basic example of how to use AWS Croniter:

```python
from aws_cronite import AwsCroniter

# Example AWS cron expression
cron_expression = "0 12 15 * ? 2023"

aws_cron = AwsCroniter(cron_expression)
```

Getting the Next Occurrence

```python
from aws_cronite import AwsCroniter
from datetime import datetime, timezone

# Example AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)
# Start from a given datetime
start_date = datetime(2023, 12, 14, tzinfo=timezone.utc)
next_occurrence = aws_cron.get_next(start_date)

print(next_occurrence)
## Results in [datetime.datetime(2023, 12, 15, 12, 0, tzinfo=datetime.timezone.utc)]
```

Getting the Previous Occurrence

```python
from aws_cronite import AwsCroniter
from datetime import datetime, timezone

# Example AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)
# Start from a given datetime
start_date = datetime(2023, 12, 14, tzinfo=timezone.utc)
prev_occurrence = aws_cron.get_prev(start_date)

print(prev_occurrence)
```

Getting All Occurrences Between Two Dates

```python
from aws_cronite import AwsCroniter
from datetime import datetime, timezone

# Example AWS cron expression
cron_expression = "0 12 15 * ? 2023"

aws_cron = AwsCroniter(cron_expression)
from_date = datetime(2023, 12, 14, tzinfo=timezone.utc)
to_date = datetime(2023, 12, 31, tzinfo=timezone.utc)

all_occurrences = aws_cron.get_all_schedule_bw_dates(from_date, to_date)

print(all_occurrences)
```

Handling Validation Errors

If an invalid AWS cron expression is provided, AwsCroniter raises specific exceptions indicating the type of error:

```python
from aws_cronite.exceptions import AwsCroniterExpressionError

try:
    invalid_cron = "0 18 ? * MON-FRI"  # Missing required fields
    AwsCroniter(invalid_cron)
except AwsCroniterExpressionError as e:
    print(f"Invalid cron expression: {e}")
```

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the maintainer
at [email@example.com](mailto:email@example.com).
