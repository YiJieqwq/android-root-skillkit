#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
NAME=android-root-skillkit
SRC="$ROOT/$NAME"
DIST="$ROOT/dist"
OUT="$DIST/$NAME.skill"

[ -f "$SRC/SKILL.md" ] || {
  echo "missing $SRC/SKILL.md" >&2
  exit 1
}

mkdir -p "$DIST"
rm -f "$OUT"

cd "$ROOT"
if command -v zip >/dev/null 2>&1; then
  zip -q -r "$OUT" "$NAME" -x '*/.DS_Store' '*/__pycache__/*'
else
  python3 - "$ROOT" "$NAME" "$OUT" <<'PY'
import sys, zipfile
from pathlib import Path
root, name, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted((root/name).rglob('*')):
        if p.is_file() and p.name != '.DS_Store' and '__pycache__' not in p.parts:
            z.write(p, p.relative_to(root))
PY
fi

printf 'built %s\n' "$OUT"
