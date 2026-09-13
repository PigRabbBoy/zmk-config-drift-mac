# Drift V3 — ZMK config for macOS

ZMK config สำหรับ **Drift Keyboard V3 by Timception** (68-key split, nice!nano v2, roller encoder 2 ตัว, OLED 2 จอ) ปรับ keymap ให้ตรงกับ macOS และตรงกับ keycap ที่ติดตั้งอยู่จริง

Fork มาจาก [Timception/zmk-config-drift-v3-editor](https://github.com/Timception/zmk-config-drift-v3-editor)

## ทำไมต้องแก้

Keymap default ของ upstream เขียนไว้สำหรับ Windows คีย์ modifier 3 ตำแหน่งส่งค่าไม่ตรงกับตัวอักษรบน keycap ที่ติดตั้ง

| ตำแหน่ง | keycap | upstream ส่ง | config นี้ส่ง |
|---|---|---|---|
| ซ้าย คอลัมน์นอก แถวบนสุด | `Pgup` | `ESC` | `PG_UP` |
| ซ้าย คอลัมน์นอก แถว 2 | `Pgdn` | `RS(LG(S))` (Windows snip) | `PG_DN` |
| ซ้าย 2u แถว home | `Shift` | `LGUI` | `LSHFT` |
| ขวา ล่าง ก่อน Del | `Shift` | `RALT` | `RSHFT` |
| ขวา ล่าง (cap โบว์) | — | `RCTRL` | `RGUI` (⌘ ขวา) |
| ซ้าย thumb นอกสุด | — | `LSHFT` | `LGUI` (⌘) |
| ซ้าย คอลัมน์นอกสุด แถว 2 / แถวล่าง | — | `LC(C)` / `LC(V)` | `LG(C)` / `LG(V)` |

`LC(C)` / `LC(V)` คือ Ctrl+C / Ctrl+V ซึ่งบน macOS ไม่ทำอะไรเลย ต้องเป็น `LG()` = Command

## Layout

### Base layer

```
| ESC  | PGUP | `    |  1 |  2 |  3 |  4 |  5 |            |  6 |  7 |  8 |  9 |  0 |  -  |  =  | ⌫    |
| ⌘C   | PGDN | TAB  |  Q |  W |  E |  R |  T |            |  Y |  U |  I |  O |  P |  [  |  ]  | \    |
|      | SHIFT (2u)  |  A |  S |  D |  F |  G |            |  H |  J |  K |  L |  ; |  '  | ENTER      |
| ⌘V   | CTRL | OPT  |  Z |  X |  C |  V |  B | 🔇 || 🔇 |  N |  M |  , |  . |  / | ⇧R  | ⌘R  | ⌦    |
                            | ⌘ | SPACE | LOWER |         | RAISE | SPACE | ⌫ |
```

Encoder: หมุน = Volume Up/Down, กด = Mute
(หมุนบน layer อื่น = scroll ตาม `enc_scroll`)

### Lower layer (กด thumb ซ้ายในสุด)

- `F1`–`F12`
- `⌘⇧4` = screenshot เลือกพื้นที่, `⌘⇧3` = เต็มจอ, `⌘⇧5` = แถบเครื่องมือ screenshot
- `^SPACE` = สลับ input source (ไทย/อังกฤษ) — ตำแหน่ง Caps Lock
- `⌘←` / `⌘→` = ต้น/ท้ายบรรทัด (แทน Home/End ที่ Mac ไม่มี)
- Arrow keys มุมขวาล่าง

### Raise layer (กด thumb ขวาในสุด)

- `BT1`–`BT5` เลือก profile Bluetooth, `BT CLR` / `BT CLR ALL`
- `⌘SPACE` = Spotlight
- ปุ่มปรับความสว่างจอ, Prev / Play-Pause / Next
- Mouse keys + คลิกซ้าย/กลาง/ขวา

### Adjust layer (กด thumb ซ้ายใน + ขวาใน พร้อมกัน)

- `OUT_USB` / `OUT_BLE` / `OUT_TOG` สลับ output ระหว่างสาย USB กับ Bluetooth
- `sys_reset`, `bootloader`

## Build

Push repo นี้ขึ้น GitHub แล้ว GitHub Actions จะ build ให้อัตโนมัติ (`.github/workflows/build.yml`)

```bash
gh repo create zmk-config-drift-mac --private --source=. --push
```

โหลด artifact `firmware.zip` จากแท็บ Actions จะได้ 5 ไฟล์:

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `drift_left-nice_nano_v2-zmk.uf2` | Production Firmware ครึ่งซ้าย — ตัวที่ใช้พิมพ์จริง |
| `drift_right-nice_nano_v2-zmk.uf2` | Production Firmware ครึ่งขวา |
| `drift_test_left-nice_nano_v2-zmk.uf2` | **Test Firmware** ครึ่งซ้าย — flash เฉพาะตอนตรวจบอร์ด แล้ว flash Production กลับ |
| `drift_test_right-nice_nano_v2-zmk.uf2` | Test Firmware ครึ่งขวา |
| `settings_reset-nice_nano_v2-zmk.uf2` | ล้าง setting เมื่อสองครึ่งไม่คุยกัน |

## Flash

1. ต่อสาย USB-C เข้าครึ่งซ้าย
2. กดปุ่ม reset บน nice!nano **2 ครั้งเร็วๆ** → จะขึ้น drive ชื่อ `NICENANO`
3. ลาก `drift_left-*.uf2` ลง drive → บอร์ด reboot เอง
4. ทำซ้ำกับครึ่งขวาด้วย `drift_right-*.uf2`

ถ้าสองครึ่งไม่คุยกันหลัง flash: flash `settings_reset-*.uf2` ทั้งสองข้างก่อน แล้วค่อย flash firmware จริงใหม่

## จับคู่กับ Mac

1. บน keyboard: กด RAISE ค้าง แล้วกด `BT CLR` เพื่อล้าง profile เดิม
2. กด `BT1` (หรือ profile ที่ว่าง)
3. macOS → System Settings → Bluetooth → เลือก **Drift V3**
4. ถ้า Keyboard Setup Assistant เด้งขึ้นมาถามให้กดปุ่มข้าง Shift ซ้าย — ปิดไปแล้วเลือก **ANSI** เองที่ System Settings → Keyboard → Change Keyboard Type

## เว็บคู่มือ + ตัวตรวจบอร์ด

https://pigrabbboy.github.io/zmk-config-drift-mac/

หน้าเดียว สองโหมด:

**โหมดคู่มือ** — รูปคีย์บอร์ดวาดจากพิกัดจริงใน `config/drift.json` แสดง legend คู่ EN + ไทย (Kedmanee)
ครบทั้ง 4 layer ซึ่ง keymap-editor ของ ZMK แสดงให้ไม่ได้ กด Shift ค้างเพื่อดู legend ชั้นที่สอง
กดปุ่มจริงแล้วปุ่มบนรูปสว่าง แต่ไม่นับคะแนน เพราะหน้าเว็บไม่มีทางรู้ว่า ZMK อยู่ layer ไหน

**โหมดทดสอบบอร์ด** — ไล่ให้ครบทั้ง 70 สวิตช์ + หมุน encoder 4 ทิศ นับแยกซ้าย/ขวา
(ครึ่งขวาคุยผ่านครึ่งซ้าย ถ้าหลุดจะตายทั้งครึ่งพร้อมกัน — ตัวเลขแยกทำให้เห็นทันที)
จับปุ่มเด้ง (chatter) ด้วย และจำผลไว้ใน localStorage ข้าม refresh

โหมดนี้**ต้อง flash Test Firmware ก่อน**: Production Firmware มี 4 ช่องที่ browser มองไม่เห็นเลย
(`&kp C_MUTE` ×2, `&mo LOWER`, `&mo RAISE`) และ 3 คู่ที่ส่งค่าเหมือนกันจนแยกไม่ออก
(`SPACE`, `BSPC`, `C_MUTE`) — `SPACE` คร่อมสองครึ่งบอร์ดด้วย เหตุผลเต็มอยู่ใน
[ADR-0001](./docs/adr/0001-separate-test-firmware.md)

ขั้นตอน: flash `drift_test_left` / `drift_test_right` → เปิดเว็บโหมดทดสอบ → กดจนครบ →
**flash `drift_left` / `drift_right` กลับ**

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
- `&kp CAPS` ยังอยู่ตำแหน่งเดิม ถ้าจะใช้สลับภาษาแบบ macOS ให้ไปตั้งที่ System Settings → Keyboard → Input Sources → "Use Caps Lock key to switch..."
- ZMK Studio (แก้ keymap สดโดยไม่ต้อง build) ยังไม่เปิด — ต้องประกาศ `zmk,physical-layout` ใน `drift.dtsi` ก่อน ซึ่ง upstream comment ไว้อยู่
