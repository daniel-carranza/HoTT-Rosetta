# HoTT Rosetta status

The active Rosetta directory is defined by `data/project-layout.json`.
Stable chapter, section, exercise, and support filenames are recorded in
`data/rosetta-files.json`.

Do not infer completion from file presence. Use these commands for current
status and validation:

```text
python3 rosetta.py inventory
python3 rosetta.py audit --from 3 --to 22
python3 rosetta.py check
```

`archive/legacy-rosetta/` is the historical former `src/` backup and is not an
input to active work.

Prioritize section prose and section Agda. Exercise prose remains generated,
but missing exercise Agda is deferred unless explicitly requested or needed by
a section.
