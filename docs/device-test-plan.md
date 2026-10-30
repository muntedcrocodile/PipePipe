# PipePipe physical-device diagnostic plan

Current access: the user's replacement AGENTS instructions and installed `android-device` skill authorize normal-account phone use on server1/ghost5 under ForkKeeper's exclusive renewable lease. No worker switch, automatic-maintenance enrollment or app-plan provisioning is required. Fleet subsequently verified isolated-package quiescence and successful maintenance release/cleanup, then cleared continuation. The latest attempt is blocked by an occupied lease: 15 normal acquire requests on 30 October returned busy, no token was issued, and no phone operation occurred. The same worker remains the only app-testing lane; wait for availability without disturbing the active owner. Earlier stale release attempts remain failures and are not reclassified by the later maintenance proof. Existing app data and unknown retained package state remain protected. Never bypass the broker.

The fixed suite and acceptance scope below remain the testing checklist. The stricter broker-specific protocol/provisioning proposal is preserved as historical design only: its patch was independently reviewed, found to require changes, and remains undeployed. Those obsolete plan/enrollment/version-policy gates do not apply to the new general leased route. Signed maintenance merge validation remains separate. Final app builds and artifact identities have been verified, but instrumentation/device outcomes must be reported from actual execution.

## Source and build identity

Root baseline: `7f8d030f6f04ca97c95d57bddcf62cee3352433a`; client baseline: `da54421e6878aef59520e80b21dfb5539bcef530`; extractor: `a1aa6841e7868c72c39bf119bf992dc83b5176b1`. Current device-tested client: `063616da91ea81d14c6783701b307cf94de5bc57` (**75/75 passed**). The Queue navigation regressions and optimized home-tab path passed after recovery; a separate application lifecycle race was fixed and verified. Further manual acceptance is currently blocked by lease-resource contention after Fleet recovered from the later UI-dump incident; no new app or infrastructure failure occurred in the latest attempt. Local branches: `feature/swipes-persistent-queue` in root and client. Only the user's `muntedcrocodile` root/client forks receive changes.

The baseline debug configuration hardcodes `.debug`; its branch-name suffix path is disabled. An optional validated debug suffix override now protects existing standard debug installations. The diagnostic identities below were verified in preliminary packaged APKs and must be reverified against final artifacts before installation:

- Instrumented target: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug`.
- Test APK: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug.test`.
- Instrumentation component: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug.test/androidx.test.runner.AndroidJUnitRunner`.
- Debug launcher: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug/org.schabi.newpipe.MainActivity`.
- Optimized manual target: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest`.
- Manual launcher: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest/org.schabi.newpipe.MainActivity`.

Build configuration: JDK 25, Gradle 9.5.1, compile SDK 37, target 36, minimum 24. Debug and Android-test builds use `-DdebugPackageSuffix=.queue.devicetest.debug`; the R8-optimized release uses `-DpackageSuffix=.queue.devicetest`. Test signing material stays outside Git, private to the build process. Final client commit, APK SHA-256, signing-certificate SHA-256, manifest identity, version and manual APK non-debuggable status must accompany the install request. Baseline hashes above are source provenance, not artifact verification or a test verdict.

Protected packages outside this plan include the official `InfinityLoop1309.NewPipeEnhanced`, existing `.queue`, and standard `.debug` installations. Do not install over, stop, inspect private data from, clear or uninstall these packages.

## Fixed instrumentation suite

The original suite had **42 methods in seven classes**, not 42 classes. Actual results progressed from 69 methods with nine failures, to corrected 70/70 and expanded 72/72 passes. The two navigation regressions then passed, but the integrated 74-method run crashed after 56 terminal passes due to a queued preference callback on a detached fragment. After fixing that lifecycle race and adding a regression, the current suite passed **75/75 methods across eight classes**, with zero failures/errors/skips:

1. `org.schabi.newpipe.player.playqueue.PersistentPlayQueueTest` — 40 tests.
2. `org.schabi.newpipe.info_list.VideoSwipeActionsTest` — 17 tests, all passed. The playlist-confirmation regression requires API 29+; it executed on the observed API 37 phone.
3. `org.schabi.newpipe.settings.FeatureDefaultsImportTest` — 4 tests.
4. `org.schabi.newpipe.player.playqueue.PersistentSourcePlaybackTest` — 4 tests.
5. `org.schabi.newpipe.player.playqueue.QueueHistoryTest` — 1 test.
6. `org.schabi.newpipe.player.playqueue.QueuePendingViewTest` — 1 test.
7. `org.schabi.newpipe.player.mediasession.QueueMediaSessionNavigationTest` — 1 test.
8. `org.schabi.newpipe.local.history.PlayerResumeHistoryTest` — 7 tests.

The suite uses the following instrumentation arguments through the installed skill's generic leased action. `PRIVATE` represents the private token-file path; clients must use the broker, never invoke raw ADB directly. The eight-class list is reproducibility evidence, not an app-plan admission gate:

```text
/opt/forkkeeper/scripts/device-session --token-file PRIVATE adb -- shell am instrument -w -r -e class org.schabi.newpipe.player.playqueue.PersistentPlayQueueTest,org.schabi.newpipe.info_list.VideoSwipeActionsTest,org.schabi.newpipe.settings.FeatureDefaultsImportTest,org.schabi.newpipe.player.playqueue.PersistentSourcePlaybackTest,org.schabi.newpipe.player.playqueue.QueueHistoryTest,org.schabi.newpipe.player.playqueue.QueuePendingViewTest,org.schabi.newpipe.player.mediasession.QueueMediaSessionNavigationTest,org.schabi.newpipe.local.history.PlayerResumeHistoryTest InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug.test/androidx.test.runner.AndroidJUnitRunner
```

Targeted reruns and new regressions use the general leased route; record the exact class/method selectors and resulting suite counts when coverage changes. The obsolete fixed-map admission restrictions belong to the historical proposal below. Existing online SABR smoke/benchmark tests are not part of this suite.

These tests create dedicated SQLite fixture files, manipulate isolated target preferences and use controlled page/extraction responses. Preference tests restore values on normal teardown, but interrupted instrumentation can leave fixture preferences modified. Therefore this package must contain only diagnostic data. If an existing installation has data of uncertain ownership, stop before install/testing and arrange a reviewed backup or another unique diagnostic identity; never clear it to proceed.

## Historical strict broker proposal

This section describes the undeployed strict extension, not prerequisites for current general leased testing. The current `android-device` skill controls access and renewal/release behavior.

Retain the existing exclusive device authority, private ADB identity, isolated client UID and lease protocol. No raw USB access, service UID/key access, privileged-user admission, socket escape, generic shell, arbitrary `run-as`, uninstall or package-data clear is requested.

Provision a diagnostic-only `pipepipe-queue-device-v1` plan with exact package/component and eight-class allowlists. Use the existing trusted staging/package inspector and signature/package/version checks for all three APKs. Observe whether each exact package is installed before installation; do not overwrite an unknown prior installation. Where the broker cannot establish that a prior install is this diagnostic lane with the expected signer, stop for reconciliation.

Instrumentation must share the existing operation lock, lease checks and cancellation fence. Bound a complete suite invocation to 600 seconds, each fixed single-class retry to 180 seconds, and cleanup to 60 seconds. Use a 30-minute lease and explicit renewal only between operations if needed; never silently renew or exceed the broker's tenure bound. Client disconnect, expiry, timeout or cancellation revokes the operation, terminates its host process group and performs trusted device-side cleanup before another lease is admitted. A killed local ADB client alone does not prove instrumentation stopped.

Cleanup must force-stop only the two debug/test packages and the manual diagnostic package, confirm their instrumentation/app processes and activities are absent, and confirm any install/input operation it started has ended. Do not abandon unrelated installer sessions or stop unrelated applications. If package-specific quiescence or connectivity cannot be established, quarantine rather than report success. Preserve package data for inspection and reruns. Release the lease and privately delete the client token after confirmed cleanup.

Capture bounded instrumentation stdout/stderr, exit status and terminal runner summary. Distinguish command completion from test success: ADB exit zero alone does not establish a pass. Report per-class counts, failures, errors and skipped tests. Missing terminal summary, cancellation, process crash, timeout or truncated output is incomplete/failed evidence. Keep existing wire/output limits; oversized output must not be silently truncated into success.

## Historical package-specific observations and manual checks

The following observation/provisioning requests belonged to the archived strict proposal. They do not add app-plan or enrollment gates to current general leased use.

The first reviewed observation set should provide:

- Fixed device properties: manufacturer/model, Android release/API and ABI list; omit serials from published evidence.
- Exact diagnostic package presence, version, signer and debuggable status; exact instrumentation registration and target package. No broad installed-app listing.
- Scoped diagnostic-process logcat with a bounded time/output window. Resolve and recheck PID/package ownership in the trusted broker; do not return the whole device log or accept caller filters/shell text. If a dead-process crash cannot be safely attributed, report that limitation instead of returning unrelated crash data.
- Existing fixed launch/stop, UI dump, screenshot, tap/swipe/key/text operations for the diagnostic app. Keep captures private and inspect for personal/system-overlay content before extracting report evidence.

Manual checks use the optimized release diagnostic package. They cover actual list swipes, first/paused enqueue, duplicate selection/removal, full/background/popup playback, natural completion/Next/errors/empty behavior, system-media controls, history/Previous, source retries, process-stop recovery and in-app settings/database import/export against the main specification. System permission dialogs may require an explicit package-specific permission flow and another plan review. A physical headset check is unavailable unless hardware is provided.

The initial broker extension does not request global reboot, arbitrary external intents, arbitrary media commands, arbitrary file access, backup restoration into another package, or new production-data authority. Record any acceptance scenario that cannot be reached through the reviewed capabilities. Expand only through a concrete follow-up plan; do not substitute emulator or static review evidence for physical execution.

## Post-75 recovery and resource wait

Fleet's new maintenance session on 30 October stopped only the three dedicated packages, verified no processes/subprocesses, active activities or instrumentation target, and checked User 0 stopped state. Explicit release and cleanup to idle succeeded; the token was removed. Private proof is `quiescence-20261030T011414Z` under the Fleet state directory. This is later recovery evidence, not retrospective success for the worker's stale stop/release attempts. Fleet identified the later dump error as `ERROR: could not get idle state.`; the first 13:09 incident's underlying cause remains unknown. The current skill uses screenshots and broker input as primary inspection for animated/loading/video screens.

The same child read the updated skill and attempted normal acquisition 15 times from **2026-10-30 01:19:46.310596 to 01:29:06.609182 UTC**. Every reply was busy/leased. Its bounded wait ended around 01:30 UTC without a token, phone calls, tests, installs, stops or release attempts. This is an occupied resource, not a new broker error or app failure. The existing 75/75 device and 8/8 JVM passes and all manual limits remain unchanged. Private acquisition receipts are in `manual75.NDKcITL3/busy-final-summary.json` and the accompanying command/operation logs. Reuse the same worker after availability; do not create a competing phone lane.
