# Drift V3 — ZMK config for macOS

ZMK config สำหรับ **Drift Keyboard V3 by Timception** แบบ **dongle** — 68 คีย์ split, nice!nano 3 ตัว
(dongle 1 + ครึ่งซ้าย/ขวาอย่างละ 1), roller encoder 2 ตัว, OLED บน dongle
ปรับ keymap ให้ตรงกับ macOS และตรงกับ keycap ที่ติดตั้งอยู่จริง

Fork มาจาก [Timception/drift-v3-dongle](https://github.com/Timception/drift-v3-dongle)

> **dongle เป็น central** — keymap อยู่บน dongle ตัวเดียว ครึ่งซ้าย/ขวาเป็น peripheral ไม่ถือ keymap
> แก้ keymap = flash แค่ dongle ไม่ต้องแตะสองครึ่ง

## ทำไมต้องแก้

Keymap default ของ upstream เขียนไว้สำหรับ Windows คีย์ modifier 3 ตำแหน่งส่งค่าไม่ตรงกับตัวอักษรบน keycap ที่ติดตั้ง

| ตำแหน่ง | keycap | upstream ส่ง | config นี้ส่ง |
|---|---|---|---|
| ซ้าย คอลัมน์นอก แถวบนสุด | `Pgup` | `ESC` | `PG_UP` |
| ซ้าย คอลัมน์นอก แถว 2 | `Pgdn` | `RS(LG(S))` (Windows snip) | `PG_DN` |
| ซ้าย 2u แถว home | `Shift` | `LGUI` | `LSHFT` |
| ขวา ล่าง ก่อน Del | `Shift` | `BACKSPACE` | `RSHFT` |
| ขวา ล่าง (cap โบว์) | — | `RCTRL` | `RGUI` (⌘ ขวา) |
| ซ้าย thumb นอกสุด | — | `LSHFT` | `LGUI` (⌘) |
| ซ้าย คอลัมน์นอกสุด แถว 2 / แถวล่าง | — | `LC(C)` / `LC(V)` | `LG(C)` / `LG(V)` |

`LC(C)` / `LC(V)` คือ Ctrl+C / Ctrl+V ซึ่งบน macOS ไม่ทำอะไรเลย ต้องเป็น `LG()` = Command

## Layout

ห้า layer ออกแบบรอบสามงาน — เขียนโค้ด เล่นเกม ใช้ทั่วไป — โดยแตะเมาส์ให้น้อยที่สุด
ลำดับเลข layer มีความหมาย: `game` เป็น overlay ที่ toggle ค้าง อยู่**ต่ำกว่า** layer ที่กดค้างทุกตัว
(ดู [ADR-0003](./docs/adr/0003-game-is-a-toggled-overlay.md)) และทุกปุ่มบน base เป็นปุ่มธรรมดา ไม่มี hold-tap ไม่มี combo
(ดู [ADR-0004](./docs/adr/0004-plain-keys-stay-plain.md))

| # | layer | เข้ายังไง | มีอะไร |
|---|---|---|---|
| 0 | `base` | — | พิมพ์งาน + shortcut macOS · ช่อง Caps ส่ง `⌃Space` สลับไทย/อังกฤษ |
| 1 | `game` | `adjust` + `G` toggle (OLED ขึ้น `game`) | WASD แบบ last-input-priority, thumb ซ้ายนอก ⌘ → ⌥ ที่เหลือทะลุไป base |
| 2 | `nav` | thumb ซ้ายในค้าง | HJKL ลูกศร, YUIO Home/PgDn/PgUp/End, F1–F12, ปุ่มจัดหน้าต่าง macOS, Caps Word, screenshot |
| 3 | `mouse` | thumb ขวาในค้าง | HJKL ขยับเคอร์เซอร์, YUIO scroll, thumb ซ้ายคลิก, N/M = ปุ่มเมาส์ 4/5 |
| 4 | `adjust` | nav + mouse ค้างพร้อมกัน | Bluetooth, USB/BLE, media, ความสว่าง, Caps Lock จริง, ล็อกจอ, bootloader, toggle game |

### Base layer

```
| ESC  | PGUP | `    |  1 |  2 |  3 |  4 |  5 |            |  6 |  7 |  8 |  9 |  0 |  -  |  =  | ⌫    |
| ⌘C   | PGDN | TAB  |  Q |  W |  E |  R |  T |            |  Y |  U |  I |  O |  P |  [  |  ]  | \    |
|      | SHIFT (2u)  | ^␣ | A |  S |  D |  F |  G |        |  H |  J |  K |  L |  ; |  '  | ENTER      |
| ⌘V   | CTRL | OPT  |  Z |  X |  C |  V |  B | 🔇 || ⏯ |  N |  M |  , |  . |  / | ⇧R  | ⌘R  | ⌦    |
                            | ⌘ | SPACE | NAV |           | MOUSE | SPACE | ⌫ |
```

Encoder สองลูกทำคนละหน้าที่ (เรียงตาม `sensors = <&left_encoder &right_encoder>` ใน `drift.dtsi`) และ**หมุนต่างกันตาม layer**:

| | หมุน (base) | หมุน (nav ค้าง) | กดลง |
|---|---|---|---|
| **encoder ซ้าย** | เลื่อนหน้าขึ้น/ลง (`&enc_scroll`) | เลื่อนหน้าซ้าย/ขวา | ปิด/เปิดเสียง |
| **encoder ขวา** | เพิ่ม/ลดเสียง (`&inc_dec_kp`) | สลับ tab `⌃Tab` / `⌃⇧Tab` | เล่น / หยุด |

### Game (toggle ด้วย adjust + G)

- `W A S D` ใช้ `&kpws` / `&kpad` ของ Timception — กด A ค้างแล้วกด D = ไปขวาทันที (last-input-priority) มี**เฉพาะที่นี่** base เป็น `&kp` ธรรมดา
- thumb ซ้ายนอก `⌘` → `⌥` — เกมบน Mac ใช้ Option/Control/Shift และ ⌘ หลุดกลางเกมคือ ⌘Q / ⌘H / ⌘Tab (`R⌘` ขวายังอยู่)
- ที่เหลือ `&trans` ทั้งหมด: nav ยังให้ F-keys, `⌃Space` ยังสลับภาษาแชท, Space สองข้างยังเป็น Space
- OLED บน dock ขึ้น `game` ตลอดที่เปิด กดชุดเดิมอีกครั้งเพื่อปิด

### Nav (thumb ซ้ายในค้าง)

- `H J K L` = ← ↓ ↑ → เป็นลูกศร**ธรรมดา** — กด `⌥` / `⌘` / `⇧` / `⌃⌥` จริงค้างร่วม = ทีละคำ / ต้น-ท้ายบรรทัด / เลือก / tile หน้าต่าง โดยไม่ต้องมีปุ่มเพิ่ม (ช่องอื่นบน nav เป็น `&trans` เพื่อให้ chord พวกนี้ทะลุถึง host)
- `Y U I O` = Home · PgDn · PgUp · End
- แถวเลข = `F1`–`F12`
- มือซ้าย: `Q` ⌘` หน้าต่างถัดไป · `W` ⌃↑ Mission Control · `E` ⌘Tab · `A` / `D` ⌃← ⌃→ ย้าย Space · `S` ⌃↓ App Exposé
- ช่อง Caps = `&caps_word` (พิมพ์ CONSTANT_NAME แล้วปิดเองเมื่อเจอ space)
- Space (ข้างไหนก็ได้) = `⌘Space` Spotlight — nav ค้าง + Space
- `⌘⇧4` / `⌘⇧3` / `⌘⇧5` screenshot ที่คอลัมน์ซ้ายนอก · `⌦` ที่มุมขวาบนและ thumb ⌫

### Mouse (thumb ขวาในค้าง)

- `H J K L` ขยับเคอร์เซอร์ — `&mmv` เร่งความเร็ว (`time-to-max-speed-ms` 300, exponent 1) แตะสั้น = นิดเดียว กดค้าง = พุ่ง
- `Y U I O` = scroll ← ↓ ↑ → (`&msc MOVE_X/Y(±10)` แยกจากค่า 120 ของ encoder)
- Space ซ้าย = คลิกซ้าย · thumb ⌘ ซ้าย = คลิกขวา · `F` = คลิกกลาง · `N` / `M` = ปุ่มเมาส์ 4/5 (Back/Forward)
- ⌘-click ใช้ `R⌘` · ⇧/⌥-click ใช้ปุ่มจริง

### Adjust (nav + mouse ค้างพร้อมกัน)

- `BT1`–`BT5` บนเลข 1–5 · `BT CLR` / `BT CLR ALL` ที่คอลัมน์ซ้ายนอกแถว 2
- `Y U I` = `OUT_USB` / `OUT_BLE` / `OUT_TOG`
- ความสว่างจอ, Prev / Play-Pause / Next
- ช่อง Caps = Caps Lock จริง · `G` = toggle `game` · `L` = `⌃⌘Q` ล็อกหน้าจอ
- `bootloader` มุมซ้ายบน/ขวาบน, `sys_reset` ถัดจากมุมซ้าย

หน้าเว็บมีคำอธิบายทุกปุ่มที่ legend บอกไม่หมด + คู่มือ "ลดการใช้เมาส์" (ฝั่งคีย์บอร์ด / setting macOS ที่ต้องตั้งเอง / cheat-sheet ต่อ app)

## Build

Push repo นี้ขึ้น GitHub แล้ว GitHub Actions จะ build ให้อัตโนมัติ (`.github/workflows/build.yml`)

```bash
gh repo create zmk-config-drift-mac --private --source=. --push
```

โหลด artifact `firmware.zip` จากแท็บ Actions จะได้ 5 ไฟล์:

| ไฟล์ | ลงที่ไหน | เมื่อไหร่ |
|---|---|---|
| `drift_central_dongle` | **dongle** | Production Firmware — ตัวที่ใช้พิมพ์จริง เปิด ZMK Studio |
| `drift_test_dongle` | **dongle** | Test Firmware — เฉพาะตอนตรวจบอร์ด แล้ว flash ตัวบนกลับ |
| `drift_left` | ครึ่งซ้าย | peripheral — ลงครั้งแรกหรือหลัง settings reset เท่านั้น |
| `drift_right` | ครึ่งขวา | peripheral — เหมือนกัน |
| `settings_reset` | ตัวที่มีปัญหา | เมื่อ dongle กับครึ่งไหนไม่คุยกัน |

เปลี่ยน keymap ลงแค่ `drift_central_dongle` พอ

## Flash

1. ต่อสาย USB-C เข้า **dongle**
2. กดปุ่ม reset บน nice!nano **2 ครั้งเร็วๆ** → จะขึ้น drive ชื่อ `NICENANO`
3. ลาก **ไฟล์เดียว** ลง drive → บอร์ด reboot เอง drive หายไปเอง (ปกติ ไม่ใช่ error)

`NICENANO` ไม่ใช่โฟลเดอร์เก็บไฟล์ มันคือช่องรับ firmware — เขียนอะไรลงไป บอร์ดเอาอันนั้น
ไปทับของเดิมทันที **ห้ามลากหลายไฟล์พร้อมกัน**

ครึ่งซ้าย/ขวาไม่ต้อง flash ตอนเปลี่ยน keymap ถ้าจำเป็นจริงก็ทำแบบเดียวกันทีละข้าง
ถ้า dongle ไม่เจอครึ่งไหน: flash `settings_reset` ลงทั้ง dongle และครึ่งนั้น แล้ว flash ของจริงกลับ

## จับคู่กับ Mac

dongle เป็นตัวที่คุยกับ Mac (ครึ่งซ้าย/ขวาคุยกับ dongle ไม่ได้คุยกับ Mac โดยตรง)

1. บน keyboard: กด thumb ซ้ายใน + ขวาใน ค้าง (layer `adjust`) แล้วกด `BT CLR` (คอลัมน์ซ้ายนอก แถว 2) เพื่อล้าง profile เดิมของ dongle
2. ยังค้างอยู่ กด `1` = `BT1` (หรือ profile ที่ว่าง)
3. macOS → System Settings → Bluetooth → เลือก **Drift V3**
4. ถ้า Keyboard Setup Assistant เด้งขึ้นมาถามให้กดปุ่มข้าง Shift ซ้าย — ปิดไปแล้วเลือก **ANSI** เองที่ System Settings → Keyboard → Change Keyboard Type

## เว็บคู่มือ + ตัวตรวจบอร์ด

https://pigrabbboy.github.io/zmk-config-drift-mac/

หน้าเดียว สองโหมด:

**โหมดคู่มือ** — รูปคีย์บอร์ดวาดจากพิกัดจริงใน `config/drift.json` แสดง legend คู่ EN + ไทย (Kedmanee)
ครบทั้ง 5 layer ซึ่ง keymap-editor ของ ZMK แสดงให้ไม่ได้ กด Shift ค้างเพื่อดู legend ชั้นที่สอง
กดปุ่มจริงแล้วปุ่มบนรูปสว่าง (เทียบทั้ง code และ modifier ที่กดค้าง — กด `C` เฉยๆ ติดที่ `C` ไม่ใช่ `⌘C`)
แต่ไม่นับคะแนน เพราะหน้าเว็บไม่มีทางรู้ว่า ZMK อยู่ layer ไหน — มันตาม layer ให้ได้เฉพาะที่ข้อมูลบอกได้
(`nav` จากลูกศร/F-keys, `adjust` จาก Caps Lock) และบอกตรงๆ ว่า `game` กับ `mouse` ตามไม่ได้
ด้านล่างมีคู่มือ "โหมดใช้งาน" และ "ลดการใช้เมาส์" — ฝั่งคีย์บอร์ด, setting macOS ที่ต้องตั้งเองครั้งเดียว
(Keyboard navigation, App Shortcuts สำหรับ tile หน้าต่าง, Vimium), และ cheat-sheet ของ Zed / Warp+tmux / Arc / Slack

**โหมดทดสอบบอร์ด** — ไล่ให้ครบทั้ง 70 สวิตช์ + หมุน encoder 4 ทิศ นับแยกซ้าย/ขวา
(แต่ละครึ่งคุยกับ dongle แยกกัน ถ้าครึ่งไหนหลุดจะตายทั้ง 35 ช่องพร้อมกัน — ตัวเลขแยกทำให้เห็นทันที)
จับปุ่มเด้ง (chatter) ด้วย และจำผลไว้ใน localStorage ข้าม refresh

โหมดนี้**ต้อง flash Test Firmware ก่อน**: Production Firmware มี 5 ช่องที่ browser มองไม่เห็นเลย
(`&kp C_MUTE`, `&kp C_PP` ที่ encoder, `&mo NAV`, `&mo MOUSE`, และ `⌃Space` ที่ macOS กินก่อน) และ 2 คู่ที่ส่งค่าเหมือนกันจนแยกไม่ออก
(`SPACE`, `BSPC`) — `SPACE` คร่อมสองครึ่งบอร์ดด้วย เหตุผลเต็มอยู่ใน
[ADR-0001](./docs/adr/0001-separate-test-firmware.md) (ตัวเลขใน ADR เป็นของ keymap ตอนตัดสินใจ)
Test Firmware ไม่ได้เปลี่ยนจากการปรับ keymap รอบนี้ — มันไม่เคยขึ้นกับ layer ของ Production

ขั้นตอน: flash `drift_test_dongle` ลง dongle → เปิดเว็บโหมดทดสอบ → กดจนครบ →
**flash `drift_central_dongle` กลับ**

Test Firmware ไม่มี `&bootloader` ผูกไว้เลย (70 ช่องเป็น `&kp` ล้วนตามนิยาม) ทางออกทางเดียวคือ
ปุ่ม reset จริงบน dongle — ซึ่งกดถึงอยู่แล้ว อย่า flash ลงอุปกรณ์ที่กดปุ่ม reset ไม่ถึง

## Generated files

`config/drift_test.keymap` และ `web/keymap-data.js` **สร้างด้วยเครื่อง ห้ามแก้มือ**
ทั้งคู่ออกมาจาก `tools/generate.py` ที่อ่าน `drift.keymap` + `drift.json`

แก้ keymap แล้วต้องรัน:

```bash
python3 tools/generate.py
```

ทั้งสองไฟล์ commit เข้า repo เพราะ workflow build ของ ZMK checkout เองและแทรกขั้นตอน
generate ก่อน build ไม่ได้ — job `verify-generated` ใน `.github/workflows/pages.yml`
เป็นตัวกันลืม มันรัน generator ใหม่แล้ว fail ถ้าผลไม่ตรงกับที่ commit ไว้

## ตรวจว่าปุ่มส่งอะไรจริง

System Settings → Keyboard → Input Sources → เปิด **Show Input menu in menu bar** → เลือก **Show Keyboard Viewer**
กดปุ่มที่เป็น keycap ลายเปล่า แล้วดูว่าไฟขึ้นตรงไหนบน Keyboard Viewer
กด modifier ค้าง (⌘ / ⌥ / ⌃ / ⇧) แล้ว Keyboard Viewer จะเปลี่ยน layer ทันที = ยืนยันได้ว่า thumb ไหนเป็น modifier อะไร

## หมายเหตุ

- `&kp BSPC` = ปุ่ม delete ปกติของ Mac (⌫), `&kp DEL` = forward delete (Fn+Delete บน Apple keyboard) — keycap `Del` มี 2 ตัวจึงไม่ใช่ใส่ซ้ำ
- keycap ที่สลัก `Caps` ส่ง `⌃Space` (shortcut สลับ input source ที่เปิดอยู่ใน macOS ของเครื่องนี้) ไม่ต้องตั้ง "Use Caps Lock key to switch…" · Caps Lock จริงอยู่ที่ `adjust` ช่องเดียวกัน
- **ZMK Studio เปิดอยู่** (`CONFIG_ZMK_STUDIO=y`, locking ปิด, snippet `studio-rpc-usb-uart`) — ต่อ dongle ด้วยสาย USB แล้วแก้ keymap สดได้โดยไม่ต้อง build **แต่ repo นี้คือ source of truth**: หน้าเว็บกับ Test Firmware สร้างจาก `config/drift.keymap` ในโปรเจกต์ แก้ผ่าน Studio หน้าเว็บจะไม่ตาม
- behavior `&kpad` / `&kpws` ของ upstream (last-input-priority บน WASD) อยู่เฉพาะ layer `game` — host มองเป็นปุ่มธรรมดา
- setting ฝั่ง macOS ที่หน้าเว็บแนะนำ (Keyboard navigation, App Shortcuts สำหรับ tiling, Vimium) เป็นของที่ต้องตั้งเองบนเครื่อง repo นี้ไม่ได้ตั้งให้
- OLED บน dongle เปิด `CONFIG_ZMK_DONGLE_DISPLAY_MAC_MODIFIERS=y` อยู่แล้ว แสดงสัญลักษณ์ ⌘ ⌥ ⌃ แบบ Mac
