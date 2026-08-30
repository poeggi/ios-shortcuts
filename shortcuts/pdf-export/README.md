# PDF Export

Share sheet action. Turns what you shared into a PDF.

It takes selected text, one or several images, a Safari page, or a file.
Several images become one multi-page PDF. Then it offers to:

- **Preview** - Quick Look. You can still share or save from there.
- **Save to Files** - asks for a file name, then the normal save dialog.
- **Share** - hands the PDF straight to the share sheet.

It names the PDF after what you shared. A web page by its title. A file by
its filename. Plain text by its own first line, since text has no filename.

## Install

See the install link on https://poeggi.github.io/ios-shortcuts/

## How it is built

1. Shortcuts > **+** > tap the name at the top > **Rename** > `PDF Export`.
2. **Get First Item** from **Shortcut Input**.
3. **Get name of** that item, **Get Web Page Title** on.
4. **Replace Text** in **Name**, **Regular Expression** on. Find `\n[\s\S]*`,
   replace with nothing. That keeps the first line only. Shared text needs it,
   because its "name" is the whole body.
5. **Make PDF** from **Shortcut Input**.
6. **Set Name** of the PDF to **Updated Text**, **Don't Include File
   Extension** on.
7. **Choose from Menu**, three items: `Preview`, `Save to Files`, `Share`.
8. Preview branch: **Quick Look**, input the Set Name output.
9. Save to Files branch: **Ask for Input**, prompt `File Name`, default answer
   the Replace Text output. Then **Set Name** of the PDF to that answer. Then
   **Save File** on the renamed item, **Ask Where to Save** on.
10. Share branch: **Share**, input the Set Name output.
11. Details (i) > **Show in Share Sheet** on. Share Sheet Types: Text, Rich
    Text, Images, Files, PDFs, Safari web pages, Articles, Maps links,
    Locations, Contacts, Dates.

Three things to watch while building it:

- New actions land at the bottom, not in the branch you tapped. Drag them in.
- An unbound input inside a branch does not fall back to the previous action.
  Point both Quick Look and Save File at Set Name explicitly.
- "Make sure to pass items to the Make PDF action" is a static editor warning.
  Shortcuts cannot know at edit time that the share sheet will supply input.

## Archived copy

- `sequence.md` - what the published version actually does, action by action.
  Read this before editing anything.
- `sequence.json` - the same list as data. The website renders it.
- `pdf-export.plist` - the published shortcut as readable XML.
- `pdf-export.shortcut` - Apple's signed, installable version.
- `pdf-export.png` - the icon, also used for link previews.
- `index.html` - this shortcut's page on the website. Generated.

All of them come from `tools/fetch-shortcut.py`, which pulls them back down
from the iCloud record behind the install link.
