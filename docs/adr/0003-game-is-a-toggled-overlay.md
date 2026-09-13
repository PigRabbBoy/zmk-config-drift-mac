# 0003 — `game` is a toggled overlay below the held layers, not a second base

**Status**: accepted, 2026-09-13

## Context

The same board is used for coding on macOS and for games — League of Legends
(QWER, DF, 1–7, Space, Tab, Option for self-cast) and WASD titles from a Steam
library. The two uses want different things from the same slots: typing wants
the outer left thumb to be Command and WASD to be ordinary keys; a game wants
WASD with last-input priority (Timception's `key-press-lip` module) and no
Command anywhere near the thumb, because a stray ⌘Q, ⌘H or ⌘Tab mid-game is
worse than any typo. Everything else — number row, Esc, Tab, Shift, Control,
Option, the F-row on `nav` — is wanted by both.

Two shapes were on the table:

1. A second full base layer switched with `&to`, 70 bindings copied, every later
   keymap change made twice.
2. A toggled overlay (`&tog`) that is `&trans` everywhere it does not differ.

## Decision

`game` is a toggled overlay, layer 1, directly above `base` and **below** every
held layer (`nav` 2, `mouse` 3, `adjust` 4). It binds five slots — W A S D with
the last-input-priority behaviours and the outer left thumb as Option — and is
transparent everywhere else. It is switched on and off from `adjust` + `G`, and
the dongle's OLED shows its name for as long as it is on.

## Consequences

- Holding `nav` or `mouse` inside a game still works, because the held layers
  outrank the overlay; a game gets F1–F12 and Home/End for free.
- The layer number is load-bearing. Renumbering `game` above `nav` would make a
  held `nav` show the game's plain letters instead of F-keys. The order is
  written into the keymap's header comment for that reason.
- A keymap change is made once. The overlay cannot drift from `base` because it
  has nothing of its own to drift.
- Whether a game is on is visible on the OLED, not something to remember. The
  web page cannot follow this layer (every code it emits also exists on `base`)
  and says so.
- The SOCD behaviours live only here; `base` went back to plain `&kp` so that
  typing never meets them.
