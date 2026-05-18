import datetime
from dataclasses import dataclass
from dataclasses import field
from enum import Enum


class ConflictCollectionMode(Enum):
    """How many schedule conflicts to collect before stopping."""

    FIRST = "first"
    ALL = "all"


@dataclass(frozen=True)
class ScheduledRun:
    """One scheduled execution time attributed to a source expression."""

    expression_index: int
    expression: str
    run_at: datetime.datetime


@dataclass(frozen=True)
class ScheduleConflict:
    """Runs from different expressions that violate the minimum separation (buffer)."""

    runs: tuple[ScheduledRun, ...]
    separation: datetime.timedelta

    @property
    def earliest(self) -> datetime.datetime:
        return min(run.run_at for run in self.runs)

    @property
    def latest(self) -> datetime.datetime:
        return max(run.run_at for run in self.runs)


@dataclass
class ConflictSearchOptions:
    """
    Configuration for schedule conflict detection.

    All datetimes must use ``datetime.timezone.utc``. The search window is
    inclusive on both ends: occurrences at ``from_date`` or ``to_date`` are considered.
    """

    from_date: datetime.datetime
    to_date: datetime.datetime
    buffer: datetime.timedelta = field(default_factory=lambda: datetime.timedelta(0))
    collection_mode: ConflictCollectionMode = ConflictCollectionMode.FIRST
    max_conflicts: int = 1
    max_expressions: int = 50
    max_occurrences_per_expression: int = 10_000
    max_total_occurrences: int = 100_000

    def __post_init__(self) -> None:
        _validate_utc(self.from_date, "from_date")
        _validate_utc(self.to_date, "to_date")
        if self.buffer < datetime.timedelta(0):
            raise ValueError("buffer must be greater than or equal to zero")
        if self.from_date > self.to_date:
            raise ValueError("from_date must be less than or equal to to_date")
        if self.max_conflicts < 1:
            raise ValueError("max_conflicts must be at least 1")
        if self.max_expressions < 2:
            raise ValueError("max_expressions must be at least 2")
        if self.max_occurrences_per_expression < 1:
            raise ValueError("max_occurrences_per_expression must be at least 1")
        if self.max_total_occurrences < 1:
            raise ValueError("max_total_occurrences must be at least 1")

    @property
    def stop_on_first(self) -> bool:
        return self.collection_mode is ConflictCollectionMode.FIRST

    def effective_max_conflicts(self) -> int:
        if self.collection_mode is ConflictCollectionMode.FIRST:
            return 1
        return self.max_conflicts

    @classmethod
    def from_call(
        cls,
        *,
        from_date: datetime.datetime,
        to_date: datetime.datetime,
        buffer: datetime.timedelta | None = None,
        collection_mode: ConflictCollectionMode = ConflictCollectionMode.FIRST,
        max_conflicts: int = 1,
        max_expressions: int = 50,
        max_occurrences_per_expression: int = 10_000,
        max_total_occurrences: int = 100_000,
    ) -> "ConflictSearchOptions":
        if buffer is None:
            buffer = datetime.timedelta(0)
        return cls(
            from_date=from_date,
            to_date=to_date,
            buffer=buffer,
            collection_mode=collection_mode,
            max_conflicts=max_conflicts,
            max_expressions=max_expressions,
            max_occurrences_per_expression=max_occurrences_per_expression,
            max_total_occurrences=max_total_occurrences,
        )


@dataclass
class ConflictSearchResult:
    """Outcome of a conflict search over one or more cron expressions."""

    has_conflict: bool
    conflicts: list[ScheduleConflict] = field(default_factory=list)
    occurrences_examined: int = 0

    @property
    def first_conflict(self) -> ScheduleConflict | None:
        if not self.conflicts:
            return None
        return self.conflicts[0]


def _validate_utc(value: datetime.datetime, name: str) -> None:
    if value.tzinfo is None or value.tzinfo != datetime.timezone.utc:
        raise ValueError(f"{name} must be a datetime with tzinfo=datetime.timezone.utc")
