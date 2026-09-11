# Implementation handoff

Updated 2026-09-11. Current authority: docs/conversion-contract.md.

## Direction

The Rosetta is maintained source, shared across the development fork, its
release branch, and the public repository. Generation creates only missing
files. Existing prose, Agda, support modules, and imports are edited directly.

Public content is the configured Rosetta directory, latex-book/, README.md, and
BENCHMARK.md. Everything else stays development-only. The old proposal and
artificial-hole policy is retired. Add future prerequisites where they belong.

## September 11 reconciliation

Development main was fast-forwarded from 17c3cb8 to public main ab71ec2, preserving
all accepted proposal solutions, reviewer comments, and today's direct exercise
and Markdown edits. Public merge fae1df6 accepted the proposal solutions.

Release 581887e supplies the README revisions and latex-book/ rename.
Its older Section 6.4 and 7.3 versions were superseded by the deliberate human
revision d827e1c; retain the newer public versions. Only one Agda integration
correction was required: Exercise 2.4's unbound implicit parameter line is now
part of the swap-Π signature, with its proof body unchanged.

## Maintenance changes

- Conversion and individual creation commands skip existing files before
  rendering. Exclusive file creation protects against accidental overwrites.
- Support modules are created only if absent.
- Review reads maintained code and recognizes direct contributions without
  provenance records. Missing markers never cause stale manifest code to be
  presented as current code.
- Review is read-only for Rosetta files and manifests. Automatic promotion is
  disabled, including old confirmation forms and the legacy apply function.
  Passing drafts show suggested diffs for application in the collaborator's
  editor. Draft checks overlay maintained content, not reconstructed content.
- Metadata updates use one locked read-modify-write transaction across threads
  and processes. Draft revision checks reject stale saves/discards and prevent
  a finishing typecheck from restoring an older draft. Restart running review
  servers after updating; they retain old code until restarted.
- Typechecks use actual files and local imports. Cached review evidence tracks
  transitive dependencies. Agda's ignored interface caches are enabled.
- Ordinary checks do not load review metadata. CI checks file preservation
  instead of requiring equality with reconstructed output.
- content-diff compares committed shared content and checks the public allowlist.
  See repository-layout.md for propagation and permissions.

## Validation and publication

All 22 aggregate chapters pass actual Agda 2.9.0-295c60c locally after the small
Exercise 2.4 correction. This does not imply complete formalization.
All 20 Agda files changed by the accepted-history reconciliation pass individual
maintained-file checks. Sections 7.3 and 14.1 also pass after trailing-whitespace
normalization for the release diff. There are no new proofs.
The 200 tests not requiring loopback connections, the provenance and ordinary
repository checks, and whitespace checks pass. The skill frontmatter was
validated with Ruby's YAML parser; the bundled Python validator lacks PyYAML
in this environment.

GitHub CI passed the full 201-test suite, including the review-server HTTP smoke
test, content-preservation checks, and aggregate Chapters 1--22 with Agda 2.8.0:
https://github.com/daniel-carranza/HoTT-Rosetta/actions/runs/34631141699
This run validates backend commit 01e13b5. Locally, starting the HTTP server
works, but connecting to 127.0.0.1 is denied, including one elevated retry.
Do not work around that restriction; CI supplies the external smoke-test result.

The subsequent concurrency hardening has regression coverage for simultaneous
comments, cross-process first creation, stale tabs, superseded typechecks, and
rejection of old write endpoints. Handler tests exercise POST requests without
network access. No Rosetta or Agda changes are part of this hardening; manifest
helper scripts remain unchanged as requested. The earlier CI result above is
historical validation, not a claim about these subsequent changes.
For the hardening, all 212 non-network tests pass locally, along with repository
and whitespace checks. The full 213-test suite still encounters the known local
loopback restriction; do not treat that environment error as a passing test.

The reconciled public snapshot is commit 76cb07a. Release 86105c4 records the
accepted public ancestry without changing that snapshot's tree. Both release
and development main have been pushed to the fork. Their shared content matches
development main, and its only roots are README.md, BENCHMARK.md, latex-book/,
and the configured Rosetta directory. Release's development-only .gitignore
was removed; it remains recoverable from Git history and remains in development.
Content commits on main are 4a51cec and 7299716. The backend commit is 01e13b5.
The available token is limited to the fork; publishing the prepared release
into EgbertRijke/HoTT-Rosetta requires a maintainer with access and remains
outstanding. Release descends from the inspected public main ab71ec2, permitting
a normal fast-forward publication. Fetch and check public main again before
publishing; reconcile any intervening contributions rather than force-pushing.

## Future mathematics

Resume section formalization in Chapter 15 when requested. Chapters 3--22 remain
the section priority; accepted exercise contributions are preserved. Keep the
existing source-backed content of Chapters 10--14 and their accepted auxiliaries.
Consult section-agda-audit.md and invisible-math.md as historical mathematical
evidence, not current branch restrictions. File presence, reviews, and compiler
success do not replace a mathematical coverage audit.

Run the validations in AGENTS.md on current files before handing off further work.
