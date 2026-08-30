# Export as PDF

Share sheet action. Takes whatever you shared - selected text, one or several
images, a Safari page, a file - turns it into a PDF, then offers a choice:

- **Preview** - Quick Look, from which you can still share or save
- **Save to Files** - the normal document save dialog, with "Ask Where to Save"

Several selected images become one multi-page PDF.

## Install

See the install link on https://poeggi.github.io/ios-shortcuts/

## How it is built

1. Shortcuts > **+** > tap the name at the top > **Rename** > `Export as PDF`.
2. Add **Make PDF**, input **Shortcut Input**.
3. Add **Choose from Menu**, prompt `Export as PDF`, two items:
   `Preview` and `Save to Files`.
4. Inside the Preview branch: **Quick Look**, input the Make PDF output.
5. Inside the Save to Files branch: **Save File**, input the Make PDF output,
   **Ask Where to Save** on.
6. Details (i) > **Show in Share Sheet** on > Share Sheet Types: leave only
   Text, Rich Text, Images, URLs, Safari web pages, Files, PDFs.

New actions land at the bottom of the shortcut rather than in the branch you
tapped, so step 4 and 5 usually need a drag into the right menu item.
