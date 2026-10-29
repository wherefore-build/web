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
| `brand/tokens.json` | **the brand**: every colour, typeface and radius, once, each with its role and reason | authored |
| `brand/fonts/` | the three typefaces and their licences (SIL OFL 1.1), unchanged | authored |
| `gen/brand.py` | the brand pack's generator: the stylesheet, the fonts and the brand page | authored |
| `gen/site.py` | the site's generator: layout, filled from the facts and the pinned engine | authored |
| `gen/page.css` | the site's layout; every colour and face in it is a `var(--…)` from the brand | authored |
| `gen/kit.py` | what the generators share: the two sources, the draft banner, contrast | authored |
| `site/index.html` | the page | generated |
| `site/_headers` | what Cloudflare Pages serves with every file | generated |
| `site/brand.css`, `site/fonts/` | the brand as custom properties, and the fonts it serves itself | generated |
| `site/brand/` | the brand pack a person reads: every token, every contrast, the type, the licences | generated |
| `checks/self_contained.py` | the site loads nothing from elsewhere, and every link on it goes somewhere | authored |
| `checks/one_palette.py` | no colour or typeface is said anywhere but the brand | authored |
| `checks/contrast.py` | every text colour reaches 4.5:1 on every ground it is set on | authored |
| `checks/controls_press.py` | every control on the site does something a visitor sees, pressed cold on a phone | authored |
| `checks/*_proof.py` | each check, and the gate, shown to fail | authored |
| `wherefore.json` | what this repository is to the engine | authored |
| `requirements-engine.txt` | the engine release this is built and judged by | authored |
| `requirements-browser.txt` | the browser library the press check drives | authored |
| `wrangler.jsonc` | the hosting: Cloudflare serves `site/` as committed | authored |

Never edit `site/` by hand. The gate fails a page that is not what its sources
make.

## The brand

`brand/tokens.json` holds every colour, typeface and radius, with what each is
for and why it is what it is. `gen/brand.py` writes them into `site/brand.css`
as custom properties, copies the fonts the site serves itself, and builds the
brand pack at `site/brand/`.
- **Nothing else says a colour or a face.** `checks/one_palette.py` fails a
  `#hex`, an `rgb()` or a typeface written into a stylesheet or a generator.
  Change the accent in one place and every page follows when it is rebuilt.
- **Every text colour stays readable.** `checks/contrast.py` computes each pair
  `contrast.pairs` lists and fails one under its minimum. The brand page prints
  the same numbers.
- **It is a draft.** The look was a first attempt kept as a starting point
  (`origin` in the tokens), and it changes by editing the tokens.

## The page

It leads with the pain, then shows the cure working.
- **The picture.** Three panels under the headline, drawn by the generator:
  your code branches, is tested and merges back; everything else forks and
  never comes back; with Wherefore, everything else has code's shape - one
  source, built into every asset, through the gate. Its assets are the demo's
  own, and the commands it names are checked against the engine.
- **Sound familiar?** Three pains in the words of the teams who have them -
  no shared picture of what is current, features that ship and never reach the
  site or the docs, six copies and no telling which is true - and what
  Wherefore does about them.
- **The demo.** One fact (a made-up company's seats on its Pro plan) and the
  seven assets that state it. Three steps: today, the change, and the fix for
  the one asset written by hand. The page says it is an illustration, and names
  the real commands behind it.
- **Why "Wherefore".** The word means *why*. Beside it, five tabs ask an asset
  of the same made-up company "Wherefore art thou?" and show what it was built
  from, and why.
- **How it works**, in three steps.
- **The case study**: Chaotic Pendulums, the founder's own hardware company and
  the first to run on Wherefore - what it compiles, what holds it, and a link
  to the live site. Its counts are stated with the release they were counted at.
- **The rule, and the pilot**, with what is available, next and later.

**How this page is built.** A switch at the bottom of the screen (and a
second label for it beside the questions) shows, above every part of the
page, the facts it was built from and the checks that hold it, with a key at
the top. It is not a description typed beside the page: `gen/site.py` renders
each part through a view of the facts that records every fact it reads and
every command it asks the engine for, and that record is what the part shows.

Every line is in `facts/company.json`. A number appears in the facts once: a
line that mentions it names it as `{before}`, `{after}`, `{total}` and the
rest, and the generator fills it in. An unknown name stops the build.

**No script runs on the site.** The switch, the demo's steps and the tabs are
checkboxes, radio buttons and their labels, and `gen/page.css` shows what the checked one
selects. `checks/controls_press.py` loads every page in a real browser at 390
by 844 with touch, presses each control on a fresh load, and fails one that
cannot be pressed, is smaller than 44 by 44, presses nothing, or shows nothing
new on the screen.

## What comes from the engine, not from here

The page states the product's **version** and names some of its **commands**.
None of them is typed here. `gen/site.py` reads them from the installed engine,
the release `requirements-engine.txt` pins, and refuses to name a command that
release does not have. So:

- a release that renames a command fails the build until the facts follow it;
- a new version reaches the site by moving the pin, in a pull request whose
  gate fails until the site is regenerated against it.

The site can never describe an engine it does not pin.

## Changing the site

```
python3 -m venv .venv && . .venv/bin/activate
pip install --force-reinstall --no-deps -r requirements-engine.txt

wherefore build                      # regenerate site/ from the facts
wherefore gate                       # every file classified, every generated one current
wherefore check reach                # every fact reaches what a visitor receives
python3 checks/self_contained.py     # nothing loaded from elsewhere, no dead links
python3 checks/controls_press.py     # every control works under a thumb (needs the browser)
wherefore prove                      # each of those fails when it should
```

The press check and its proof need Playwright and its Chromium:
`pip install -r requirements-browser.txt && python3 -m playwright install chromium`.

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
address to write to and says the pilot is not open. With no `pilot.terms`, it
states none, and with no `case.quote` the case study quotes no one. Each appears when its fact is filled in.

## CI

`.github/workflows/corpus.yml` runs on every push, on a hosted runner, in about
two minutes, most of it installing the browser the press check drives. The engine's repository is private, so CI reads it with a token.

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
