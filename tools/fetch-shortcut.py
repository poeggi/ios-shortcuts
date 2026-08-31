#!/usr/bin/env python3
# Copyright (C) 2026 Kai Poggensee
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pull every published shortcut back down from iCloud and write its archive.

Reads shortcuts.json, and for each entry with an `icloud` link:

  shortcuts/<slug>/<slug>.plist      readable XML, diffable, not installable
  shortcuts/<slug>/<slug>.shortcut   Apple-signed, installable, opaque
  shortcuts/<slug>/<slug>.png        the icon iOS renders, used by the website
  shortcuts/<slug>/sequence.md       generated action-by-action description
  shortcuts/<slug>/sequence.json     the same, for the website to render
  shortcuts/<slug>/index.html        the shortcut's page, with link previews
  og.png                             the site's link preview image

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
SITE = "https://poeggi.github.io/ios-shortcuts"
PREFIX = "is.workflow.actions."

# Variable references are marked out of band rather than with brackets, because
# a parameter value can legitimately contain a bracket and a regex usually does.
VAR_OPEN = chr(2)
VAR_CLOSE = chr(3)

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
    "detect.phonenumber": "Get Phone Numbers from Input",
    "delay": "Wait",
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
    "WFRepeatCount": "count",
    "WFDelayTime": "seconds",
    "WFCallContact": "number",
    "WFCondition": "condition",
    "WFInputType": "input type",
    "WFAskActionDefaultAnswerNumber": "default answer",
    "WFAskActionAllowsDecimalNumbers": "allow decimals",
    "WFAskActionAllowsNegativeNumbers": "allow negatives",
    "AppIntentDescriptor": "app",
    "IntentAppDefinition": "app",
}

# An action supplied by an app, not by Shortcuts, names the app here.
APP_KEYS = ("AppIntentDescriptor", "IntentAppDefinition")

# Comparison codes of the If action. Only the one in use is named.
CONDITIONS = {4: "is"}

# WFWorkflowTypes as the Shortcuts app words them.
RUNS_AS = {
    "ActionExtension": "Share Sheet",
    "WFWorkflowTypeShowInSearch": "Spotlight",
    "NCWidget": "Widget",
    "Watch": "Watch",
    "Sleep": "Sleep Focus",
}


def friendly(identifier):
    if identifier.startswith(PREFIX):
        short = identifier[len(PREFIX):]
        if short in NAMES:
            return NAMES[short]
        words = re.split(r"[._]", short)
    else:
        # An app's own action: com.vendor.App.IsCallActive is Is Call Active.
        words = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+",
                           identifier.rsplit(".", 1)[-1])
    return " ".join(w[:1].upper() + w[1:] for w in words if w)


def reference(value):
    """Render one variable reference the way the Shortcuts editor shows it."""
    kind = value.get("Type")
    if kind == "ExtensionInput":
        return mark("Shortcut Input")
    if kind == "ActionOutput":
        return mark(value.get("OutputName", "output"))
    if kind == "Variable":
        name = value.get("VariableName")
        nested = value.get("Variable")
        if not name and isinstance(nested, dict):
            inner = nested.get("Value", nested)
            if isinstance(inner, dict):
                # A wrapped reference, such as an If reading an action output.
                if inner.get("Type"):
                    return reference(inner)
                name = inner.get("VariableName")
        return mark(name or "variable")
    if kind == "Ask":
        return mark("Ask Each Time")
    return mark(kind or "?")


def token(value):
    """Render a parameter value, resolving embedded variable attachments."""
    if isinstance(value, dict) and "Type" in value and "Value" not in value:
        return reference(value)
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
    keep = (VAR_OPEN, VAR_CLOSE)
    return "".join(c if c in keep or 32 <= ord(c) < 127 else "\\u%04x" % ord(c) for c in out)


def mark(name):
    return VAR_OPEN + name + VAR_CLOSE


def flat(text):
    """A marked string as plain text: a variable reads as [Name]."""
    return text.replace(VAR_OPEN, "[").replace(VAR_CLOSE, "]")


def pieces(text):
    """A marked string as segments, so a renderer can draw the variables."""
    out = []
    for index, part in enumerate(re.split("[%s%s]" % (VAR_OPEN, VAR_CLOSE), text)):
        if part:
            out.append({"t": "var" if index % 2 else "text", "v": part})
    return out


def param(key, raw):
    """A parameter value, with the keys that carry a code or a payload named."""
    if key in APP_KEYS and isinstance(raw, dict):
        return str(raw.get("Name", "")) or token(raw)
    if key == "WFCondition":
        return CONDITIONS.get(raw, str(raw))
    return token(raw)


def steps(actions):
    """Structured action list. Both sequence.md and the website render this,
    so the two can never drift apart."""
    out = []
    depth = 0
    step = 0
    for action in actions:
        params = dict(action.get("WFWorkflowActionParameters", {}))
        name = friendly(action["WFWorkflowActionIdentifier"])
        mode = params.get("WFControlFlowMode")

        if mode == 2:
            depth = max(0, depth - 1)
            out.append({"kind": "end", "depth": depth, "name": name})
            continue
        if mode == 1:
            depth = max(0, depth - 1)
            out.append({"kind": "case", "depth": depth,
                        "name": show(str(params.get("WFMenuItemTitle", "Otherwise")))})
            depth += 1
            continue

        step += 1
        target = None
        for key in ("WFInput", "WFMedia"):
            if key in params:
                target = show(token(params.pop(key)))
                break
        entry = {"kind": "action", "depth": depth, "n": step, "name": name,
                 "target": target, "params": []}
        for key in sorted(params):
            if key in SKIP:
                continue
            entry["params"].append({"label": LABELS.get(key, key),
                                    "value": show(param(key, params[key])) or "(empty)"})
        out.append(entry)

        if mode == 0:
            depth += 1
    return out


def describe(items):
    """Render the structured steps as the indented text block in sequence.md."""
    lines = []
    for item in items:
        pad = "    " * item["depth"]
        if item["kind"] == "end":
            lines.append("%sEnd %s" % (pad, item["name"]))
            continue
        if item["kind"] == "case":
            lines.append('%sCase "%s"' % (pad, flat(item["name"])))
            continue
        head = "%s%d. %s" % (pad, item["n"], item["name"])
        if item["target"]:
            head += " of %s" % flat(item["target"])
        lines.append(head)
        for param in item["params"]:
            lines.append("%s   - %s: %s" % (
                pad, param["label"], flat(param["value"])))
    return lines


def icon_color(plist):
    """WFWorkflowIconStartColor is a 32-bit RGBA value; drop the alpha byte."""
    raw = (plist.get("WFWorkflowIcon") or {}).get("WFWorkflowIconStartColor")
    if not isinstance(raw, int):
        return None
    return "#%06x" % ((raw & 0xFFFFFFFF) >> 8)


def stamp(milliseconds):
    return datetime.datetime.fromtimestamp(milliseconds / 1000, datetime.timezone.utc)


def sequence_markdown(name, slug, record, plist, sizes, items):
    fields = record["fields"]
    types = ", ".join(RUNS_AS.get(t, t)
                      for t in plist.get("WFWorkflowTypes") or ["(none)"])
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
        "| Icon | glyph %s, %s |" % (
            (plist.get("WFWorkflowIcon") or {}).get("WFWorkflowIconGlyphNumber", "?"),
            icon_color(plist) or "unknown"),
        "| Archived | `%s.plist` %d B, `%s.shortcut` %d B, `%s.png` %d B |" % (
            slug, sizes["plist"], slug, sizes["signed"], slug, sizes["icon"]),
        "",
        "## Steps",
        "",
        "```",
    ]
    out += describe(items)
    out += ["```", ""]
    if inputs:
        out += ["## Accepted share sheet input", ""]
        out += ["- `%s`" % item for item in inputs]
        out += [""]
    return "\n".join(out)


def jsonable(item):
    """One step for the website: variable references become segments."""
    if item["kind"] != "action":
        return dict(item, name=flat(item["name"]))
    return dict(item,
                target=pieces(item["target"]) if item["target"] else None,
                params=[{"label": p["label"], "value": pieces(p["value"])}
                        for p in item["params"]])


def sequence_json(name, slug, record, plist, sizes, items):
    """The same content as sequence.md, for the website to render."""
    fields = record["fields"]
    icon = plist.get("WFWorkflowIcon") or {}
    return {
        "name": name,
        "slug": slug,
        "published": fields["name"]["value"],
        "record": record["recordName"].lower().replace("-", ""),
        "shared": stamp(record["created"]["timestamp"]).strftime("%Y-%m-%d %H:%M UTC"),
        "signing": fields["signingStatus"]["value"],
        "expires": stamp(
            fields["signingCertificateExpirationDate"]["value"]).strftime("%Y-%m-%d"),
        "types": plist.get("WFWorkflowTypes") or [],
        "inputs": plist.get("WFWorkflowInputContentItemClasses") or [],
        "glyph": icon.get("WFWorkflowIconGlyphNumber"),
        "color": icon_color(plist),
        "sizes": sizes,
        "steps": [jsonable(item) for item in items],
    }


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{name}</title>
<meta name="description" content="{summary}">
<meta name="theme-color" content="{color}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{site_name}">
<meta property="og:title" content="{name}">
<meta property="og:description" content="{summary}">
<meta property="og:url" content="{site}/shortcuts/{slug}/">
<meta property="og:image" content="{site}/shortcuts/{slug}/{slug}.png">
<meta property="og:image:width" content="450">
<meta property="og:image:height" content="450">
<meta property="og:image:alt" content="{name} icon">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{name}">
<meta name="twitter:description" content="{summary}">
<meta name="twitter:image" content="{site}/shortcuts/{slug}/{slug}.png">
<link rel="icon" href="{slug}.png">
<link rel="apple-touch-icon" href="{slug}.png">
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<main>
  <a class="back" href="../../">All shortcuts</a>
  <div id="top"></div>
  <div id="body"></div>
  <footer>
    <p>The action list is generated from the published iCloud record rather
    than written by hand, so it is what the Install button actually installs.
    <code>tools/fetch-shortcut.py</code> rewrites this page after every
    re-share.</p>
    <p><a href="https://github.com/poeggi/ios-shortcuts">Source on GitHub</a></p>
  </footer>
</main>
<script>window.BASE = "../../";</script>
<script src="../../render.js"></script>
<script>mountDetail("{slug}");</script>
</body>
</html>
"""


def attr(text):
    """Escape for an HTML attribute."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def page_html(entry, plist, site_name):
    return PAGE.format(
        name=attr(entry["name"]),
        summary=attr(entry.get("summary", "")),
        slug=entry["slug"],
        color=icon_color(plist) or "#007aff",
        site=SITE,
        site_name=attr(site_name))


def write_og_image(manifest, slugs):
    """Compose the 1200x630 image link previews show for the site itself."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("%-16s skipped og.png, Pillow is not installed" % "")
        return

    def font(size, bold):
        for name in (("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf") if bold
                     else ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf")):
            for folder in ("C:/Windows/Fonts/", "/usr/share/fonts/truetype/dejavu/", ""):
                try:
                    return ImageFont.truetype(folder + name, size)
                except OSError:
                    continue
        return ImageFont.load_default()

    width, height = 1200, 630
    card = Image.new("RGB", (width, height), "#0c0c0f")
    draw = ImageDraw.Draw(card)
    draw.text((80, 108), manifest.get("title", "iOS Shortcuts"),
              font=font(66, True), fill="#f2f2f7")
    draw.text((80, 196), "One-tap iCloud install links, mirrored and archived",
              font=font(32, False), fill="#98989f")

    size, gap, x = 156, 28, 80
    for slug in slugs:
        path = os.path.join(ROOT, "shortcuts", slug, slug + ".png")
        if not os.path.exists(path) or x + size > width - 80:
            continue
        icon = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, size - 1, size - 1), radius=int(size * 0.23), fill=255)
        card.paste(icon, (x, 330), mask)
        x += size + gap

    draw.text((80, 540), "poeggi.github.io/ios-shortcuts",
              font=font(28, False), fill="#0a84ff")
    card.save(os.path.join(ROOT, "og.png"))
    print("%-16s %d x %d link preview image" % ("og.png", width, height))


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "ios-shortcuts-archiver"})
    return urllib.request.urlopen(request, timeout=60).read()


def process(entry, check_only, manifest_title):
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
    icon = fetch(fields["icon"]["value"]["downloadURL"].replace("${f}", "s.png"))
    plist = plistlib.loads(raw)
    xml = plistlib.dumps(plist, fmt=plistlib.FMT_XML)

    folder = os.path.join(ROOT, "shortcuts", slug)
    plist_path = os.path.join(folder, slug + ".plist")
    signed_path = os.path.join(folder, slug + ".shortcut")
    icon_path = os.path.join(folder, slug + ".png")
    sequence_path = os.path.join(folder, "sequence.md")
    json_path = os.path.join(folder, "sequence.json")
    page_path = os.path.join(folder, "index.html")

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
    sizes = {"plist": len(xml), "signed": len(signed), "icon": len(icon)}
    items = steps(plist["WFWorkflowActions"])
    io.open(plist_path, "wb").write(xml)
    io.open(signed_path, "wb").write(signed)
    io.open(icon_path, "wb").write(icon)
    io.open(sequence_path, "w", encoding="utf-8", newline="\n").write(
        sequence_markdown(entry["name"], slug, record, plist, sizes, items))
    io.open(json_path, "w", encoding="utf-8", newline="\n").write(
        json.dumps(sequence_json(entry["name"], slug, record, plist, sizes, items),
                   indent=2, ensure_ascii=True, sort_keys=True) + "\n")
    io.open(page_path, "w", encoding="utf-8", newline="\n").write(
        page_html(entry, plist, manifest_title))
    print("%-16s %-16s %d actions, %d B signed, icon %s %d B" % (
        slug, fields["name"]["value"], len(plist["WFWorkflowActions"]), len(signed),
        icon_color(plist) or "?", len(icon)))
    return True


def main(argv):
    check_only = "--check" in argv
    wanted = [a for a in argv if not a.startswith("-")]
    manifest = json.load(io.open(os.path.join(ROOT, "shortcuts.json"), encoding="utf-8"))
    entries = [e for e in manifest["shortcuts"] if not wanted or e["slug"] in wanted]
    if not entries:
        print("no matching slug in shortcuts.json")
        return 2
    title = manifest.get("title", "iOS Shortcuts")
    ok = all([process(entry, check_only, title) for entry in entries])
    if not check_only:
        write_og_image(manifest, [e["slug"] for e in manifest["shortcuts"]])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
