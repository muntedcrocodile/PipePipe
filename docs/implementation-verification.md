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
