#!/usr/bin/env python3
"""Emit the web page's key data and the Test Firmware keymap from one source.

Reads  config/drift.json    - the physical position of all 70 Binding Slots
       config/drift.keymap  - the Production Firmware, four layers of 70

Writes web/keymap-data.js   - what the page draws and matches against
       config/drift_test.keymap - the Test Firmware (see docs/adr/0001)

Both outputs come from this one pass on purpose: a hand-kept Test Firmware would
eventually disagree with the page, and the page would call a healthy switch dead.
"""

import json
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAYOUT = ROOT / "config" / "drift.json"
KEYMAP = ROOT / "config" / "drift.keymap"
OUT_JS = ROOT / "web" / "keymap-data.js"
OUT_TEST = ROOT / "config" / "drift_test.keymap"

SLOTS = 70
LAYER_ORDER = ["base", "lower", "raise", "adjust"]

# --- Kedmanee: the Thai character each physical position produces -------------
# (unshifted, shifted), keyed by the US keycode that sits at that position.
KEDMANEE = {
    "GRAVE": ("_", "%"),
    "N1": ("ๅ", "+"), "N2": ("/", "๑"), "N3": ("-", "๒"), "N4": ("ภ", "๓"),
    "N5": ("ถ", "๔"), "N6": ("ุ", "ู"), "N7": ("ึ", "฿"), "N8": ("ค", "๕"),
    "N9": ("ต", "๖"), "N0": ("จ", "๗"), "MINUS": ("ข", "๘"), "EQUAL": ("ช", "๙"),
    "Q": ("ๆ", "๐"), "W": ("ไ", '"'), "E": ("ำ", "ฎ"), "R": ("พ", "ฑ"), "T": ("ะ", "ธ"),
    "Y": ("ั", "ํ"), "U": ("ี", "๊"), "I": ("ร", "ณ"), "O": ("น", "ฯ"), "P": ("ย", "ญ"),
    "LBKT": ("บ", "ฐ"), "RBKT": ("ล", ","), "BSLH": ("ฃ", "ฅ"),
    "A": ("ฟ", "ฤ"), "S": ("ห", "ฆ"), "D": ("ก", "ฏ"), "F": ("ด", "โ"), "G": ("เ", "ฌ"),
    "H": ("้", "็"), "J": ("่", "๋"), "K": ("า", "ษ"), "L": ("ส", "ศ"),
    "SEMI": ("ว", "ซ"), "SQT": ("ง", "."),
    "Z": ("ผ", "("), "X": ("ป", ")"), "C": ("แ", "ฉ"), "V": ("อ", "ฮ"), "B": ("ิ", "ฺ"),
    "N": ("ื", "์"), "M": ("ท", "?"), "COMMA": ("ม", "ฒ"), "DOT": ("ใ", "ฬ"),
    "FSLH": ("ฝ", "ฦ"),
}

EN_SHIFT = {
    "N1": "!", "N2": "@", "N3": "#", "N4": "$", "N5": "%", "N6": "^", "N7": "&",
    "N8": "*", "N9": "(", "N0": ")", "MINUS": "_", "EQUAL": "+", "GRAVE": "~",
    "LBKT": "{", "RBKT": "}", "BSLH": "|", "SEMI": ":", "SQT": '"',
    "COMMA": "<", "DOT": ">", "FSLH": "?",
}

# --- ZMK keycode -> KeyboardEvent.code ----------------------------------------
CODES = {
    "GRAVE": "Backquote", "MINUS": "Minus", "EQUAL": "Equal",
    "LBKT": "BracketLeft", "RBKT": "BracketRight", "BSLH": "Backslash",
    "SEMI": "Semicolon", "SQT": "Quote", "COMMA": "Comma", "DOT": "Period",
    "FSLH": "Slash", "TAB": "Tab", "CAPS": "CapsLock", "ESC": "Escape",
    "SPACE": "Space", "BSPC": "Backspace", "DEL": "Delete", "ENTER": "Enter",
    "RET": "Enter", "PG_UP": "PageUp", "PG_DN": "PageDown", "HOME": "Home",
    "END": "End", "INS": "Insert", "UP": "ArrowUp", "DOWN": "ArrowDown",
    "LEFT": "ArrowLeft", "RIGHT": "ArrowRight", "SLCK": "ScrollLock",
    "PAUSE_BREAK": "Pause",
    "LSHFT": "ShiftLeft", "RSHFT": "ShiftRight", "LCTRL": "ControlLeft",
    "RCTRL": "ControlRight", "LALT": "AltLeft", "RALT": "AltRight",
    "LGUI": "MetaLeft", "RGUI": "MetaRight",
}
for _c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    CODES[_c] = "Key" + _c
for _d in range(10):
    CODES[f"N{_d}"] = f"Digit{_d}"
for _f in range(1, 25):
    CODES[f"F{_f}"] = f"F{_f}"

# --- how each keycode reads on screen -----------------------------------------
GLYPHS = {
    "GRAVE": "`", "MINUS": "-", "EQUAL": "=", "LBKT": "[", "RBKT": "]",
    "BSLH": "\\", "SEMI": ";", "SQT": "'", "COMMA": ",", "DOT": ".", "FSLH": "/",
    "ESC": "Esc", "TAB": "Tab", "CAPS": "Caps", "SPACE": "␣", "BSPC": "⌫",
    "DEL": "⌦", "ENTER": "⏎", "RET": "⏎", "PG_UP": "PgUp", "PG_DN": "PgDn",
    "HOME": "Home", "END": "End", "INS": "Ins", "UP": "↑", "DOWN": "↓",
    "LEFT": "←", "RIGHT": "→", "SLCK": "ScrLk", "PAUSE_BREAK": "Pause",
    "LSHFT": "⇧", "RSHFT": "⇧", "LCTRL": "⌃", "RCTRL": "⌃",
    "LALT": "⌥", "RALT": "⌥", "LGUI": "⌘", "RGUI": "⌘",
    "C_MUTE": "🔇", "C_VOL_UP": "🔊", "C_VOL_DN": "🔉",
    "C_BRI_UP": "☀+", "C_BRI_DN": "☀−", "C_PREV": "⏮", "C_PP": "⏯", "C_NEXT": "⏭",
}
MOD_WRAP = {"LG": ("⌘", "Meta"), "RG": ("⌘", "Meta"), "LC": ("⌃", "Control"),
            "RC": ("⌃", "Control"), "LA": ("⌥", "Alt"), "RA": ("⌥", "Alt"),
            "LS": ("⇧", "Shift"), "RS": ("⇧", "Shift")}

# Codes the Test Firmware may hand out, in a fixed order so a rebuild is stable.
# F1-F12 are absent on purpose: macOS eats them unless the user has changed a
# system preference, and a board checker must not depend on that (ADR-0001).
TEST_POOL = (
    list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    + [f"N{d}" for d in list(range(1, 10)) + [0]]
    + [f"F{n}" for n in range(13, 25)]
    + ["GRAVE", "MINUS", "EQUAL", "LBKT", "RBKT", "BSLH", "SEMI", "SQT",
       "COMMA", "DOT", "FSLH"]
    + ["TAB", "SPACE", "BSPC", "DEL", "ENTER", "PG_UP", "PG_DN", "HOME", "END", "INS"]
    + ["UP", "DOWN", "LEFT", "RIGHT"]
    + ["ESC", "SLCK", "PAUSE_BREAK"]
)


def read_layers(text):
    """Pull the four layers out of the keymap as lists of binding strings."""
    text = re.sub(r"//.*", "", text)
    layers = {}
    for m in re.finditer(r"(\w+)_layer\s*\{.*?bindings\s*=\s*<(.*?)>;", text, re.S):
        name, body = m.group(1), m.group(2)
        if name == "default":  # ZMK calls it default_layer; we call it base
            name = "base"
        if name not in LAYER_ORDER:
            continue
        bindings = [" ".join(b.split()) for b in re.findall(r"&[^&>]+", body)]
        if len(bindings) != SLOTS:
            sys.exit(f"{name}: {len(bindings)} bindings, expected {SLOTS}")
        layers[name] = bindings
    missing = [n for n in LAYER_ORDER if n not in layers]
    if missing:
        sys.exit(f"missing layers: {missing}")
    return layers


def describe(binding):
    """Turn one ZMK binding into what the page shows and what it listens for."""
    out = {"raw": binding, "en": binding, "en_shift": "", "th": "", "th_shift": "",
           "code": None, "mods": []}
    behaviour, _, arg = binding.partition(" ")
    arg = arg.strip()

    if behaviour == "&kp":
        mods, inner = [], arg
        while True:
            m = re.fullmatch(r"([LR][GCAS])\((.+)\)", inner)
            if not m:
                break
            glyph, mod = MOD_WRAP[m.group(1)]
            mods.append((glyph, mod))
            inner = m.group(2)
        out["mods"] = [m for _, m in mods]
        prefix = "".join(g for g, _ in mods)
        out["code"] = CODES.get(inner)
        base = GLYPHS.get(inner, inner)
        if inner in EN_SHIFT and not mods:
            out["en_shift"] = EN_SHIFT[inner]
        if len(inner) == 1 or inner.startswith("N") and inner[1:].isdigit():
            base = GLYPHS.get(inner, inner[-1] if inner.startswith("N") else inner)
        out["en"] = prefix + base
        if not mods and inner in KEDMANEE:
            out["th"], out["th_shift"] = KEDMANEE[inner]
        return out

    labels = {
        "&trans": "▽", "&none": "", "&bootloader": "Boot", "&sys_reset": "Reset",
    }
    if binding in labels:
        out["en"] = labels[binding]
    elif behaviour == "&mo":
        out["en"] = arg.lower()
    elif behaviour == "&bt":
        out["en"] = {"BT_CLR": "BT clr", "BT_CLR_ALL": "BT clr all"}.get(
            arg, "BT" + str(int(arg.split()[-1]) + 1) if "BT_SEL" in arg else arg)
    elif behaviour == "&out":
        out["en"] = {"OUT_USB": "USB", "OUT_BLE": "BLE", "OUT_TOG": "USB/BLE"}.get(arg, arg)
    elif behaviour == "&mkp":
        out["en"] = {"LCLK": "click L", "RCLK": "click R", "MCLK": "click M"}.get(arg, arg)
    elif behaviour == "&mmv":
        out["en"] = "mouse " + {"MOVE_UP": "↑", "MOVE_DOWN": "↓",
                                "MOVE_LEFT": "←", "MOVE_RIGHT": "→"}.get(arg, arg)
    elif behaviour == "&msc":
        out["en"] = "scroll " + {"SCRL_UP": "↑", "SCRL_DOWN": "↓"}.get(arg, arg)
    return out


TEST_TEMPLATE = """// GENERATED by tools/generate.py - do not edit.
//
// Test Firmware: every Binding Slot and every encoder direction emits a distinct
// plain keycode, so a browser can prove each switch individually. See
// docs/adr/0001-separate-test-firmware.md. Never leave this on the board.

#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {{
    keymap {{
        compatible = "zmk,keymap";

        default_layer {{
            display-name = "test";
            bindings = <
{bindings}
            >;

            sensor-bindings = <&inc_dec_kp {l_cw} {l_ccw}>, <&inc_dec_kp {r_cw} {r_ccw}>;
        }};
    }};
}};
"""


def main():
    layout = json.load(LAYOUT.open())["layouts"]["default_layout"]["layout"]
    if len(layout) != SLOTS:
        sys.exit(f"drift.json has {len(layout)} slots, expected {SLOTS}")
    layers = read_layers(KEYMAP.read_text())

    needed = SLOTS + 4
    if len(TEST_POOL) < needed:
        sys.exit(f"test pool holds {len(TEST_POOL)}, needs {needed}")
    unknown = [k for k in TEST_POOL if k not in CODES]
    if unknown:
        sys.exit(f"test pool has keycodes with no browser code: {unknown}")

    slot_keys = TEST_POOL[:SLOTS]
    l_cw, l_ccw, r_cw, r_ccw = TEST_POOL[SLOTS:needed]

    # --- Test Firmware --------------------------------------------------------
    rows, i = [], 0
    for line_len in (16, 16, 14, 18, 6):
        rows.append("".join(f"&kp {k:<12}" for k in slot_keys[i:i + line_len]).rstrip())
        i += line_len
    OUT_TEST.write_text(TEST_TEMPLATE.format(
        bindings="\n".join(" " * 16 + r for r in rows),
        l_cw=l_cw, l_ccw=l_ccw, r_cw=r_cw, r_ccw=r_ccw))

    # --- page data ------------------------------------------------------------
    data = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "unit": 56,
        "layout": [
            {"x": k["x"], "y": k["y"], "r": k.get("r", 0),
             "rx": k.get("rx", k["x"]), "ry": k.get("ry", k["y"]),
             "half": "left" if k["x"] < 10 else "right"}
            for k in layout
        ],
        "layers": {name: [describe(b) for b in layers[name]] for name in LAYER_ORDER},
        "test": {
            "slots": [CODES[k] for k in slot_keys],
            "encoders": [
                {"label": "encoder ซ้าย", "half": "left",
                 "cw": CODES[l_cw], "ccw": CODES[l_ccw]},
                {"label": "encoder ขวา", "half": "right",
                 "cw": CODES[r_cw], "ccw": CODES[r_ccw]},
            ],
        },
    }
    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUT_JS.write_text(
        "// GENERATED by tools/generate.py - do not edit.\n"
        "window.DRIFT_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")

    halves = [s["half"] for s in data["layout"]]
    print(f"{OUT_TEST.relative_to(ROOT)}: {SLOTS} slots + 4 encoder directions")
    print(f"{OUT_JS.relative_to(ROOT)}: {len(LAYER_ORDER)} layers, "
          f"{halves.count('left')} left / {halves.count('right')} right, "
          f"{len(TEST_POOL) - needed} spare test codes")


if __name__ == "__main__":
    main()
