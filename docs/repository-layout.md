# Repository layout and inventory

This inventory distinguishes durable inputs and products from disposable local
state.

| Path | Classification | Versioned | Purpose |
| --- | --- | --- | --- |
| `book/` | source | yes | LaTeX, bibliography, class files, and source PDF |
| `rosetta-book/` | generated product | yes | 22 chapters plus registered sections, exercises, and support modules |
| `converter/` | tool | yes | Python conversion, checks, provenance, and review server |
| `data/` | curated data/configuration | yes | layout, names, Agda provenance, coverage, gaps, and reviews |
| `tests/` | tool validation | yes | standard-library unit tests |
| `scripts/` | maintenance tools | yes | controlled manifest utilities |
| `docs/` | documentation | yes | contracts, guides, handoff, and baseline evidence |
| `skills/` | agent workflow | yes | translation instructions and references |
| `external/agda-unimath/` | pinned external source | gitlink | provenance source only; never a generated-book import |
| `archive/legacy-rosetta/` | historical archive | yes | former `src/`; forbidden to active runtime workflows |
| `_build/` | cache/staging | no | candidate typechecks and review cache |
| `.rosetta-backups/` | recoverable local backup | no | atomic-edit recovery copies |

The authoritative active-product path is the value in
`data/project-layout.json`. Runtime code must not infer another product path.
The file registry in `data/rosetta-files.json` enumerates durable generated
documents; unregistered caches and Agda `.agdai` interfaces are not product
files.
