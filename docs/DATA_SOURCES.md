# Data sources

Everything in this document was read from the live official source on the date stated.
Nothing here is recalled from training data or inferred. Where a fact has **not** been
verified, it says so.

## Loto — official FDJ archive

**Retrieved:** 2026-09-19
**Publisher:** La Française des Jeux (FDJ)
**Landing page:** <https://www.fdj.fr/jeux-de-tirage/loto/historique>

FDJ splits the Loto history into five archives. The split points are format and rule
changes, not arbitrary chunking. Only the current era is ingested; see *Era scope*.

| Period | URL suffix (under the base below) | Size | Ingested |
|---|---|---|---|
| Nov 2019 → Sep 2026 | `1a2b3c4d-9876-4562-b3fc-2c963f66afp6` | 180 kB | **yes** |
| Feb 2019 → Nov 2019 | `…afo6` | 14 kB | no |
| Mar 2017 → Feb 2019 | `…afn6` | 39 kB | no |
| Oct 2008 → Mar 2017 | `…afm6` | 69 kB | no |
| May 1976 → Oct 2008 | `…afl6` | 239 kB | no |

Base: `https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/documentations/`

The same page also publishes Grand Loto and Super Loto archives. These are different
games with different mechanics and are deliberately out of scope.

### Verified file format (2019-11 era)

| Property | Value |
|---|---|
| Container | ZIP, single member `loto_201911.csv` |
| SHA-256 of the ZIP as retrieved | `66a0f0a94c3f9ba45758f8cea886764be7ab9ef4f4e0e1931f3c7f6f5170e074` |
| ZIP size | 183 954 bytes |
| Encoding | Windows-1252 (`cp1252`) |
| Separator | `;` |
| Columns | 50, the 50th empty — every line ends with a trailing `;` |
| Line endings | CRLF |
| Row order | **descending** by draw date |
| Rows | 1 075 draws, 2019-11-06 → 2026-09-16 |
| Date format | `DD/MM/YYYY` |
| Ball range | 1–49, five per draw (all 5 375 values checked) |
| `numero_chance` range | 1–10, one per draw |
| Weekday counts | LUNDI 358, MERCREDI 359, SAMEDI 358 |
| Currency column | `eur` on every row |

### Quirks that would silently corrupt a naive parser

1. **`jour_de_tirage` is right-padded.** 277 of 1 075 rows carry trailing spaces
   (`"LUNDI   "`, `"SAMEDI  "`). Grouping on the raw string yields five weekday
   values instead of three. The parser strips before mapping.
2. **`annee_numero_de_tirage` changes format inside one file.** `20199133` in 2019
   versus `26111` in 2026. It is therefore kept verbatim for traceability only and
   never used as a key; the canonical key is derived from the draw date.
3. **`numero_7` is a Joker+ code, not a lottery number.** Three incompatible
   formats appear (`1003591`, `0 000 212`, and the literal string
   `Jokerplus indisponible`). Excluded from the predictive dataset.
4. **A "second tirage" block exists on every row.** Columns
   `boule_1_second_tirage` … are populated throughout the era. This is a second,
   separate draw, not part of the main one. It is **not** ingested in Milestone 1,
   and is noted in `docs/STATUS.md` as a candidate additional dataset.
5. **Prize and winner columns are read but discarded.** They describe how the public
   bet, not how the balls fell. Keeping them next to the numbers invites narrative
   fitting after the fact.

### Integrity checks applied at parse time

Each row must satisfy all of the following or ingestion stops:

- the five balls, sorted, plus the chance number must reproduce the source's own
  `combinaison_gagnante_en_ordre_croissant` string exactly;
- the stated weekday must match the calendar weekday of `date_de_tirage`;
- that weekday must be a draw day for the era (Mon/Wed/Sat);
- the date must fall inside the era's range;
- all numbers must lie in their declared pool;
- no two rows may share a draw date.

The header is compared against an exact expected tuple. If FDJ renames, adds or
reorders a column, ingestion fails with a message naming the difference. This is
intentional: a one-column shift would silently move `numero_chance` into `boule_5`
and poison every downstream result. The fix is to review the change and bump
`PARSER_VERSION`, never to relax the check.

### Era scope

Only `loto/2019-11` is defined as a `GameSpec`, because only its mechanics were
verified against data. The 1976, 2008, 2017 and 2019-02 archives exist and can be
downloaded, but their ball counts and rules have **not** been confirmed, so
`get_spec("loto", "1976-05")` deliberately raises rather than guessing.

Pooling draws across a format change is a methodological error, not an
approximation. Extending coverage means verifying each era's mechanics first.

### Known limitations

- The current-era file is **republished after every draw**, so its SHA-256 changes
  roughly three times a week. A different hash is expected, not alarming; a *changed
  historical row* is alarming, and `DrawStore` refuses it by default.
- The endpoint is undocumented. It is the download link the official history page
  actually uses, but FDJ publishes no contract for it and may change it without
  notice.
- No licence statement accompanies the archives. Usage here is non-commercial
  research. Redistribution of the raw files is not assumed to be permitted, which is
  why `data/raw/` is git-ignored while the provenance manifest is tracked.
- `data.gouv.fr` has not been evaluated as a cross-check source.

## Rules

Confirmed on <https://www.fdj.fr/jeux-de-tirage/loto> (2026-09-19): draws take place
Monday, Wednesday and Saturday.

FDJ announced a change of player return rate (TRJ 54.85% → 54.35%) effective
**2026-05-04**. Whether this touched the draw mechanics or only the prize structure
has **not** been verified. It is flagged as a candidate regime boundary and should be
checked before treating the era as homogeneous.
