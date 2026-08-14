# Historical existing-translation audit baseline

This is archived evidence, not current workflow guidance or a declaration of
completeness. Current status belongs in `docs/implementation-handoff.md`. It was
produced with:

```text
python3 rosetta.py audit --from 3 --to 17
```

## Findings

- Every expected section file from Chapters 3--17 is present.
- Every numbered theorem-like environment found in the corresponding LaTeX
  subsections has a matching numbered Markdown heading.
- Chapters 3--5 contain substantive Agda blocks in nearly every section.
- Sections 6.1 and 6.2 have no substantive Agda blocks under the audit's
  conservative definition; this may be appropriate for their content and must
  be checked rather than automatically classified as incomplete.
- Sections 6.3--7.3 contain substantive Agda blocks.
- Sections 7.4--17.6 contain no substantive Agda blocks. Their files are useful
  prose/structure fixtures but cannot serve as complete Agda fixtures.
- A full-block byte comparison of the 44 substantive section blocks in
  Chapters 3--6 found 10 exact agda-unimath matches. The other 34 require
  classification: some are clearly local compatibility adaptations (for
  example `UU` changed to `Type`), some rename or reformat upstream code, some
  combine excerpts, and some may be handwritten.

The source comparison can be reproduced with:

```text
python3 rosetta.py agda-source-audit --from 3 --to 6
```

The source audit now includes both section and exercise files. “Exact” means
the complete fenced block occurs byte-for-byte in the pinned agda-unimath
source. “Adapted/unmatched” is a provenance classification, not a claim that
the Agda code is incorrect.

With exercise files included, Chapters 3--6 contain 145 substantive blocks: 59
are exact full-block matches, 11 combine multiple exact excerpts from one
upstream file, 17 are normalization-evidenced adaptations, and 58 are
handwritten/local blocks with no upstream match. The earlier 10-of-44 figure above
remains the section-only baseline.

All 145 historical-baseline blocks now have curated manifest records. Manifest
provenance records 59 exact blocks, 33 adapted blocks, and 53 handwritten/local
blocks; the category totals differ from the mechanical audit because combined
excerpts and manually established related-source adaptations are recorded as
adapted rather than exact.

## What this does not establish

The audit does not yet prove that prose is complete, mathematics is rendered
correctly, each required definition/result/proof has a corresponding Agda
block, copied blocks match agda-unimath, or files typecheck. These dimensions
remain `unknown` until dedicated checks establish them.

After Agda filesystem access was enabled, the Chapter 3, 4, 5, and 6 aggregate
files all typechecked successfully with Agda 2.9.0-295c60c. This also checked
the section and exercise modules imported by those aggregate files. This is
compilation evidence for the current files, not evidence that a future
conversion reproduces their prose or Agda-block placement accurately.
