# A separate Test Firmware, not a cleverer web page

To answer "is every switch on this board still working", a browser has to see a distinct event for each of the 70 Binding Slots. Under the Production Firmware it cannot: `&mo LOWER` and `&mo RAISE` emit no HID report at all, `&kp C_MUTE` (both encoder pushes) and the encoder rotations are consumer-page codes the browser never receives, and `&kp SPACE`, `&kp BSPC` and `&kp C_MUTE` each sit on two Binding Slots that produce byte-identical events. We therefore build a second firmware — same shields, `-DKEYMAP_FILE` pointed at a generated `config/drift_test.keymap` — in which all 70 slots plus all four encoder directions emit a distinct plain keycode. Testing means flashing it, running the page to 74/74, and flashing the Production Firmware back.

## Considered options

Four ways to keep a single firmware were worked through and rejected together:

- **Mark both slots when a duplicated keycode arrives.** Cheapest, and a lie. `SPACE` sits on the left thumb *and* the right thumb, so one press would credit both Halves — destroying the per-Half count that exists precisely to expose a dead right Half.
- **Move the invisible slots to a manual "I confirm this works" checklist.** Replaces evidence with testimony for the encoders and layer keys, which are among the most-used and most failure-prone parts of the board.
- **Prove `&mo LOWER` indirectly** by holding it and pressing `1`: `base` has no F-keys, so an `F1` event can only have come from the lower Layer. Genuinely works for `lower`, but `raise` is almost entirely `&trans` and invisible codes, leaving only mouse behaviours and a `contextmenu` heuristic that is hard to separate from a real right-click.
- **Add `F13`–`F24` to the `raise` Layer** so it is easy to test. Changes the keyboard people type on in order to suit the tool that inspects it.

Each of these is a workaround for one symptom of the same cause. Swapping the firmware removes the cause, and all four symptoms with it.

## Consequences

Checking the board costs two flashes and a re-pair rather than opening a page — acceptable for something done when a switch is suspected, not daily. The Test Firmware must never be the one left on the board, so the page says so in the mode that requires it. Both firmwares and the web page's key data are emitted by one generator from `config/drift.json`, because a hand-maintained Test Firmware that drifts from the page would report healthy switches as dead — worse than having no page at all.

The keycode set deliberately excludes `F1`–`F12`: on macOS those are media keys unless "Use F1, F2, etc. keys as standard function keys" is on, and a tool that reports twelve dead switches because of a system preference fails in the most dangerous direction. Avoiding them leaves 75 usable codes for 74 slots.
