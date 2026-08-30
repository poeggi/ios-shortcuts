# PDF Export

Share sheet action. Takes whatever you shared - selected text, one or several
images, a Safari page, a file - turns it into a PDF, names it after the input,
then offers a choice:

- **Preview** - Quick Look, from which you can still share or save
- **Save to Files** - asks for a file name, then the normal document save
  dialog with "Ask Where to Save"
- **Share** - hands the PDF straight to the share sheet

Several selected images become one multi-page PDF.

The name comes from the shared item: a web page gives its title, a file its
filename. Shared text has no filename, so its own first line is used.

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
    Text, Rich Text, Images, URLs, Safari web pages, Files, PDFs.

Three things to watch while building it:

- New actions land at the bottom of the shortcut rather than in the branch you
  tapped, so the branch actions usually need a drag into the right menu item.
- Inside a menu branch an unbound input does not fall back to the previous
  action. Both Quick Look and Save File must be pointed at Set Name explicitly.
- "Make sure to pass items to the Make PDF action" is a static editor warning.
  Shortcuts cannot prove at edit time that the share sheet will supply input.

## Archived copy

`pdf-export.plist` is the published shortcut as readable XML, and
`pdf-export.shortcut` is Apple's signed, installable version. Both were pulled
from the iCloud record behind the install link. See the top-level README.
