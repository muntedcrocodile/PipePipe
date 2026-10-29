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

These are reviewed build inputs, not admission or device-test results. Independent broker review is still in progress. Artifact reconciliation identified a concrete compatibility blocker: the generated test APK has an absent/effective-zero version code, whereas the frozen broker patch requires positive numeric versions for every role. The device owner will revise only the exact pinned diagnostic test-role handling after the frozen review returns, preserving app/managed-production version checks. Scoped logcat is unavailable in this broker revision; no broad-log fallback is authorized. Cleanup-platform verification, provisioning and the full physical acceptance checklist remain pending.
