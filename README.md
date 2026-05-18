# AWS Croniter

AWS Croniter is a Python package for parsing, validating, and calculating occurrences of AWS EventBridge cron
expressions. AWS cron expressions are a powerful way to schedule events, but they differ from standard Unix cron syntax.
This library makes it easy to work
with [AWS-specific cron](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-scheduled-rule-pattern.html#eb-cron-expressions)
schedules programmatically.

---

![PyPI](https://img.shields.io/pypi/v/aws-croniter)
[![PyPI Downloads](https://static.pepy.tech/badge/aws-croniter)](https://pepy.tech/projects/aws-croniter)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aws-croniter)
[![GitHub stars](https://img.shields.io/github/stars/siddarth-patil/aws-croniter)](https://github.com/siddarth-patil/aws-croniter/stargazers)
![Tests](https://github.com/siddarth-patil/aws-croniter/actions/workflows/tests.yml/badge.svg)

---

## Table of Contents

1. [Inspiration](#inspiration)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
    - [AWS Cron Expression Example](#aws-cron-expression-example)
    - [Handling Invalid Cron Expressions](#handling-invalid-cron-expressions)
    - [Fetch Next Occurrence](#fetching-the-next-occurrence)
    - [Fetch Previous Occurrence](#fetching-the-previous-occurrence)
    - [Fetch All Schedules in Range](#fetch-all-schedules-in-range)
    - [Get Final Execution Time](#get-final-execution-time)
    - [Detect Schedule Conflicts](#detect-schedule-conflicts)
5. [Contributing](#contributing)
6. [License](#license)
7. [Contact](#contact)

---

## Inspiration

AWS Croniter was inspired by two existing packages, [
`aws-cron-expression-validator`](https://github.com/grumBit/aws_cron_expression_validator) and [
`pyawscron`](https://github.com/pitchblack408/pyawscron), which serve similar purposes. The
`aws-cron-expression-validator` package focuses solely on validating AWS cron expressions, while `pyawscron` provides
functionality for parsing and calculating schedules such as next and previous occurrences. However, both packages had
limitations, and users often needed to install and integrate both packages to work effectively with AWS cron schedules.
AWS Croniter was developed to address these issues by combining the features of both packages into a single, robust
solution that also provides an improved and comprehensive tool for working with AWS cron expressions.

---

## Features

- Validate AWS cron expressions against AWS EventBridge syntax.
- Parse and interpret cron rules with detailed validation error messages.
- Compute:
    - Next and previous occurrence times for a given schedule.
    - All occurrences of a schedule between two given dates.
    - Final execution time between two given dates (optimized for performance).
    - Conflicts between two or more schedules inside a bounded UTC time window.
- Handle special AWS cron syntax (e.g., `?`, `L`, `W`, `#`) and aliases for months (`JAN`, `FEB`, ...) and days of the
  week (`SUN`, `MON`, ...).

---

## Installation

Install the package via pip:

```bash
pip install aws-croniter
```

---

## Usage

### **AWS Cron Expression Example**

```python
from aws_croniter import AwsCroniter

cron_expression = "0 12 15 * ? 2023"  # AWS cron syntax
aws_cron = AwsCroniter(cron_expression)
```

---

### **Handling Invalid Cron Expressions**

When an invalid AWS cron expression is passed, `AwsCroniter` raises specific exceptions indicating the nature of the
error:

```python
from aws_croniter import AwsCroniter
from aws_croniter.exceptions import AwsCroniterExpressionError

try:
    invalid_cron = "0 18 ? * MON-FRI"  # Missing fields
    AwsCroniter(invalid_cron)
except AwsCroniterExpressionError as e:
    print(f"Invalid cron expression: {e}")
# Output: Invalid cron expression: Incorrect number of values in '0 18 ? * MON-FRI'. 6 required, 5 provided.
```

---

### **Fetching the Next Occurrence**

The `get_next` method retrieves the next occurrence(s) of the cron schedule from a specified date. This method
always returns a list with `n` items and sets the items to `None` if no valid occurrences are found.

#### **Basic Usage**

```python
from aws_croniter import AwsCroniter
from datetime import datetime, timezone

# AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)

# Starting datetime
start_date = datetime(2023, 12, 14, tzinfo=timezone.utc)
next_occurrence = aws_cron.get_next(start_date)

print(next_occurrence)
# Output: [datetime.datetime(2023, 12, 15, 12, 0, tzinfo=datetime.timezone.utc)]
```

#### **Retrieving Multiple Occurrences (n > 1)**

```python
from aws_croniter import AwsCroniter
from datetime import datetime, timezone

# AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)

# Starting datetime
start_date = datetime(2023, 9, 14, tzinfo=timezone.utc)

# Fetch the next 3 occurrences
next_occurrences = aws_cron.get_next(start_date, n=3)

print(next_occurrences)
# Output: [datetime.datetime(2023, 9, 15, 12, 0, tzinfo=datetime.timezone.utc),
#          datetime.datetime(2023, 10, 15, 12, 0, tzinfo=datetime.timezone.utc),
#          datetime.datetime(2023, 11, 15, 12, 0, tzinfo=datetime.timezone.utc)]
```

#### **Using the Inclusive Parameter**

Setting `inclusive=True` includes the start date in the results if it matches the schedule. The default is `False`.

```python
from aws_croniter import AwsCroniter
from datetime import datetime, timezone

# AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)

# Starting datetime
start_date = datetime(2023, 12, 15, 12, 0,
                      tzinfo=timezone.utc)
# Include the starting date in the results
next_occurrence_inclusive = aws_cron.get_next(start_date, inclusive=True)

print(next_occurrence_inclusive)
# Output: [datetime.datetime(2023, 12, 15, 12, 0, tzinfo=datetime.timezone.utc)]
```

---

### **Fetching the Previous Occurrence**

The `get_prev` method retrieves the previous occurrence(s) of the cron schedule from a specified date. This method
always returns a list with `n` items and sets the items to `None` if no valid occurrences are found.

#### **Basic Usage**

```python
from aws_croniter import AwsCroniter
from datetime import datetime, timezone

# AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)

# Starting datetime
start_date = datetime(2023, 12, 14, tzinfo=timezone.utc)
prev_occurrence = aws_cron.get_prev(start_date)

print(prev_occurrence)
# Output: [datetime.datetime(2023, 11, 15, 12, 0, tzinfo=datetime.timezone.utc)]
```

#### **Retrieving Multiple Occurrences (n > 1)**

```python
from aws_croniter import AwsCroniter
from datetime import datetime, timezone

# AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)

# Starting datetime
start_date = datetime(2023, 12, 14, tzinfo=timezone.utc)

# Fetch the previous 2 occurrences
prev_occurrences = aws_cron.get_prev(start_date, n=2)

print(prev_occurrences)
# Output: [datetime.datetime(2023, 11, 15, 12, 0, tzinfo=datetime.timezone.utc),
#          datetime.datetime(2023, 10, 15, 12, 0, tzinfo=datetime.timezone.utc)]
```

#### **Using the Inclusive Parameter**

Setting `inclusive=True` includes the start date in the results if it matches the schedule. The default is `False`.

```python
from aws_croniter import AwsCroniter
from datetime import datetime, timezone

# AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)

# Starting datetime
start_date = datetime(2023, 12, 15, 12, 0,
                      tzinfo=timezone.utc)
# Include the starting date in the results
prev_occurrence_inclusive = aws_cron.get_prev(start_date, inclusive=True)

print(prev_occurrence_inclusive)
# Output: [datetime.datetime(2023, 12, 15, 12, 0, tzinfo=datetime.timezone.utc)]
```

---

### **Fetch All Schedules in Range**

The `get_all_schedule_bw_dates` method retrieves all occurrences of the cron schedule between two specified dates.

#### **Basic Usage**

```python
from aws_croniter import AwsCroniter
from datetime import datetime, timezone

# AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)

# Define the date range
from_date = datetime(2023, 11, 14, tzinfo=timezone.utc)
to_date = datetime(2023, 12, 31, tzinfo=timezone.utc)

# Fetch all occurrences in the range
all_occurrences = aws_cron.get_all_schedule_bw_dates(from_date, to_date)

print(all_occurrences)
# Output: [datetime.datetime(2023, 11, 15, 12, 0, tzinfo=datetime.timezone.utc),
#          datetime.datetime(2023, 12, 15, 12, 0, tzinfo=datetime.timezone.utc)]
```

#### **Excluding Start and End Dates**

Setting `exclude_ends=True` omits occurrences that match the start and end dates. The default is `False`.

```python
from aws_croniter import AwsCroniter
from datetime import datetime, timezone

# AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)

# Define the date range
from_date = datetime(2023, 11, 14, tzinfo=timezone.utc)
to_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
# Exclude the start and end dates from the results
all_occurrences_exclude_ends = aws_cron.get_all_schedule_bw_dates(from_date, to_date, exclude_ends=True)

print(all_occurrences_exclude_ends)
# Output: [datetime.datetime(2023, 11, 15, 12, 0, tzinfo=datetime.timezone.utc), 
#          datetime.datetime(2023, 12, 15, 12, 0, tzinfo=datetime.timezone.utc)]
```

---

### **Get Final Execution Time**

The `get_final_execution_time` method retrieves the final execution datetime between two specified dates.
The `to_date` is exclusive, meaning if it exactly matches the cron expression, it will not be included
in the result. Only executions strictly before `to_date` will be returned.

#### **Basic Usage**

```python
from aws_croniter import AwsCroniter
from datetime import datetime, timezone

# AWS cron expression
cron_expression = "0 12 15 * ? 2023"
aws_cron = AwsCroniter(cron_expression)

# Define the date range
from_date = datetime(2023, 11, 14, tzinfo=timezone.utc)
to_date = datetime(2023, 12, 31, tzinfo=timezone.utc)

# Get the final execution time in the range
final_execution = aws_cron.get_final_execution_time(from_date, to_date)

print(final_execution)
# Output: datetime.datetime(2023, 12, 15, 12, 0, tzinfo=datetime.timezone.utc)
```

---

### **Detect Schedule Conflicts**

Use `find_conflicts` with a list of **two or more** schedules. Each item may be a cron string or
an `AwsCroniter` instance (already parsed). Passing only one expression raises `ValueError`.

All datetimes must use `datetime.timezone.utc` (the package is not timezone-aware yet).

**What counts as a conflict**

Runs from **different** expressions that are closer than the minimum separation (`buffer`):

| `buffer` | Meaning |
|----------|---------|
| `timedelta(0)` | Exact same run time only |
| `timedelta(minutes=15)` | Runs within 15 minutes of each other |
| `timedelta(hours=1)` | Runs within one hour of each other |

`buffer` is a standard `timedelta` - seconds, minutes, hours, or combined units all work.
Schedules are evaluated at **minute** precision (AWS cron has no seconds field).

**Collection modes**

| Mode | Behavior |
|------|----------|
| `ConflictCollectionMode.FIRST` (default) | Stop after the earliest conflict in the window |
| `ConflictCollectionMode.ALL` | Collect up to `max_conflicts` conflicts, in time order |

The search window `[from_date, to_date]` is inclusive. Work scales with occurrences examined in
the window, not with the cartesian product of all schedule pairs.

**Safety limits** (defaults shown) raise `AwsCroniterConflictSearchLimitError` when exceeded:

| Option | Default | Purpose |
|--------|---------|---------|
| `max_expressions` | `50` | Maximum schedules in one call |
| `max_occurrences_per_expression` | `10_000` | Maximum runs generated per schedule |
| `max_total_occurrences` | `100_000` | Maximum runs generated across all schedules |

#### **First conflict with cron strings (default mode)**

Pass raw cron strings and use the default collection mode to answer “do these two schedules
clash, and when is the first clash?”

```python
from datetime import datetime, timedelta, timezone

from aws_croniter import find_conflicts

from_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
to_date = datetime(2024, 1, 31, 23, 59, tzinfo=timezone.utc)

result = find_conflicts(
    [
        "0 12 15 * ? 2024",   # 12:00 on the 15th
        "5 12 15 * ? 2024",   # 12:05 on the 15th
    ],
    from_date=from_date,
    to_date=to_date,
    buffer=timedelta(minutes=10),
    # collection_mode defaults to ConflictCollectionMode.FIRST
)

if result.has_conflict:
    conflict = result.first_conflict
    print(conflict.separation)  # 0:05:00
    for run in conflict.runs:
        print(run.expression_index, run.expression, run.run_at)
# Output (example):
# 0:05:00
# 0 0 12 15 * ? 2024 2024-01-15 12:00:00+00:00
# 1 5 12 15 * ? 2024 2024-01-15 12:05:00+00:00
```

#### **Multiple conflicts with `AwsCroniter` objects (`ALL` mode)**

Reuse parsed `AwsCroniter` instances (for example after validation elsewhere) and collect
several conflicts across three or more schedules.

```python
from datetime import datetime, timedelta, timezone

from aws_croniter import AwsCroniter, ConflictCollectionMode, find_conflicts

from_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
to_date = datetime(2024, 1, 3, tzinfo=timezone.utc)

schedules = [
    AwsCroniter("*/15 * * * ? 2024"),  # every 15 minutes
    AwsCroniter("*/10 * * * ? 2024"),  # every 10 minutes
    AwsCroniter("0 12 15 * ? 2024"),   # once daily at noon on the 15th
]

result = find_conflicts(
    schedules,
    from_date=from_date,
    to_date=to_date,
    buffer=timedelta(0),  # exact timestamp collisions only
    collection_mode=ConflictCollectionMode.ALL,
    max_conflicts=3,
)

print(result.has_conflict, len(result.conflicts), result.occurrences_examined)
for i, conflict in enumerate(result.conflicts, start=1):
    print(f"Conflict {i} at {conflict.earliest}, separation={conflict.separation}")
# Output (example):
# True 3 13
# Conflict 1 at 2024-01-01 00:00:00+00:00, separation=0:00:00
# Conflict 2 at 2024-01-01 00:30:00+00:00, separation=0:00:00
# Conflict 3 at 2024-01-01 01:00:00+00:00, separation=0:00:00
```

`*/15` and `*/10` align every 30 minutes (`00:00`, `00:30`, `01:00`, …), so `buffer=0` reports
those exact collisions. Search stops after three conflicts, so `occurrences_examined` stays
small even for dense schedules.

#### **Reusable settings with `ConflictSearchOptions`**

Pass keyword arguments directly, or bundle them once and reuse via `options`:

```python
from datetime import datetime, timezone

from aws_croniter import ConflictSearchOptions, find_conflicts

options = ConflictSearchOptions.from_call(
    from_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    to_date=datetime(2024, 1, 31, tzinfo=timezone.utc),
)

result = find_conflicts(
    ["0 12 15 * ? 2024", "0 13 15 * ? 2024"],
    options=options,
)
```

When `options` is provided, other keyword arguments to `find_conflicts` are ignored.

---

## Contributing

Contributions are welcome! Please read the [contributing guidelines](docs/CONTRIBUTING.md) first.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For any questions or suggestions, please open an issue or contact the maintainer
at [hello@techwithsid.com](mailto:hello@techwithsid.com).
