# 0004 — Plain keys stay plain: no hold-taps on letters or Space, no combos

**Status**: accepted, 2026-09-13

## Context

Home-row mods, layer-tap on Space and chord combos are the usual way a split
board sheds its modifier keys. Three facts about this board argued against all
three:

- The board types **Thai** (Kedmanee), where roughly half the characters sit on
  the shifted layer of a key, so Shift is held constantly and letter keys are
  pressed in fast overlapping rolls. A hold-tap on a home-row letter turns those
  rolls into modifiers and mistyped Thai; a layer-tap on Space misfires on the
  long Space holds Thai does not have but English and code do.
- The board is also used for **games**, which need every letter to be a letter
  the instant it is pressed, with no tapping-term.
- The board-check page, its generator and the Test Firmware model the keyboard
  as **70 Binding Slots** (see `CONTEXT.md`). A combo is not a slot: it is a
  relation between slots, with its own timing, and neither the page nor the
  Test Firmware has any place to put it.

This board also does not lack modifiers: it has a 2u Shift, Control and Option
in a dedicated column, Command on a thumb, and three thumb keys per side.

## Decision

Every key on `base` is a plain `&kp`. Layers are reached only by holding a
dedicated thumb key (`&mo`) or by an explicit toggle on `adjust` (`&tog`). No
hold-tap sits on a letter, digit, punctuation or Space slot. No combos are
defined.

Word and line movement, text selection and window tiling are obtained by
holding the **real** Option, Command, Shift and Control keys over the plain
arrows on `nav`; the unused `nav` slots are `&trans` precisely so those chords
reach the host.

## Consequences

- Thai typing and games never meet a tapping-term. Nothing about typing speed
  or rhythm changes what a key does.
- The page's slot model, its glossary and the Test Firmware need no new concept.
- Modifier reach is what the physical layout gives — the trade-off accepted.
  `caps_word` on `nav` covers the one case (ALL_CAPS identifiers) where a held
  Shift is genuinely awkward.
- Revisiting this means revisiting the page model too. Combos in particular
  would need their own rendering and their own way of being proven on a real
  board; that work is the price, and it is written here so it is not paid by
  accident.
