# Busy Redialer

Share sheet action. Redials a number until the call connects.

Share a contact or a phone number to it. It asks how many attempts to make.
Then it dials, hangs on for a moment, and dials again. It stops dialing as soon
as a call is up.

Use it on a hotline that is permanently busy.

## Before you install

One action comes from **Actions** by Sindre Sorhus, a free app on the App
Store. Install that app first. Without it the **Is Call Active** step has
nothing to run and the shortcut stops there.

## Install

See the install link on https://poeggi.github.io/ios-shortcuts/

## How it is built

1. Shortcuts > **+** > tap the name at the top > **Rename** > `Busy Redialer`.
2. **Get Phone Numbers from Input**, input **Shortcut Input**.
3. **Set Variable** `NumberToCall` to that output.
4. **Ask for Input**, **Number**, prompt `Repeat Count`, default answer `50`.
5. **Repeat**, count the Ask for Input output. Everything below goes inside it.
6. **Is Call Active**, from the Actions app.
7. **If** on that output. Leave the top branch empty. Fill **Otherwise**:
   - **Wait** 3 seconds.
   - **Call** `NumberToCall`.
   - **Wait** 3 seconds.
8. Details (i) > **Show in Share Sheet**, **Show on Apple Watch** and **Show in
   Spotlight** on. Share Sheet Types: Contacts and Phone Numbers.

Three things to watch while building it:

- The empty branch is the point. A call is already running, so the loop must do
  nothing rather than dial over it and drop it.
- Both waits matter. The first gives the last attempt time to fail, the second
  gives the new call time to register as active.
- The repeat count is a ceiling, not a plan. Once connected, the remaining runs
  fall through the empty branch and the shortcut just ends.

## Archived copy

- `sequence.md` - what the published version actually does, action by action.
  Read this before editing anything.
- `sequence.json` - the same list as data. The website renders it.
- `busy-redialer.plist` - the published shortcut as readable XML.
- `busy-redialer.shortcut` - Apple's signed, installable version.
- `busy-redialer.png` - the icon, also used for link previews.
- `index.html` - this shortcut's page on the website. Generated.

All of them come from `tools/fetch-shortcut.py`, which pulls them back down
from the iCloud record behind the install link.
