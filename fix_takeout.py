#!/usr/bin/env python3
"""Fix Google Takeout photo metadata: set EXIF datetime and GPS from sidecar JSON files."""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

import piexif


def collect_files(input_path: Path) -> list[tuple[Path, Path]]:
    """Return (media_path, json_path) pairs for all files that have a sidecar JSON.

    Each sidecar is named <file>.<ext>.json, so stripping .json gives the media file.
    """
    pairs = []
    for json_path in sorted(input_path.rglob('*.json')):
        media_path = json_path.with_suffix('')
        if media_path.is_file():
            pairs.append((media_path, json_path))
    return pairs


def to_dms_rational(degrees: float) -> tuple:
    """Convert decimal degrees to EXIF DMS rational triplet."""
    degrees = abs(degrees)
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = round((degrees - d - m / 60) * 3600, 4)
    return (d, 1), (m, 1), (int(s * 10000), 10000)


def read_exif_before(exif_dict: dict) -> tuple[str, str]:
    """Extract current datetime and GPS strings from loaded EXIF for before/after logging."""
    # Datetime
    raw_dt = (
        exif_dict.get('Exif', {}).get(piexif.ExifIFD.DateTimeOriginal)
        or exif_dict.get('0th', {}).get(piexif.ImageIFD.DateTime)
    )
    if raw_dt:
        dt_str = raw_dt.decode(errors='replace').strip('\x00')
    else:
        dt_str = 'none'

    # GPS
    gps = exif_dict.get('GPS', {})
    lat_val = gps.get(piexif.GPSIFD.GPSLatitude)
    lon_val = gps.get(piexif.GPSIFD.GPSLongitude)
    lat_ref = gps.get(piexif.GPSIFD.GPSLatitudeRef, b'N')
    lon_ref = gps.get(piexif.GPSIFD.GPSLongitudeRef, b'E')

    if lat_val and lon_val:
        def dms_to_deg(dms):
            return dms[0][0]/dms[0][1] + dms[1][0]/dms[1][1]/60 + dms[2][0]/dms[2][1]/3600
        lat = dms_to_deg(lat_val) * (-1 if lat_ref in (b'S', 'S') else 1)
        lon = dms_to_deg(lon_val) * (-1 if lon_ref in (b'W', 'W') else 1)
        gps_str = f"lat={lat:.5f} lon={lon:.5f}"
    else:
        gps_str = 'none'

    return dt_str, gps_str


def process_image(img_path: Path, meta: dict) -> tuple[str, str, str, str]:
    """Apply metadata from JSON to image EXIF and file timestamps, logging before/after."""
    photo_taken_ts = int(meta.get('photoTakenTime', {}).get('timestamp', 0))
    if not photo_taken_ts:
        raise ValueError("no photoTakenTime in metadata")

    dt = datetime.fromtimestamp(photo_taken_ts, tz=timezone.utc)
    exif_dt = dt.strftime('%Y:%m:%d %H:%M:%S').encode()

    geo = meta.get('geoData', {})
    lat = geo.get('latitude', 0.0)
    lon = geo.get('longitude', 0.0)
    alt = geo.get('altitude', 0.0)

    if lat == 0.0 and lon == 0.0:
        geo_exif = meta.get('geoDataExif', {})
        lat = geo_exif.get('latitude', 0.0)
        lon = geo_exif.get('longitude', 0.0)
        alt = geo_exif.get('altitude', 0.0)

    has_gps = lat != 0.0 or lon != 0.0

    # Try EXIF update (JPEG only); fall back to timestamps-only for other formats
    before_dt = before_gps = 'n/a'
    try:
        exif_dict = piexif.load(str(img_path))
        before_dt, before_gps = read_exif_before(exif_dict)

        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_dt
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = exif_dt
        exif_dict['0th'][piexif.ImageIFD.DateTime] = exif_dt

        if has_gps:
            exif_dict['GPS'] = {
                piexif.GPSIFD.GPSLatitudeRef: b'N' if lat >= 0 else b'S',
                piexif.GPSIFD.GPSLatitude: to_dms_rational(lat),
                piexif.GPSIFD.GPSLongitudeRef: b'E' if lon >= 0 else b'W',
                piexif.GPSIFD.GPSLongitude: to_dms_rational(lon),
                **({
                    piexif.GPSIFD.GPSAltitudeRef: b'\x00' if alt >= 0 else b'\x01',
                    piexif.GPSIFD.GPSAltitude: (int(abs(alt) * 100), 100),
                } if alt != 0.0 else {}),
            }

        piexif.insert(piexif.dump(exif_dict), str(img_path))
    except Exception:
        pass  # Non-JPEG or malformed EXIF — timestamps will still be updated below

    os.utime(str(img_path), (photo_taken_ts, photo_taken_ts))

    after_dt = dt.strftime('%Y:%m:%d %H:%M:%S')
    after_gps = f"lat={lat:.5f} lon={lon:.5f}" if has_gps else 'none'

    return before_dt, after_dt, before_gps, after_gps


def main():
    if len(sys.argv) < 2:
        print("Usage: fix_takeout.py <input_path>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.is_dir():
        print(f"Error: not a directory: {input_path}")
        sys.exit(1)

    processed = errors = 0

    for img_path, json_path in collect_files(input_path):
        rel = img_path.relative_to(input_path)

        with open(json_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        try:
            before_dt, after_dt, before_gps, after_gps = process_image(img_path, meta)
            print(f"{rel}  |  date: {before_dt} -> {after_dt}  |  location: {before_gps} -> {after_gps}")
            processed += 1
        except Exception as exc:
            print(f"ERROR {rel}: {exc}")
            errors += 1

    print(f"\nDone: {processed} updated, {errors} errors.")


if __name__ == '__main__':
    main()
