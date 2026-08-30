# poeggi's iOS Shortcuts

Collection of iOS Shortcuts, with one-tap install links.

**https://poeggi.github.io/ios-shortcuts/**

Open that page on the iPhone and tap **Install**, which is an
`icloud.com/shortcuts/...` link and takes one tap.

Next to it, **Mirror** downloads the signed copy kept in this repo. Safari
files it away rather than opening it, so tap it once in Files to import it.
That path does not depend on Apple keeping the iCloud link alive.

## The shortcuts

| Shortcut | What it does | Install |
|---|---|---|
| [PDF Export](shortcuts/pdf-export/) | Share sheet: text, images, a web page or a file becomes a PDF, then Preview, Save to Files or Share | [Install](https://www.icloud.com/shortcuts/607b9640b279421eb17dc8d112db2ad5) |
| [Audio Extract](shortcuts/audio-extract/) | Share sheet: pulls the audio track out of a video as an M4A, shown in Quick Look | [Install](https://www.icloud.com/shortcuts/586d84359bc64766ab39687fe10f53ba) |

## Install links, plus an archived copy

Every shortcut here is built by hand in the Shortcuts app and shared as an
iCloud link. That link is what the Install buttons point at.

One folder per shortcut, `shortcuts/<slug>/`, each holding:

- `README.md` - what it is for and how it was built, written by hand.
- `sequence.md` - what the published version actually does, action by action,
  with every variable reference resolved. Generated, never hand-edited.
- `sequence.json` - the same action list as data, which is what the website
  renders. Generated.
- `<slug>.plist` - the shortcut as a readable XML property list. This is what
  makes a shortcut diffable. It is not installable.
- `<slug>.shortcut` - the signed file Apple's servers produced. This one does
  install, but it is an opaque binary and its signing certificate expires.
- `<slug>.png` - the icon iOS renders for the shortcut, 450x450. The website
  shows it, and a pasted link previews with it. The plist itself only stores a
  glyph number and a colour, so this rendered image comes from the iCloud
  record.
- `index.html` - the shortcut's own page at
  `poeggi.github.io/ios-shortcuts/shortcuts/<slug>/`. Generated: it is only
  link-preview metadata plus a call into the shared renderer.

Everything except the first is produced by `tools/fetch-shortcut.py`, which
reads `shortcuts.json`, downloads each published shortcut from
`icloud.com/shortcuts/api/records/<id>` and writes the folder. It also writes
`og.png`, the site's link preview image. The endpoint is public and needs no
authentication.

```
python tools/fetch-shortcut.py             # all entries
python tools/fetch-shortcut.py pdf-export  # one slug
python tools/fetch-shortcut.py --check     # verify only, write nothing
```

The Shortcuts app is still the only editor, so nothing here can be edited and
pushed back. `--check` answers the question that matters instead: does the
archive still match what the link publishes?

## Adding a shortcut

1. Build or edit it in the Shortcuts app.
2. Long-press it > Share > **iCloud Link** > Copy.
3. Add an entry to `shortcuts.json` with that link in `icloud`.
4. Run `python tools/fetch-shortcut.py <slug>` to write the archive folder.
5. Commit both.

The website renders `shortcuts.json`, so step 3 is what publishes it. Step 4 is
what makes the Mirror button work and what records the action sequence.

**Rule: every shortcut ships its icon.** `<slug>.png` is not optional. The
website shows it on the card and link previews use it, so an entry without one
looks broken. Step 4 fetches it automatically; never commit a shortcut folder
without it, and if the icon changes in the Shortcuts app, re-share and re-run
step 4 so the site matches.

**Rule: keep the prose short.** These notes get read on a phone. One idea per
sentence. Split a sentence rather than let it run to three lines.

**Rule: the look lives in `style.css` and `render.js`, nowhere else.** Neither
`index.html` at the root nor a generated `shortcuts/<slug>/index.html` carries
its own styling, and a generated page is never hand-edited. That is what keeps
every entry looking the same, including ones added later: change a token in
`style.css` once and every card and every action list follows.

Re-sharing an edited shortcut always mints a **new** link, so an edit means
repeating steps 2 to 5.

## Note on iCloud links

An iCloud link is a snapshot. Change the shortcut and you have to re-share and
replace the link, or it keeps serving the old version. Deleting the shortcut
from your library eventually breaks the link.
