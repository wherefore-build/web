#!/usr/bin/env python3
"""The address wrangler deployed to, from the record it writes.

wrangler appends one JSON object per command to WRANGLER_OUTPUT_FILE_PATH:
`wrangler deploy` a "deploy" entry whose targets are the addresses, `wrangler
preview` a "preview" entry whose preview_urls are. This prints the first. A
deploy that went up with no address - preview URLs switched off for the
Worker, which is what the first preview did - fails here in those words,
because a preview nobody can open has not been delivered.

Usage:  python3 .github/scripts/deployed.py RECORD
"""
import json
import sys


def addresses(lines):
    found = []
    for line in lines:
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry.get("type") == "deploy":
            found += entry.get("targets") or []
        elif entry.get("type") == "preview":
            found += entry.get("preview_urls") or []
    return found


def main(path):
    with open(path, encoding="utf-8") as f:
        found = addresses(f)
    if not found:
        print("::error::Cloudflare took the deploy and gave it no address. Preview URLs (or "
              "workers.dev) are off for the Worker: turn them on under the Worker's Settings -> "
              "Domains & Routes, or let main deploy wrangler.jsonc, which declares both.")
        return 1
    print(found[0])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
