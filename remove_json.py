#!/usr/bin/env python3
"""Recursively remove all .json files from a directory."""

import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: remove_json.py <input_path>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.is_dir():
        print(f"Error: not a directory: {input_path}")
        sys.exit(1)

    files = sorted(input_path.rglob('*.json'))
    if not files:
        print("No .json files found.")
        return

    for path in files:
        print(path.relative_to(input_path))

    print(f"\n{len(files)} file(s) will be deleted. Proceed? [y/N] ", end='')
    if input().strip().lower() != 'y':
        print("Aborted.")
        return

    removed = errors = 0
    for path in files:
        try:
            path.unlink()
            removed += 1
        except Exception as exc:
            print(f"ERROR {path.relative_to(input_path)}: {exc}")
            errors += 1

    print(f"Done: {removed} removed, {errors} errors.")


if __name__ == '__main__':
    main()
