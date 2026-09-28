# PMU fixtures — what is real and what is not

The live feed could not be downloaded byte-for-byte from the environment that wrote
these tests (egress blocked). The contents below were read on **2026-09-28** through a
web-fetch tool that returned verbatim excerpts of the JSON. They are therefore
**excerpts**, not full responses.

| File | Verbatim | Placeholder / added |
|---|---|---|
| `programme_2026-09-28_excerpt.json` | Meeting 1 header, `hippodrome`, `pays`, `meteo`, and the first course up to `numCourseDedoublee`; meeting 2 course fields | Meeting 2: only `numOfficiel`, `hippodrome.code`, `pays.code` were given — the rest of its header is omitted, not invented |
| `participants_2026-09-28_R2C1_excerpt.json` | The complete first participant object; the four top-level keys | `ecuries` and `spriteCasaques` emptied; the eight other runners omitted |
| `programme_2026-09-27_R1C1_partial.json` | `programme.date` (derived: midnight Paris), course status fields, `ordreArrivee`, `heureDepart`, `dureeCourse`, `incidents` | `hippodrome.code = "PLACEHOLDER"`; `discipline = "ATTELE"` **inferred** (Vincennes meeting, gait disqualifications), not read |
| `participants_2026-09-27_R1C1_partial.json` | `numPmu`, `statut`, `ordreArrivee` (present/absent), both `dateRapport` values | `nom` = `RUNNER n`, `rapport` values — **placeholders** |

Replace these with full captures from `data/raw/pmu/` once the collector has run on
the Mac (`predlab racing parse-check` validates the parser against every capture).
