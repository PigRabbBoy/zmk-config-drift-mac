#!/usr/bin/env python3
"""Emit the web page's key data and the Test Firmware keymap from one source.

Reads  config/drift.json    - the physical position of all 70 Binding Slots
       config/drift.keymap  - the Production Firmware, every layer 70 slots

Writes web/keymap-data.js   - what the page draws and matches against
       config/drift_test.keymap - the Test Firmware (see docs/adr/0001)

Both outputs come from this one pass on purpose: a hand-kept Test Firmware would
eventually disagree with the page, and the page would call a healthy switch dead.
"""

import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAYOUT = ROOT / "config" / "drift.json"
KEYMAP = ROOT / "config" / "drift.keymap"
OUT_JS = ROOT / "web" / "keymap-data.js"
OUT_TEST = ROOT / "config" / "drift_test.keymap"

SLOTS = 70

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
    "SPACE": "Space", "BSPC": "Backspace", "BACKSPACE": "Backspace",
    "BACKSLASH": "Backslash", "DEL": "Delete", "ENTER": "Enter",
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

# Thai plain-language notes for anything a person cannot read off the legend.
# Letters, digits and punctuation get nothing on purpose — an entry here is a
# promise that the key needs explaining.
NOTES = {
    "&bootloader": "เข้าโหมด bootloader ของเครื่องที่กด — drive NICENANO จะโผล่ขึ้นมาให้ลากไฟล์ .uf2 ลงไป",
    "&sys_reset": "รีสตาร์ทบอร์ด เหมือนถอดแบตเสียบใหม่ ไม่ได้เข้า bootloader",
    "&trans": "โปร่งใส — ปุ่มนี้ไม่ได้ทำอะไรของตัวเอง ใช้ค่าจาก layer ที่อยู่ข้างล่าง (ปกติคือ base)",
    "&none": "ไม่ผูกอะไรไว้ กดแล้วไม่เกิดอะไรขึ้น",
    "&caps_word": "Caps Word — ตัวอักษรถัดไปเป็นตัวใหญ่ทั้งหมด แล้วปิดเองเมื่อเจอ space หรือเครื่องหมาย "
                  "(ขีดล่าง ตัวเลข ⌫ ไม่ตัด) เหมาะกับ CONSTANT_NAME ในโค้ด",
    "&bt BT_CLR": "ลบการจับคู่ของ Bluetooth profile ที่ใช้อยู่ตอนนี้ ใช้ตอนจับคู่ใหม่ไม่ติด",
    "&bt BT_CLR_ALL": "ลบการจับคู่ของทุก profile พร้อมกัน",
    "&out OUT_USB": "บังคับส่งสัญญาณออกทางสาย USB อย่างเดียว",
    "&out OUT_BLE": "บังคับส่งสัญญาณออกทาง Bluetooth อย่างเดียว",
    "&out OUT_TOG": "สลับไปมาระหว่าง USB กับ Bluetooth",
    "&mkp LCLK": "คลิกซ้ายของเมาส์ — กดค้างแล้วขยับ = ลาก",
    "&mkp RCLK": "คลิกขวาของเมาส์",
    "&mkp MCLK": "คลิกล้อกลางของเมาส์",
    "&mkp MB4": "ปุ่มเมาส์ 4 = ย้อนกลับ (Back) ใน browser และ Finder",
    "&mkp MB5": "ปุ่มเมาส์ 5 = ไปข้างหน้า (Forward) ใน browser และ Finder",
    "&kp C_MUTE": "ปิด/เปิดเสียง — ช่องนี้คือการกด encoder ซ้ายลงไป ไม่ใช่ปุ่มธรรมดา",
    "&kp C_PP": "เล่น / หยุดชั่วคราว — ช่องตรงกลางบอร์ดคือการกด encoder ขวาลงไป",
    "&kp C_BRI_UP": "เพิ่มความสว่างหน้าจอ",
    "&kp C_BRI_DN": "ลดความสว่างหน้าจอ",
    "&kp C_PREV": "เพลง/วิดีโอ ก่อนหน้า",
    "&kp C_NEXT": "เพลง/วิดีโอ ถัดไป",
    "&kp LG(C)": "⌘C คัดลอก — บน Mac ต้องเป็น ⌘ ไม่ใช่ Ctrl",
    "&kp LG(V)": "⌘V วาง",
    "&kp LG(SPACE)": "⌘Space เปิด Spotlight — ค้นหา/เปิด app โดยไม่แตะเมาส์ · ในโหมดคู่มือปุ่มนี้ไม่สว่าง "
                     "เพราะ macOS กินไปก่อนถึง browser",
    "&kp LC(SPACE)": "⌃Space สลับ input source ไทย ↔ อังกฤษ — อยู่บน keycap ที่สลักว่า Caps "
                     "(Caps Lock จริงย้ายไป layer adjust ช่องเดียวกัน) · ในโหมดคู่มือปุ่มนี้ไม่สว่าง "
                     "เพราะ macOS กินไปก่อนถึง browser",
    "&kp LC(UP)": "⌃↑ Mission Control — เห็นทุกหน้าต่างและทุก Space",
    "&kp LC(DOWN)": "⌃↓ App Exposé — หน้าต่างทั้งหมดของ app ที่ใช้อยู่",
    "&kp LC(LEFT)": "⌃← ไป Space ทางซ้าย",
    "&kp LC(RIGHT)": "⌃→ ไป Space ทางขวา",
    "&kp LG(TAB)": "⌘Tab สลับไป app ที่ใช้ล่าสุด (กดค้างจะเปิดตัวเลือก app) · "
                   "ในโหมดคู่มือปุ่มนี้ไม่สว่างเพราะ macOS กินไปก่อน",
    "&kp LG(GRAVE)": "⌘` หน้าต่างถัดไปของ app เดียวกัน",
    "&kp LG(LC(Q))": "⌃⌘Q ล็อกหน้าจอ",
    "&kp LG(LS(N3))": "⌘⇧3 ถ่ายภาพหน้าจอทั้งจอ เซฟลง Desktop ทันที",
    "&kp LG(LS(N4))": "⌘⇧4 ถ่ายภาพหน้าจอแบบลากเลือกพื้นที่",
    "&kp LG(LS(N5))": "⌘⇧5 เปิดแถบเครื่องมือถ่ายภาพ/อัดวิดีโอหน้าจอ",
    "&kp CAPS": "Caps Lock จริง — บน base ช่องนี้เป็น ⌃Space สลับภาษา ถ้าอยากล็อกตัวใหญ่จริงๆ มากดที่นี่",
    "&kp PG_UP": "เลื่อนขึ้นหนึ่งหน้าจอ",
    "&kp PG_DN": "เลื่อนลงหนึ่งหน้าจอ",
    "&kp HOME": "ไปต้นเอกสาร/ต้นหน้า (ใน editor ส่วนใหญ่ = ต้นบรรทัด)",
    "&kp END": "ไปท้ายเอกสาร/ท้ายหน้า (ใน editor ส่วนใหญ่ = ท้ายบรรทัด)",
    "&kp BSPC": "ปุ่ม delete ปกติของ Mac (⌫) ลบตัวอักษรทางซ้าย",
    "&kp DEL": "forward delete (⌦) ลบตัวอักษรทางขวา — บนคีย์บอร์ด Apple ต้องกด Fn+Delete",
    "&kp LGUI": "⌘ Command",
    "&kp RGUI": "⌘ Command ตัวขวา — ใช้ ⌘-click ในโหมด mouse ได้ เพราะ thumb ⌘ ซ้ายกลายเป็นคลิกขวา",
    "&kp LALT": "⌥ Option",
    "&kp RALT": "⌥ Option ตัวขวา",
    "&kp LCTRL": "⌃ Control",
    "&kp RCTRL": "⌃ Control ตัวขวา",
    "&kp LSHFT": "⇧ Shift",
    "&kp RSHFT": "⇧ Shift ตัวขวา",
    "&kp ESC": "Escape",
    "&kp TAB": "Tab",
    "&kp ENTER": "Return / Enter",
    "&kp GRAVE": "` กับ ~ (ไทย: _ กับ %)",
    "&kp LEFT": "← กด ⌥ ค้าง = ถอยทีละคำ · ⌘ ค้าง = ต้นบรรทัด · ⇧ ค้าง = เลือกข้อความ · ⌃⌥ ค้าง = tile หน้าต่างซ้าย",
    "&kp RIGHT": "→ กด ⌥ ค้าง = ไปทีละคำ · ⌘ ค้าง = ท้ายบรรทัด · ⇧ ค้าง = เลือกข้อความ · ⌃⌥ ค้าง = tile หน้าต่างขวา",
    "&kp UP": "↑ กด ⌥ ค้าง = ต้นย่อหน้า · ⌘ ค้าง = ต้นเอกสาร · ⌃⌥ ค้าง = tile หน้าต่างบน",
    "&kp DOWN": "↓ กด ⌥ ค้าง = ท้ายย่อหน้า · ⌘ ค้าง = ท้ายเอกสาร · ⌃⌥ ค้าง = tile หน้าต่างล่าง",
}
MOVE_NOTE = {"up": "ขึ้น", "down": "ลง", "left": "ไปทางซ้าย", "right": "ไปทางขวา"}
ARROW = {"up": "↑", "down": "↓", "left": "←", "right": "→"}

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


def strip_comments(text):
    return re.sub(r"//.*", "", text)


def read_keymap(raw):
    """Layers in file order, the layer-number defines, and the conditional layer.

    Returns (layers, layer_names, conditional) where
      layers      = {display_name: [70 binding strings]}
      encoders    = {display_name: [(cw, ccw), (cw, ccw)]}   left, then right
      by_define   = {"NAV": "nav", ...}   so `&mo NAV` can be named on the page
      conditional = {"if": ["nav", "mouse"], "then": "adjust"} or None
    """
    text = strip_comments(raw)
    defines = {m.group(1): int(m.group(2))
               for m in re.finditer(r"#define\s+([A-Z_]+)\s+(\d+)\s*$", text, re.M)}

    heads = list(re.finditer(r"(\w+)_layer\s*\{\s*display-name\s*=\s*\"([^\"]+)\"\s*;", text))
    if not heads:
        sys.exit("no layers with a display-name found")
    layers, encoders, order = {}, {}, []
    for i, h in enumerate(heads):
        name = h.group(2)
        body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        bm = re.search(r"bindings\s*=\s*<(.*?)>\s*;", body, re.S)
        if not bm:
            sys.exit(f"{name}: no bindings block")
        bindings = [" ".join(b.split()) for b in re.findall(r"&[^&>]+", bm.group(1))]
        if len(bindings) != SLOTS:
            sys.exit(f"{name}: {len(bindings)} bindings, expected {SLOTS}")
        sm = re.search(r"sensor-bindings\s*=\s*(.*?);", body, re.S)
        if not sm:
            sys.exit(f"{name}: no sensor-bindings (every layer must list both encoders)")
        pairs = re.findall(r"<\s*&\w+\s+([\w()]+)\s+([\w()]+)\s*>", sm.group(1))
        if len(pairs) != 2:
            sys.exit(f"{name}: {len(pairs)} sensor bindings, expected 2 (left, right)")
        layers[name] = bindings
        encoders[name] = pairs
        order.append(name)

    by_define = {d: order[n] for d, n in defines.items() if n < len(order)}

    conditional = None
    cm = re.search(r"if-layers\s*=\s*<([^>]+)>\s*;\s*then-layer\s*=\s*<\s*(\w+)\s*>", text)
    if cm:
        conditional = {"if": [by_define.get(x, x) for x in cm.group(1).split()],
                       "then": by_define.get(cm.group(2), cm.group(2))}
    return layers, encoders, by_define, conditional


def parse_move(arg):
    """MOVE_UP / SCRL_DOWN / MOVE_X(-10) -> (axis-direction, magnitude or None)."""
    m = re.fullmatch(r"(?:MOVE|SCRL)_(UP|DOWN|LEFT|RIGHT)", arg)
    if m:
        return m.group(1).lower(), None
    m = re.fullmatch(r"MOVE_([XY])\((-?\d+)\)", arg)
    if m:
        axis, n = m.group(1), int(m.group(2))
        if axis == "X":
            return ("right" if n > 0 else "left"), abs(n)
        return ("__y_pos" if n > 0 else "__y_neg"), abs(n)
    return arg, None


def scroll_dir(arg):
    d, n = parse_move(arg)
    # &msc: positive Y scrolls UP (ZMK docs), so MOVE_Y(10) is "up".
    return {"__y_pos": "up", "__y_neg": "down"}.get(d, d), n


def mouse_dir(arg):
    d, n = parse_move(arg)
    # &mmv: positive Y moves DOWN.
    return {"__y_pos": "down", "__y_neg": "up"}.get(d, d), n


def note_for(binding, behaviour, arg, by_define, conditional):
    """A plain-Thai explanation, or "" when the legend already says everything."""
    if binding in NOTES:
        return NOTES[binding]
    if behaviour == "&mo":
        name = by_define.get(arg, arg.lower())
        text = f"กดค้างเพื่อเข้า layer {name} ปล่อยแล้วกลับ layer เดิม"
        if conditional and name in conditional["if"]:
            others = [x for x in conditional["if"] if x != name]
            text += f" — กดพร้อมกับ {' + '.join(others)} จะเข้า layer {conditional['then']}"
        return text
    if behaviour == "&tog":
        name = by_define.get(arg, arg.lower())
        return (f"เปิด/ปิดโหมด {name} ค้างไว้ — กดครั้งเดียวเปิด กดชุดเดียวกันอีกครั้งปิด "
                f"จอ OLED บน dock โชว์ชื่อ {name} ตอนที่เปิดอยู่")
    if behaviour == "&bt" and arg.startswith("BT_SEL"):
        n = int(arg.split()[-1]) + 1
        return (f"สลับไปใช้ Bluetooth profile ที่ {n} — dongle จำเครื่องได้ 5 เครื่องแยกกัน "
                f"สลับเครื่องโดยไม่ต้องจับคู่ใหม่")
    if behaviour == "&mmv":
        d, _ = mouse_dir(arg)
        return f"ขยับเคอร์เซอร์เมาส์{MOVE_NOTE.get(d, d)} — แตะสั้นขยับนิดเดียว กดค้างจะเร่งความเร็วขึ้น"
    if behaviour == "&msc":
        d, n = scroll_dir(arg)
        speed = f" (ความเร็ว {n})" if n else ""
        return f"เลื่อนหน้า{MOVE_NOTE.get(d, d)} เหมือนหมุนล้อเมาส์{speed}"
    if behaviour in ("&kpad", "&kpws"):
        pair = "A กับ D" if behaviour == "&kpad" else "W กับ S"
        return (f"ปุ่มธรรมดาสำหรับ host แต่ถ้ากด {pair} ค้างพร้อมกัน ตัวที่กดทีหลังชนะ "
                f"(last-input-priority สำหรับเกม จาก module ของ Timception) — มีเฉพาะโหมด game "
                f"บน base เป็นปุ่มธรรมดา")
    return ""


def describe(binding, by_define, conditional):
    """Turn one ZMK binding into what the page shows and what it listens for."""
    out = {"raw": binding, "en": binding, "en_shift": "", "th": "", "th_shift": "",
           "code": None, "mods": [], "note": ""}
    behaviour, _, arg = binding.partition(" ")
    arg = arg.strip()
    out["note"] = note_for(binding, behaviour, arg, by_define, conditional)

    # &kpad / &kpws are Timception's last-input-priority behaviours on WASD. To a
    # host they are ordinary key presses, so treat them exactly like &kp.
    if behaviour in ("&kpad", "&kpws"):
        behaviour = "&kp"

    if behaviour == "&kp":
        mods, inner = [], arg
        while True:
            m = re.fullmatch(r"([LR][GCAS])\((.+)\)", inner)
            if not m:
                break
            glyph, mod = MOD_WRAP[m.group(1)]
            mods.append((glyph, mod))
            inner = m.group(2)
        out["mods"] = sorted(m for _, m in mods)
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
        "&caps_word": "CapsW",
    }
    if binding in labels:
        out["en"] = labels[binding]
    elif behaviour == "&mo":
        out["en"] = by_define.get(arg, arg.lower())
    elif behaviour == "&tog":
        out["en"] = by_define.get(arg, arg.lower()) + " ⏻"
    elif behaviour == "&bt":
        out["en"] = {"BT_CLR": "BT clr", "BT_CLR_ALL": "BT clr all"}.get(
            arg, "BT" + str(int(arg.split()[-1]) + 1) if "BT_SEL" in arg else arg)
    elif behaviour == "&out":
        out["en"] = {"OUT_USB": "USB", "OUT_BLE": "BLE", "OUT_TOG": "USB/BLE"}.get(arg, arg)
    elif behaviour == "&mkp":
        out["en"] = {"LCLK": "click L", "RCLK": "click R", "MCLK": "click M",
                     "MB4": "back", "MB5": "fwd"}.get(arg, arg)
    elif behaviour == "&mmv":
        d, _ = mouse_dir(arg)
        out["en"] = "mouse " + ARROW.get(d, d)
    elif behaviour == "&msc":
        d, _ = scroll_dir(arg)
        out["en"] = "scroll " + ARROW.get(d, d)
    return out


# What the page says about each encoder argument. Both encoder halves share
# these; the first sensor-binding in a layer is the LEFT encoder.
ENC_NOTE = {
    "SCRL_UP": "เลื่อนหน้าขึ้น", "SCRL_DOWN": "เลื่อนหน้าลง",
    "SCRL_LEFT": "เลื่อนหน้าไปทางซ้าย", "SCRL_RIGHT": "เลื่อนหน้าไปทางขวา",
    "C_VOL_UP": "เพิ่มเสียง", "C_VOL_DN": "ลดเสียง",
    "C_BRI_UP": "เพิ่มความสว่างจอ", "C_BRI_DN": "ลดความสว่างจอ",
    "LC(TAB)": "tab ถัดไป (⌃Tab)", "LC(LS(TAB))": "tab ก่อนหน้า (⌃⇧Tab)",
}


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
    keymap_text = KEYMAP.read_text()
    layers, encoders, by_define, conditional = read_keymap(keymap_text)
    order = list(layers)

    # The two encoders are not Binding Slots, and which one does what is easy to
    # get backwards: sensors are listed left-then-right in drift.dtsi, so the
    # first sensor-binding is the LEFT encoder.
    def encoder_rows(pairs):
        return [
            {"half": half, "label": label,
             "cw": ENC_NOTE.get(a, a), "ccw": ENC_NOTE.get(b, b)}
            for (a, b), half, label in zip(pairs, ("left", "right"),
                                           ("encoder ซ้าย", "encoder ขวา"))
        ]

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
    # A fingerprint of the inputs, not a timestamp: the output has to be
    # byte-identical on a rebuild or the staleness check in CI can never pass.
    digest = hashlib.sha256(LAYOUT.read_bytes() + KEYMAP.read_bytes()).hexdigest()[:8]

    data = {
        "source": digest,
        "unit": 56,
        "layout": [
            {"x": k["x"], "y": k["y"], "r": k.get("r", 0),
             "rx": k.get("rx", k["x"]), "ry": k.get("ry", k["y"]),
             "half": "left" if k["x"] < 10 else "right"}
            for k in layout
        ],
        "layer_order": order,
        "conditional": conditional,
        "layers": {name: [describe(b, by_define, conditional) for b in layers[name]]
                   for name in order},
        "encoders": encoder_rows(encoders[order[0]]),
        "layers_encoders": {name: encoder_rows(encoders[name]) for name in order},
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
    print(f"{OUT_JS.relative_to(ROOT)}: {len(order)} layers ({', '.join(order)}), "
          f"{halves.count('left')} left / {halves.count('right')} right, "
          f"{len(TEST_POOL) - needed} spare test codes")


if __name__ == "__main__":
    main()
