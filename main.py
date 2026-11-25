#!/usr/bin/env python3
"""news-image-20261125 entry.

Copies this repository's committed entry.png (a 1024x1024 summary of
25 November 2026 world news) into the output directory.

Only the Python standard library is used: argparse, hashlib, os, shutil,
struct and sys. No third-party package, no network access, no clock and no
randomness, so every run writes exactly the same bytes. That matters because
the grader runs the program where nothing beyond the standard library is
installed; a program importing Pillow would die there with
ModuleNotFoundError even though it runs fine on a machine that has Pillow.

Run it like this:

    MAKEFUN_OUTPUT_DIR=/tmp/ni25-out python3 main.py
    python3 main.py --out-dir /tmp/ni25-out
    python3 main.py --verify-only   # check entry.png, write nothing

The program first checks the committed image (PNG signature, 1024x1024
dimensions from the IHDR chunk, at most 1 MiB), then copies it, then reads
the copy back and compares both its length and its SHA-256 digest with the
committed file, so a short or corrupted copy is caught before exit 0.
"""

import argparse
import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024
MAX_IMAGE_BYTES = 1024 * 1024


def die(message):
    """Abort with the message on stderr and exit code 1."""
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def png_dimensions(blob):
    """Read (width, height) out of a PNG byte string's IHDR chunk.

    A PNG starts with an 8-byte signature, then the IHDR chunk: a 4-byte
    big-endian length, the four letters IHDR, then 13 bytes of data whose
    first eight bytes are the width and height as big-endian uint32s.
    """
    if len(blob) < 33:
        die("entry.png is too short to hold a PNG header")
    if blob[:8] != PNG_SIGNATURE:
        die("entry.png does not start with the PNG signature")
    if blob[12:16] != b"IHDR":
        die("entry.png has no IHDR chunk where one belongs")
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def digest_of(blob):
    """SHA-256 hex digest of a byte string."""
    return hashlib.sha256(blob).hexdigest()


def check_png(blob):
    """Validate the committed image bytes; return their SHA-256 digest."""
    width, height = png_dimensions(blob)
    if (width, height) != (IMAGE_WIDTH, IMAGE_HEIGHT):
        die(
            "entry.png is %dx%d, expected %dx%d"
            % (width, height, IMAGE_WIDTH, IMAGE_HEIGHT)
        )
    if len(blob) > MAX_IMAGE_BYTES:
        die(
            "entry.png is %d bytes, over the %d-byte limit"
            % (len(blob), MAX_IMAGE_BYTES)
        )
    return digest_of(blob)


def output_dir(cli_dir):
    """Work out where to write: --out-dir, then $MAKEFUN_OUTPUT_DIR, else /output.

    An explicitly set but empty $MAKEFUN_OUTPUT_DIR is an error rather than
    a silent fall back to /output.
    """
    if cli_dir:
        return Path(cli_dir)
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir is not None:
        if not env_dir.strip():
            die("MAKEFUN_OUTPUT_DIR is set but empty")
        return Path(env_dir)
    return Path("/output")


def parse_args(argv):
    """Command-line options for this program."""
    parser = argparse.ArgumentParser(
        description="Copy the committed entry.png to the output directory."
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="where to write entry.png (overrides $MAKEFUN_OUTPUT_DIR)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="only check the committed entry.png, write nothing",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Entry point: verify the committed image, then copy it out."""
    args = parse_args(argv)

    here = Path(__file__).resolve().parent
    committed = here / "entry.png"
    if not committed.is_file():
        die("committed entry.png not found next to main.py: %s" % committed)

    try:
        blob = committed.read_bytes()
    except OSError as exc:
        die("cannot read %s: %s" % (committed, exc))

    digest = check_png(blob)

    if args.verify_only:
        print(
            "entry.png OK: %d bytes, %dx%d, sha256=%s"
            % (len(blob), IMAGE_WIDTH, IMAGE_HEIGHT, digest)
        )
        return 0

    target_dir = output_dir(args.out_dir)
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        die("cannot create output directory %s: %s" % (target_dir, exc))

    target = target_dir / "entry.png"
    try:
        shutil.copyfile(committed, target)
    except OSError as exc:
        die("cannot copy entry.png to %s: %s" % (target, exc))

    try:
        written = target.read_bytes()
    except OSError as exc:
        die("cannot read back %s: %s" % (target, exc))

    if len(written) != len(blob):
        die(
            "output entry.png is %d bytes, expected %d — the copy looks "
            "truncated" % (len(written), len(blob))
        )
    if digest_of(written) != digest:
        die("output entry.png digest differs from the committed image")

    print(
        "wrote %s: %d bytes, sha256=%s"
        % (target, len(written), digest)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
