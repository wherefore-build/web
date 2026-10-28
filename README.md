# wherefore-co

The company that makes Wherefore, as a corpus that compiles. Its first asset is
the site, and every asset after it goes through the same process: it is
generated from facts said once, and judged on every push by the engine release
it pins.

The engine and its own documents live in `zakholdsworth/wherefore`. This
repository holds what the company says and shows, and moves at the company's
pace: an engine release reaches the site only when this repository moves its
pin. The reasons are in the engine's `DIRECTIONS.md`, §13 and §14.

## Where everything is

| path | what | kind |
|---|---|---|
| `facts/company.json` | **the source**: every fact the company states about itself, once | authored |
| `gen/site.py` | the site's generator: layout, filled from the facts and the pinned engine | authored |
| `gen/page.css` | the site's design, inlined into every page | authored |
| `site/index.html` | the page | generated |
| `site/_headers` | what Cloudflare Pages serves with every file | generated |
| `checks/self_contained.py` | the site loads nothing from elsewhere, and every link on it goes somewhere | authored |
| `checks/*_proof.py` | each check, and the gate, shown to fail | authored |
| `wherefore.json` | what this repository is to the engine | authored |
| `requirements-engine.txt` | the engine release this is built and judged by | authored |
| `wrangler.jsonc` | the hosting: Cloudflare serves `site/` as committed | authored |

Never edit `site/` by hand. The gate fails a page that is not what its sources
make.

## What comes from the engine, not from here

The page states the product's **principles**, its **commands** and its
**version**. None of them is typed here. `gen/site.py` reads them from the
installed engine, the release `requirements-engine.txt` pins. So:

- a release that rewords a principle or renames a command reaches the site by
  moving the pin, in a pull request;
- that pull request's gate fails until the site is regenerated against the new
  release.

The site can never describe an engine it does not pin.

## Changing the site

```
python3 -m venv .venv && . .venv/bin/activate
pip install --force-reinstall --no-deps -r requirements-engine.txt

wherefore build                      # regenerate site/ from the facts
wherefore gate                       # every file classified, every generated one current
wherefore check reach                # every fact reaches what a visitor receives
python3 checks/self_contained.py     # nothing loaded from elsewhere, no dead links
wherefore prove                      # each of those fails when it should
```

Change a fact in `facts/company.json`, run `wherefore build`, and commit the
fact and the regenerated `site/` together. `--force-reinstall` matters
whenever the pin moves, because pip leaves an installed package of the same
version where it is.

## Draft and launch

`site.status` in the facts is `draft` or `launched`, and the generator refuses
anything else.

- **While it is a draft,** the page carries a banner saying nothing is
  launched, and asks search engines not to index it, both in the page and in
  `site/_headers`.
- **Launching** is changing that one word, and only the owner decides it. The
  gate holds the page and its headers to the word.

A `null` in the facts is a fact not decided yet. With no `company.domain`, the
page names no canonical address. With no `company.contact`, it offers no
address to write to. Each appears when its fact is filled in.

## CI

`.github/workflows/corpus.yml` runs on every push, on a hosted runner, in about
a minute. The engine's repository is private, so CI reads it with a token.

**One-time setup (owner).** Create a fine-grained token, *Contents: read* on
`zakholdsworth/wherefore` only:
- GitHub → Settings → Developer settings → Fine-grained tokens → Generate new token
- Repository access: Only select repositories, `wherefore`
- Permissions: Contents, Read-only

Then save it in this repository: Settings → Secrets and variables → Actions → New repository
secret, named `WHEREFORE_READ_TOKEN`. Until the secret exists, CI fails at its
first step and says that this is the reason.

## Hosting

Cloudflare Workers serves `site/` exactly as committed, as static assets
(`wrangler.jsonc`), with the headers in `site/_headers`.

**CI deploys it, and only after every check has passed.** The `deploy` job in
`.github/workflows/corpus.yml` needs `corpus`, so a tree the gate or a proof
failed never reaches Cloudflare, and nothing builds on Cloudflare's side.
- `main` deploys to the site's address.
- Every other branch deploys to a preview of its own. The job posts the
  preview's address on the branch's pull request, with the commit it was
  built from, and updates that one comment on every push.

**One-time setup (owner):**
- A Cloudflare API token made from the **Edit Cloudflare Workers** template
  (Zone Resources: All zones), saved here as the secret `CLOUDFLARE_API_TOKEN`.
  Without it the deploy fails at its first step and says so.
- Cloudflare's own Git builds for the `wherefore` Worker disconnected (Worker
  → Settings → Build), so that this is the only deploy.
- Nothing in the dashboard. `workers.dev` and Preview URLs are declared in
  `wrangler.jsonc`: `main`'s deploy applies them, and before every preview CI
  applies them itself (`.github/scripts/cloudflare_urls.py`). They need the
  account to have a `workers.dev` subdomain; if it has none, the deploy says
  so.

Previews open for anyone who has the address. The page asks not to be indexed
while it is a draft.
