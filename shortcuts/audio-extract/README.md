# Audio Extract

Share sheet action. Hands back just the audio track of a video, as an M4A.

The file opens in Quick Look. From there you can share it or save it to Files.
Nothing is re-recorded or re-timed. The video's audio is encoded straight to
M4A, with metadata stripped.

## Install

See the install link on https://poeggi.github.io/ios-shortcuts/

## How it is built

1. Shortcuts > **+** > tap the name at the top > **Rename** > `Audio Extract`.
2. **Encode Media**, input **Shortcut Input**, **Audio Only** on,
   Format **M4A**, Metadata off.
3. **Quick Look**, input the Encode Media output.
4. Details (i) > **Show in Share Sheet** on. Share Sheet Types: Media, Images,
   Apps.

Two actions, no menu. Everything else happens in the Quick Look share sheet.

## Archived copy

- `sequence.md` - what the published version actually does, action by action.
  Read this before editing anything.
- `sequence.json` - the same list as data. The website renders it.
- `audio-extract.plist` - the published shortcut as readable XML.
- `audio-extract.shortcut` - Apple's signed, installable version.
- `audio-extract.png` - the icon, also used for link previews.
- `index.html` - this shortcut's page on the website. Generated.

All of them come from `tools/fetch-shortcut.py`, which pulls them back down
from the iCloud record behind the install link.
