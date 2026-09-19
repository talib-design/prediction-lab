from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pytest

from predlab.core.gamespec import GameSpec
from predlab.core.hashing import AppendOnlyLedger
from predlab.core.historyview import build_view
from predlab.models.baselines import UniformPredictor
from predlab.models.selection import TopKPolicy
from predlab.registry.hypotheses import Hypothesis, HypothesisRegistry, Status
from predlab.registry.predictions import (
    HindsightError,
    PredictionLedger,
    PrematureScoringError,
)

from .conftest import synthetic_draws

TODAY = date(2026, 9, 19)


def _forecast(loto: GameSpec, target: date):
    dates, pools = synthetic_draws(loto, 300, seed=0, start=date(2020, 1, 1))
    history = build_view(loto, dates, pools, as_of=target)
    return UniformPredictor(spec=loto).forecast(history, target)


def _ledger(tmp_path: Path) -> PredictionLedger:
    return PredictionLedger(AppendOnlyLedger(tmp_path / "predictions.jsonl"))


def _record(ledger: PredictionLedger, loto: GameSpec, target: date, **kw):
    forecast = _forecast(loto, target)
    policy = TopKPolicy()
    return ledger.record(
        loto,
        forecast,
        policy.ticket(forecast),
        selection_policy=policy.name,
        model_name="uniform",
        model_version="1",
        config={},
        training_cutoff=target - timedelta(days=2),
        dataset_fingerprint="abc123",
        today=TODAY,
        **kw,
    )


def test_a_future_prediction_is_recorded(tmp_path: Path, loto: GameSpec) -> None:
    ledger = _ledger(tmp_path)
    prediction = _record(ledger, loto, date(2026, 9, 21))  # a Monday
    assert prediction.target_draw_key == "loto/2019-11/2026-09-21"
    assert len(prediction.ticket["main"]) == 5
    ledger.verify()


def test_predicting_the_past_is_refused(tmp_path: Path, loto: GameSpec) -> None:
    """The guarantee the whole ledger exists for."""
    with pytest.raises(HindsightError, match="not in the future"):
        _record(_ledger(tmp_path), loto, date(2026, 9, 16))


def test_predicting_today_is_refused(tmp_path: Path, loto: GameSpec) -> None:
    with pytest.raises(HindsightError, match="not in the future"):
        _record(_ledger(tmp_path), loto, TODAY)


def test_predicting_an_already_recorded_draw_is_refused(tmp_path: Path, loto: GameSpec) -> None:
    with pytest.raises(HindsightError, match="already in the dataset"):
        _record(
            _ledger(tmp_path),
            loto,
            date(2026, 9, 21),
            known_draw_dates=frozenset({date(2026, 9, 21)}),
        )


def test_predicting_a_non_draw_day_is_refused(tmp_path: Path, loto: GameSpec) -> None:
    with pytest.raises(ValueError, match="not a draw day"):
        _record(_ledger(tmp_path), loto, date(2026, 9, 22))  # Tuesday


def test_editing_a_recorded_prediction_is_detected(tmp_path: Path, loto: GameSpec) -> None:
    path = tmp_path / "predictions.jsonl"
    ledger = PredictionLedger(AppendOnlyLedger(path))
    _record(ledger, loto, date(2026, 9, 21))
    _record(ledger, loto, date(2026, 9, 23))

    lines = path.read_text(encoding="utf-8").splitlines()
    lines[0] = lines[0].replace('"selection_policy":"top_k"', '"selection_policy":"other"')
    lines[0] = lines[0].replace('"selection_policy": "top_k"', '"selection_policy": "other"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    from predlab.core.hashing import LedgerCorruptionError

    with pytest.raises(LedgerCorruptionError):
        ledger.verify()


def test_pending_and_matured_are_split_by_date(tmp_path: Path, loto: GameSpec) -> None:
    ledger = _ledger(tmp_path)
    _record(ledger, loto, date(2026, 9, 21))
    _record(ledger, loto, date(2026, 9, 26))
    assert len(ledger.pending(today=TODAY)) == 2
    assert len(ledger.matured(today=TODAY)) == 0
    assert len(ledger.matured(today=date(2026, 9, 22))) == 1


def test_probabilities_are_validated_on_load(tmp_path: Path, loto: GameSpec) -> None:
    from predlab.registry.predictions import ForwardPrediction

    with pytest.raises(ValueError, match="strictly in"):
        ForwardPrediction(
            game="loto",
            era="2019-11",
            target_draw_key="k",
            target_date=date(2026, 9, 21),
            model_name="m",
            model_version="1",
            training_cutoff=date(2026, 9, 16),
            n_training_draws=1,
            dataset_fingerprint="x",
            inclusion_probabilities={"main": [0.0, 1.0]},
            ticket={"main": [1]},
            selection_policy="top_k",
        )


def test_premature_scoring_error_exists_for_callers() -> None:
    assert issubclass(PrematureScoringError, RuntimeError)


# ------------------------------------------------------------------------ hypotheses


def _registry(tmp_path: Path) -> HypothesisRegistry:
    return HypothesisRegistry(AppendOnlyLedger(tmp_path / "hypotheses.jsonl"))


def test_hypotheses_are_appended_and_listed(tmp_path: Path) -> None:
    reg = _registry(tmp_path)
    reg.add(Hypothesis(description="Hot numbers repeat."))
    reg.add(Hypothesis(description="Gaps predict the next draw."))
    assert len(reg.current()) == 2
    reg.verify()


def test_updating_supersedes_rather_than_rewrites(tmp_path: Path) -> None:
    reg = _registry(tmp_path)
    h = reg.add(Hypothesis(description="Hot numbers repeat."))
    updated = reg.update(h.hypothesis_id, status=Status.REJECTED, conclusion="No lift.")

    current = reg.current()
    assert len(current) == 1
    assert current[0].status == Status.REJECTED
    assert updated.hypothesis_id == h.hypothesis_id
    assert updated.revision == 1
    assert len(reg.history()) == 2, "the original record must still be there"
    assert reg.history()[0].status == Status.PROPOSED
    reg.verify()


def test_inconclusive_is_available_and_distinct_from_rejected() -> None:
    """Failing to detect an effect is not the same as showing there is none."""
    assert Status.INCONCLUSIVE != Status.REJECTED
    assert set(Status) >= {
        Status.PROPOSED,
        Status.TESTING,
        Status.REJECTED,
        Status.INCONCLUSIVE,
        Status.SUPPORTED,
    }


def test_unknown_hypothesis_raises(tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        _registry(tmp_path).get("nope")


def test_numpy_values_survive_the_round_trip(tmp_path: Path, loto: GameSpec) -> None:
    ledger = _ledger(tmp_path)
    recorded = _record(ledger, loto, date(2026, 9, 21))
    loaded = ledger.all()[0]
    assert loaded.prediction_id == recorded.prediction_id
    np.testing.assert_allclose(
        loaded.inclusion_probabilities["main"], recorded.inclusion_probabilities["main"]
    )
