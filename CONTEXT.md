# Drift V3 Keymap & Board Check

The ZMK keymap for a Drift V3 split keyboard used on macOS, plus a web page that renders that keymap with Thai legends and proves every switch on the board still works.

## Language

### The board

**Binding Slot**:
One of the 70 positions in the keymap, ordered exactly as `config/drift.json` lists them. Not "key" — one slot is one physical switch, but its legend and its function both change per Layer.
_Avoid_: key, keypos, button

**Half**:
The left or right side of the board, 35 Binding Slots each. The unit that fails as a whole: a Half reaches the host only through the Dongle, so one lost link kills all 35 of its slots at once.
_Avoid_: side, board, split

**Dongle**:
The third nice!nano, in a dock, that both Halves connect to and that alone talks to the Mac. It is the central: it holds the keymap, so it is the only device a keymap change is flashed to.
_Avoid_: receiver, hub, dock

**Layer**:
One complete assignment of behaviours across all 70 Binding Slots. This keymap has four: `base`, `lower`, `raise`, `adjust`.

**Legend Pair**:
The English and Thai characters shown together on one Binding Slot, mirroring how the physical keycaps are printed. Thai follows the Kedmanee arrangement.
_Avoid_: label, caption

### The two firmwares

**Production Firmware**:
The Dongle build people actually type on, carrying `config/drift.keymap`. Contains behaviours that emit nothing over HID (`&mo`, `&bt`, `&out`) and repeats the same keycode on more than one Binding Slot, so a browser can neither see nor tell apart every switch under it.

**Test Firmware**:
A throwaway Dongle build in which all 70 Binding Slots and all four encoder directions emit a distinct, plain keycode. Flashed only to answer "is this board still fully working", then replaced by the Production Firmware. See [ADR-0001](./docs/adr/0001-separate-test-firmware.md).
_Avoid_: debug firmware, diagnostic mode

### The web page

**Proven**:
A Binding Slot the page has observed a real `KeyboardEvent` for during the current Coverage run. The only thing the page ever treats as evidence — a person's word that a switch works is not recorded anywhere. See [ADR-0002](./docs/adr/0002-event-code-decides-pass-fail.md).
_Avoid_: tested, checked, verified, attested

**Coverage**:
The share of Binding Slots Proven so far in the current run, counted per Half. Only meaningful while the Test Firmware is flashed.

**Chatter**:
A switch that emits more than one non-repeat keydown for a single press. Distinct from a dead switch: it is Proven, and still faulty.
_Avoid_: bounce, double-fire
