# PDF Export

Share sheet action. Takes whatever you shared - selected text, one or several
images, a Safari page, a file - turns it into a PDF, then offers a choice:

- **Preview** - Quick Look, from which you can still share or save
- **Save to Files** - asks for a file name, then the normal document save
  dialog with "Ask Where to Save"
- **Share** - hands the PDF straight to the share sheet

Several selected images become one multi-page PDF.

It is meant to name the PDF after what you shared - a web page by its title, a
file by its filename, and plain text by its own first line, since text has no
filename of its own. That part is built but not yet working; see Known issues.

## Install

See the install link on https://poeggi.github.io/ios-shortcuts/

## How it is built

1. Shortcuts > **+** > tap the name at the top > **Rename** > `PDF Export`.
2. **Get First Item** from **Shortcut Input**.
3. **Get name of** that item, **Get Web Page Title** on.
4. **Replace Text** in **Name**, **Regular Expression** on, find `\n[\s\S]*`,
   replace with nothing. This keeps only the first line, which matters for
   shared text, where the "name" is the whole body.
5. **Make PDF** from **Shortcut Input**.
6. **Set Name** of the PDF to **Updated Text**, **Don't Include File
   Extension** on.
7. **Choose from Menu**, three items: `Preview`, `Save to Files`, `Share`.
8. Preview branch: **Quick Look**, input the Set Name output.
9. Save to Files branch: **Ask for Input**, prompt `File Name`, default answer
   the Replace Text output; **Set Name** of the PDF to that answer; then
   **Save File** on that renamed item, **Ask Where to Save** on.
10. Share branch: **Share**, input the Set Name output.
11. Details (i) > **Show in Share Sheet** on > Share Sheet Types: leave only
    Text, Rich Text, Images, URLs, Safari web pages, Files, PDFs. Not done yet
    - all 18 types are still enabled, including contacts, phone numbers, dates
    and Maps links.

Three things to watch while building it:

- New actions land at the bottom of the shortcut rather than in the branch you
  tapped, so the branch actions usually need a drag into the right menu item.
- Inside a menu branch an unbound input does not fall back to the previous
  action. Both Quick Look and Save File must be pointed at Set Name explicitly.
- "Make sure to pass items to the Make PDF action" is a static editor warning.
  Shortcuts cannot prove at edit time that the share sheet will supply input.

## Known issues

The steps above are the intended build. `sequence.md` is what the published
link really contains, and the naming does not work in it at all:

- **Set Name's output is never used.** It returns a new renamed item, but the
  Preview, Save and Share branches all take `PDF`, the raw Make PDF output. So
  every branch gets an unnamed file.
- **The Save branch Set Name is inverted.** It reads `Set Name of
  [Ask for Input], name: [PDF]`, which names the typed text after the file.
  The two chips need swapping.
- **The rename prompt pre-fills from `Name`, not `Updated Text`,** so it offers
  the untrimmed value. Sharing from Notes puts the whole note body in the
  filename field.

Fixing the first two makes the name work; the third makes it sensible for text.

## Archived copy

- `sequence.md` - what the published version actually does, action by action,
  generated from the plist. Read this before editing anything.
- `pdf-export.plist` - the published shortcut as readable XML.
- `pdf-export.shortcut` - Apple's signed, installable version.

All three come from `tools/fetch-shortcut.py`, which pulls them back down from
the iCloud record behind the install link.
