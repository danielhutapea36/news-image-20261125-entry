# World News — Tuesday 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/danielhutapea36/news-image-20261125-entry/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/danielhutapea36/news-image-20261125-entry/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

An entry for the [news-image-20261125](https://make.fun/bounty/news-image-20261125) bounty on make.fun: a single 1024×1024 news image summarising the day's world headlines, built to be read at a glance.

## The six stories

1. **China probes top official Chen Jining** — Reuters / Xinhua
2. **Shenzhou-24 lifts off with first Pakistani astronaut** — Reuters
3. **Russian strike kills two in Odesa region** — Reuters
4. **Trump set to unveil new tariffs on trading partners** — Reuters / BBC
5. **Australia signs Solomons security pact** — Reuters
6. **Also today:** US pauses joint military operations with Ecuador, Nvidia slides 6% as Huang's comeback is questioned, US consumer confidence at a near two-year high — Reuters / BBC

## The image

- File: `entry.png`
- Dimensions: 1024×1024
- Size: 136840 bytes
- SHA-256: `dbd0c81c26048387b371ebe867e7528eb95e52c0fb45eb49524a585c041cf094`

## How it works

The PNG was drawn during the build (Pillow, offline) and committed to this repository. The entry program itself (`main.py`) is standard-library-only: it simply copies the committed `entry.png` to the output directory — the pattern the competition's own starter uses ("the simplest program copies an image the repository holds").

This matters because the grader runs the program in an environment where "standard library only: nothing is installed before it runs". A program that imports Pillow would fail there with `ModuleNotFoundError` even though it works locally. This entry program imports only `argparse`, `hashlib`, `os`, `struct`, `sys`, `pathlib`, and `shutil`, makes no network calls, and is fully deterministic: the same committed bytes are copied every run.

Before writing, the program verifies the image: PNG magic bytes, 1024×1024 dimensions, and size at most 1 MiB. After copying, it reads the output back and checks the size and SHA-256 digest match the committed image.

## Run it

```bash
MAKEFUN_OUTPUT_DIR=/tmp/ni25-out python3 main.py
```

Or check the committed image without writing anything:

```bash
python3 main.py --verify-only
```

`--out-dir` overrides `$MAKEFUN_OUTPUT_DIR`; if neither is set, the program writes to `/output`. An explicitly set but empty `$MAKEFUN_OUTPUT_DIR` is an error.

## Verification

A successful run exits 0 and prints the output path, byte count, and digest, for example:

```
wrote /tmp/ni25-out/entry.png: 136840 bytes, sha256=dbd0c81c26048387b371ebe867e7528eb95e52c0fb45eb49524a585c041cf094
```

`--verify-only` exits 0 and prints the same size and digest for the committed image. Re-running into a fresh directory produces byte-identical output.

## About make.fun

Built for the make.fun bounty platform — [make.fun](https://make.fun/?ref=danielhutapea36&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125).
