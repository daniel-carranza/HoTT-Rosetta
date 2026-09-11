"""Git synchronization and semantic merging of shared review metadata.

No automatic pulls, commits, pushes, stashes, or Rosetta writes. Git's built-in
binary merge driver stops overlapping review-file changes; explicit commands
merge comments and surface decision conflicts without editing JSON by hand.
"""

import copy
import json
import subprocess
from collections import Counter
from pathlib import Path

REPOSITORY = "daniel-carranza/HoTT-Rosetta"
STORES = {"agda": ("data/agda-reviews.json", "blocks"),
          "diagram": ("data/diagram-reviews.json", "diagrams")}


def git(root, *args, check=True):
    result = subprocess.run(["git", "-C", str(root), *args], text=True,
                            capture_output=True, check=False)
    if check and result.returncode:
        raise ValueError(result.stderr.strip() or "Git command failed")
    return result


def canonical_remote(root):
    for remote in git(root, "remote").stdout.splitlines():
        url = git(root, "remote", "get-url", remote).stdout.strip().removesuffix(".git").rstrip("/")
        if url.lower() in {("https://github.com/" + REPOSITORY).lower(),
                           ("git@github.com:" + REPOSITORY).lower(),
                           ("ssh://git@github.com/" + REPOSITORY).lower()}:
            return remote
    return None


def sync_status(root, fetch=False):
    result = {"branch": "not a Git checkout", "remote": None, "ahead": None,
              "behind": None, "dirty_reviews": [], "unmerged": [],
              "unpushed_review_commits": None, "writable": False}
    if git(root, "rev-parse", "--show-toplevel", check=False).returncode:
        result["reason"] = "Review sharing requires a Git checkout of the development fork."
        return result
    branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False).stdout.strip()
    result["branch"] = branch or "detached HEAD (historical snapshot)"
    remote = canonical_remote(root)
    result["remote"] = remote
    if fetch:
        if remote is None:
            raise ValueError("No remote for " + REPOSITORY)
        git(root, "fetch", "--no-tags", remote, "refs/heads/main:refs/remotes/" + remote + "/main")
    paths = [value[0] for value in STORES.values()]
    result["dirty_reviews"] = sorted(set(
        git(root, "diff", "--name-only", "HEAD", "--", *paths).stdout.splitlines()
        + git(root, "ls-files", "--others", "--exclude-standard", "--", *paths).stdout.splitlines()))
    result["unmerged"] = git(root, "diff", "--name-only", "--diff-filter=U").stdout.splitlines()
    try:
        result["review_conflicts"] = sorted(review_conflicts(root))
        result["review_error"] = ""
    except (OSError, ValueError) as error:
        result["review_conflicts"] = []
        result["review_error"] = str(error)
    if remote:
        reference = "refs/remotes/" + remote + "/main"
        if not git(root, "rev-parse", "--verify", reference, check=False).returncode:
            ahead, behind = git(root, "rev-list", "--left-right", "--count", "HEAD..." + reference).stdout.split()
            result.update(ahead=int(ahead), behind=int(behind))
            result["unpushed_review_commits"] = len(git(
                root, "log", "--format=%H", reference + "..HEAD", "--", *paths).stdout.splitlines())
    if branch != "main":
        result["reason"] = "Shared reviews may be saved only on development main, never on topic/archive branches or detached tags."
    elif remote is None:
        result["reason"] = "No remote for the authoritative development fork " + REPOSITORY
    elif result["unmerged"] or result["review_conflicts"] or result["review_error"]:
        result["reason"] = "Finish the Git merge before saving new reviews; use review-sync merge/resolve for review conflicts."
    else:
        result.update(writable=True, reason="Shared reviews belong to development main.")
    return result


def require_review_branch(root, allow_conflicts=False):
    status = sync_status(root)
    if allow_conflicts and status["branch"] == "main" and status["remote"]:
        return
    if not status["writable"]:
        raise ValueError(status["reason"])


def validate_store(value, collection):
    if not isinstance(value, dict) or value.get("version") != 1 or not isinstance(value.get(collection), dict):
        raise ValueError("Invalid review store")
    for key, record in value[collection].items():
        if not isinstance(record, dict) or not isinstance(record.get("comments", []), list):
            raise ValueError("Invalid review record: " + key)
        for comment in record.get("comments", []):
            if not isinstance(comment, str) and not (
                isinstance(comment, dict) and isinstance(comment.get("text"), str)
                and isinstance(comment.get("author"), str)
            ):
                raise ValueError("Invalid review comment: " + key)
        states = {"pending", "approved", "rejected", "needs-further-review"} if collection == "blocks" else {"pending", "approved"}
        if record.get("state", "pending") not in states:
            raise ValueError("Invalid review decision: " + key)
    return value


def _merge_comments(base, ours, theirs):
    # Existing comments can lack IDs; preserve their multiplicity. New comments
    # have UUIDs, so identical text submitted independently is still retained.
    encode = lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False)
    counts = [Counter(map(encode, side)) for side in (base, ours, theirs)]
    remaining = {}
    for key in sorted(counts[0].keys() | counts[1].keys() | counts[2].keys()):
        value = json.loads(key)
        if isinstance(value, dict) and value.get("id"):
            count = max(counter[key] for counter in counts)
        else:
            # With legacy ID-less comments, retain independent additions even
            # when their text is identical rather than losing a contribution.
            before, left, right = (counter[key] for counter in counts)
            count = before + max(0, left - before) + max(0, right - before)
        remaining[key] = count
    merged = []
    for value in [*base, *ours, *theirs]:
        key = encode(value)
        if remaining[key]:
            merged.append(copy.deepcopy(value))
            remaining[key] -= 1
    return merged


def merge_stores(base, ours, theirs, collection):
    for store in (base, ours, theirs):
        validate_store(store, collection)
    if any(set(store) - {"version", collection} for store in (base, ours, theirs)):
        raise ValueError("Unrecognized store fields; refusing to discard them")
    merged = {"version": 1, collection: {}}
    conflicts = []
    for key in sorted(set(base[collection]) | set(ours[collection]) | set(theirs[collection])):
        records = [store[collection].get(key, {}) for store in (base, ours, theirs)]
        if any("decision_conflict" in record for record in records):
            raise ValueError("Resolve the existing review conflict first: " + key)
        decisions = [{k: v for k, v in record.items() if k != "comments"} for record in records]
        before, left, right = decisions
        if left == right or right == before:
            decision = copy.deepcopy(left)
        elif left == before:
            decision = copy.deepcopy(right)
        else:
            decision = {"state": "pending", "decision_conflict": {"base": before, "ours": left, "theirs": right}}
            conflicts.append(key)
        comments = _merge_comments(*(record.get("comments", []) for record in records))
        # Never silently remove historical comments when one side deletes a record.
        if decision or comments:
            merged[collection][key] = {**decision, "comments": comments}
    return merged, conflicts


def merge_pending(root, kind):
    from .editing import update_json_store, EditConflict
    require_review_branch(root, allow_conflicts=True)
    filename, collection = STORES[kind]
    stages = {}
    for stage in (1, 2, 3):
        result = git(root, "show", f":{stage}:{filename}", check=False)
        if result.returncode and stage != 1:
            raise ValueError("Expected an unresolved two-sided review merge for " + filename)
        stages[stage] = result.stdout if not result.returncode else None
    base = json.loads(stages[1]) if stages[1] else {"version": 1, collection: {}}
    merged, conflicts = merge_stores(base, json.loads(stages[2]), json.loads(stages[3]), collection)

    def update(store):
        if store != json.loads(stages[2]):
            raise EditConflict("The working review file changed after Git stopped; preserve it and resolve the existing review conflicts first")
        for stage in (2, 3):
            if git(root, "show", f":{stage}:{filename}").stdout != stages[stage]:
                raise EditConflict("The Git merge changed while preparing reviews")
        store.clear()
        store.update(merged)

    update_json_store(root / filename, root, collection, update, allow_merge=True)
    if not conflicts:
        git(root, "add", "--", filename)
    return conflicts


def resolve_pending(root, kind, key, choice):
    from .editing import update_json_store
    require_review_branch(root, allow_conflicts=True)
    filename, collection = STORES[kind]

    def update(store):
        record = store[collection].get(key, {})
        conflict = record.get("decision_conflict")
        if not conflict:
            raise ValueError("No decision conflict for " + key)
        decision = conflict[choice] if choice in {"ours", "theirs"} else {"state": "pending"}
        store[collection][key] = {**copy.deepcopy(decision), "comments": record.get("comments", [])}

    store = update_json_store(root / filename, root, collection, update, allow_merge=True)
    remaining = [key for key, record in store[collection].items() if "decision_conflict" in record]
    if not remaining:
        git(root, "add", "--", filename)
    return remaining


def review_conflicts(root):
    result = {}
    for kind, (filename, collection) in STORES.items():
        path = root / filename
        if path.exists():
            store = validate_store(json.loads(path.read_text()), collection)
            for key, record in store[collection].items():
                if "decision_conflict" in record:
                    result[kind + ":" + key] = record["decision_conflict"]
    return result
