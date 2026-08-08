#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
name = "android-root-skillkit"
skill = root / name
main = skill / "SKILL.md"
out = root / "dist" / f"{name}.skill"

errors = []
if not main.is_file():
    errors.append(f"missing {main}")
else:
    text = main.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("SKILL.md has no YAML frontmatter")
    if "name: android-root-skillkit" not in text:
        errors.append("frontmatter name mismatch")
    for target in re.findall(r"`([^`]+\.md)`", text):
        if not (skill / target).is_file():
            errors.append(f"broken internal reference: {target}")

for p in skill.rglob("*.md"):
    text = p.read_text(encoding="utf-8")
    if "android-root-toolkit" in text:
        errors.append(f"stale project name in {p.relative_to(root)}")

if out.exists():
    with zipfile.ZipFile(out) as z:
        names = set(z.namelist())
        expected = f"{name}/SKILL.md"
        if expected not in names:
            errors.append(f"archive missing {expected}")
        if any(n.startswith("skills/") for n in names):
            errors.append("archive contains unwanted skills/ prefix")

if errors:
    print("verification failed:")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)

print("verification passed")
