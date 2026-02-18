# Google Takeout Fixer

Fixes photo and video metadata after a Google Takeout export.

Google Takeout exports your media files alongside `.json` sidecar files containing the original metadata (date taken, GPS location). The media files themselves often have wrong or missing EXIF data and incorrect file timestamps. This tool reads the sidecar files and applies the correct metadata back to the media files.

## What it does

- Sets EXIF `DateTimeOriginal`, `DateTimeDigitized`, and `DateTime` from `photoTakenTime` in the sidecar
- Sets GPS EXIF data from `geoData` / `geoDataExif` if coordinates are non-zero
- Updates file modification timestamps to match the photo taken time
- Works with any file format that has a sidecar — JPEG files get full EXIF updates, other formats (PNG, MP4, MOV, etc.) get timestamps updated
- Only touches files that have a corresponding `.json` sidecar — everything else is left untouched
- Logs before/after values for date and location for every processed file

## Requirements

- Python 3.10+
- [piexif](https://pypi.org/project/piexif/)

## Setup

```bash
python3 -m venv venv
venv/bin/pip install piexif
```

## Usage

### Fix metadata

```bash
venv/bin/python3 fix_takeout.py <path>
```

Example:

```bash
venv/bin/python3 fix_takeout.py "/Volumes/photos/Takeout/Google Photos"
```

Output:

```
2023/_DSC0042.JPG  |  date: 2019:01:05 10:22:11 -> 2019:01:05 10:22:11  |  location: none -> lat=48.85341 lon=2.34880
2023/_DSC0043.MP4  |  date: n/a -> 2019:01:05 10:25:03  |  location: n/a -> none

Done: 338 updated, 0 errors.
```

### Remove sidecar JSON files

After fixing metadata, the `.json` sidecar files are no longer needed. To remove them:

```bash
venv/bin/python3 remove_json.py <path>
```

The script lists all files it will delete and asks for confirmation before proceeding.

## SMB / network shares

Mount the share first, then pass the local mount path:

```bash
# macOS — via Finder: Go > Connect to Server > smb://192.168.1.x/share
# Or via terminal:
mkdir -p /Volumes/my_share
mount_smbfs //192.168.1.x/my_share /Volumes/my_share

venv/bin/python3 fix_takeout.py "/Volumes/my_share/path/to/Takeout/Google Photos"
```
