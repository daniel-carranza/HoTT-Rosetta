# Reviewing Agda code

The review program is optional. Conversion works without it.

## Start the review program

From the project directory, run:

```text
python3 rosetta.py review --web
```

Open the address printed in the terminal, normally:

```text
http://127.0.0.1:8765/
```

Press `Ctrl-C` in the terminal when you are finished.

## What the page shows

Each review page contains three parts:

1. The statement or proof from the book.
2. The Agda code used by this project.
3. The recorded code from agda-unimath, including its file, lines, and commit.

An **exact** block is a byte-for-byte copy of the recorded source. An
**adapted** block was changed for this project. Adapted blocks are clearly
marked and must not be treated as exact copies.

You can approve or reject a block, add a shared comment, and move to the next
or previous block. Decisions are saved in `data/agda-reviews.json` so they can
be shared with collaborators.

Numbered items without candidate Agda code use the same review page. They show
empty code and a **missing** label, and accept comments about useful upstream
search results. They cannot be approved, rejected, or typechecked until code is
supplied.

## Viewing generated files

Choose **Read generated .lagda.md files** on the review home page. The browser
lists the active files from the directory configured in
`data/project-layout.json` and displays their complete current contents.
Generated documents are read-only here; durable changes belong in the converter
or its curated data.

If the book statement, project code, or recorded source changes, an earlier
decision becomes **stale** and must be reviewed again.

## Current coverage

Curated blocks appear automatically from `data/agda-blocks.json`. Numbered
items without curated code also appear automatically unless the
file's required coverage has been explicitly confirmed in
`data/agda-coverage.json`.
