#!/usr/bin/env python3
"""Pull every published shortcut back down from iCloud and write its archive.

Reads shortcuts.json, and for each entry with an `icloud` link:

  shortcuts/<slug>/<slug>.plist      readable XML, diffable, not installable
  shortcuts/<slug>/<slug>.shortcut   Apple-signed, installable, opaque
  shortcuts/<slug>/sequence.md       generated action-by-action description

An iCloud link is a snapshot, so this is also the check that the published
version still matches what the repo claims. Run it after every re-share:

    python tools/fetch-shortcut.py             all entries
    python tools/fetch-shortcut.py pdf-export  one slug
    python tools/fetch-shortcut.py --check     verify only, write nothing

The record endpoint is public and needs no authentication.
"""

import datetime
import io
import json
import os
import plistlib
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORD_URL = "https://www.icloud.com/shortcuts/api/records/%s"
PREFIX = "is.workflow.actions."

# Only the identifiers whose generated name would otherwise read badly.
NAMES = {
    "getitemfromlist": "Get Item from List",
    "getitemname": "Get Name",
    "setitemname": "Set Name",
    "text.replace": "Replace Text",
    "text.split": "Split Text",
    "text.combine": "Combine Text",
    "makepdf": "Make PDF",
    "previewdocument": "Quick Look",
    "documentpicker.save": "Save File",
    "documentpicker.open": "Get File",
    "choosefrommenu": "Choose from Menu",
    "encodemedia": "Encode Media",
    "detect.text": "Get Text from Input",
    "conditional": "If",
    "repeat.count": "Repeat",
    "repeat.each": "Repeat with Each Item",
    "ask": "Ask for Input",
    "share": "Share",
    "gettext": "Text",
    "setvariable": "Set Variable",
    "getvariable": "Get Variable",
    "url": "URL",
    "downloadurl": "Get Contents of URL",
    "getitemtype": "Get Item Type",
    "nothing": "Nothing",
    "exit": "Stop This Shortcut",
    "notification": "Show Notification",
    "alert": "Show Alert",
    "openurl": "Open URL",
    "saveimage": "Save to Photo Album",
    "getimages": "Get Images from Input",
}

# Parameters already shown in the headline, or pure bookkeeping.
SKIP = {"UUID", "GroupingIdentifier", "WFControlFlowMode", "WFMenuItemTitle"}

LABELS = {
    "WFInput": "input",
    "WFMedia": "input",
    "WFName": "name",
    "WFVariableName": "variable",
    "WFMenuPrompt": "prompt",
    "WFMenuItems": "items",
    "WFReplaceTextFind": "find",
    "WFReplaceTextReplace": "replace with",
    "WFReplaceTextRegularExpression": "regular expression",
    "WFReplaceTextCaseSensitive": "case sensitive",
    "WFAskActionPrompt": "prompt",
    "WFAskActionDefaultAnswer": "default answer",
    "WFAllowsMultilineText": "multiline",
    "WFAskWhereToSave": "ask where to save",
    "WFDontIncludeFileExtension": "no file extension",
    "WFMediaAudioOnly": "audio only",
    "WFMediaAudioFormat": "audio format",
    "WFMediaMetadata": "metadata",
    "Metadata": "metadata",
    "WFGetItemFromListItemSpecifier": "item",
    "WFTextSeparator": "separator",
    "Show-WFInput": "show input",
}


def friendly(identifier):
    short = identifier[len(PREFIX):] if identifier.startswith(PREFIX) else identifier
    if short in NAMES:
        return NAMES[short]
    words = re.split(r"[._]", short)
    return " ".join(w[:1].upper() + w[1:] for w in words if w)


def reference(value):
    """Render one variable reference the way the Shortcuts editor shows it."""
    kind = value.get("Type")
    if kind == "ExtensionInput":
        return "[Shortcut Input]"
    if kind == "ActionOutput":
        return "[%s]" % value.get("OutputName", "output")
    if kind == "Variable":
        name = value.get("VariableName")
        if not name:
            nested = value.get("Variable", {})
            if isinstance(nested, dict):
                name = nested.get("Value", {}).get("VariableName")
        return "[%s]" % (name or "variable")
    if kind == "Ask":
        return "[Ask Each Time]"
    return "[%s]" % (kind or "?")


def token(value):
    """Render a parameter value, resolving embedded variable attachments."""
    if isinstance(value, dict) and "WFSerializationType" in value:
        kind = value["WFSerializationType"]
        inner = value.get("Value")
        if kind == "WFTextTokenAttachment":
            return reference(inner) if isinstance(inner, dict) else str(inner)
        if kind == "WFTextTokenString":
            text = inner.get("string", "")
            spans = inner.get("attachmentsByRange", {}) or {}
            marks = []
            for span, attachment in spans.items():
                found = re.match(r"\{(\d+), *(\d+)\}", span)
                if found:
                    marks.append((int(found.group(1)), int(found.group(2)), attachment))
            # Substitute from the end so the earlier offsets still hold.
            for start, length, attachment in sorted(marks, reverse=True):
                text = text[:start] + reference(attachment) + text[start + length:]
            return text.replace("\ufffc", "[?]")
        return json.dumps(inner, ensure_ascii=True, default=str)
    if isinstance(value, bool):
        return "on" if value else "off"
    if isinstance(value, list):
        return ", ".join(token(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=True, default=str)
    return str(value)


def show(text):
    """Keep generated markdown ASCII and on one line."""
    out = text.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return "".join(c if 32 <= ord(c) < 127 else "\\u%04x" % ord(c) for c in out)


def describe(actions):
    """Render the action list as indented, numbered steps."""
    lines = []
    depth = 0
    step = 0
    for action in actions:
        params = dict(action.get("WFWorkflowActionParameters", {}))
        name = friendly(action["WFWorkflowActionIdentifier"])
        mode = params.get("WFControlFlowMode")

        if mode == 2:
            depth = max(0, depth - 1)
            lines.append("%sEnd %s" % ("    " * depth, name))
            continue
        if mode == 1:
            depth = max(0, depth - 1)
            branch = params.get("WFMenuItemTitle", "Otherwise")
            lines.append('%sCase "%s"' % ("    " * depth, show(str(branch))))
            depth += 1
            continue

        step += 1
        head = "%s%d. %s" % ("    " * depth, step, name)
        primary = None
        for key in ("WFInput", "WFMedia"):
            if key in params:
                primary = token(params.pop(key))
                break
        if primary:
            head += " of %s" % show(primary)
        lines.append(head)

        for key in sorted(params):
            if key in SKIP:
                continue
            value = show(token(params[key])) or "(empty)"
            lines.append("%s   - %s: %s" % ("    " * depth, LABELS.get(key, key), value))

        if mode == 0:
            depth += 1
    return lines


def stamp(milliseconds):
    return datetime.datetime.fromtimestamp(milliseconds / 1000, datetime.timezone.utc)


def sequence_markdown(name, slug, record, plist, sizes):
    fields = record["fields"]
    types = ", ".join(plist.get("WFWorkflowTypes") or ["(none)"])
    inputs = plist.get("WFWorkflowInputContentItemClasses") or []
    out = [
        "# %s - action sequence" % name,
        "",
        "Generated by `tools/fetch-shortcut.py` from the published iCloud record.",
        "Do not edit by hand; re-run the script after re-sharing the shortcut.",
        "",
        "| | |",
        "|---|---|",
        "| Published name | %s |" % fields["name"]["value"],
        "| Record | `%s` |" % record["recordName"].lower().replace("-", ""),
        "| Shared | %s UTC |" % stamp(record["created"]["timestamp"]).strftime("%Y-%m-%d %H:%M"),
        "| Signing | %s |" % fields["signingStatus"]["value"],
        "| Certificate expires | %s |" % stamp(
            fields["signingCertificateExpirationDate"]["value"]).strftime("%Y-%m-%d"),
        "| Runs as | %s |" % types,
        "| Accepts | %d content types |" % len(inputs),
        "| Actions | %d |" % len(plist["WFWorkflowActions"]),
        "| Archived | `%s.plist` %d B, `%s.shortcut` %d B |" % (
            slug, sizes["plist"], slug, sizes["signed"]),
        "",
        "## Steps",
        "",
        "```",
    ]
    out += describe(plist["WFWorkflowActions"])
    out += ["```", ""]
    if inputs:
        out += ["## Accepted share sheet input", ""]
        out += ["- `%s`" % item for item in inputs]
        out += [""]
    return "\n".join(out)


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "ios-shortcuts-archiver"})
    return urllib.request.urlopen(request, timeout=60).read()


def process(entry, check_only):
    slug = entry["slug"]
    link = entry.get("icloud")
    if not link:
        print("%-16s skipped, no icloud link" % slug)
        return True
    record_id = link.rstrip("/").rsplit("/", 1)[-1]
    record = json.loads(fetch(RECORD_URL % record_id).decode("utf-8"))
    if record.get("deleted"):
        print("%-16s LINK IS DEAD (record deleted)" % slug)
        return False

    fields = record["fields"]
    raw = fetch(fields["shortcut"]["value"]["downloadURL"].replace("${f}", "s.plist"))
    signed = fetch(fields["signedShortcut"]["value"]["downloadURL"].replace("${f}", "s.shortcut"))
    plist = plistlib.loads(raw)
    xml = plistlib.dumps(plist, fmt=plistlib.FMT_XML)

    folder = os.path.join(ROOT, "shortcuts", slug)
    plist_path = os.path.join(folder, slug + ".plist")
    signed_path = os.path.join(folder, slug + ".shortcut")
    sequence_path = os.path.join(folder, "sequence.md")

    if check_only:
        stored = None
        if os.path.exists(plist_path):
            stored = plistlib.load(io.open(plist_path, "rb"))
        same = stored == plist
        print("%-16s %-16s signing=%-9s archive %s" % (
            slug, fields["name"]["value"], fields["signingStatus"]["value"],
            "matches" if same else "IS STALE"))
        return same

    if not os.path.isdir(folder):
        os.makedirs(folder)
    io.open(plist_path, "wb").write(xml)
    io.open(signed_path, "wb").write(signed)
    io.open(sequence_path, "w", encoding="utf-8", newline="\n").write(
        sequence_markdown(entry["name"], slug, record, plist,
                          {"plist": len(xml), "signed": len(signed)}))
    print("%-16s %-16s %d actions, %d B signed" % (
        slug, fields["name"]["value"], len(plist["WFWorkflowActions"]), len(signed)))
    return True


def main(argv):
    check_only = "--check" in argv
    wanted = [a for a in argv if not a.startswith("-")]
    manifest = json.load(io.open(os.path.join(ROOT, "shortcuts.json"), encoding="utf-8"))
    entries = [e for e in manifest["shortcuts"] if not wanted or e["slug"] in wanted]
    if not entries:
        print("no matching slug in shortcuts.json")
        return 2
    return 0 if all([process(entry, check_only) for entry in entries]) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
