import datetime
from collections.abc import Iterator

from aws_croniter.aws_croniter import AwsCroniter
from aws_croniter.exceptions import AwsCroniterConflictSearchLimitError


class OccurrenceCounter:
    """Tracks generated occurrences across all streams for a conflict search."""

    def __init__(self, max_total_occurrences: int) -> None:
        self.max_total_occurrences = max_total_occurrences
        self.total = 0

    def record(self) -> None:
        self.total += 1
        if self.total > self.max_total_occurrences:
            raise AwsCroniterConflictSearchLimitError(f"Exceeded max_total_occurrences ({self.max_total_occurrences}).")


class OccurrenceStream:
    """Lazily yields ascending UTC occurrence times within a bounded window."""

    def __init__(
        self,
        cron: "AwsCroniter",
        expression: str,
        expression_index: int,
        from_date: datetime.datetime,
        to_date: datetime.datetime,
        max_occurrences: int,
        counter: OccurrenceCounter,
    ) -> None:
        self._cron = cron
        self.expression = expression
        self.expression_index = expression_index
        self._to_date = to_date.replace(second=0, microsecond=0)
        self._max_occurrences = max_occurrences
        self._counter = counter
        self._count = 0
        self._exhausted = False
        self._cursor = from_date.replace(second=0, microsecond=0) - datetime.timedelta(seconds=1)
        self._next: datetime.datetime | None = None
        self._advance()

    def peek(self) -> datetime.datetime | None:
        return self._next

    def pop(self) -> datetime.datetime:
        if self._next is None:
            raise StopIteration
        current = self._next
        self._advance()
        return current

    def _advance(self) -> None:
        self._next = None
        if self._exhausted:
            return
        while True:
            if self._count >= self._max_occurrences:
                raise AwsCroniterConflictSearchLimitError(
                    f"Exceeded max_occurrences_per_expression ({self._max_occurrences}) "
                    f"for expression index {self.expression_index}."
                )
            candidate = self._cron.occurrence(self._cursor).next()
            if candidate is None or candidate > self._to_date:
                self._exhausted = True
                return
            self._cursor = candidate
            self._count += 1
            self._counter.record()
            self._next = candidate
            return

    def __iter__(self) -> Iterator[datetime.datetime]:
        while self._next is not None:
            yield self.pop()
