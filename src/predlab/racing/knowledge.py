"""What the past tells a model, released only when it became knowable.

The engine walks races in prediction-time order. Before asking for a forecast at
time *t*, it releases every earlier race whose result was known before *t* (see
``events.result_known_at``). Nothing else ever enters this object: a model reading it
cannot see a result that was not yet published, because that result has not been
added -- not because a filter hides it.

Kept deliberately generic (horse, jockey, trainer tallies and recent runs). Anything
model-specific lives in the model, fed by its own ``observe`` hook.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from predlab.racing.events import RaceEvent


@dataclass(frozen=True, slots=True)
class Run:
    day: date
    position: int | None  # None: unplaced, disqualified, fell
    field_size: int

    @property
    def relative_position(self) -> float:
        """0 = won, 1 = last or unplaced."""
        if self.position is None or self.field_size <= 1:
            return 1.0
        return min(1.0, (self.position - 1) / (self.field_size - 1))


@dataclass
class Tally:
    runs: int = 0
    wins: int = 0


@dataclass
class Knowledge:
    horses: dict[str, list[Run]] = field(default_factory=dict)
    jockeys: dict[str, Tally] = field(default_factory=dict)
    trainers: dict[str, Tally] = field(default_factory=dict)
    starts: int = 0
    wins: int = 0
    released: set[str] = field(default_factory=set)
    last_known_at: datetime | None = None

    def release(self, event: RaceEvent) -> None:
        """Add one finished race. Called by the engine only, in known_at order."""
        if event.card.race_id in self.released:
            raise ValueError(f"{event.card.race_id} released twice")
        if self.last_known_at is not None and event.known_at < self.last_known_at:
            raise ValueError("results must be released in known_at order")
        self.last_known_at = event.known_at
        self.released.add(event.card.race_id)
        n = event.card.n
        for s in event.card.starters:
            pos = event.outcome.positions.get(s.number)
            won = pos == 1
            self.starts += 1
            self.wins += int(won)
            if s.horse_id:
                self.horses.setdefault(s.horse_id, []).append(Run(event.card.day, pos, n))
            for table, key in ((self.jockeys, s.jockey), (self.trainers, s.trainer)):
                if key:
                    t = table.setdefault(key, Tally())
                    t.runs += 1
                    t.wins += int(won)

    @property
    def base_rate(self) -> float:
        """Share of starts that were wins, over everything released so far."""
        return self.wins / self.starts if self.starts else 0.1

    def horse_runs(self, horse_id: str | None) -> list[Run]:
        return self.horses.get(horse_id, []) if horse_id else []
