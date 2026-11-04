# PipePipe physical-device test plan

Current result: **124/124 instrumentation methods passed**, plus **8 JVM tests**, at client `4746c6286b97e1b765d20c5c28e6d3291d269075`. See [exact artifacts and actual manual results](latest-device-acceptance.md). The older [31 October plan](device-test-plan-20261031.md) is historical.

## Access and build

On server1/ghost5 load the installed `android-adb` skill, acquire ForkKeeper’s exclusive renewable lease, and serialize all broker-mediated phone operations. Renew before expiry, retain safe failure/UTC receipts, and release after stopping owned work and verifying quiescence. Ordinary `disposition:retained` errors preserve the token; revoked tokens must never be reused. No direct ADB, worker switching, enrollment or broker changes are needed.

Build from `PipePipeClient` with JDK 25, SDK/build-tools 37:

```bash
./gradlew -DdebugPackageSuffix=.queue.devicetest.debug \
  :app:testDebugUnitTest :app:assembleDebug :app:assembleDebugAndroidTest \
  --no-configuration-cache --console=plain
```

Verify package, certificate, version, ABI and exact installed bytes before updating only the owned `.queue.devicetest.debug` and `.queue.devicetest.debug.test` packages. Preserve normal PipePipe, `.queue`, standard `.debug` and unrelated data. Use a normal app backup before fixture changes. The optimized release has a different `.queue.devicetest` package and its existing dedicated signing identity.

## Instrumentation selection

1. `org.schabi.newpipe.player.playqueue.PersistentPlayQueueTest` — 41 methods.
2. `org.schabi.newpipe.info_list.VideoSwipeActionsTest` — 55 methods.
3. `org.schabi.newpipe.settings.FeatureDefaultsImportTest` — 4 methods.
4. `org.schabi.newpipe.player.playqueue.PersistentSourcePlaybackTest` — 4 methods.
5. `org.schabi.newpipe.player.playqueue.QueueHistoryTest` — 1 methods.
6. `org.schabi.newpipe.player.playqueue.QueuePendingViewTest` — 1 methods.
7. `org.schabi.newpipe.player.mediasession.QueueMediaSessionNavigationTest` — 1 methods.
8. `org.schabi.newpipe.local.history.PlayerResumeHistoryTest` — 7 methods.
9. `org.schabi.newpipe.fragments.list.kiosk.KioskRefreshTest` — 5 methods.
10. `org.schabi.newpipe.local.feed.service.FeedRefreshRoutingTest` — 3 methods.
11. `org.schabi.newpipe.fragments.detail.DetailViewLifecycleTest` — 2 methods.

Run under the valid lease through the broker (PRIVATE is the private token path):

```text
/opt/forkkeeper/scripts/device-session --token-file PRIVATE adb -- shell am instrument -w -r -e class org.schabi.newpipe.player.playqueue.PersistentPlayQueueTest,org.schabi.newpipe.info_list.VideoSwipeActionsTest,org.schabi.newpipe.settings.FeatureDefaultsImportTest,org.schabi.newpipe.player.playqueue.PersistentSourcePlaybackTest,org.schabi.newpipe.player.playqueue.QueueHistoryTest,org.schabi.newpipe.player.playqueue.QueuePendingViewTest,org.schabi.newpipe.player.mediasession.QueueMediaSessionNavigationTest,org.schabi.newpipe.local.history.PlayerResumeHistoryTest,org.schabi.newpipe.fragments.list.kiosk.KioskRefreshTest,org.schabi.newpipe.local.feed.service.FeedRefreshRoutingTest,org.schabi.newpipe.fragments.detail.DetailViewLifecycleTest InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug.test/androidx.test.runner.AndroidJUnitRunner
```

Require all 124 terminal method passes, no failures/errors/ignored/assumptions, complete `OK (124 tests)` and `INSTRUMENTATION_CODE: -1`. Partial/crashed/truncated runs are failures, even when earlier methods passed.

## Manual acceptance

- In What’s New, refresh real active subscriptions, verify visible videos and exported `feed_last_updated`/feed rows; immediately pull inside a clickable video row and require new timestamps within the old 300-second cooldown. Verify Queue state remains unchanged.
- Exercise left/right video-row actions and verify source rows, Queue order/duplicates and paused transport. Exercise first enqueue from empty, explicit video opening, pause, real rotation and cold Queue restoration.
- Restore the exact original app backup/settings and rotation settings. Re-export to compare owned Queue/subscriptions, stop owned packages, capture bounded own-UID diagnostics, verify quiescence, explicitly release to idle and remove the private token.

A debug build successfully tested on the physical phone satisfies functional device validation per AGENTS.md. The optimized CI release must still build and pass signature/package/version/ABI/R8 checks. Do not attribute a release-device or whole-app performance verdict to the debug suite.
