# Export as PDF

Share sheet action. Takes whatever you shared - selected text, one or several
images, a Safari page, a file - turns it into a PDF, names it after the input,
then offers a choice:

- **Preview** - Quick Look, from which you can still share or save
- **Save to Files** - the normal document save dialog, with "Ask Where to Save"

Several selected images become one multi-page PDF.

The name comes from the shared item: a web page gives its title, a file its
filename. Shared text has no filename, so its own first line is used.

## Install

See the install link on https://poeggi.github.io/ios-shortcuts/

## How it is built

1. Shortcuts > **+** > tap the name at the top > **Rename** > `Export as PDF`.
2. **Get First Item** from **Shortcut Input**.
3. **Get name of** that item, **Get Web Page Title** on.
4. **Replace Text** in **Name**, **Regular Expression** on, find `\n[\s\S]*`,
   replace with nothing. This keeps only the first line, which matters for
   shared text, where the "name" is the whole body.
5. **Make PDF** from **Shortcut Input**.
6. **Set Name** of the PDF to **Updated Text**, **Don't Include File
   Extension** on.
7. **Choose from Menu**, prompt `Export as PDF`, two items: `Preview` and
   `Save to Files`.
8. Inside the Preview branch: **Quick Look**, input the Set Name output.
9. Inside the Save to Files branch: **Save File**, input the Set Name output,
   **Ask Where to Save** on.
10. Details (i) > **Show in Share Sheet** on > Share Sheet Types: leave only
    Text, Rich Text, Images, URLs, Safari web pages, Files, PDFs.

Three things to watch while building it:

- New actions land at the bottom of the shortcut rather than in the branch you
  tapped, so steps 8 and 9 usually need a drag into the right menu item.
- Inside a menu branch an unbound input does not fall back to the previous
  action. Both Quick Look and Save File must be pointed at Set Name explicitly.
- "Make sure to pass items to the Make PDF action" is a static editor warning.
  Shortcuts cannot prove at edit time that the share sheet will supply input.
