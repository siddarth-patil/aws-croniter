# AWS Croniter

AWS Croniter is a Python library that provides utilities for working with AWS cron expressions. It allows you to easily parse, manipulate, and validate cron expressions used in AWS services like CloudWatch and EventBridge.

## Features

- Parse AWS cron expressions
- Validate cron expressions
- Generate next execution times
- Convert cron expressions to human-readable format

## Installation

You can install AWS Croniter using pip:

```sh
pip install aws-croniter
```

## Usage

Here is a basic example of how to use AWS Croniter:

```python
from aws_croniter import Croniter

# Create a Croniter object with an AWS cron expression
cron = Croniter('cron(0 12 * * ? *)')

# Validate the cron expression
if cron.is_valid():
    print("The cron expression is valid.")

# Get the next execution time
next_time = cron.get_next()
print(f"The next execution time is: {next_time}")

# Convert to human-readable format
human_readable = cron.to_human_readable()
print(f"Human-readable format: {human_readable}")
```

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the maintainer at [email@example.com](mailto:email@example.com).
