# Review program

Run python3 rosetta.py review --web in the development fork, open the printed
local address, and stop with Ctrl-C. Startup and browsing read the existing
Rosetta. There is no conversion prerequisite and existing files are never
regenerated. Review is read-only for Rosetta files and provenance manifests.
A sandbox must allow local server connections for browser use. After updating
the tools, stop and restart any existing review server: a running process keeps
its previously loaded code.

The loading page stays visible while files are indexed. The file reader shows
current maintained prose and Agda. External edits refresh the index. The review
table supports status filters, sorting, text search, and comment filters.

Each curated block shows the maintained code, recorded source, provenance,
typecheck evidence, and reviewer comments. Directly added blocks without
provenance records also appear, labeled unrecorded; they can be reviewed and
their containing file can be checked. Edit these blocks directly until their
provenance is recorded. A deleted or absent block is never replaced on screen
with stale manifest code.

Run Agda check checks the actual maintained file and its local imports. A passing
result becomes outdated when the file or any transitive local dependency changes.
Agda's ordinary interface caches are ignored by Git. A pass only establishes
acceptance of the code that exists, not mathematical coverage.

## Curated block edits

Open the scratchpad editor to draft a change to a curated block. The draft
overlays only that block on the current maintained document. Its temporary
typecheck file is discarded after checking; there is no preview Rosetta tree.

A passing draft can show a suggested file and provenance diff. This is read-only:
there is no automatic promotion or confirmation save. Compare the suggestion
with the latest file in your editor, make the focused changes there, and check
the maintained file. Never replace an entire file with an old draft. Old browser
confirmation forms are rejected without writing files.

Draft forms carry a revision. If another tab saves, discards, or finishes checking
that draft, a stale action is rejected. A check finishing after a newer save
cannot restore the older draft. A conflict response retains submitted code for
copying before you reload. If the underlying Rosetta changes, reload and discard
the stale draft before starting a new one.

Comment and decision saves use complete locked transactions, including first
creation of the stores. Two ordinary comment submissions preserve both comments;
a comment alone does not reset another reviewer's decision. An explicit later
decision can still change the current decision. The locks work across threads
and separate review/CLI processes sharing a checkout. They require POSIX file
locking (macOS/Linux); unsupported platforms refuse metadata writes rather than
silently disabling protection. They do not coordinate independent JSON editors.

Metadata backups live under .rosetta-backups/. Scratchpad state and check evidence
live under _build/rosetta-review/. These are ignored development artifacts.
The review metadata in data/agda-reviews.json preserves comments and decisions.
Changed evidence makes earlier decisions stale; nothing is silently reapproved.

Review decisions are optional. Pending means no decision, needs-further-review
means inspected but undecided, and approved/rejected record explicit decisions.
Missing-code items are comment-only. Ordinary conversion and checks do not
depend on these decisions or on loading the review metadata.

The former proposal-only auxiliary holes are retired. Accepted solutions belong
in the shared Rosetta. BENCHMARK.md separately lists intentional public benchmark
exercises; it is not an instruction to remove accepted auxiliary mathematics.
