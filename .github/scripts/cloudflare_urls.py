#!/usr/bin/env python3
"""Give the Worker the addresses wrangler.jsonc declares, before a preview.

`workers_dev` and `preview_urls` in wrangler.jsonc are applied by `wrangler
deploy` - which only main runs - and not by `wrangler preview`. So until main
has deployed, and whenever the dashboard and the file disagree, a preview goes
up with no address: "This Preview deployment has no active URLs", which is what
the first one did. This sets both on the Worker from the file, through the same
Workers API that `wrangler preview` uses to create it, so the file is the one
place they are said.

Both need the account to have a workers.dev subdomain, chosen once; this fails
in those words if it has none, and otherwise prints where the previews live.

Usage:  CLOUDFLARE_API_TOKEN=... python3 .github/scripts/cloudflare_urls.py
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
API = "https://api.cloudflare.com/client/v4"


def config():
    """wrangler.jsonc, whose comments are whole lines."""
    text = (ROOT / "wrangler.jsonc").read_text(encoding="utf-8")
    return json.loads("\n".join(l for l in text.splitlines() if not l.strip().startswith("//")))


def call(method, path, body=None, content_type="application/json"):
    req = urllib.request.Request(API + path, method=method,
                                 data=None if body is None else json.dumps(body).encode())
    req.add_header("Authorization", "Bearer " + os.environ["CLOUDFLARE_API_TOKEN"])
    if body is not None:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return json.load(e)
        except ValueError:
            return {"success": False, "errors": [{"message": f"HTTP {e.code}"}]}


def said(reply):
    return "; ".join(f"{e.get('message')} ({e.get('code')})" for e in reply.get("errors") or []) \
        or "no reason given"


def main():
    cfg = config()
    account, name = cfg["account_id"], cfg["name"]
    want = {"enabled": bool(cfg.get("workers_dev")), "previews_enabled": bool(cfg.get("preview_urls"))}

    sub = call("GET", f"/accounts/{account}/workers/subdomain")
    if not sub.get("success") or not (sub.get("result") or {}).get("subdomain"):
        print(f"::error::The Cloudflare account has no workers.dev subdomain, so nothing deployed "
              f"there can have an address ({said(sub)}). Choose one once, in Cloudflare under "
              f"Workers & Pages, then re-run this job.")
        return 1
    host = f"{sub['result']['subdomain']}.workers.dev"

    done = call("PATCH", f"/accounts/{account}/workers/workers/{name}", {"subdomain": want},
                "application/merge-patch+json")
    if not done.get("success"):
        print(f"::error::Cloudflare refused to set {name}'s addresses to {want}: {said(done)}")
        return 1
    print(f"{name}: workers.dev {'on' if want['enabled'] else 'off'}, preview URLs "
          f"{'on' if want['previews_enabled'] else 'off'} - previews at <preview>-{name}.{host}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
