"""Read-only EuroMillions endpoints for the dashboard (``/api/euromillions/...``).

Everything is read from what the CLI already wrote: the draw store, the forward carnet,
the JSON results of the pre-registered analysis and backtest, the hypothesis registry and
the agent's log. Nothing here computes a statistic or writes a file.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from predlab.core.hashing import AppendOnlyLedger, LedgerCorruptionError
from predlab.core.paths import Paths
from predlab.lottery.euromillions import EuroMillionsStore
from predlab.lottery.forward_em import Carnet, next_draw_date, summarise
from predlab.registry.hypotheses import HypothesisRegistry

RECENT_DRAWS = 12
LOG_LINES = 12


def _json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _tail(path: Path, n: int) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return [line for line in lines if line.strip()][-n:]


def _carnet(paths: Paths) -> Carnet:
    return Carnet(AppendOnlyLedger(paths.lottery / "euromillions_carnet.jsonl"))


def lottery_router(paths: Paths) -> APIRouter:
    router = APIRouter(prefix="/api/euromillions")
    store = EuroMillionsStore(paths.euromillions_store)

    def draws_by_date() -> dict[str, dict[str, Any]]:
        if not store.exists():
            return {}
        df = store.read()
        return {
            d.isoformat(): {
                "draw_date": d.isoformat(),
                "balls": main,
                "stars": stars,
                "balls_order": order,
            }
            for d, main, stars, order in zip(
                df["draw_date"].to_list(),
                df["main_numbers"].to_list(),
                df["stars_numbers"].to_list(),
                df["main_order"].to_list(),
                strict=True,
            )
        }

    @router.get("/carnet")
    def carnet() -> dict[str, Any]:
        """Frozen grids waiting for their draw, settled draws (newest first), totals."""
        book = _carnet(paths)
        try:
            book.ledger.verify()
            chain_ok = True
        except LedgerCorruptionError:
            chain_ok = False
        draws = draws_by_date()
        last = max(draws) if draws else None
        settled = book.settled()
        grids = book.grids()
        results = {(r["draw_date"], r["logic"]): r for r in book.results()}
        pending = [g for g in grids if (g["draw_date"], g["logic"]) not in settled]
        by_draw: dict[str, list[dict[str, Any]]] = {}
        for g in grids:
            r = results.get((g["draw_date"], g["logic"]))
            if r is None:
                continue
            by_draw.setdefault(g["draw_date"], []).append(
                {
                    "logic": g["logic"],
                    "balls": g["balls"],
                    "stars": g["stars"],
                    "ball_hits": r["ball_hits"],
                    "star_hits": r["star_hits"],
                    "rank": r["rank"],
                    "payout_eur": r["payout_eur"],
                }
            )
        settled_draws = [
            {
                "draw_date": day,
                "balls": draws.get(day, {}).get("balls"),
                "stars": draws.get(day, {}).get("stars"),
                "grids": rows,
            }
            for day, rows in sorted(by_draw.items(), reverse=True)
        ]
        return {
            "last_draw": draws.get(last) if last else None,
            "next_draw": next_draw_date(date.fromisoformat(last)).isoformat() if last else None,
            "pending": pending,
            "draws": settled_draws,
            "summary": summarise(book),
            "chain_ok": chain_ok,
            "agent_log": _tail(paths.logs / "lottery.log", LOG_LINES),
        }

    @router.get("/analysis")
    def analysis() -> dict[str, Any]:
        """Pre-registered historical tests, the pure-chance control and the registry."""
        registry = HypothesisRegistry(AppendOnlyLedger(paths.hypotheses))
        hyps = [
            h.model_dump(mode="json")
            for h in registry.current()
            if h.hypothesis_id.startswith("em-")
        ]
        return {
            "analysis": _json(paths.lottery / "analysis_v1.json"),
            "control": _json(paths.lottery / "control_r2.json"),
            "hypotheses": hyps,
        }

    @router.get("/backtest")
    def backtest() -> dict[str, Any]:
        return {"backtest": _json(paths.lottery / "backtest_v1.json")}

    @router.get("/data")
    def data() -> dict[str, Any]:
        """Store contents, latest draws, archive provenance, agent log."""
        manifest = paths.manifests / "euromillions_fdj.json"
        archives = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
        if not store.exists():
            return {"store": None, "recent": [], "archives": archives, "agent_log": []}
        df = store.read()
        eras = dict(df.group_by("era").len().sort("era").iter_rows())
        recent = df.tail(RECENT_DRAWS).reverse()
        rows = []
        for rec in recent.iter_rows(named=True):
            winners = rec["winners_eu"] or []
            rapports = rec["rapports"] or []
            rows.append(
                {
                    "draw_date": rec["draw_date"].isoformat(),
                    "weekday": rec["weekday"],
                    "balls": rec["main_numbers"],
                    "balls_order": rec["main_order"],
                    "stars": rec["stars_numbers"],
                    "jackpot_winners": winners[0] if winners else None,
                    "jackpot_eur": rapports[0] if rapports else None,
                }
            )
        dates = df["draw_date"].to_list()
        return {
            "store": {
                "draws": len(df),
                "first": dates[0].isoformat(),
                "last": dates[-1].isoformat(),
                "eras": eras,
                "retrieved_at": df["retrieved_at"].to_list()[-1],
            },
            "recent": rows,
            "archives": archives,
            "agent_log": _tail(paths.logs / "lottery.log", LOG_LINES),
            "agent_errors": _tail(paths.logs / "lottery.err.log", 5),
        }

    return router
