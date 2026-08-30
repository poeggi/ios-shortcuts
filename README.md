# poegg's iOS Shortcuts

Collection of iOS Shortcuts, with one-tap install links.

**https://poeggi.github.io/ios-shortcuts/**

Open that page on the iPhone and tap Install. Each Install button is an
`icloud.com/shortcuts/...` link, which is the only thing iOS accepts as a
web install.

## The shortcuts

| Shortcut | What it does | Install |
|---|---|---|
| [Export as PDF](shortcuts/export-as-pdf/) | Share sheet: text, images, a web page or a file becomes a PDF, then Preview or Save to Files | not published yet |

## Why there are no downloadable .shortcut files here

Since iOS 15 a `.shortcut` file must be signed with an Apple Encrypted Archive
before iOS will import it. Signing needs macOS (`shortcuts sign`); it cannot be
done on-device, and Settings > Shortcuts > Allow Untrusted Shortcuts does not
lift the requirement. Tapping an unsigned file or passing its URL to
`shortcuts://import-shortcut` fails with "the shortcut URL provided was invalid".

So the install links point at iCloud, and the `.shortcut` files kept in this
repo are **source only**: readable XML plists, useful for diffing and review,
not installable.

## Adding a shortcut

1. Build or edit it in the Shortcuts app on the iPhone.
2. Shortcut details (the ... menu) > Share > **Copy iCloud Link**.
3. Add an entry to `shortcuts.json` with that link in `icloud`.
4. Optionally drop the exported `.shortcut` file under `shortcuts/<slug>/` as source.

The website is generated from `shortcuts.json`, so step 3 is all that is
strictly needed.

## Note on iCloud links

An iCloud link is a snapshot. If you change the shortcut, re-share it and
replace the link - the old one keeps serving the old version. Deleting the
shortcut from your library eventually breaks the link.
