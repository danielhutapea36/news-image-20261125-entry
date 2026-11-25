#!/usr/bin/env python3
"""news-image-20261125 entry program.

Standard-library-only program (Python 3.13). It copies the repository's own
committed entry.png to the output directory — the same pattern the
competition's own starter uses ("the simplest program copies an image the
repository holds").

No Pillow, no third-party packages, no network access: the grader image runs
"standard library only: nothing is installed before it runs", and Pillow is
not available there. Everything the program needs is already committed in
this repository.

Usage:
    MAKEFUN_OUTPUT_DIR=/tmp/ni25-out python3 main.py
    python3 main.py --out-dir /tmp/ni25-out
    python3 main.py --verify-only        # check the committed entry.png only
"""

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

# PNG magic bytes (first 8 bytes of every PNG file).
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

# The image the build produced and committed to this repository.
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1 * 1024 * 1024  # 1 MiB


def fail(message: str) -> "SystemExit":
    """Print an error to stderr and return an exit-1 exception."""
    print(f"error: {message}", file=sys.stderr)
    return SystemExit(1)


def read_png_dimensions(data: bytes) -> tuple[int, int]:
    """Return (width, height) from a PNG's IHDR chunk.

    PNG layout: 8-byte signature, then the IHDR chunk (4-byte length,
    4-byte type "IHDR", 13 bytes of data). Width is the first 4 bytes of
    that data, height the next 4, both big-endian unsigned integers.
    """
    if len(data) < 24 + 4:
        raise ValueError("file too short to contain a PNG IHDR chunk")
    if data[12:16] != b"IHDR":
        raise ValueError("first chunk is not IHDR; not a valid PNG")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    return width, height


def check_image(data: bytes, label: str) -> str:
    """Validate the PNG bytes and return their SHA-256 hex digest.

    Checks: PNG magic, 1024x1024 dimensions, size at most 1 MiB.
    Raises ValueError with a clear message on any failure.
    """
    if not data.startswith(PNG_MAGIC):
        raise ValueError(f"{label}: missing PNG magic bytes")
    width, height = read_png_dimensions(data)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(
            f"{label}: expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}, "
            f"got {width}x{height}"
        )
    if len(data) > MAX_BYTES:
        raise ValueError(
            f"{label}: {len(data)} bytes exceeds the {MAX_BYTES}-byte limit"
        )
    return hashlib.sha256(data).hexdigest()


def resolve_output_dir(out_dir_flag: str | None) -> Path:
    """Resolve the output directory: --out-dir wins, then $MAKEFUN_OUTPUT_DIR,
    then /output. An explicitly set but empty $MAKEFUN_OUTPUT_DIR is an
    error (exit 1) instead of silently falling back to /output."""
    if out_dir_flag:
        return Path(out_dir_flag)
    env_value = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_value is not None:
        if env_value.strip() == "":
            raise ValueError(
                "MAKEFUN_OUTPUT_DIR is set but empty; "
                "set it to a directory or unset it"
            )
        return Path(env_value)
    return Path("/output")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Copy the committed entry.png to the output directory."
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="output directory (overrides $MAKEFUN_OUTPUT_DIR)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="only verify the committed entry.png, write nothing",
    )
    args = parser.parse_args(argv)

    repo_dir = Path(__file__).resolve().parent
    source = repo_dir / "entry.png"
    if not source.is_file():
        raise fail(f"committed entry.png not found next to main.py: {source}")

    try:
        data = source.read_bytes()
    except OSError as exc:
        raise fail(f"cannot read {source}: {exc}") from exc

    try:
        digest = check_image(data, "entry.png")
    except ValueError as exc:
        raise fail(str(exc)) from exc

    if args.verify_only:
        print(
            f"entry.png OK: {len(data)} bytes, "
            f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}, sha256={digest}"
        )
        return 0

    try:
        out_dir = resolve_output_dir(args.out_dir)
    except ValueError as exc:
        raise fail(str(exc)) from exc

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise fail(f"cannot create output directory {out_dir}: {exc}") from exc

    destination = out_dir / "entry.png"
    try:
        shutil.copyfile(source, destination)
    except OSError as exc:
        raise fail(f"cannot copy entry.png to {destination}: {exc}") from exc

    # Verify the bytes actually written, not just the source: first the size,
    # then the full content hash, so a truncated copy is caught even before
    # the digest comparison runs.
    try:
        written = destination.read_bytes()
    except OSError as exc:
        raise fail(f"cannot read back {destination}: {exc}") from exc

    if len(written) != len(data):
        raise fail(
            f"output entry.png is {len(written)} bytes, expected {len(data)} "
            f"bytes — the copy looks truncated"
        )

    try:
        written_digest = check_image(written, "output entry.png")
    except ValueError as exc:
        raise fail(str(exc)) from exc

    if written_digest != digest:
        raise fail("output entry.png digest differs from the committed image")

    print(f"wrote {destination}: {len(written)} bytes, sha256={written_digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
