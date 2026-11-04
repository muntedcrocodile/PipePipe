# One queue with an editable playlist view

The persistent queue and the exposed queue playlist represent the same collection, rather than independent copies. One persistent queue owner stores playback state and coordinates changes from both views, so playlist edits cannot overwrite independent player edits. The playlist is a special editable view of that queue rather than a separately saved ordinary playlist.

The queue retains unfinished entries, allows duplicate occurrences, and removes finished entries. Removing the current entry advances immediately while preserving playing/paused state; restoration retains the current occurrence and timestamp but waits for Play. A plain saved list of video identities is therefore insufficient to restore this queue.

Manual Next also consumes an entry; both repeat modes and automatic recommendations are disabled. The player queue view additionally presents recent global watch history for Previous navigation, while the queue playlist contains only unfinished entries. See [ADR 0002](0002-reuse-global-watch-history.md) for history ownership and [ADR 0003](0003-current-entry-first.md) for ordering.
