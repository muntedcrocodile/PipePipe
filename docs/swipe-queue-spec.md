# Configurable video swipes and a persistent consuming queue

Status: confirmed by the user at Q59; design interview complete. Subsequently published as [muntedcrocodile/PipePipe#1](https://github.com/muntedcrocodile/PipePipe/issues/1), with implementation authorized by the user's request to launch a new implementation thread.

Deliver the complete feature in the user's fork, with independently reviewable incremental commits for gesture support and persistent queue behavior. Upstream acceptance is desirable but does not limit the fork's feature set. The [interview record](swipe-queue-design.md) preserves decisions Q1–Q59 and code evidence; [the glossary](../GLOSSARY.md) defines the terms.

## Settings and scope

Updated by the user after delivery: persistent Queue mode and the new video-row swipe controls default to enabled. This supersedes the original interview and issue requirements for initially disabled controls. Missing settings in older imported backups use these enabled defaults; explicit saved/imported disabled values remain respected. Swipe enablement and physical left/right actions are separately configurable and work even when Queue mode is off. Right defaults to Add to queue end; left defaults to Play next. Physical directions never mirror for language.

Apply swipes to video list rows in What's New/feed, recommendations, search, channel results, remote/local playlists and history, including rows hosted in tabs. Preserve card/grid layouts without adding swipe support or forcing list layout. Non-video tiles retain existing behavior.

Swipe actions are Do nothing, Add to queue end, Play next, Play in background, Play in popup, Add to playlist, Download, Share, Open in browser, Mark watched, Open channel, and Filter channel. Also offer explicitly named Remove from this playlist and Delete from watch history on their respective source screens, with confirmation. Reuse normal action dialogs and permission prerequisites; explain unavailable actions without substituting another action. Kodi is excluded.

When enabled, the new source-row swipe configuration replaces old local-playlist swipe behavior entirely; a disabled direction must not fall through to deletion. Inside the player queue and special queue playlist, swipes remove the selected occurrence rather than run source-row actions. Queue edits have success/failure feedback but no Undo.

## One unfinished queue

One persistent owner coordinates queue membership, order, stable duplicate-occurrence identities, pending remote sources and per-entry playback progress. The special queue playlist is an editable view of the same queue, not a separate ordinary-playlist snapshot. See [ADR 0001](adr/0001-one-queue-with-a-playlist-view.md).

The current entry is always first. Drag reordering affects upcoming entries only. Tapping an existing queued occurrence moves it to the front and plays it without creating a duplicate. For example, selecting C in [A, B, C, D] produces [C, A, B, D]; A and B remain unfinished, not falsely watched. See [ADR 0003](adr/0003-current-entry-first.md).

Natural completion and manual Next remove the current occurrence and advance. Explicitly removing current also advances immediately while retaining playing/paused state. Removing an upcoming occurrence does not change the current one. Stop when empty. Both repeat modes and automatic recommendation enqueueing are disabled in Queue mode, including external-control paths.

## Insertion and playback

With current A in [A, B, C]:

- Add to end X gives [A, B, C, X] without interrupting A.
- Play next X gives [A, X, B, C] without interrupting A.
- An explicit play-now selection X gives [X, A, B, C] and plays X, preserving A's progress.
- Play all [X, Y] gives [X, Y, A, B, C] and plays X.

Apply play-now preservation consistently to video rows, detail-page Play, external playback links and explicit background/popup actions. The latter choose the requested player mode while retaining the old queue. Switching the current player between full video, background and popup also retains queue and progress. Sharing, downloading and other non-playback actions do not enqueue.

Queue-building swipes preserve an existing paused/closed player's paused state. If no unfinished queue exists, either enqueue action starts the inserted video in the full player. Newly added videos follow the existing resume-history preference; interrupted duplicate occurrences retain their own queue progress.

Rapid additions execute in gesture order despite metadata-fetch timing. Repeated Play next actions each insert directly after current, so the last successful gesture becomes next. Failed additions receive failure feedback rather than false success.

## History and Previous

The player queue view additionally shows recent global watch-history videos, default 20 with configurable depth including 0. These rows are not editable queue membership until chosen for replay. Global history merges repeated plays, so this feature does not promise exact occurrence chronology or distinct skipped/finished occurrence records. There is no separate persistent playback trail. See [ADR 0002](adr/0002-reuse-global-watch-history.md).

Previous always chooses a prior history video when available, even after five seconds of current playback; otherwise it restarts current. The rule also applies to headset, notification and media-session controls. Going backward reintroduces the selected history video at the queue head, retaining the interrupted entry behind it. With history A then B and active [C, D], successive Previous actions produce [B, C, D] then [A, B, C, D].

Use a temporary stable recent-history snapshot excluding the current video, so recency updates caused by replay do not create a backward-navigation loop. Refresh on normal forward playback or a new non-history playback selection, rather than each Previous press. History replay follows global per-video resume state, the resume preference and existing finished detection.

Disabling watch-history recording hides this history section and disables history-backed Previous; unfinished membership and its own progress remain persistent. Deleting relevant global history immediately invalidates displayed/backward snapshot items. History/position deletion also clears applicable saved queue positions while retaining membership/order. Do not seek or stop an already playing video; subsequent playback may save progress again under normal rules.

## Source sequences, shuffle and saved copies

Play from here contributes only the selected source suffix. Remote batches retain lazy pagination and a boundary ahead of the old queue, including across restart. Later source pages must not append after the preserved old queue. Remote sources may change between fetches. A page failure pauses for retry rather than bypassing missing items.

Shuffle upcoming is a one-time persistent reorder, preserving current and reflected in both views. There is no shuffle toggle, original-order backup or Unshuffle in this mode. Fetch remaining remote pages before shuffling; allow cancellation. A failed/cancelled shuffle leaves the prior order intact. Later queue edits respect their requested insertion positions.

Save queue as playlist creates an independent ordinary-playlist copy of all unfinished videos, excluding displayed history and playback positions. Fetch pending source pages first. Cancellation/error leaves the live queue unchanged. Ordinary saved copies do not consume themselves when the persistent queue advances.

## Visibility, mode changes and clearing

The special queue playlist is visible by default in Queue mode and can be hidden without losing membership/progress. Its identity is not deletable as an ordinary playlist. Confirmed Clear queue stops playback and removes entries and pending source pages, leaving global history intact.

Either mode switch stops the current player. Disabling saves and hides the persistent queue and leaves ordinary mode empty. Enabling discards any ordinary temporary queue and restores saved persistent state paused, or begins empty if none exists. No adoption, merge or queue-choice prompt. While Queue mode is off, swipe actions use the ordinary nonpersistent player queue; Queue-mode tap semantics, consumption and history-backed Previous do not apply.

## Durability and failure

Save acknowledged membership/order edits durably before showing success. Checkpoint playback progress about every five seconds and on pause, seek and transitions. Closing the player, force-stop and reboot retain queue state; restoration waits for Play. Abrupt termination can lose a few seconds of playback progress but must not lose an acknowledged edit.

Playback, extraction and network errors retain the affected entry and stop for explicit retry, skip or removal. They do not count as completion. Avoid independent playlist/player writers that can overwrite each other's edits.

Normal app backups include membership, occurrence identities, progress, pending sources and queue/swipe preferences. Import uses the existing database-overwrite confirmation, replaces the device queue with backup state and restores paused.

## Acceptance review

Verification must cover the behavior above, including:

1. Both directions and custom actions on each supported list family; cards/grids unchanged; no accidental source deletion through disabled directions.
2. Exact duplicate occurrence edits, paused enqueue, first enqueue full-player startup, interrupted progress, row selection and upcoming-only reorder.
3. Consumption on completion/Next, immediate removal, stop-on-empty, repeat suppression and queue preservation across player modes and external playback/control paths.
4. Stable backward traversal of merged global history, replay progress fallback, disabled history, deletion invalidation and depth 0.
5. Lazy source boundaries across new insertions/restart, failed page retry, cancelled shuffle and complete ordinary-playlist copies.
6. Concurrent playlist/player edits and rapid gestures; no stale overwrite or false durable-success feedback.
7. Process-death/reboot restoration, progress checkpoints, mode switches, Clear queue and backup replacement, all with the agreed paused restoration behavior.
8. Relevant automated tests and an Android build, plus on-device checks for gestures, system media controls and player modes. Report unavailable checks explicitly.

## Final confirmation

The user confirmed this specification as the shared understanding at Q59, completing the interview. Product decisions Q1–Q58 are captured; the user subsequently changed the initial Queue-mode and video-row swipe defaults to enabled, as recorded above. A read-only consistency audit found no material contradictions between this specification, the interview record, glossary and ADRs. Gesture thresholds, concrete UI presentation and internal class/schema design belong to implementation; they must preserve these behaviors. Q59 itself confirmed only the design; a subsequent user instruction authorized publication and launching implementation in a new thread using the implementation skill. The published issue is the self-contained implementation brief and includes user stories, architectural decisions, test seams, acceptance coverage and exclusions.
