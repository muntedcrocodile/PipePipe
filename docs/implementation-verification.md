# Swipe and persistent Queue mode implementation

Implements [issue #1](https://github.com/muntedcrocodile/PipePipe/issues/1) against the latest upstream fetched on 29 October 2026: root `3fd38c6`, client `e40a1819c` (5.5.0), extractor `a1aa6841`. Feature client: `da54421e6878aef59520e80b21dfb5539bcef530`, in 26 incremental commits.

## Implementation

- Independent source-row swipe controls use literal left/right directions, preserve cards/grids, retain legacy gestures when explicitly disabled, and reuse normal source actions and confirmations. Queue mode and video-row swipes now default to enabled following the user’s post-delivery instruction.
- `PersistentQueueManager` owns one current-first consuming queue shared by playback and the Queue playlist. A versioned JSON record in the app database stores duplicate occurrence identities, recovery positions and remote continuation boundaries. SQLite commits precede successful mutations/events.
- Playback entry points preserve interrupted membership and progress. Completion/Next consume, errors retain, and repeat/recommendation injection is suppressed. Paused restoration and mode changes, stable global-history Previous, deletion invalidation, remote retries, cancellable shuffle and independent saved playlists use the shared owner.
- Ordinary database/preferences backups include queue state and settings. Confirmed import freezes old writers before replacement. The special playlist can be hidden without clearing its state.

The confirmed [specification](swipe-queue-spec.md), [glossary](../GLOSSARY.md) and [ADRs](adr/0001-one-queue-with-a-playlist-view.md) remain the behavior contract.

## Verification

Eight JVM tests passed with no failures or skips. Debug app and Android test APKs compiled successfully. The 42 feature instrumentation tests compiled but were not executed:

- 25 real SQLite queue/storage/remote continuation tests.
- 6 swipe action, layout and ordering tests.
- 4 controlled source-manager playback tests.
- 1 each for media-session navigation, global history and pending-only queue views.
- 4 settings import/startup/default-preservation tests.

Independent reviews found and corrected seven integration defects, including transport visibility/routing, same-head retry, gesture ordering, upcoming edits during delayed extraction and failure ownership across remote batches. The final review of `89ca735f5` found no remaining concrete material defects. Review is static evidence, not a substitute for device execution.

The host has no KVM or attached physical Android device. An Android 36 x86_64 software emulator was installed and started. It never completed boot, rejected APK installation with `Error: device is still booting`, then hung and exited. Instrumentation, real playback, physical gestures/tabs/RTL, popup permissions, notification/headset controls, force-stop/reboot and active-player backup roundtrips remain unverified on a device. No performance or playback-smoothness benchmark is claimed.

Commands used from `PipePipeClient`, with JDK 25 and Android SDK 37.0/build-tools 37 installed:

```bash
./gradlew clean :app:testDebugUnitTest :app:assembleDebug \
  :app:assembleDebugAndroidTest --no-configuration-cache --console=plain
./gradlew -DpackageSuffix=.queue :app:testDebugUnitTest :app:assembleDebug \
  :app:assembleDebugAndroidTest :app:assembleRelease \
  --no-configuration-cache --console=plain
```

## Build verification

The updated build of client `da54421e6` passed all eight JVM tests and produced debug, Android test and R8-optimized release APKs (2 minutes 12 seconds). All four release APKs passed APK Signature Scheme v2/v3 verification and the non-debuggable manifest check. The ARM64 APK also passed 16 KiB page-alignment verification.

ARM64 SHA-256: `46b5de7cf8876390ee29a0e7f229d721875f5eb820064674f85443eef1a59f46`. The release configuration enables R8 minification/optimization and disables debugging. The `.queue` application suffix permits installation alongside the official app. Local release signing material is stored outside the repositories and is not included in downloads.

## Enabled-default follow-up

The user superseded the initial opt-in policy after delivery. Runtime fallbacks and XML defaults enable Queue mode and video-row swipes when their keys are absent. Gesture XML defaults are also initialized at startup. The settings importer continues to replace the preference map: older imported settings without the feature keys therefore use enabled defaults, while explicit imported `false` values remain respected. Database-only import or declining settings import retains current settings. Watch-history recording/privacy settings are unchanged. Regression tests exercise the existing serialized settings/ZIP import boundary and startup initialization.

This enabled-default follow-up was built and verified locally; the user requested that this version not be sent. The earlier published APK remains the earlier opt-in-default version.

## Server1 device-testing preparation

The fork and exact client/extractor pins were cloned into `/home/user/Documents/PipePipe`. Server1 now has checksum-verified JDK 25.0.2, Android SDK 37.0/build-tools 37 and Gradle 9.5.1 available in a user-local toolchain. Client `ead3ac5a2` adds an optional validated `debugPackageSuffix` so diagnostic builds can use `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug` while retaining the normal `.debug` default. Packaged app/test manifests confirm that target, its `.test` package and `androidx.test.runner.AndroidJUnitRunner`.

Static acceptance review identified and corrected sparse-row history resume using an unknown source duration (`573019ff1`), false success feedback after a failed durable selection (`d36f3c61c`), and deferred rapid swipes sharing one mutable row target (`5227c48dc`). Follow-up reviews corrected transitions continuing after failed progress checkpoints (`cf39daa01`) and live-pause cleanup issuing another failing durable write (`10222dec3`). Independent source reviews found no remaining material defect in these fixes. The 27 added instrumentation methods bring the suite to 69 across eight classes; prepared fixtures include actual ExoPlayer event-adapter callbacks, but do not establish real network/live-edge behavior.

At client `5227c48dc4107e3172b74003afa7c633e94cbaff`, eight JVM tests passed with zero failures/skips, and isolated debug plus Android-test APKs built successfully. All 57 feature instrumentation methods compiled; **none executed**. These build outputs are superseded/on hold pending the checkpoint fix. No final optimized release or final artifact provenance is claimed for this intermediate state.

The Samsung phone remains authorized, but device access is now exclusively owned by ForkKeeper's broker. PipePipe tests require the source-only broker extension and restricted diagnostic plan described in [the device test plan](device-test-plan.md), independent review, and subsequent provisioning by the device owner. This thread has made no PipePipe device calls, broker changes or automatic-maintenance enrollment. Physical acceptance and final integrated build evidence remain outstanding.

## Reviewed server candidate build

Client `10222dec3255ea3e0a618337ca1837ad1b3b9306`, pinned by root `4c40746dc766ff75d487600699b4ca52e21159ac`, passed the final isolated JVM/debug/Android-test build in 55 seconds and the signed R8 release build in 2 minutes 40 seconds. Eight JVM tests passed with zero failures/errors/skips. All **69 instrumentation methods across eight classes compiled; zero executed**. The class counts are 40/11/4/4/1/1/1/7 in [device-plan order](device-test-plan.md); one swipe confirmation method requires API 29+.

All nine APKs passed signature and packaged-identity checks, with Signature Scheme v2 enabled. All four optimized release manifests are non-debuggable. ARM64 release ZIP alignment and every load segment in its ten native libraries satisfy 16 KiB alignment. Exact bytes, logs, R8 mapping, test XML, manifests and verification scripts are preserved privately outside Git. No APK was published or sent.

The nonsecret artifact/source manifest SHA-256 is `d183a080214e92f46ec3b7e85239e846ae1d4b4d79aa0e6e2833265c162ecfa8`; reviewed plan SHA-256 is `b942c324e0d5ae427e1ddf8e2c6ec1d8326b83c51dbed098cad7854aeb15751a`. The manifest records exact root/client/extractor revisions, toolchain, commands, all ABI identities and per-file verification. For the ARM64 diagnostic lane:

- Debug target APK SHA-256: `469f5736e9a65d5305ca02dedb58780162f6e0cbc5171903c90935e2e72abcf5`, version 111004, debuggable.
- Android test APK SHA-256: `89ed224bb83d7a19c9bd238b010204af149f721875a2ed53f955d60830a4aeb9`, debuggable, no declared version code. Its runner is `androidx.test.runner.AndroidJUnitRunner`, targeting the dedicated debug package.
- Optimized manual APK SHA-256: `1b926f09415c9d37dc96638696816d7675875b42167c6d0ab21f861672903c55`, version 111004, non-debuggable.
- Debug/test signing certificate SHA-256: `bfadb6be9109016e35054c9591542ffc14df0c360eb8d635b595b1716ae043ce`.
- Manual test signing certificate SHA-256: `5644fffef9eebff9f4446e6bbd8844d225f03879511f88bc3502f3a42812eb49`.

These are reviewed build inputs, not admission or device-test results. Independent review of frozen broker patch `44ac9ac373858b518de67fec7dba32a44b6b8499f72226abe3a4264986adb8d5` requires changes before enabling: distinguish absent APKs from retained unknown package data, restrict JUnit summaries to a valid terminal result bundle, reject incomplete/failed activity observations during cleanup, apply the diagnostic foreground guard to text input, and replace an unsupported reference-Android-10 instrumentation dump command. The reviewer independently passed 30 fake tests and reproduced the parser, cleanup-observation and text-routing gaps; no device operations were performed.

Artifact reconciliation also identified a compatibility blocker: the generated test APK has an absent/effective-zero version code, whereas the frozen broker patch requires positive numeric versions for every role. The device owner will address all six findings in a fresh source-only implementation/review round, narrowing absent-version support to the exact pinned diagnostic test role and preserving app/managed-production version checks. Scoped logcat is unavailable in this broker revision; no broad-log fallback is authorized. Cleanup-platform verification, provisioning and the full physical acceptance checklist remain pending.

## General leased device access supersedes the strict proposal

The user's replacement AGENTS instructions and installed `android-device` skill now authorize any local agent's normal-account phone use on server1/ghost5 under ForkKeeper's exclusive renewable lease, without worker switching, enrollment or app-plan gates. The older strict patch remains archived and undeployed; its six findings are historical source-review results and do not block this replacement route. In particular, the actual test APK's absent/effective-zero version code needs no rebuild for generic installation. Signed maintenance merge validation remains separate.

The physical test agent acquired the exclusive lease and performed dedicated-package installed/retained-state checks and actual instrumentation. Existing regular installations and unknown retained data remained protected. The original artifact manifest preserves the reviewed pre-access-change plan bytes and digest; the current plan documents the superseding access rule.

## Actual device results and interrupted manual acceptance

Device: Samsung SM-G960F, Android 17/API 37, ARM64. The first actual run at client `10222dec3` completed in 6.740 seconds: **69 methods, 60 passed, 9 failed, zero errors/skips**. Eight failures exposed production `PlayerMediaItem.forStreamInfoItem` rejecting a nullable uploader on sparse rows. The ninth was a legacy-preference fixture using the wrong key. Client `16a275d5a9518fd239aa17a025ae3f091fb32f8c` normalizes absent uploader metadata, corrects the fixture and adds sparse-duplicate plus real touchscreen regressions. Independent source review found no material defect in that change.

Affected tests passed 17/17; the complete fixed suite passed **70/70** in 7.431 seconds, and the expanded suite passed **72/72** in 15.437 seconds, with zero failures/errors/skips. The latter includes touchscreen DOWN/MOVE/UP through attached ItemTouchHelper instances for source/local rows and physical left/right in LTR/RTL. Synthetic source adapters and intercepted service starts do not establish every production screen, permission flow or playback path. All 40 persistent-queue tests passed on the phone, including prepared ExoPlayer event-adapter failure cases.

Tested ARM64 debug SHA-256: `70a9e969de395966a5370b0a6993ff3eca7afd568c588266d225a5d66ac2db1e`. The 70-test APK SHA-256 is `2769d9e252fe15d3e2217850a6315066388343899e1251f9c6510656b865756d`; the expanded 72-test APK is `ce94827a71f97e3ab1e8a4366f7617310580a273b57efe55bbfcfe1f8352ac1c`. The installed optimized non-debuggable manual APK is `defd2a49702ce6e4c9eaddbbc08ea3f3079428147cedaabc8eafb41361932308`, signed with the same local test certificate recorded above. A clean client `16a275d5a` rebuild/JVM recheck passed with eight JVM tests and unchanged APK hashes.

Optimized manual testing successfully imported a synthetic legacy backup and showed the default Queue entry. Opening Queue from Bookmarked Playlists hosted in the home tab then crashed because the fragment transaction used a manager that could not find the activity container. Candidate `5899b95e68c0bea4009a1d738949eb05716b6141` uses the existing root navigator and adds two attached BookmarkFragment regression cases, nested and standalone/back-stack. Static review confirms use of the existing bookmark navigation helper. Its debug/Android-test build and eight JVM tests passed in 27 seconds; a clean-source recheck passed in 15 seconds and the optimized build passed in 2 minutes 11 seconds. The new candidate and its two tests remain **uninstalled and unexecuted** because an infrastructure failure interrupted staging and UI work.

Testing stopped after unexpected lease loss despite a successful renewal at 13:06:07.856 UTC reporting approximately 3,600 seconds remaining. The local completion log lists staging (10.130 seconds, exit 1), UI dump (11.526 seconds, exit 1), then a screenshot response of `stale or invalid session`; it does not record start order. Owner host evidence establishes that UI dump began at 13:08:57.500 UTC, before the stage input copy at 13:08:58.688 UTC: these operations overlapped. UI dump failed at 13:09:08.956 UTC and the broker revoked the lease at 13:09:08.962 UTC with classification `operation failed or disconnected`. No upload event occurred and staging did not cause revocation. The underlying UI error and original local stage/UI error bodies were not retained, so timeout, transport and UiAutomator subtypes cannot be distinguished. No expiry, restart or successful release caused this event.

Owner metadata reports cleanup OK at 13:09:10.095 UTC, but general cleanup does not force-stop app UIDs. The stale guard exited and its private token was removed; its app-stop/release attempts returned stale. **Device-side package/process quiescence was not independently verified**. Fleet placed the service in maintenance quarantine; no reacquisition or further phone calls were attempted. Controlled owner recovery and clearance for a fresh exclusive lease to stop only the diagnostic packages and verify inactivity are required before continuation. The old lease also had eight staged artifacts, reaching its per-lease slot cap; continuation must account for that cap. Future task wrappers must serialize device commands and preserve sanitized failure output plus start/end UTC. Fleet owns infrastructure investigation and recovery.

Host-verified, uninstalled navigation-candidate APK SHA-256 values are debug `0b5d65c6c01b6cf5af2dbf12d3bc56298320a1dfa608a21628bf00407971e658`, Android test `679da84be510448096b0a5ed1bbae6658a01fcd775b3033a906ca70e64e4d136`, and optimized release `5ea78bc159a87fb691ca6e13c026bb6557b063b17000906006341018467bdf8a`. Packages, version codes and test signing certificates remain those recorded above. These are build results, not a 74-test device pass or confirmation that the navigation crash is fixed on the phone.

Natural playback completion/transport, optimized playback smoothness, background/popup/notification/headset behavior, complete real-list coverage, real progress recovery/process-death/reboot, remote pagination/retry and complete backup roundtrips remain incomplete manual acceptance. Passing instrumentation and infrastructure checks do not establish those outcomes. Exact runner bundles, staged/tested APK copies, host build logs, private crash/UI evidence and sanitized lease receipts are preserved outside Git; no APK or personal capture was published.

## Resumed verification: 75 passing tests and a new infrastructure block

Fleet verified recovery and isolated-package quiescence, then cleared the same worker to acquire a fresh exclusive lease under runtime `951b538d06d4f4cc7b03ce4c15f8a323168938cc`. This was current recovery evidence, not retrospective proof for the old stale token. Updated wrappers serialized every phone/stage/UI operation, retained bounded safe failures with UTC start/end and correlation IDs, and discarded installed staged artifacts to release their slots.

The two new navigation regressions passed 2/2. The integrated 74-method attempt then produced 56 passing terminal events followed by `Process crashed`/`INSTRUMENTATION_CODE: 0`, not a complete pass. Target-UID-only logcat identified an application lifecycle race: a SharedPreferences listener snapshot already posted before unregistering called `getString` after BookmarkFragment detached. Client `063616da91ea81d14c6783701b307cf94de5bc57` ignores that stale callback before context access and adds a deterministic queued-notification regression. Parent independent source review found no material defect in the two-file fix.

Affected navigation/listener cases passed **3/3 in 2.123 seconds**. The complete suite then passed **75/75 in 16.647 seconds, zero failures/errors/skips**, ending with `OK (75 tests)` and `INSTRUMENTATION_CODE: -1`. Class counts are 40/17/4/4/1/1/1/7. Eight JVM tests passed. Clean committed-source debug/test and optimized assembly rechecks passed in 26/12 seconds and reproduced the exact installed/tested bytes. Signatures, packages/manifests and ARM64 ZIP 16 KiB alignment were verified; the optimized release is non-debuggable. Final APK SHA-256 values:

- Debug: `9ffb47ab6d6cfa03ae047d75b9cad750386f8554580340fb2b29e3fb0aebcb12`.
- Android test: `4285bbb4509f28dae2cc0fe81b6668ef7b136c169f524c0cacc9353b21f81f4d`.
- Optimized release: `fe1c990e091ee6282f44fb2fa0ad0fcd84c7ac60a13eb2420e4e25f1c988cda3`.

Package IDs, app version 5.5.0/111004, test effective version 0 and signing certificates are unchanged from the dedicated lane above. Original failing and fixed APKs, the incomplete 74-method bundle and the 75-test evidence remain preserved separately.

Actual optimized Queue navigation from the Bookmarked Playlists home tab **passed**, reaching the empty Queue screen without the original crash. The synthetic five-row local playlist and duplicates survived upgrade. A physical-right swipe reached actual resolved video details with service/ExoPlayer initialization and a displayed position; follow-up was blocked, so this is partial evidence, not proof of enqueue order, uninterrupted playback, progress recovery or smoothness.

A later serialized UI dump on the optimized detail/video screen revoked the fresh lease. The retained receipt spans **2026-10-29 13:58:16.656761–13:58:28.968851 UTC** and reports `code=validation`, `phase=dump`, operation ID `817d15fc8c4007c0ac8048868619bf2a`. This is a new correlated infrastructure failure, separate from both the application lifecycle crash and historical overlapping-command incident. The worker stopped phone work; finally attempts to stop all three diagnostic packages, observe processes and release were rejected with `stale_session`/`ownership`. Guard exited, private token was removed, status was idle. **No successful explicit release or current app-UID/activity/instrumentation quiescence proof is claimed.** No reacquisition or infrastructure changes followed. Fleet owns investigation/recovery.

Private resumed evidence contains exact runner bundles, commands/UTC/error receipts, final tested artifacts and cleanup distinctions. The Fleet owner report is `/home/user/.local/state/fleet/pipepipe-debug-20261029/remote-owner-report.md`. Remaining manual/system cases listed above are still incomplete; **no full-spec acceptance or optimized-release performance verdict** is made. No protected app/data changes, merge or APK publication occurred.
