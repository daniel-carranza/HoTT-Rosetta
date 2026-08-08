# HoTT Rosetta

HoTT Rosetta pairs the prose of *Introduction to Homotopy Type Theory* with
self-contained Agda formalizations. The tracked literate Agda Markdown in
[`rosetta-book/`](rosetta-book/) is generated reproducibly from the LaTeX in
[`book/`](book/), the converter in [`converter/`](converter/), and curated
provenance data in [`data/`](data/).

The project targets faithful conversion of Chapters 3–22. Chapters 1–2 are
included as useful supporting material. A generated file being present does
not by itself mean its prose, formalization, provenance, or review is complete.

## Install

Clone the repository and its pinned agda-unimath submodule:

```sh
git clone --recurse-submodules https://github.com/daniel-carranza/HoTT-Rosetta.git
cd HoTT-Rosetta
```

If the repository is already cloned, initialize the submodule with:

```sh
git submodule update --init --recursive
```

Required tools are Python 3.10 or newer, Pandoc 3.10.1, and Agda 2.8.0 or
newer. The converter
uses only Python’s standard library. Agda is needed for typechecking but not
for ordinary conversion or browsing. Confirm installations with:

```sh
python3 --version
pandoc --version
agda --version
```

Install those programs with your operating system’s package manager or their
official installation instructions. The pinned submodule revision is recorded
in Git; generated files never import from it at typecheck time.

## Convert and check

From the repository root, regenerate the required compatibility range and run
the ordinary checks:

```sh
python3 rosetta.py convert
python3 -m unittest discover
python3 rosetta.py check
git diff --check
```

To regenerate every chapter, including the optional first two:

```sh
python3 rosetta.py convert --from 1 --to 22
```

The active product location is configured only in
[`data/project-layout.json`](data/project-layout.json). Typecheck all aggregate
chapter modules with:

```sh
python3 rosetta.py typecheck-all
```

## Read the generated book

Open [`rosetta-book/`](rosetta-book/) and begin with a `chapter-*.lagda.md`
file. Chapter files contain the chapter introduction and import their section
and exercise modules. Section files are the primary prose-and-code reading
units. GitHub renders the Markdown; Agda checks the fenced `agda` blocks.

## Optional review UI

Start the local, read-only book browser and review interface with:

```sh
python3 rosetta.py review --web
```

Then open <http://127.0.0.1:8765/> and stop the server with `Ctrl-C`. Review
records are separate from generation and never gate ordinary conversion or
checks. See [`docs/review-guide.md`](docs/review-guide.md) for the workflow.

## Repository layout

- `book/`: original LaTeX sources and the source PDF
- `rosetta-book/`: tracked generated literate Agda product
- `converter/`: converter, provenance checks, and review server
- `data/`: configuration, filename registry, provenance, and review records
- `tests/`: Python unit tests
- `scripts/`: maintenance utilities
- `docs/`: user and implementation documentation
- `skills/`: agent translation workflow
- `external/agda-unimath/`: pinned source submodule
- `archive/legacy-rosetta/`: historical backup, never used at runtime

## Contributing

Put durable fixes in the converter or curated data and regenerate; do not edit
generated product files as the source of truth. Never write a new Agda block
by hand. Find the closest applicable code in the pinned agda-unimath checkout,
copy it with exact commit/file/line/hash provenance, and label adaptations
honestly. Generated modules must use repository-local imports.

Before opening a pull request, run the commands under “Convert and check.” If a
changed section contains Agda, also run `python3 rosetta.py typecheck-candidate
CHAPTER SECTION`. See [`docs/conversion-contract.md`](docs/conversion-contract.md)
for the complete contract.

## Troubleshooting

- “Pandoc is not installed”: install Pandoc and ensure `pandoc` is on `PATH`.
- “Agda is not installed”: install Agda 2.8.0 or newer and ensure `agda` is on `PATH`.
- Provenance checks cannot read agda-unimath: run `git submodule update --init`.
- A local import is missing: regenerate the complete dependency range and
  confirm `data/project-layout.json` points to `rosetta-book`.
- Stale `.agdai` behavior: remove local Agda build caches; `.agdai` files are
  generated artifacts and must not be committed.

## Current limitations

Conversion fidelity is required for Chapters 3–22; Chapters 1–2 remain
optional compatibility material. Some numbered items have no curated Agda,
some historical blocks are explicitly classified as handwritten/local, and
automatically rendered diagrams still require human judgment. Review state is
informational unless a strict release check is explicitly requested.

## Acknowledgments

The prose source is the [arXiv version](https://arxiv.org/abs/2212.11082) of
Egbert Rijke’s book, and formalizations are copied from or adapted from
[agda-unimath](https://unimath.github.io/agda-unimath/) with recorded
provenance. The project was developed by ASTRAL contributors as part of
DARPA’s expMath program; Git history preserves individual contributions.
