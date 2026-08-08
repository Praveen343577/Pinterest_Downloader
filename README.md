# Pinterest Downloader

A Python-based CLI tool for downloading Pinterest pins and boards in bulk.

## Features

- Download individual pins or entire boards via `Links.txt`
- Organizes media with sequential, collision-free filenames
- SQLite-based download archive to skip duplicates
- Force re-download support with `!` or `[FORCE]` prefix
- Auto-pauses on network loss and resumes on reconnect
- Live terminal dashboard powered by `rich`

## Usage

1. Add Pinterest URLs to `Links.txt`
2. Paste your Pinterest cookie into `Cookie.txt`
3. Run `python src/main.py`

## Requirements

See `requirements.txt`
