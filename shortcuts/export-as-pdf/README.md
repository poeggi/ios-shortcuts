# Export as PDF

Share sheet action. Takes whatever you shared - selected text, one or several
images, a Safari page, a file - turns it into a PDF, then offers a choice:

- **Preview** - Quick Look, from which you can still share or save
- **Save to Files** - the normal document save dialog, with "Ask Where to Save"

Several selected images become one multi-page PDF.

## Install

See the install link on https://poeggi.github.io/ios-shortcuts/

## Build it by hand

`ExportAsPDF.shortcut` in this folder is the source plist, not an installable
file (see the repo README for why). To recreate it:

1. Shortcuts > new shortcut > tap the (i) Details.
2. Turn on **Show in Share Sheet**.
3. Under Share Sheet Types leave on: Text, Rich Text, Images, URLs,
   Safari web pages, Files, PDFs. Turn the rest off.
4. Add **Make PDF**, input = Shortcut Input.
5. Add **Choose from Menu**, prompt "Export as PDF", two items:
   "Preview" and "Save to Files".
6. Under Preview: add **Quick Look**, input = the Make PDF output.
7. Under Save to Files: add **Save File**, input = the Make PDF output,
   and turn **Ask Where to Save** on.
8. Name it "Export as PDF".

## Actions

1. `is.workflow.actions.makepdf` - input: Shortcut Input
2. `is.workflow.actions.choosefrommenu` - "Preview", "Save to Files"
3. `is.workflow.actions.previewdocument`
4. `is.workflow.actions.documentpicker.save` - WFAskWhereToSave = true
