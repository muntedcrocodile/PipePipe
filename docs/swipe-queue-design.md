# Swipe-to-queue and persistent queue design

Status: shared understanding confirmed at Q59; design interview complete. A subsequent user instruction authorized publication and implementation in a new thread. The consolidated behavior is in [the specification](swipe-queue-spec.md) and the published [implementation issue](https://github.com/muntedcrocodile/PipePipe/issues/1); this document retains the interview record and research evidence.

## Agreed decisions

- Q1: Prioritize a usable build in the user's fork even if upstream declines persistence. Keep swipe support and persistence separately reviewable in incremental commits.
- Q2: Deliver swipe support and persistence together. A swipe-only build is not the agreed first usable milestone.
- Q3: The exposed queue playlist edits the same queue as the player, including order and membership. See [ADR 0001](adr/0001-one-queue-with-a-playlist-view.md).
- Q4: Preserve order, current video occurrence and playback timestamp across closing the player, force-stop and reboot. Restoration waits for an explicit Play action.
- Q5: Remove each finished entry. The queue eventually becomes empty rather than retaining played entries for replay.
- Q6: Allow duplicate video occurrences; each enqueue creates a distinct entry.
- Q7: Removing the current entry immediately advances to the following entry, preserving playing/paused state. Stop if there is no following entry.
- Q8: A normal video tap adds the video to the start of the queue and begins playback. It does not replace the existing queue. Q55 settles entry-point scope.
- Q9: Swiping into an existing paused queue, including one whose player is closed, preserves the paused state. Starting immediately applies only when no queue exists. Q26 defines add-to-start as play next.
- Q10: The first swipe with no queue opens the full video player and starts playback.
- Q11: Newly enqueued videos follow the existing resume-history preference. This is distinct from restoring the persistent queue's own playback position.
- Q12: Tapping X while A plays in [A, B, C] produces [X, A, B, C]. Preserve interrupted A immediately after X with its playback progress.
- Q13: Manual Next removes the skipped entry from the queue playlist. The rendered player queue must additionally show recent global watch history, allowing Previous to navigate back. See Q19–Q21 and Q28–Q29 for refinements.
- Q14: Disable both repeat-one and repeat-all for this queue.
- Q15: Tapping a row in the player queue or queue playlist selects the existing occurrence without inserting a duplicate. Q53 supersedes the initial no-reordering detail: move that occurrence to the front.
- Q16: Play all and Play from here prepend the requested sequence and start it, preserving the old queue afterward. For example [A, B, C] plus Play all on [X, Y] becomes [X, Y, A, B, C].
- Q17: Stop when the requested queue becomes empty; do not add automatic recommendations.
- Q18: Use one persistent queue owner with playback state and a special editable playlist view, rather than independent playlist and player copies. See [ADR 0001](adr/0001-one-queue-with-a-playlist-view.md).
- Q19: Show the last 20 history entries by default, with a configurable limit including 0 to hide them.
- Q20: Previous brings a history entry back into active queue membership while retaining the interrupted entry and its progress. From current C with D next and history A then B, successive Previous actions produce [B, C, D], then [A, B, C, D]. Backward traversal must not bounce between freshly replayed items.
- Q21: Originally requested exact finished-versus-skipped replay behavior; superseded by Q33's per-video resume fallback after selecting merged global history.
- Q22: New persistent Queue mode and tap-to-prepend behavior are opt-in. Swipe enablement and configuration are separate controls.
- Q23: Swipe support covers video list rows only, preserving card/grid layouts without adding swipe support or forcing list view.
- Q24: Left/right always mean physical directions, and each direction has a configurable action. Defaults: right adds to the end, left adds to the start (play next per Q26). Q38 and Q41 settle available choices.
- Q25: With swipe-to-enqueue enabled, replace old local-playlist swipe actions entirely. A disabled direction must not fall through to delete. Inside the player queue and queue playlist, swipes remove entries instead of enqueueing them again.
- Q26: Add-to-start means play next: while A plays with B next, swiping X produces [A, X, B], without interrupting A. With no queue, either enqueue swipe starts X in the full player.
- Q27: Include unrelated video actions in configurable left/right actions, rather than limiting the choices to queue operations. Q38–Q41 settle the action set and applicability rules.
- Q28: Use recent global watch-history videos for backward navigation, accepting merged repeated occurrences. Do not build the proposed persistent per-occurrence playback trail.
- Q29: Previous always selects a prior history video when available, regardless of elapsed playback time; otherwise restart the current video. Apply this to external media controls too.
- Q30: Feedback only for additions/removals; no Undo.
- Q31: The special queue playlist is visible by default after Queue mode is enabled. A visibility setting can hide it without removing the queue or playback state.
- Q32: Use a temporary stable snapshot of recent global history, excluding the current video, for backward traversal. Do not reorder it after each Previous; refresh on normal forward playback or a new playback selection. Never create a persistent occurrence trail.
- Q33: History replay follows existing per-video resume state and resume preference, restarting videos considered finished by existing detection. This supersedes Q21's unavailable occurrence-specific distinction.
- Q34: Disabling watch-history recording hides the player history section and disables history-backed Previous. Keep unfinished queue membership and its own progress; do not delete existing global history unless explicitly requested.
- Q35: History deletion immediately invalidates relevant backward-navigation items. Deleting global history or playback positions also clears applicable saved queue progress without removing queued videos. Do not seek or stop an already playing video; later playback can save progress again under normal recording rules.
- Q36: Playback/network/extraction failure retains the affected entry and stops for retry or explicit user skip/removal. Do not consume it as finished or silently advance.
- Q37: Apply rapid gestures in gesture order, not metadata-fetch completion order. Repeated Play next actions insert directly after the current entry, so the latest successful action is next. Failed additions receive failure feedback, never false success.
- Q38: Swipe choices: Do nothing, Add to queue end, Play next, Play in background, Play in popup, Add to playlist, Download, Share, Open in browser, Mark watched, Open channel, Filter channel. Reuse normal dialogs; exclude currently hidden Kodi.
- Q39: If an action is unavailable, explain why and leave the item unchanged. Preserve existing permission prompts and prerequisites; never silently substitute another action.
- Q40: Background/popup actions prepend the selected video and immediately play it in that mode, preserving old queue membership and interrupted-entry progress. Player-mode switches also preserve the existing queue.
- Q41: Also offer Remove from this playlist and Delete from watch history, only on their corresponding source screens and with confirmation. Queue-entry swipe removal remains immediate, not a source-deletion fallback.
- Q42: Play from here adds only the selected source suffix. Source [W, X, Y, Z], starting at Y, contributes [Y, Z].
- Q43: Retain lazy remote pagination and sequence boundaries ahead of the preserved old queue, including across restart. Page-fetch failure pauses for retry rather than bypassing missing source entries. Accept that remote sources can change between fetches.
- Q44: Queue mode uses one-shot Shuffle upcoming: preserve current video, reorder upcoming membership consistently in both views and persist the resulting order. No shuffle toggle or Unshuffle. Later insertions respect their requested positions. Q47 settles unloaded remote pages.
- Q45: Initially accepted wrapping to earlier unfinished entries after reaching the tail. Superseded by Q53/Q56: current entry stays first, eliminating an out-of-order cursor and the need to wrap.
- Q46: The user questioned why A/B would remain queued while C plays. Clarified that this was a direct jump rather than sequential playback. Resolved by Q53: selecting C moves it to the front and keeps unfinished A/B behind it.
- Q47: Before Shuffle upcoming, finish loading pending remote pages; allow cancellation. Cancellation or fetch failure leaves the existing order intact.
- Q48: Mode switching is rare and ordinary temporary queues may be discarded. Disabling persistent Queue mode must hide and retain the persistent queue for re-enablement. Do not add a saved-versus-live merge prompt. Q54 settles playback-stop and adoption behavior.
- Q49: Swipe controls work independently of Queue mode using the ordinary nonpersistent queue when it is off. Tap-to-prepend, consumption, persistent playlist and history-backed Previous remain Queue-mode features. First enqueue swipe still opens the full player.
- Q50: Preserve the special playlist's identity. Provide confirmed Clear queue: stop playback, remove unfinished entries and pending source pages, preserve global watch history. Hiding is separate and non-destructive.
- Q51: App backups include membership, duplicate identities, current position, pending remote sources and settings. Import uses existing database-overwrite confirmation, replaces the device queue and restores paused.
- Q52: Save acknowledged membership/order edits durably before success feedback. Checkpoint progress about every five seconds and on pause, seek and transitions. Abrupt termination may lose a few seconds of timestamp progress, but not an acknowledged edit.
- Q53: Current entry stays at the front. Selecting existing C in [A, B, C, D] moves that occurrence to the front, producing [C, A, B, D], without duplicating C or treating unfinished A/B as watched. Supersedes Q15's no-reordering detail and Q45's wrapping.
- Q54: Stop the current player on either mode switch. Disabling saves/hides the persistent queue and leaves ordinary mode empty. Re-enabling discards the ordinary queue and restores retained persistent state paused, or starts empty if none exists. No adoption, merge or queue-choice prompt.
- Q55: Preserve-and-prepend applies consistently to explicit play-now entry points: video rows, detail Play, external playback links, background/popup actions. Non-playback actions do not enqueue.
- Q56: Current entry stays first; drag reordering applies only to upcoming entries. History rows are outside editable membership. Select an entry to play it immediately rather than dragging it ahead of current.
- Q57: Save queue as playlist creates a complete independent copy of unfinished video membership only, excluding displayed history and playback positions. Load pending source pages before saving; cancellation/error leaves the live queue unchanged.
- Q58: New swipe controls initially disabled on fresh installs and upgrades until explicitly enabled. Separate from opt-in Queue mode; once enabled, right defaults to Add to queue end and left to Play next.
- Q59: User confirmed the consolidated specification matches the intended design and completed the interview. This confirms shared understanding, not authorization to start implementation.

## Requested scope carried forward

These requests come from the earlier project thread; details and acceptance criteria are still being refined.

- Swipe-to-enqueue across What's New, recommendations, search/channel results, playlists, history, and other video lists.
- Independently configurable physical left/right swipe actions (Q24 refines the original left/right/both request).
- Create a queue and start playback when none exists.
- Persist the queue and allow resumption and management through an optionally exposed local playlist.
- Use GitHub account `muntedcrocodile` for repository operations that require an account.

## Decision tree

- Delivery: fork first; one complete feature delivery; incremental reviewable commits (agreed).
- Queue identity: one queue with two editable views (agreed).
  - Lifecycle: restore paused, consume finished entries, allow duplicates, immediate current-entry removal (agreed).
    - Preserve interrupted entries; consume manual skips; disable repeat and automatic recommendations (agreed).
    - Recent global watch history supports Previous, defaults to 20 entries, and replay reintroduces entries to active membership. Always go backward when available; no persistent occurrence trail. Stable transient traversal, per-video resume fallback and privacy/deletion rules (agreed).
  - Playback: swipes insert per configured action; taps insert at front and play; first swipe opens full player; follow resume-history preference (agreed).
    - Queue-row taps select occurrences; play-all prepends a sequence; from-here adds only its suffix; background/popup prepend and preserve the queue (agreed).
    - Load all pending source pages before one-shot shuffle; cancellation/error preserves order (agreed).
    - Current always first; selection moves an occurrence to the front; all explicit playback entry points preserve-and-prepend (agreed).
  - Persistent queue ownership, durable acknowledged edits, roughly five-second progress checkpoints, backup inclusion and paused restoration (agreed).
  - Queue-playlist visible by default, with non-destructive hiding and confirmed Clear queue; identity is not deletable. Reorder upcoming entries; save independent complete ordinary-playlist copies (agreed).
- Swipe behavior: separate control initially disabled; list rows only; configurable physical directions; right defaults append and left defaults add-to-start; override legacy playlist swipes when enabled; queue swipes remove (agreed).
  - Add-to-start means play next; feedback without Undo; unrelated actions are in scope (agreed).
  - Action set, unavailable-action feedback, confirmed context-specific source deletions and independent operation with Queue mode off (agreed).
- Mode transitions stop playback, retain/hide persistent state and discard temporary queues; no adoption or merge prompt (agreed).
- Playback failures retain the entry and stop for retry; gestures apply in action order (agreed). Consolidated acceptance criteria await final review.
- Final shared-understanding review (confirmed at Q59; interview complete).

## Evidence

A read-only delegated investigation inspected the root checkout at `7349b0f` and client submodule at `c2a166f` (v5.4.0). Historical upstream findings in the earlier thread have not been refreshed in this interview.

- Shared enqueue starts background audio when no player exists; appending to an existing queue preserves its playback readiness. See client `NavigationHelper.java:196` and `PlayerStartController.kt:41`.
- Queue-to-playlist saving captures loaded videos, not current occurrence, playback timestamp or full queue state. See client `PlayerClickController.kt:167`.
- Ordinary playlist membership permits duplicate videos but lacks stable queue-entry identity and a playback cursor. See client `PlaylistStreamEntity.java:21` and `PlayQueue.java:59`.
- Playlist editing currently delays writes and replaces whole membership; sharing it with live playback needs coordinated updates. See client `LocalPlaylistFragment.java:82,1114`.
- Gesture support spans multiple adapter families. Existing local-playlist right swipes and player queue removal gestures need explicit interaction rules.
- No durable whole-queue restoration was found in the inspected playback paths. Stream progress persistence already exists separately.

A targeted read-only investigation of watch-history and Previous-button behavior completed following Q13. Q28 subsequently selected global-history reuse despite its limitations.

- Existing watch history merges repeated visits to a video, and records manually marked-as-watched items as well as playback visits. It cannot reconstruct an ordered occurrence trail. See client `HistoryRecordManager.java:141` and `StreamHistoryEntity.java:18`.
- Global resume state is per video; existing queue recovery state is per entry UUID. See client `StreamStateEntity.java:14` and `PlayQueue.java:59,455`.
- Previous currently restarts the current video after five seconds, or selects the prior queue index otherwise. Media-session Previous uses the same transport method. See client `PlayerTransportController.kt:87`.
- Queue navigation can wrap even with repeat off. Stop-on-empty and disabled repeat must be enforced across transport and external controls, not only visible buttons. See client `PlayQueue.java:155` and `PlayerMediaSession.java:106`.
- History recording, history deletion and position deletion have existing user-facing controls. Any new playback trail must have explicit behavior for these controls, including unfinished queue positions. See client `HistorySettingsFragment.java:124,139`.

Rejected alternative (Q28): a bounded persistent occurrence trail would preserve exact playback chronology, but the user prefers existing global watch history despite merged occurrences. Do not add history to active queue membership merely to display it. A stable transient traversal snapshot may still be necessary to prevent backward-navigation loops; it is not a new persistent trail.

## Interview completion

Q1–Q59 are recorded; superseded choices are identified above. A read-only consistency audit found no material contradictions between the consolidated spec, this record, glossary and ADRs. The user accepted Q59, confirming shared understanding and completing the design interview. No interview questions remain pending. This confirmation does not authorize implementation.

Subsequently, the user explicitly requested using the to-spec skill to publish to the `muntedcrocodile` fork and launch a new thread using the implementation skill. Published [PipePipe#1](https://github.com/muntedcrocodile/PipePipe/issues/1) as `muntedcrocodile`, with the `ready-for-agent` label. The issue tracker was enabled on the existing fork to fulfill that request. This later instruction authorizes implementation; it does not alter the confirmed product decisions.

## Action and integration evidence

A third local read-only investigation inventoried existing action handlers and playback integration. These findings do not settle the associated product choices.

- `StreamDialogDefaultEntry.java:52` provides enqueue/end, enqueue-next, background, popup, playlist chooser, download dialog, share, browser, mark watched, channel navigation and channel-filter handlers. Kodi is currently hidden by `KoreUtils.java:25`. Delete and several other enum entries need screen-specific handlers.
- Available actions vary by metadata, player readiness and video type. Popup needs overlay permission and is not offered for pure audio; mark-watched requires history and excludes live streams. Sparse feed actions may need metadata extraction. See `InfoItemDialog.java:271` and `SparseItemUtil.java:51`.
- Default background/popup item actions start a new single-video queue, replacing the old session. They cannot be reused unchanged under accepted queue-preservation rules. Actual player-mode switching does carry the existing queue. See `NavigationHelper.java:156`, `PlayerStartController.kt:193` and `PlayQueueActivity.java:134`.
- Remote Play all carries a next-page token, but enqueue copies only loaded streams. Preserving the full remote sequence ahead of an old queue requires retaining pagination ownership and an insertion boundary, not merely prepending currently loaded rows. See `PlaylistFragment.java:379` and `AbstractInfoPlayQueue.java:95`.
- Existing Play from here retains preceding loaded entries behind its selected index; Q42 deliberately chooses suffix-only behavior instead.
- Shuffle changes membership order and keeps an original-order backup. Persistence must define which order survives restart and how newly added items behave. See `PlayQueue.java:511,323`.
- Manual export copies the entire `newpipe.db` and default preferences; import replaces the database and restarts. Queue data stored there would be included unless explicitly treated differently. See `BackupSettingsFragment.java:205` and `ContentSettingsManager.kt:26`.

Q47 resolves lazy-pagination versus shuffle by loading pending pages before shuffling. Q49–Q52 resolve independent swipe operation, Clear queue, backup inclusion and durability. Q53–Q58 settle the remaining product boundaries and defaults; Q59 confirms the full design.
