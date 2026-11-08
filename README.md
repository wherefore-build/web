# web

The company that makes Wherefore, as a corpus that compiles. Its first asset is
the site, and every asset after it goes through the same process: it is
generated from facts said once, and judged on every push by the engine release
it pins.

The engine lives in `wherefore-build/wherefore` and is published on PyPI as
`wherefore-build`. This repository holds what the company says and shows, and
moves at the company's pace: an engine release reaches the site only when this
repository moves its pin (`requirements-engine.txt`). The company's
decisions - why the site and the product are as they are - are kept in its
private repository, not here, so that none of them goes public with the site.

## Where everything is

| path | what | kind |
|---|---|---|
| `facts/company.json` | **the source**: every fact the company states about itself, once | authored |
| `brand/tokens.json` | **the brand**: every colour, typeface and radius, once, each with its role and reason | authored |
| `facts/pendulum.json` | the case study's counts: a dated snapshot of the pendulum's own repository, which is private, counted once at the commit it names | captured, stamped inside |
| `facts/roadmap.json` | the engine's roadmap, byte for byte the `roadmap.json` beside its code; What's next is built from it, and `wherefore check upstream` fails the deploy when the engine's file has moved | captured |
| `cases/pendulum/model.html` | the pendulum's interactive 3D model, the file https://chaoticpendulums.com/ embeds, copied byte for byte from the pendulum's repository at the commit `case.model.taken` names | captured |
| `cases/pendulum/plate.html` | the pendulum's mounting plate alone: its public model opened on one part, the same bytes after one line, copied byte for byte at the commit `case.part.taken` names | captured |
| `brand/fonts/` | the three typefaces and their licences (SIL OFL 1.1), unchanged | authored |
| `brand/icon/icon-1024.png`, `brand/shoot_icon.py` | the icon as a PNG, for accounts that take only PNG, and the script that shoots it from `site/brand/icon.svg` | captured, stamped |
| `gen/brand.py` | the brand pack's generator: the stylesheet, the fonts and the brand page | authored |
| `gen/site.py` | the site's generator: layout, filled from the facts and the pinned engine | authored |
| `gen/page.css` | the site's layout; every colour and face in it is a `var(--…)` from the brand | authored |
| `gen/kit.py` | what the generators share: the sources, the draft banner, contrast | authored |
| `site/index.html` | the home page | generated |
| `site/features/`, `site/changelog/` | everything it does and what's next, and every release | generated |
| `site/map/` | the site's own map, written by `wherefore graph` run as a generator: every source, the scripts that read it, and every file they make, from a real run, in the brand's own colours (`--theme site/brand/map.css`) | generated |
| `gen/motion.py` | a clip for every feature the pinned release ships, compiled from the engine's features, releases and docs, the roadmap's ledger and this company's own words: the version, who asked, the command run and what it printed, what the feature does in this site's own numbers, the claim, the address - as a page in motion in the brand's own stylesheet | authored |
| `site/motion/`, `motion/` | the clips, one page per feature, played on each card of the features page and the changelog; the storyboards, as data for the checks, sit in `motion/`, out of `site/`, because a storyboard quotes what a command printed | generated |
| `gen/motion_render.py` | the camera: each clip stepped frame by frame into portrait and landscape video, on request (`.github/workflows/clips.yml`), never committed | authored |
| `site/_headers` | what Cloudflare Pages serves with every file | generated |
| `site/install.sh` | the one-line installer `wherefore.sh` serves, from the pinned release (`gen/install.py`) | generated |
| `site/brand.css`, `site/fonts/` | the brand as custom properties, and the fonts it serves itself | generated |
| `site/brand/` | the brand pack a person reads: every token, every contrast, the type, the icon, the licences | generated |
| `checks/self_contained.py` | the site loads nothing from elsewhere, and every link on it goes somewhere | authored |
| `checks/one_palette.py` | no colour or typeface is said anywhere but the brand, and no page a visitor receives carries a colour that is not the brand's, unless it is named as another's with the reason | authored |
| `checks/contrast.py` | every text colour reaches 4.5:1 on every ground it is set on | authored |
| `checks/brand_reasons.py` | every colour, typeface and radius says what it is for and why, so does the icon, and the brand says its idea | authored |
| `checks/install_line.py` | no install line on the site names the bare `wherefore` - another project's package; ours is `wherefore-build` | authored |
| `checks/install_script.py` | the installer installs the pinned release with uv, pipx or pip, and refuses an old Python and an empty machine in words | authored |
| `checks/controls_press.py` | every control on the site does something a visitor sees, pressed cold on a phone | authored |
| `checks/case_study.py` | the snapshot says where and when it was counted, and each count on the page moves the page | authored |
| `checks/questions_turn.py` | the questions on "Why Wherefore" turn by themselves, stop on the chip a thumb taps, and hold still for a visitor who asks for less motion | authored |
| `checks/fits_phone.py` | every page fits a phone's width, moving or still and with "how this page is built" open, and no icon is bigger than the words it follows | authored |
| `checks/model_turns.py` | the pendulum's model stands beside the case study's heading and its plate beside the counts; each draws, and turns under a thumb; only their frames may run a script | authored |
| `checks/motion_for_every_feature.py` | every feature the pinned release ships has its clip, and the features page plays it | authored |
| `checks/motion_reads.py` | every clip runs 16 to 40 s, no scene outruns a reader, every command run is one the CLI has, every printed line is one the engine prints, and every word is on the page | authored |
| `checks/motion_fits.py` | every clip fits a portrait frame and a landscape one at the middle of every scene, and every scene shows its words | authored |
| `checks/*_proof.py` | each check, and the gate, shown to fail | authored |
| `wherefore.json` | what this repository is to the engine | authored |
| `requirements-engine.txt` | the engine release this is built and judged by | authored |
| `requirements-browser.txt` | the browser library the press check drives | authored |
| `wrangler.jsonc` | the hosting: Cloudflare serves `site/` as committed | authored |
| `.github/workflows/wherefore-pin.yml` | a release reaches the site by a pull request this repository opens itself: every few hours it asks PyPI for the newest engine, moves the pin, rebuilds, and opens a draft whose checks say what the site still has to describe. Written by `wherefore init`, ours since | authored |

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
  `contrast.pairs` lists and fails one under its minimum; the light scheme
  lists its own pairs, because on paper the accent is a fill under text, never
  text. The brand page prints the same numbers.
- **One brand, two grounds.** `light` in the tokens is the same brand on paper:
  every role keeps its name, the neutrals invert, the accent and the caution
  keep their values as a highlighter, and only fail is deepened to read as
  text. The map is drawn on it (`site/brand/map.css`); the app inherits it.
- **Every decision carries its reason.** Each colour, typeface and radius says
  what it is for and why, and `idea` says what the whole look follows.
  `checks/brand_reasons.py` fails a token without its reason. A colour that is
  another one in a different role (`on-accent` is the ground's black) says
  `same_as` instead of copying a value.
- **The icon is shot from the brand, and held to it.** `icon` in the tokens is
  the letter, its colours and its place. `gen/brand.py` writes
  `site/brand/icon.svg` with its face embedded, so it draws the same anywhere.
  The PNG that profiles need takes a browser to draw, so it is captured, not
  generated: when the icon or a colour it uses changes, the gate fails until it
  is shot again -
  `python3 brand/shoot_icon.py`, regenerate, then `wherefore gate --restamp icon`.

## The pages

**The home page** says why before what, then shows it working.
- **The headline and the install.** Your product compiles; your site, docs and
  decks drift. Under it, the one line that installs Wherefore, the pip line,
  that it is open source and under which licence, then Get started and the
  repository. Every command is in Get started.
- **The picture.** Your code branches, is tested and merges back; everything
  else forks and never comes back; with Wherefore, everything else gets code's
  shape.
- **The demo.** One fact (an example company renaming Workspaces to Projects)
  and the six assets that state it - the feature page, the demo video's
  captions, the deck, the docs, the app's button and a help article. Three
  steps: today, the rename, and the fix for the one asset written by hand. The
  page says it is an illustration, and names the real commands behind it.
- **How it works**, in three steps: scan, build, gate - and under it, what
  else it catches: three of the release's features in a line each, and the
  way to all of them.
- **The case study**: Chaotic Pendulums, the small hardware company the founder
  started to test the idea - its counts, with one of its parts beside them
  (`cases/pendulum/plate.html`, the mounting plate, machined and anodised,
  turning in a frame a visitor can take hold of), and what the spec makes and
  what it proves before anything is cut, behind one press.
- **The rule.** Agents already run your code's pipeline; Wherefore lets them
  run the rest.
- **Why Wherefore**: the word means *why*, and five tabs ask an asset of the
  example company "Wherefore art thou?" and show what it was built from, and
  why.
- **Getting started**: the install line and the release's own commands.

**Features** (`site/features/`) lists everything the pinned release does, each
with the release it arrived in, and **what's next** - the engine's own roadmap,
from the copy this site holds (`facts/roadmap.json`), each item marked next or
later. The site owns no roadmap: the engine's sits beside its code, and the copy
is held to it. The build stops if an item is one the pinned release already
ships: an item leaves the roadmap in the change that ships it.

**How this page is built.** A switch at the bottom of the screen shows, above
every part of the page, the facts it was built from and the checks that hold
it, with a key at the top. The key links the map (`site/map/`): the whole
chain, every source, the scripts that read it and every file they make, drawn
by the pinned engine from a real run of every generator - `wherefore graph`
is itself a generator of this site, which the gate runs like any command and
which `wherefore graph` credits rather than runs. It is not a description typed beside the page:
`gen/site.py` renders each part through a view of the facts that records every
fact it reads and every command it asks the engine for, and that record is what
the part shows.

Every line is in `facts/company.json`. A number appears in the facts once: a
line that mentions it names it as `{before}`, `{after}`, `{total}` and the
rest, and the generator fills it in. An unknown name stops the build.

**No script runs on the site's own pages.** The switch, the demo's steps and the tabs are
checkboxes, radio buttons and their labels, and `gen/page.css` shows what the checked one
selects; the case study's list opens as a `<details>`. `checks/controls_press.py` loads every page in a real browser at 390
by 844 with touch, presses each control on a fresh load, and fails one that
cannot be pressed, is smaller than 44 by 44, presses nothing, or shows nothing
new on the screen.

The one page that runs a script is the pendulum's own model, beside the case
study's heading. It is shown in a frame sandboxed to its script alone, which
cannot reach the page around it, and `site/_headers` gives its path a policy
of its own: its inline script, its own pictures and font, nothing loaded from
anywhere, framed only here. `checks/model_turns.py` serves the site with those
headers, and at 390 by 844 with touch and at 1280 by 900 requires the model to
be to the right of the heading, to draw on the ground the facts name, and to
turn when dragged.

## What comes from the engine, not from here

The page states the product's **version** and names some of its **commands**.
None of them is typed here. `gen/site.py` reads them from the installed engine,
the release `requirements-engine.txt` pins, and refuses to name a command that
release does not have. So:

- a release that renames a command fails the build until the facts follow it;
- a new version reaches the site by moving the pin, in a pull request whose
  gate fails until the site is regenerated against it.

The same holds for **what it does** and **every release**:

- **Everything it does** lists each feature in the pinned release's
  `features.json`, in our words (`does.words`). A feature with no words, or
  words for one the release no longer ships, stops the build.
- **The changelog** (`site/changelog/`) is built from the pinned release's
  `releases.json`: each release's version, date, title and sentence, a
  terminal card of what that release printed when it was run, and the
  features it brought, in our words. A release is on it the moment the pin
  moves to it, and the build stops if the engine names a feature in a release
  it does not list, or the newest release it lists is not the one pinned.

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
python3 checks/model_turns.py        # the pendulum's model turns under a thumb (needs the browser)
python3 checks/questions_turn.py     # the questions turn, and stop when one is picked (needs the browser)
python3 checks/fits_phone.py         # every page fits a phone, and no icon outgrows its words (needs the browser)
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
address to write to. With no `start.install`, it says Wherefore is not public
yet, and with no `case.quote` the case study quotes no one. Each appears when its fact is filled in.

## The case study

The case study's numbers - the pendulum's proofs, parts, print plates, and the
release they stand at - are not typed into the page. `facts/pendulum.json`
holds them as a dated snapshot, counted once from the pendulum's own
repository - private; its public face is https://chaoticpendulums.com/ - at
the commit and on the day it names.
- **Nothing reads the pendulum's repository.** The two repositories stay
  apart: the pendulum may be open-sourced or split out, and should carry
  nothing for this company, nor be readable from here. A case study is a dated
  story, so when it is retold a person counts again and rewrites the snapshot.
- **Each stat names its count** (`case.stats[].of` in the facts), and the as-of
  line fills `{version}` and `{on}` from the snapshot. A count the snapshot does
  not have stops the build.
- **`checks/case_study.py`** requires the snapshot to say where and when it was
  counted, requires every value in it to be on the page or excused with a
  reason, and moves each one on the page to see the page move. The release this
  pins sweeps only the facts for reach, so this does it for the snapshot.
- **The model beside the heading is a snapshot too:** the file the pendulum's
  home page embeds, copied into `cases/pendulum/model.html` at the commit
  `case.model.taken` names. `gen/site.py` writes it to `site/pendulum/` with a
  few lines that frame it - a view drawn back far enough that the whole swing
  stays in a small frame, then a swing, unless the visitor asks for less
  motion. It stands on the brand colour `case.model.ground` names.
- **The model and the counts are both watched.** The model's captured group names
  an `upstream`: the pendulum's public home page, which embeds the same file.
  `wherefore check upstream` reads it whenever the site is compiled - so
  before every deploy - and fails when the pendulum has moved,
  until the copy is taken again - re-copy the file, record the commit and day
  in `case.model.taken`, never the commit alone. The counts' group names
  the pendulum's `/release.json`, a mark that changes when a release is cut
  and says nothing else: when it no longer matches `captured.release`, count
  again - proofs, parts, plates, the release - and record the new mark with
  them.

## CI

`.github/workflows/corpus.yml` runs on every push, on a hosted runner, as two
jobs side by side: `corpus` runs every check, and `proofs` plants each check's
fault and requires the check to fail. The proofs are the long half, and they
run only when something that decides what a check does has moved - a check, a
generator, the brand's source, the workflow, `wherefore.json`; a push that only
moves the pin, the facts or the pages they make skips them, and the job says
so. The browser the press check drives is cached by the file that pins it. The
workflow installs the engine release `requirements-engine.txt` pins from PyPI,
so it needs no secret to read it; the one secret it holds is the deploy's,
`CLOUDFLARE_API_TOKEN` (below).

## Hosting

Cloudflare Workers serves `site/` exactly as committed, as static assets
(`wrangler.jsonc`), with the headers in `site/_headers`.

**CI deploys it, and only after its checks have passed.** Nothing builds on
Cloudflare's side; `.github/actions/deploy` is the one deploy, and
`.github/workflows/corpus.yml` decides when it runs.
- `main` deploys to the site's address, `wherefore.build`, a Custom Domain
  declared in `wrangler.jsonc` (and still at its `workers.dev` address). Its
  `deploy` job needs `corpus` and `proofs`, so a tree the gate, a check or a
  proof failed never reaches the site.
- Every other branch deploys to a preview of its own as soon as `corpus` has
  passed (its `preview` job), without waiting for the proofs, which judge the
  checks rather than the page. The job posts the preview's address on the
  branch's pull request, with the commit it was built from, and updates that
  one comment on every push.
- The checks on the page run in two jobs side by side, `checks` (the files)
  and `browser` (the site at a phone's size), and `corpus` is their verdict.
  The proofs run one job per proof (`proof`), each in its own checkout, and
  `proofs` is their verdict.

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
  so. The custom domain is declared there too, and `main`'s deploy attaches it.
  If that deploy fails on the domain for want of a permission, the token needs
  *Zone · DNS · Edit* on `wherefore.build` as well.
- The other addresses redirect, by one Redirect Rule in each zone (Rules →
  Redirect Rules):
  - `www.wherefore.build`: the "Redirect from WWW to root" template in the
    `wherefore.build` zone, every path to `https://wherefore.build` with the
    path and query kept, status 301.
  - `getwherefore.com`: the "Redirect from one domain to another" template,
    every path to `https://wherefore.build/` with the path kept, status 301 -
    it only ever redirects.
  - `wherefore.sh`: every request to `https://wherefore.build/install.sh`,
    status 302, so `curl -fsSL https://wherefore.sh | sh` runs the installer
    (curl's `-L` follows the redirect). A 302, not a 301: a browser keeps a 301
    for good, and the address may serve something else one day.

  Each zone needs a proxied DNS record for its rule to see a request: `AAAA @
  100::`, orange cloud on - and in the `wherefore.build` zone, `AAAA www 100::`,
  since `@` there is the Worker's own.

## The installer

`site/install.sh` is what `curl -fsSL https://wherefore.sh | sh` runs.
`gen/install.py` writes it from the release this site pins - the package's name
(`wherefore-build`), the command, the oldest Python, and the words for the two
commands it suggests next - so the installer moves with the pin. It installs
with uv if it is there, else pipx, else Python's own pip for this user (after
checking Python is new enough), and changes nothing else. `site/_headers`
serves it as plain text, so a browser shows it to read.
`checks/install_script.py` runs it under `sh` against stand-ins for uv, pipx and
Python, so each path is exercised with no network, and its proof plants the
wrong package, uv ignored, an old Python let through and a script `sh` cannot
parse. It installs nothing real until the release is on PyPI.

Previews open for anyone who has the address. The page asks not to be indexed
while it is a draft.
