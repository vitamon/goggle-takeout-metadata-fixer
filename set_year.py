#!/usr/bin/env python3
"""Set the year for all files in a folder, leaving month/day/time intact."""

import os
import sys
from pathlib import Path
from datetime import datetime


def set_year_for_files(folder: str, year: int, recursive: bool = False) -> None:
    folder_path = Path(folder)
    if not folder_path.is_dir():
        print(f"Error: '{folder}' is not a directory")
        sys.exit(1)

    pattern = "**/*" if recursive else "*"
    files = [p for p in folder_path.glob(pattern) if p.is_file()]

    if not files:
        print("No files found.")
        return

    for file in files:
        stat = file.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)
        atime = datetime.fromtimestamp(stat.st_atime)

        new_mtime = mtime.replace(year=year)
        new_atime = atime.replace(year=year)

        os.utime(file, (new_atime.timestamp(), new_mtime.timestamp()))
        print(f"{file.name}: {mtime.strftime('%Y-%m-%d %H:%M:%S')} -> {new_mtime.strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\nDone. Updated {len(files)} file(s).")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python set_year.py <folder> <year> [--recursive]")
        print("Example: python set_year.py ./photos 2020")
        sys.exit(1)

    folder_arg = sys.argv[1]
    year_arg = int(sys.argv[2])
    recursive_arg = "--recursive" in sys.argv or "-r" in sys.argv

    set_year_for_files(folder_arg, year_arg, recursive_arg)
