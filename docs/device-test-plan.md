# PipePipe physical-device diagnostic plan

Status: proposed broker plan, awaiting capability review, provisioning and final APK identity verification. App fixes and regression additions have passed independent source review; the final integrated builds are in progress. The device owner's frozen source-only broker extension is under independent review after the coordinated Fleet update; provisioning/restart/leases/device operations remain on hold. This plan does not enroll PipePipe in automatic maintenance. No PipePipe device operation is authorized through an unprovisioned route.

## Source and build identity

Root baseline: `7f8d030f6f04ca97c95d57bddcf62cee3352433a`; client baseline: `da54421e6878aef59520e80b21dfb5539bcef530`; extractor: `a1aa6841e7868c72c39bf119bf992dc83b5176b1`. Current client candidate: `10222dec3255ea3e0a618337ca1837ad1b3b9306`, independently source-reviewed with integrated builds pending. Local branches: `feature/swipes-persistent-queue` in root and client. Only the user's `muntedcrocodile` root/client forks receive changes.

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

The original suite had **42 methods in seven classes**, not 42 classes. Resume/selection regressions add ten methods, swipe regressions add five, prepared-player checkpoint-failure regressions add nine, and production live-pause callback regressions add three, bringing the current candidate suite to **69 methods in eight classes**:

1. `org.schabi.newpipe.player.playqueue.PersistentPlayQueueTest` — 40 tests.
2. `org.schabi.newpipe.info_list.VideoSwipeActionsTest` — 11 tests; the playlist-confirmation regression requires API 29+ and must be reported as skipped on an older device.
3. `org.schabi.newpipe.settings.FeatureDefaultsImportTest` — 4 tests.
4. `org.schabi.newpipe.player.playqueue.PersistentSourcePlaybackTest` — 4 tests.
5. `org.schabi.newpipe.player.playqueue.QueueHistoryTest` — 1 test.
6. `org.schabi.newpipe.player.playqueue.QueuePendingViewTest` — 1 test.
7. `org.schabi.newpipe.player.mediasession.QueueMediaSessionNavigationTest` — 1 test.
8. `org.schabi.newpipe.local.history.PlayerResumeHistoryTest` — 7 tests.

The reviewed broker must translate a fixed suite/class identifier to the following exact serial-targeted argument array. This is a specification for trusted broker execution, **not** permission for clients to invoke raw ADB:

```text
adb -s CONFIGURED_SERIAL shell am instrument -w -r -e class org.schabi.newpipe.player.playqueue.PersistentPlayQueueTest,org.schabi.newpipe.info_list.VideoSwipeActionsTest,org.schabi.newpipe.settings.FeatureDefaultsImportTest,org.schabi.newpipe.player.playqueue.PersistentSourcePlaybackTest,org.schabi.newpipe.player.playqueue.QueueHistoryTest,org.schabi.newpipe.player.playqueue.QueuePendingViewTest,org.schabi.newpipe.player.mediasession.QueueMediaSessionNavigationTest,org.schabi.newpipe.local.history.PlayerResumeHistoryTest InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug.test/androidx.test.runner.AndroidJUnitRunner
```

Allow single-class reruns only through a fixed identifier-to-class map for the eight classes above. Do not accept caller-supplied runner names, class strings, shell fragments, instrumentation arguments, filesystem paths or package IDs. Adding regressions or other test classes requires an explicit reviewed plan revision. Existing online SABR smoke/benchmark tests are not part of this first suite.

These tests create dedicated SQLite fixture files, manipulate isolated target preferences and use controlled page/extraction responses. Preference tests restore values on normal teardown, but interrupted instrumentation can leave fixture preferences modified. Therefore this package must contain only diagnostic data. If an existing installation has data of uncertain ownership, stop before install/testing and arrange a reviewed backup or another unique diagnostic identity; never clear it to proceed.

## Required broker behavior

Retain the existing exclusive device authority, private ADB identity, isolated client UID and lease protocol. No raw USB access, service UID/key access, privileged-user admission, socket escape, generic shell, arbitrary `run-as`, uninstall or package-data clear is requested.

Provision a diagnostic-only `pipepipe-queue-device-v1` plan with exact package/component and eight-class allowlists. Use the existing trusted staging/package inspector and signature/package/version checks for all three APKs. Observe whether each exact package is installed before installation; do not overwrite an unknown prior installation. Where the broker cannot establish that a prior install is this diagnostic lane with the expected signer, stop for reconciliation.

Instrumentation must share the existing operation lock, lease checks and cancellation fence. Bound a complete suite invocation to 600 seconds, each fixed single-class retry to 180 seconds, and cleanup to 60 seconds. Use a 30-minute lease and explicit renewal only between operations if needed; never silently renew or exceed the broker's tenure bound. Client disconnect, expiry, timeout or cancellation revokes the operation, terminates its host process group and performs trusted device-side cleanup before another lease is admitted. A killed local ADB client alone does not prove instrumentation stopped.

Cleanup must force-stop only the two debug/test packages and the manual diagnostic package, confirm their instrumentation/app processes and activities are absent, and confirm any install/input operation it started has ended. Do not abandon unrelated installer sessions or stop unrelated applications. If package-specific quiescence or connectivity cannot be established, quarantine rather than report success. Preserve package data for inspection and reruns. Release the lease and privately delete the client token after confirmed cleanup.

Capture bounded instrumentation stdout/stderr, exit status and terminal runner summary. Distinguish command completion from test success: ADB exit zero alone does not establish a pass. Report per-class counts, failures, errors and skipped tests. Missing terminal summary, cancellation, process crash, timeout or truncated output is incomplete/failed evidence. Keep existing wire/output limits; oversized output must not be silently truncated into success.

## Package-specific observations and manual checks

The first reviewed observation set should provide:

- Fixed device properties: manufacturer/model, Android release/API and ABI list; omit serials from published evidence.
- Exact diagnostic package presence, version, signer and debuggable status; exact instrumentation registration and target package. No broad installed-app listing.
- Scoped diagnostic-process logcat with a bounded time/output window. Resolve and recheck PID/package ownership in the trusted broker; do not return the whole device log or accept caller filters/shell text. If a dead-process crash cannot be safely attributed, report that limitation instead of returning unrelated crash data.
- Existing fixed launch/stop, UI dump, screenshot, tap/swipe/key/text operations for the diagnostic app. Keep captures private and inspect for personal/system-overlay content before extracting report evidence.

Manual checks use the optimized release diagnostic package. They cover actual list swipes, first/paused enqueue, duplicate selection/removal, full/background/popup playback, natural completion/Next/errors/empty behavior, system-media controls, history/Previous, source retries, process-stop recovery and in-app settings/database import/export against the main specification. System permission dialogs may require an explicit package-specific permission flow and another plan review. A physical headset check is unavailable unless hardware is provided.

The initial broker extension does not request global reboot, arbitrary external intents, arbitrary media commands, arbitrary file access, backup restoration into another package, or new production-data authority. Record any acceptance scenario that cannot be reached through the reviewed capabilities. Expand only through a concrete follow-up plan; do not substitute emulator or static review evidence for physical execution.
