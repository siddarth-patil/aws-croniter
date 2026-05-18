import datetime
import heapq
from collections import deque
from collections.abc import Sequence
from typing import Union

from aws_croniter.aws_croniter import AwsCroniter
from aws_croniter.conflict_models import ConflictCollectionMode
from aws_croniter.conflict_models import ConflictSearchOptions
from aws_croniter.conflict_models import ConflictSearchResult
from aws_croniter.conflict_models import ScheduleConflict
from aws_croniter.conflict_models import ScheduledRun
from aws_croniter.exceptions import AwsCroniterConflictSearchLimitError
from aws_croniter.occurrence_stream import OccurrenceCounter
from aws_croniter.occurrence_stream import OccurrenceStream

CronInput = Union[str, AwsCroniter]


def find_conflicts(
    expressions: Sequence[CronInput],
    *,
    from_date: datetime.datetime | None = None,
    to_date: datetime.datetime | None = None,
    options: ConflictSearchOptions | None = None,
    buffer: datetime.timedelta | None = None,
    collection_mode: ConflictCollectionMode = ConflictCollectionMode.FIRST,
    max_conflicts: int = 1,
    max_expressions: int = 50,
    max_occurrences_per_expression: int = 10_000,
    max_total_occurrences: int = 100_000,
) -> ConflictSearchResult:
    """
    Find schedule conflicts across two or more AWS cron expressions.

    Pass ``from_date``/``to_date`` (and optional keywords), or a pre-built
    ``ConflictSearchOptions`` as ``options`` (keywords are then ignored).

    A conflict is when runs from different expressions fall within ``buffer`` of
    each other (``buffer=0`` requires the exact same timestamp).
    """
    if options is None:
        if from_date is None or to_date is None:
            raise ValueError("from_date and to_date are required when options is not provided")
        options = ConflictSearchOptions.from_call(
            from_date=from_date,
            to_date=to_date,
            buffer=buffer,
            collection_mode=collection_mode,
            max_conflicts=max_conflicts,
            max_expressions=max_expressions,
            max_occurrences_per_expression=max_occurrences_per_expression,
            max_total_occurrences=max_total_occurrences,
        )

    cron_pairs = _prepare_expressions(expressions, options.max_expressions)
    return _search_conflicts(cron_pairs, options)


def _prepare_expressions(
    expressions: Sequence[CronInput],
    max_expressions: int,
) -> list[tuple[AwsCroniter, str]]:
    expression_count = len(expressions)
    if expression_count == 0:
        raise ValueError("at least two cron expressions are required; none were provided")
    if expression_count == 1:
        raise ValueError("at least two cron expressions are required; only one was provided")
    if expression_count > max_expressions:
        raise AwsCroniterConflictSearchLimitError(
            f"Expression count {expression_count} exceeds max_expressions ({max_expressions})."
        )

    prepared: list[tuple[AwsCroniter, str]] = []
    for item in expressions:
        if isinstance(item, AwsCroniter):
            prepared.append((item, item.cron))
        else:
            prepared.append((AwsCroniter(item), item))
    return prepared


def _search_conflicts(
    cron_pairs: list[tuple[AwsCroniter, str]],
    options: ConflictSearchOptions,
) -> ConflictSearchResult:
    counter = OccurrenceCounter(options.max_total_occurrences)
    streams = [
        OccurrenceStream(
            cron,
            expression,
            index,
            options.from_date,
            options.to_date,
            options.max_occurrences_per_expression,
            counter,
        )
        for index, (cron, expression) in enumerate(cron_pairs)
    ]

    heap: list[tuple[datetime.datetime, int, OccurrenceStream]] = []
    for stream in streams:
        next_time = stream.peek()
        if next_time is not None:
            heapq.heappush(heap, (next_time, stream.expression_index, stream))

    recent: deque[ScheduledRun] = deque()
    conflicts: list[ScheduleConflict] = []
    target = options.effective_max_conflicts()

    while heap:
        run_at, _, stream = heapq.heappop(heap)
        run = ScheduledRun(stream.expression_index, stream.expression, run_at)

        _prune_recent(recent, run_at, options.buffer)
        conflict = _conflict_with_recent(run, recent, options.buffer)
        if conflict is not None:
            conflicts.append(conflict)
            if len(conflicts) >= target:
                return ConflictSearchResult(True, conflicts, counter.total)

        recent.append(run)
        stream.pop()
        next_time = stream.peek()
        if next_time is not None:
            heapq.heappush(heap, (next_time, stream.expression_index, stream))

    return ConflictSearchResult(bool(conflicts), conflicts, counter.total)


def _prune_recent(recent: deque[ScheduledRun], current_time: datetime.datetime, buffer: datetime.timedelta) -> None:
    threshold = current_time - buffer
    while recent and recent[0].run_at < threshold:
        recent.popleft()


def _conflict_with_recent(
    current: ScheduledRun,
    recent: deque[ScheduledRun],
    buffer: datetime.timedelta,
) -> ScheduleConflict | None:
    conflicting = [
        prior
        for prior in recent
        if prior.expression_index != current.expression_index
        and abs(current.run_at - prior.run_at) <= buffer
    ]
    if not conflicting:
        return None

    runs = _dedupe_runs([current, *conflicting])
    if len(runs) < 2:
        return None

    separation = min(
        abs(a.run_at - b.run_at) for i, a in enumerate(runs) for b in runs[i + 1 :]
    )
    return ScheduleConflict(tuple(runs), separation)


def _dedupe_runs(runs: list[ScheduledRun]) -> list[ScheduledRun]:
    seen: set[tuple[int, datetime.datetime]] = set()
    unique: list[ScheduledRun] = []
    for run in sorted(runs, key=lambda item: (item.run_at, item.expression_index)):
        key = (run.expression_index, run.run_at)
        if key not in seen:
            seen.add(key)
            unique.append(run)
    return unique
