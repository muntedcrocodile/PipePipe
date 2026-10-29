# Swipe and persistent Queue mode implementation

Implements [issue #1](https://github.com/muntedcrocodile/PipePipe/issues/1) against the latest upstream fetched on 29 October 2026: root `3fd38c6`, client `e40a1819c` (5.5.0), extractor `a1aa6841`. Feature client: `89ca735f56d70ca31be75d1c26eaf7a57c0e5012`, in 25 incremental commits.

## Implementation

- Independent opt-in source-row swipe controls use literal left/right directions, preserve cards/grids and existing gestures before opt-in, and reuse normal source actions and confirmations.
- `PersistentQueueManager` owns one current-first consuming queue shared by playback and the Queue playlist. A versioned JSON record in the app database stores duplicate occurrence identities, recovery positions and remote continuation boundaries. SQLite commits precede successful mutations/events.
- Playback entry points preserve interrupted membership and progress. Completion/Next consume, errors retain, and repeat/recommendation injection is suppressed. Paused restoration and mode changes, stable global-history Previous, deletion invalidation, remote retries, cancellable shuffle and independent saved playlists use the shared owner.
- Ordinary database/preferences backups include queue state and settings. Confirmed import freezes old writers before replacement. The special playlist can be hidden without clearing its state.

The confirmed [specification](swipe-queue-spec.md), [glossary](../GLOSSARY.md) and [ADRs](adr/0001-one-queue-with-a-playlist-view.md) remain the behavior contract.

## Verification

Eight JVM tests passed with no failures or skips. Debug app and Android test APKs compiled successfully. The 38 feature instrumentation tests compiled but were not executed:

- 25 real SQLite queue/storage/remote continuation tests.
- 6 swipe action, layout and ordering tests.
- 4 controlled source-manager playback tests.
- 1 each for media-session navigation, global history and pending-only queue views.

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

## Delivered build

The final build of client `89ca735f5` passed all eight JVM tests and produced debug, Android test and R8-optimized release APKs (1 minute 51 seconds). All four release APKs passed APK Signature Scheme v2/v3 verification and the non-debuggable manifest check. The ARM64 APK also passed 16 KiB page-alignment verification.

ARM64 SHA-256: `15edec111ac19290d6e958fd9f33dea9c1694679b2cef30940291648940b0764`. The release configuration enables R8 minification/optimization and disables debugging. The `.queue` application suffix permits installation alongside the official app. Local release signing material is stored outside the repositories and is not included in downloads.
