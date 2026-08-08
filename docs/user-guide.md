# HoTT Rosetta user guide

This guide covers conversion and review. Both are run from the project folder.

## Convert the book

Run:

```text
python3 rosetta.py convert
```

This creates the active Rosetta files in the directory configured by
`data/project-layout.json` (currently `rosetta-book/`). The product is tracked;
local Agda caches remain under ignored `_build/` directories.

To convert only a range of chapters, use:

```text
python3 rosetta.py convert --from 18 --to 22
```

Open the configured directory to inspect the generated files. File existence
alone does not mean a conversion is complete.

## Check the project

Run the ordinary checks with:

```text
python3 rosetta.py check
```

These checks do not require optional human reviews to be finished.

When a section candidate contains Agda, check it with:

```text
python3 rosetta.py typecheck-candidate CHAPTER SECTION
```

For example:

```text
python3 rosetta.py typecheck-candidate 3 2
```

Check an exercise candidate with:

```text
python3 rosetta.py typecheck-exercise-candidate CHAPTER EXERCISE
```

Check all aggregate chapter modules with:

```text
python3 rosetta.py typecheck-all
```

## Start the review program

Run:

```text
python3 rosetta.py review --web
```

Open the address printed in the terminal, normally
`http://127.0.0.1:8765/`. Press `Ctrl-C` in the terminal to stop the program.

## Review Agda code

Each Agda review page shows:

1. The statement or proof from the active generated Rosetta file.
2. The Agda code currently in that file.
3. Its recorded agda-unimath source, when one exists.

An **exact** block matches the recorded source byte for byte. An **adapted**
block has project changes. A **handwritten** block has no claimed upstream
source. A **blocked** block is recorded for review but is not inserted during
conversion because it is unfinished or fails a required check.

Reviewers can approve, reject, comment, and move between blocks. If relevant
content changes, an earlier decision becomes **stale** and must be reviewed
again. Reviews are shared in `data/agda-reviews.json`.

Numbered items with no candidate Agda code appear in this same list with empty
code and a **missing** label. Their pages accept shared comments, including
useful notes about relevant agda-unimath results, but cannot be approved,
rejected, or checked by Agda until candidate code is supplied.

## View a generated file

Choose **Read generated .lagda.md files** on the review home page for
a searchable file list and a clean, read-only view of each complete file.

Choose **Mathematical items missing Agda** to browse numbered definitions,
results, remarks, and similar items that do not yet have a substantive Agda
block. Each entry can be expanded to show its statement and proof and links to
the corresponding position in the complete file and its ordinary Agda review
page.

Files whose required Agda coverage has been explicitly confirmed are recorded
in `data/agda-coverage.json` and are omitted from this list. This accounts for
shared or later code blocks and for mathematical remarks that need no separate
formalization. Do not infer completeness from file presence alone; add a file
to this data only after its required Agda coverage has been checked.

Generated files are read-only in the review program. Make durable changes in
the converter or its curated data, then regenerate.

## Strict release checks

Use this only when preparing a reviewed release:

```text
python3 rosetta.py check --strict
```

Unlike the ordinary check, this reports unfinished source records and optional
reviews as failures.
