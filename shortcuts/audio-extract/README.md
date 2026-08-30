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

`audio-extract.plist` is the published shortcut as readable XML, and
`audio-extract.shortcut` is Apple's signed, installable version. Both were
pulled from the iCloud record behind the install link. See the top-level
README.
