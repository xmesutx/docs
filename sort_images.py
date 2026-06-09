#!/usr/bin/env python3
"""Sort assets/images by git first-commit date into YYYY/MM subfolders."""

import subprocess
import os
import shutil
import re
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path('/home/user/docs')
IMAGES_DIR = REPO_ROOT / 'assets' / 'images'
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico'}
UNKNOWN_DATE = 'unknown'

def get_file_dates():
    """Return dict of relative_path -> 'YYYY/MM' using oldest Add commit."""
    print("Reading git history (this may take a minute)...")
    result = subprocess.run(
        ['git', 'log', '--all', '--diff-filter=A', '--name-only',
         '--format=COMMIT_DATE:%ai'],
        capture_output=True, text=True, cwd=REPO_ROOT
    )

    file_dates = {}
    current_date = None

    for line in result.stdout.split('\n'):
        line = line.rstrip()
        if line.startswith('COMMIT_DATE:'):
            # Format: "2022-03-07 20:40:03 +0000" -> "2022/03"
            date_str = line[12:]
            current_date = date_str[:7].replace('-', '/')
        elif line and current_date:
            # Overwrite to keep OLDEST (git log is newest->oldest)
            file_dates[line] = current_date

    return file_dates


def build_move_plan(file_dates):
    """Build list of (old_abs, new_abs) for image files."""
    plan = []
    no_date = []

    for rel_path, date in file_dates.items():
        ext = Path(rel_path).suffix.lower()
        if 'assets/images/' not in rel_path or ext not in IMAGE_EXTENSIONS:
            continue

        old_abs = REPO_ROOT / rel_path
        if not old_abs.exists():
            continue

        # Relative path inside assets/images/
        inner = rel_path.replace('assets/images/', '', 1)

        # Skip if already in a date-based folder (YYYY/MM/...)
        parts = inner.split('/')
        if len(parts) >= 2 and parts[0].isdigit() and len(parts[0]) == 4:
            continue

        new_rel = f'assets/images/{date}/{inner}'
        new_abs = REPO_ROOT / new_rel

        if old_abs != new_abs:
            plan.append((rel_path, new_rel, old_abs, new_abs))

    # Files with no git history
    for img in IMAGES_DIR.rglob('*'):
        if img.is_file() and img.suffix.lower() in IMAGE_EXTENSIONS:
            rel = str(img.relative_to(REPO_ROOT))
            if rel not in file_dates and rel not in {p[0] for p in plan}:
                inner = rel.replace('assets/images/', '', 1)
                parts = inner.split('/')
                if not (len(parts) >= 2 and parts[0].isdigit() and len(parts[0]) == 4):
                    no_date.append(rel)

    if no_date:
        print(f"  {len(no_date)} images without git history -> assets/images/unknown/")
        for rel in no_date:
            inner = rel.replace('assets/images/', '', 1)
            new_rel = f'assets/images/{UNKNOWN_DATE}/{inner}'
            new_abs = REPO_ROOT / new_rel
            plan.append((rel, new_rel, REPO_ROOT / rel, new_abs))

    return plan


def move_files(plan):
    """Create directories and move files."""
    print(f"Moving {len(plan)} files...")
    for i, (old_rel, new_rel, old_abs, new_abs) in enumerate(plan):
        new_abs.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_abs), str(new_abs))
        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{len(plan)} moved...")
    print(f"  Done.")


def update_references(plan):
    """Update all image references in text files."""
    # Build old->new mapping (repo-relative paths)
    path_map = {old_rel: new_rel for old_rel, new_rel, _, _ in plan}

    # Also build mapping without leading slash for variants used in markdown
    # Files can be referenced as: /assets/images/foo.png OR assets/images/foo.png
    variant_map = {}
    for old_rel, new_rel in path_map.items():
        variant_map[old_rel] = new_rel
        variant_map['/' + old_rel] = '/' + new_rel

    print("Scanning source files for references...")
    text_extensions = {'.md', '.yml', '.yaml', '.json', '.html', '.jsx', '.tsx', '.ts', '.js'}
    updated_files = 0

    for f in REPO_ROOT.rglob('*'):
        if not f.is_file() or f.suffix.lower() not in text_extensions:
            continue
        if '.git' in f.parts:
            continue

        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        new_content = content
        for old_path, new_path in variant_map.items():
            if old_path in new_content:
                new_content = new_content.replace(old_path, new_path)

        if new_content != content:
            f.write_text(new_content, encoding='utf-8')
            updated_files += 1

    print(f"  Updated {updated_files} files.")


def cleanup_empty_dirs():
    """Remove empty directories left after moving."""
    for dirpath, dirnames, filenames in os.walk(str(IMAGES_DIR), topdown=False):
        if not os.listdir(dirpath) and dirpath != str(IMAGES_DIR):
            os.rmdir(dirpath)


def main():
    file_dates = get_file_dates()
    print(f"Git history: {len(file_dates)} file entries found.")

    plan = build_move_plan(file_dates)
    print(f"Move plan: {len(plan)} images to relocate.")

    if not plan:
        print("Nothing to do.")
        return

    # Show summary by year/month
    summary = defaultdict(int)
    for _, new_rel, _, _ in plan:
        parts = new_rel.replace('assets/images/', '', 1).split('/')
        key = '/'.join(parts[:2]) if len(parts) >= 2 else 'unknown'
        summary[key] += 1
    for k in sorted(summary):
        print(f"  {k}: {summary[k]} images")

    move_files(plan)
    update_references(plan)
    cleanup_empty_dirs()
    print("Done! All images sorted by commit date.")


if __name__ == '__main__':
    main()
