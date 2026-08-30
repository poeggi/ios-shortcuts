# Audio Extract

Share sheet action. Takes a video and hands back just its audio track as an
M4A, opened in Quick Look. From there you can share it or save it to Files.

Nothing is re-recorded or re-timed: the video's audio is encoded straight to
M4A, metadata stripped.

## Install

See the install link on https://poeggi.github.io/ios-shortcuts/

## How it is built

1. Shortcuts > **+** > tap the name at the top > **Rename** > `Audio Extract`.
2. **Encode Media**, input **Shortcut Input**, **Audio Only** on,
   Format **M4A**, Metadata off.
3. **Quick Look**, input the Encode Media output.
4. Details (i) > **Show in Share Sheet** on > Share Sheet Types: Media, Images,
   Apps.

Two actions, no menu. Everything else happens in the Quick Look share sheet.

## Archived copy

- `sequence.md` - what the published version actually does, action by action,
  generated from the plist. Read this before editing anything.
- `audio-extract.plist` - the published shortcut as readable XML.
- `audio-extract.shortcut` - Apple's signed, installable version.

All three come from `tools/fetch-shortcut.py`, which pulls them back down from
the iCloud record behind the install link.
