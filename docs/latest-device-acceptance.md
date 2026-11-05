Latest hotfix: [unavailable-service feed isolation, 127 device tests](feed-service-hotfix-20261105.md). The dated baseline below belongs to its original artifacts.

# Physical-device acceptance — 4 November 2026

## Tested source and artifacts

Client `4746c6286b97e1b765d20c5c28e6d3291d269075` includes upstream `f8aca8529ee010e5aa3ed4d44350bc72d096983c`. Extractor is upstream `28a1a5ee889fadb36a435c43e0bc9483b59bb3bf`. Both upstream heads were fetched again on 4 November before delivery and were unchanged. The root includes upstream `3fd38c6dbdfa1d29c97d9d5b1344836347793ec3`. A merge commit with the same client tree preserves these tested sources.

The Samsung SM-G960F ran Android 17 / API 37, ARM64. Tests used the debug variant, version `5.5.0` / `111004`, with JDK 25.0.2, SDK/build-tools 37 and Gradle 9.5.1. All phone operations used ForkKeeper's exclusive renewable lease and broker.

| Artifact | Package | SHA-256 |
| --- | --- | --- |
| ARM64 debug | `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug` | `9cee9d029168c9e6fc0e2dd0f7aea7f3c9806e8cf1d03b5a22617f85d013b4bd` |
| Instrumentation | `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug.test` | `9fef3ac814c14c364af6bf612cde78c2903a37ebd15798b2b42f45e73f39adf2` |

Debug certificate SHA-256: `bfadb6be9109016e35054c9591542ffc14df0c360eb8d635b595b1716ae043ce`. Exact previous package hashes were checked before updating the owned test installations. Staged APKs were discarded after installation. Official PipePipe and unrelated package data were preserved.

## Automated results

**124/124 instrumentation methods passed in 52.641 seconds**, with zero failures, errors, ignored tests or assumption skips. The terminal bundle contains `OK (124 tests)` and `INSTRUMENTATION_CODE: -1`. **8/8 JVM tests passed** with zero failures/errors/skips. The two lifecycle tests also passed separately before the full run.

Counts in [test-plan order](device-test-plan.md): **41 / 55 / 4 / 4 / 1 / 1 / 1 / 7 / 5 / 3 / 2**. Coverage includes durable Queue edits and duplicate occurrences, checkpoints/history, source boundaries, deferred video opening/cancellation, first enqueue, paused recreation, physical nested refresh gestures, import defaults, kiosk refresh cleanup, manual/background feed routing, and detached/recreated real fragment callbacks.

## Real subscribed-feed refresh

A temporary fixture contained Rick Astley and BBC News subscriptions and four Queue occurrences. The normal app UI and database backup export/import were used; no privileged private-data reads were needed.

1. The refresh icon on What’s New fetched **33 feed entries** and populated visible BBC News videos. Both subscriptions received new `feed_last_updated` values.
2. A physical downward pull starting inside the first clickable video row fetched again **65.8 seconds later**, below the old 300-second threshold. Both timestamps advanced (`65768` and `65773` ms); 33 entries remained. Updated network metadata was visible.
3. Exact exported serialized Queue state was unchanged across these refreshes.

Manual refresh now sends an explicit force flag to bypass the outdated-subscription threshold. Background requests without that flag retain their previous throttling. Kiosk pull refresh was also added; its routing and spinner lifecycle have five passing device regressions. The user’s reported feed was What’s New.

## Queue and playback checks

Physical left/right gestures on the local source playlist showed Enqueued next / Enqueued feedback. The source retained five rows. Queue changed from four to six occurrences in the expected order (D, inserted A, C, A, duplicate A, appended B), retaining existing duplicates. MediaSession remained PAUSED at `158774` ms. Explicit opening produced decoded Big Buck Bunny video and PLAYING state.

Actual portrait-to-landscape rotation retained PAUSED state and the exact `198560` ms position. Original accelerometer/user-rotation settings were restored. Automated retained-ViewModel and real detached/recreated-fragment tests cover the relevant lifecycle boundaries. After force-stop/relaunch, the six expected Queue rows returned and transport stayed PAUSED at `198562` ms (2 ms checkpoint rounding). Clearing the temporary Queue and swiping its first source item started decoded Rick Astley video with PLAYING state, confirming first-enqueue behavior from empty.

## Failure history and scope

The first integrated upstream run crashed after 91 terminal passes because an obsolete sheet layout listener accessed a detached fragment. That run is a failure, preserved privately. Fix `4746c6286` removes callbacks from the observer that registered them and rejects obsolete bindings. The complete 124-test pass above is the corrected candidate.

Earlier nested-gesture fixture failures also occurred with the unguarded control after SwipeRefreshLayout entered its refreshing state. Real-time event dispatch corrected the fixture; guarded and unguarded controls now pass with the original callback assertions. No speculative production gesture change was made.

Historical extensive manual checks belong to their exact earlier artifacts: [31 October report](device-acceptance-20261031.md). They are not attributed to this new build. The current result establishes the tested functional paths on one physical device, not every app path or optimized performance. Per AGENTS.md, a successful debug device pass is sufficient; the optimized release must build and pass package/version/signature/R8 verification, with no separate release-device claim. Release provenance is published in `release-manifest.json` by [the workflow](fork-release.md).

## Restoration and ownership

The original debug-package backup was restored through normal import with settings accepted. Re-export verified the original empty Queue and zero subscriptions, removing the temporary feed/Queue fixtures. Original rotation settings (`accelerometer_rotation=1`, `user_rotation=0`) were verified after restoration. The earlier optimized diagnostic installation had already been restored separately; no official app data was changed.

All three owned diagnostic packages were stopped. Fresh quiescence checks found no matching process/subprocess or active activity and verified stopped package state. Explicit release completed to broker `idle`; the guard exited and removed its private token. A complete bounded final own-UID log capture had no `FATAL EXCEPTION`, `Fatal signal`, `ANR in` or detached-activity exception match. This is a scoped final capture, not a claim about all historical logs.

Private raw results and safe UTC operation receipts are under `/home/user/.local/share/pipepipe-device-finalfeed3.ozwge20x`. Earlier failed attempts remain intact. APKs, backups and raw logs are outside Git; only this sanitized evidence is committed. Client main merge `d1a90457f8dbdefc26fcd1a23fd22217c6c6cf75` has the exact tested `4746c6286` tree.
