# Playback queue

Language for the swipe-to-queue and persistent-queue feature.

## Language

**Queue**:
The ordered collection of unfinished videos selected for playback, with the current entry first. Entries leave the queue when finished, skipped with Next, or explicitly removed.
_Avoid_: Queue snapshot, queue copy

**Queue playlist**:
The optional playlist view of the same queue. Edits to its order or membership are edits to the queue itself.
_Avoid_: Saved queue copy, exported queue

**Queue entry**:
One occurrence of a video in the queue. The same video can have multiple distinct entries.
_Avoid_: Unique queued video

**Current entry**:
The first queue entry, selected for playback or resumption. A restored queue retains its current entry even while playback is paused.

**Upcoming entries**:
The unfinished queue entries after the current entry, in their intended playback order.

**Player queue view**:
The player's presentation of the current queue together with recent global watch-history videos available for backward navigation. Displaying a history video does not make it a member of the queue playlist; choosing to replay it adds a queue entry.
_Avoid_: Queue playlist (when referring to the combined history and queue view)

**Play next**:
Insertion immediately after the current queue entry without interrupting it. When the queue is empty, it starts playback of the inserted video.
_Avoid_: Add to start (when it could imply interrupting the current video)
