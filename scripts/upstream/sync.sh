#!/usr/bin/env bash
# Pull the newest pstack into mstack.
#
#   scripts/upstream/sync.sh          sync and commit on main (no push)
#   scripts/upstream/sync.sh --push   also push main and the upstream branch
#
# How it works: the `upstream` branch holds pstack with only the mechanical
# renames from transform.py. main holds mstack's own edits on top. Each sync
# commits a fresh pstack snapshot to `upstream` and merges it into main, so
# git carries mstack's edits forward and only stops where upstream rewrote
# the very lines mstack changed.
#
# Exit codes: 0 synced or already current, 2 merge conflict (main untouched,
# the new snapshot is on `upstream`; resolve by hand with `git merge upstream`).
set -euo pipefail

PUSH=0; [ "${1:-}" = "--push" ] && PUSH=1
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT"
HERE="$ROOT/scripts/upstream"
TMP=$(mktemp -d); trap 'git worktree remove --force "$TMP/up-wt" 2>/dev/null || true; rm -rf "$TMP"' EXIT

[ -z "$(git status --porcelain)" ] || { echo "working tree not clean" >&2; exit 1; }
[ "$(git rev-parse --abbrev-ref HEAD)" = main ] || { echo "run on main" >&2; exit 1; }

git clone --quiet --depth 1 --filter=blob:none --sparse https://github.com/cursor/plugins "$TMP/plugins"
git -C "$TMP/plugins" sparse-checkout set pstack
SHA=$(git -C "$TMP/plugins" rev-parse HEAD)
TREE=$(git -C "$TMP/plugins" rev-parse HEAD:pstack)
VER=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['version'])" "$TMP/plugins/pstack/.cursor-plugin/plugin.json")

if grep -q "^tree: $TREE$" UPSTREAM 2>/dev/null; then
  echo "already on pstack $VER"; exit 0
fi
echo "syncing pstack $VER (cursor/plugins ${SHA:0:7})"

git fetch --quiet origin upstream:upstream 2>/dev/null || true
git worktree add --quiet "$TMP/up-wt" upstream
python3 "$HERE/transform.py" "$TMP/plugins/pstack" "$TMP/snap"
( cd "$TMP/up-wt"
  git rm -rq --ignore-unmatch . >/dev/null
  cp -R "$TMP/snap/." .
  git add -A
  if git diff --cached --quiet; then echo "upstream branch unchanged"
  else git commit -qm "Upstream pstack $VER (cursor/plugins ${SHA:0:7}), renamed for mstack"; fi )

if ! git merge --no-edit -m "Merge pstack $VER into mstack" upstream >/dev/null 2>&1; then
  # Upstream deleting a file that mstack edited is not a real conflict: follow upstream.
  for f in $(git status --porcelain | awk '$1=="UD"{print $2}'); do git rm -q "$f"; done
  if [ -n "$(git diff --name-only --diff-filter=U)" ]; then
    echo "merge conflict in:" >&2; git diff --name-only --diff-filter=U >&2
    git merge --abort
    [ $PUSH = 1 ] && git push --quiet origin upstream
    exit 2
  fi
  git commit -q --no-edit
fi

python3 "$HERE/index.py"
printf 'upstream: https://github.com/cursor/plugins/tree/main/pstack\nversion: %s\ncommit: %s\ntree: %s\n' "$VER" "$SHA" "$TREE" > UPSTREAM
git add -A
git diff --cached --quiet || git commit -qm "Record pstack $VER as the synced upstream"

[ $PUSH = 1 ] && git push --quiet origin main upstream
echo "synced to pstack $VER"
