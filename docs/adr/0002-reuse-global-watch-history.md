# Reuse global watch history for backward navigation

Use recent global watch-history videos as the source for the player's history section and Previous navigation, accepting that repeated plays are merged and occurrence-specific departure reasons and progress are unavailable. A separate persistent playback-occurrence trail would provide exact chronology, but the user chose reuse of global history instead. Queue membership and unfinished-entry progress remain independently persistent; displaying a history item does not enqueue it until the user chooses to replay it.

Backward traversal uses a temporary stable snapshot excluding the current video, so playback-driven changes to global recency cannot create navigation loops. History replay uses existing per-video resume state and finished detection. Disabling history hides backward items, while history/position deletion invalidates applicable history and saved queue progress without removing unfinished queue membership.
