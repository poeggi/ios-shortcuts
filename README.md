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
| [PDF Export](shortcuts/pdf-export/) | Share sheet: text, images, a web page or a file becomes a PDF, then Preview, Save to Files or Share | [Install](https://www.icloud.com/shortcuts/c74fd0e9d5ca44779cc5d71ec335db47) |
| [Audio Extract](shortcuts/audio-extract/) | Share sheet: pulls the audio track out of a video as an M4A, shown in Quick Look | [Install](https://www.icloud.com/shortcuts/586d84359bc64766ab39687fe10f53ba) |

## Install links, plus an archived copy

Every shortcut here is built by hand in the Shortcuts app and shared as an
iCloud link. That link is what the Install buttons point at.

One folder per shortcut, `shortcuts/<slug>/`, each holding:

- `README.md` - what it is for and how it was built, written by hand.
- `sequence.md` - what the published version actually does, action by action,
  with every variable reference resolved. Generated, never hand-edited.
- `<slug>.plist` - the shortcut as a readable XML property list. This is what
  makes a shortcut diffable. It is not installable.
- `<slug>.shortcut` - the signed file Apple's servers produced. This one does
  install, but it is an opaque binary and its signing certificate expires.

The last three are produced by `tools/fetch-shortcut.py`, which reads
`shortcuts.json`, downloads each published shortcut from
`icloud.com/shortcuts/api/records/<id>` and writes the folder. The endpoint is
public and needs no authentication.

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

Re-sharing an edited shortcut always mints a **new** link, so an edit means
repeating steps 2 to 5.

## Note on iCloud links

An iCloud link is a snapshot. Change the shortcut and you have to re-share and
replace the link, or it keeps serving the old version. Deleting the shortcut
from your library eventually breaks the link.
