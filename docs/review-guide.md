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

## Sharing reviews

Development main in daniel-carranza/HoTT-Rosetta is the single authoritative home
for shared reviews. Saving in the browser writes locally; it does not commit,
push, or publish anything. Other developers receive committed reviews by pulling.
Review metadata stays development-only, never in release or the public repository.
Historical tags are frozen evidence, not additional live review stores.

Browser pages show a muted tip explaining where reviews are saved and how to
share them. Git status stays hidden when the checkout is ready for reviews and
matches the last-known remote main. A notice appears for uncommitted reviews,
unpushed or incoming commits, unknown remote status, or blocked review writes.
Only relevant counts are shown. The notice's explicit Fetch review status button
refreshes the remote reference only; it never merges, stashes, resets, commits,
or pushes. Counts may be outdated until fetched; when the notice is hidden, use
review-sync status --fetch to check for new remote changes.
Shared review writes are allowed only on development main with a remote pointing
to the canonical fork. Topic branches, archival branches, and detached tags are
read-only for shared reviews. Resolve Git/review conflicts before reviewing again.

The remote may be named fork or origin; review-sync status identifies it. With
a remote named fork, the normal workflow is:

```text
python3 rosetta.py review-sync status --fetch
git merge fork/main
python3 rosetta.py review --web
```

Before merging incoming changes, commit your existing work deliberately; never
discard or auto-stash it. After reviewing, inspect and commit only the intended
review files (data/agda-reviews.json and, if changed, data/diagram-reviews.json).
Then fetch again, merge any incoming main changes, and push normally:

```text
python3 rosetta.py review-sync status --fetch
git merge fork/main
git push fork main
```

A rejected push means someone published first: fetch and merge again, never
force-push. Separate developers' checkouts are synchronized through Git, not the
local file locks. Scratchpads, compiler caches, and local backups are not shared.

### Concurrent review changes

The versioned .gitattributes uses Git's built-in binary merge behavior for the two
review JSON stores. This deliberately stops concurrent whole-file edits instead
of allowing a line merge to combine a decision with the wrong evidence hash.
No custom Git merge-driver installation is required. GitHub's web merge may also
stop on these files; resolve locally using the following commands, not by picking
the entire "ours" or "theirs" file.

After Git reports a review-file conflict:

```text
python3 rosetta.py review-sync merge agda
python3 rosetta.py review-sync merge diagram
```

Run only the command for each file Git marked conflicted. Independent comments
are retained and nonconflicting decisions are merged. New Agda comments have
stable IDs; legacy comments are retained conservatively, including duplicates
when distinct additions cannot be distinguished. A conflict-free result is
staged, but never committed or pushed automatically.

If decisions conflict, both versions and their original evidence are retained in
the JSON, displayed as conflict rather than approved, and the file stays unmerged.
Inspect the alternatives and choose explicitly without hand-editing JSON:

```text
python3 rosetta.py review-sync conflicts
python3 rosetta.py review-sync resolve agda BLOCK_ID --choose ours
```

The choices are ours, theirs, or pending; for diagrams use diagram and DIAGRAM_ID.
Only the decision is selected: both sides' comments remain. Selecting an old
decision does not refresh its evidence. Once every conflict in that review file
is resolved, it is staged. Inspect git diff --cached, finish any other Git merge
conflicts, commit the merge, and push. The tool refuses to replace review-file
edits made after Git stopped; preserve those edits before proceeding.

python3 rosetta.py review-sync check validates the review stores and rejects
unresolved decisions. CI runs this integrity check separately; ordinary Rosetta
checks still do not require review approval or completeness.

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
Adding a comment preserves the original decision fingerprint. Only an explicit
decision action can approve the current evidence again.
Decision forms also carry the evidence fingerprint shown to the reviewer; an
old browser page cannot approve code that changed since that page was opened.

Review decisions are optional. Pending means no decision, needs-further-review
means inspected but undecided, and approved/rejected record explicit decisions.
Missing-code items are comment-only. Ordinary conversion and checks do not
depend on these decisions or on loading the review metadata.

The former proposal-only auxiliary holes are retired. Accepted solutions belong
in the shared Rosetta. BENCHMARK.md separately lists intentional public benchmark
exercises; it is not an instruction to remove accepted auxiliary mathematics.
