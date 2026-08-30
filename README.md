# poeggi's iOS Shortcuts

Collection of iOS Shortcuts, with one-tap install links.

**https://poeggi.github.io/ios-shortcuts/**

Open that page on the iPhone and tap Install. Every Install button is an
`icloud.com/shortcuts/...` link.

## The shortcuts

| Shortcut | What it does | Install |
|---|---|---|
| [Export as PDF](shortcuts/export-as-pdf/) | Share sheet: text, images, a web page or a file becomes a PDF, then Preview or Save to Files | not published yet |

## Links only, never files

Every shortcut here is built by hand in the Shortcuts app and shared as an
iCloud link. This repo holds those links and a note on what each shortcut
does. It holds no `.shortcut` files, on purpose:

- Since iOS 15 an unsigned `.shortcut` file cannot be imported at all. Signing
  needs macOS, or Apple's own Share > File > Anyone flow. Settings > Shortcuts
  > Allow Untrusted Shortcuts does not lift that.
- A signed export is an opaque binary. It installs, but it cannot be read or
  diffed, so version control adds nothing over the iCloud link.
- There is no round trip. The Shortcuts app is the only editor, so a file in a
  repo could never be edited and republished anyway.

## Adding a shortcut

1. Build or edit it in the Shortcuts app.
2. Long-press it > Share > **iCloud Link** > Copy.
3. Add an entry to `shortcuts.json` with that link in `icloud`.

The website renders `shortcuts.json`, so step 3 is the whole job.

## Note on iCloud links

An iCloud link is a snapshot. Change the shortcut and you have to re-share and
replace the link, or it keeps serving the old version. Deleting the shortcut
from your library eventually breaks the link.
