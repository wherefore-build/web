#!/usr/bin/env python3
"""The address wrangler deployed to, from the record it writes.

wrangler appends one JSON object per command to WRANGLER_OUTPUT_FILE_PATH:
`wrangler deploy` a "deploy" entry whose targets are the addresses, `wrangler
preview` a "preview" entry whose preview_urls are. This takes the first, gives
it to the job as the step output `url` and to the run's summary, and prints it.
A deploy that went up with no address fails here in those words, because a
preview nobody can open has not been delivered.

Usage:  python3 .github/scripts/deployed.py RECORD
"""
import json
import os
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


def append(var, text):
    if os.environ.get(var):
        with open(os.environ[var], "a", encoding="utf-8") as f:
            f.write(text + "\n")


def main(path):
    with open(path, encoding="utf-8") as f:
        found = addresses(f)
    if not found:
        print("::error::Cloudflare took the deploy and gave it no address: workers.dev or Preview "
              "URLs are off for the Worker. .github/scripts/cloudflare_urls.py sets both from "
              "wrangler.jsonc, and runs before every preview.")
        return 1
    url = found[0] if "://" in found[0] else "https://" + found[0]
    append("GITHUB_OUTPUT", f"url={url}")
    append("GITHUB_STEP_SUMMARY", f"**{os.environ.get('GITHUB_REF_NAME', '')}** is at {url}, built "
                                  f"from `{os.environ.get('GITHUB_SHA', '')[:7]}`.")
    print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
