# Working agreements

Read by every Claude Code session and every agent started in this repository.
They are the owner's standing instructions, carried over from
`chaotic-pendulums-co` when this repository was made. They are the owner's to
change.

## Everything is a draft until the owner says otherwise

**Do not set `site.status` to `launched`.** Do not cut a release or publish
anything as final, unless the owner has authorized *that* launch. Cut freely
inside a draft, then stop at the launch and ask.

The asymmetry is the reason. A launch is a promise: it removes the banner and
asks to be indexed, and a page that has been read cannot be unread. A draft
promises nothing, and abandoning one costs nothing.

## Never merge without being asked

**Do not merge a pull request unless the owner has said to merge that PR.**
Green CI is not permission. The owner tests previews on a phone, and on the
first client that testing has found what every check passed.

When CI passes: say so, give the **current** preview address (a stale one
looks identical to a fresh one), and stop.

## The facts are the source

Never edit `site/` by hand. Change `facts/company.json`, or the generator, and
regenerate. A fact about the product (a principle, a command, the version) is
the engine's, so change it in `zakholdsworth/wherefore` and move the pin here.
