---
status: accepted
---

# `event.code` decides Proven; `event.key` is only displayed

This page exists because ZMK's keymap editor cannot show Thai legends, so the obvious rule would be "a Binding Slot is Proven when it produces the Thai character we expect". We do the opposite: `KeyboardEvent.code` — the physical position, unaffected by the active input source — is what marks a slot Proven, and `event.key` is shown beside it as information only.

`event.key` reports whatever the current macOS input source produces. Judging on it would fail every slot the moment someone tests in English, or after any app steals focus and switches the source mid-run — reporting a healthy board as broken. Displaying it still delivers what the page was built for: seeing `ฟ` actually come out of the `A` position is the proof the keymap editor could never give, and the page separately warns when no Thai output has been seen at all, rather than letting someone finish all 74 slots before discovering the input source was wrong.
