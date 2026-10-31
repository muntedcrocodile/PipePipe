# Physical-device acceptance — 31 October 2026

This is the current evidence summary. Earlier quarantine reports, compiled-only candidates and intermediate failures in `implementation-verification.md` are historical. This run uses the installed `android-adb` skill and normal-account exclusive renewable ForkKeeper lease; the parent drives the phone directly. APKs and raw captures remain private.

## Source and exact tested artifacts

Client: `c12bb6713a06ff3e89a3823478f9bc8e4e4fb061`. Extractor: `a1aa6841e7868c72c39bf119bf992dc83b5176b1`. Root before this evidence update: `c7a5e8a71185ff4f93f43e46818b61a35a25d330`. Client/extractor source stayed clean during this run. These are dedicated diagnostic packages; official, `.queue` and standard `.debug` data were preserved.

| Artifact | Package suffix | SHA-256 |
| --- | --- | --- |
| DEBUG target | `.queue.devicetest.debug` | `a9fdd997f2d292ce8905d5ae01e66288bb68c155c93c2e96cd5e67db22562148` |
| Android test | `.queue.devicetest.debug.test` | `69411771ce5d5fa3fa026682892af7afc63d579337981ec0d46ca8a952f4188b` |
| Optimized ARM64 release | `.queue.devicetest` | `974a9ad6dddca650b0d0defe077c513501b1414e5dee9700e6bfd0605a4c11b0` |

All package names start `InfinityLoop1309.NewPipeEnhanced`. App version is 5.5.0 / 111004; generated test version is absent/effective zero. Target/test are debuggable; optimized release is non-debuggable and R8 processed. Exact installed bytes were checked before updating from the preceding owned diagnostic build; all three candidate APKs were installed serially and staged artifacts discarded. Packaged identities, runner/target, signatures and ARM64 ZIP 16 KiB alignment passed host verification.

DEBUG/test certificate SHA-256: `bfadb6be9109016e35054c9591542ffc14df0c360eb8d635b595b1716ae043ce`. Optimized local test certificate: `5644fffef9eebff9f4446e6bbd8844d225f03879511f88bc3502f3a42812eb49`. No release signing secret or APK is published.

Phone: Samsung SM-G960F, Android 17 / API 37, ARM64. Harness: T3 Code / Codex, gpt-6.1-sol with high reasoning effort, normal user `user` on `server1`, `/home/user/Documents/PipePipe`. JDK 25.0.2, SDK/build-tools 37, Gradle 9.5.1; diagnostic suffix properties are recorded in `device-test-plan.md`.

## Automated functional results

**82/82 instrumentation methods passed in 24.936 seconds**, with zero assertion failures, errors, ignored tests or assumption skips. The final result bundle contains `OK (82 tests)` followed by `INSTRUMENTATION_CODE: -1`. Class counts in plan order: **41 / 23 / 4 / 4 / 1 / 1 / 1 / 7**. The two new disabled-direction touchscreen regressions also passed separately. **8/8 JVM tests passed**, zero failures/errors/skips. Debug/test and optimized APK builds passed; no unchanged suite was rerun merely to reacquire a lease.

Instrumentation uses the exact eight-class broker-mediated invocation in `device-test-plan.md`, with runner `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.debug.test/androidx.test.runner.AndroidJUnitRunner`. DEBUG functional results do not establish optimized performance or every manual scenario.

Original 69-test DEBUG SHA-256 was `469f5736e9a65d5305ca02dedb58780162f6e0cbc5171903c90935e2e72abcf5`; test APK `89ed224bb83d7a19c9bd238b010204af149f721875a2ed53f955d60830a4aeb9`. Corrected 70-test DEBUG was `70a9e969de395966a5370b0a6993ff3eca7afd568c588266d225a5d66ac2db1e`, test `2769d9e252fe15d3e2217850a6315066388343899e1251f9c6510656b865756d`; expanded 72-test APK `ce94827a71f97e3ab1e8a4366f7617310580a273b57efe55bbfcfe1f8352ac1c`.

Preserved failure history includes original 69 methods / nine failures (nullable sparse uploader and a legacy fixture key), corrected 70/70 and expanded 72/72, the 74-method process crash after 56 passes (detached preference callback, fixed in `063616da9`), and the later 79-method startup-dialog crash. Subsequent 75/80/82 passes are attributed to their exact candidates. Partial/crashed runs were never promoted to passes.

Manual findings produced these additional client fixes: requested playback survives first-enqueue buffering (`b42439da3`), explicit opening waits for metadata from both callback paths (`4438df03b`, completed by `686dc5c94`), cold Queue views connect to the service and late activity startup avoids invalid dialogs (`77ec23671`), and disabled horizontal swipes cancel child clicks/long-clicks (`c12bb6713`). The intermediate incomplete fixes and original observed failures remain in private evidence.

## Actual optimized usage checks

The following were driven through normal app/system UI, touch input, media keys and real app backup export/import. Exact SQLite/serialized Queue comparisons come from those exported diagnostic backups, not privileged reads of app data. Public YouTube media/source behavior is environmental evidence, not a deterministic service guarantee.

| Area | Observed outcome |
| --- | --- |
| Swipes and list families | Physical left/right across local playlists, search, channel videos, subscription feed and related rows target the intended videos. Rapid search Play-next gestures preserve submission order (latest becomes next). Filtered/header rows resolve displayed targets. Source rows remain. Non-video tiles retain normal tab paging. |
| Disabled/layout behavior | Actual 180/450 ms disabled local swipes cause neither Play, long-press, delete nor enqueue. Card and grid video rows exclude custom swipes. Arabic strings work but this app's manifest does not enable actual mirrored RTL layout; injected LTR/RTL tests passed separately. |
| Action dialogs | Share chooser canceled without send; existing-playlist and Download dialogs canceled without mutation/download; browser and channel dispatch observed. Filter-channel confirmation canceled. Mark-watched explains unavailability with recording OFF; with recording ON its real SQLite global progress becomes finished without enqueue. |
| Source/history deletion | Local duplicate delete Cancel/Confirm removes the selected source occurrence while both queued copies remain. History deletion Cancel retains the row; Confirm clears saved history/progress without consuming either queued occurrence or interrupting the playing one. Backward-history snapshot invalidation prevents reinsertion of deleted history. |
| Queue edits | Empty first enqueue starts actual decoded video after the metadata fixes. Paused enqueue stays paused. Existing-occurrence selection, duplicate identities/progress, upcoming/current removal, consuming natural completion, final Next, Clear cancel/confirm and reorder behave as specified. Head drag is excluded. |
| Independent duplicate progress | Same-URL occurrences saved around 33.444 s and 100.500 s resume independently around 31.709 s and 101.778 s. Early failed seek-control taps were not counted as failures or passes. |
| Modes and system controls | Background survives Home; media Play/Pause/Next and Previous exercised. Popup permission request/denial explanation and decoded popup over Home observed. A clean background-to-main switch retains five occurrences and progress. Direct popup-to-main controls were not reliably isolated. |
| History/privacy | Previous beyond five seconds traverses actual history without loops. Depth zero and recording OFF restart current without adding history. Queue progress/recovery works with recording OFF. Missing feature keys enable both features; accepted explicit OFF stays OFF. Declining settings import preserves explicit feature/privacy OFF values. |
| Mode/entry preferences | Hiding/unhiding Queue preserves state. Disabling mode stops/hides it; ordinary playback does not replace saved membership. Re-enabling restores the saved Queue paused. |
| Process death and real backup | Force-stop/relaunch preserves acknowledged order/UUIDs and paused progress. Real backup replacement during playback restores exact four-node UUID/order/progress, verified by re-export; late old-player work does not overwrite that result. Saved ordinary copies remain independent of subsequent live edits. |
| Remote continuation | A real 407-advertised-item remote playlist starts a 99-item suffix plus boundary before the old 16 entries. Restart retains all 116 nodes. Confirmed offline Shuffle fails visibly without mutation; cancellation also leaves exact state; retry materializes 419 currently accessible entries with the old tail retained. A saved 419-row copy remains independent. |
| Actual source boundary | Offline media Next consumes 99 loaded rows, then blocks at the boundary instead of bypassing the preserved 16 old rows. Online Play retries the page and inserts 100 rows before the boundary and old tail. |
| Extraction failure | Invalid test URL remains current through extraction error and explicit retry; only manual Next consumes it. Own-UID extraction-error evidence is retained. |
| Phone reboot | Reboot command succeeded, but transport loss revoked the lease and all three documented trusted recovery attempts failed. Actual post-reboot Queue restoration remains UNVERIFIED; this is the current infrastructure block. |

## Optimized performance and limits

A narrow **419-row optimized Queue scroll smoke** recorded 293 frames, six deadline-janky frames (2.05%), legacy jank 43/293 (14.68%), p50 16 ms, p90 18 ms, p95 21 ms, p99 31 ms. Actual video frames decoded and changed over time. This is one device/session/list smoke measurement, not a whole-app smoothness or performance acceptance verdict.

Physical headset hardware was unavailable. Actual mirrored app RTL, direct popup-to-main preservation, every custom action crossed with every list family, and every system permission/rotation combination have not been established. A portrait fullscreen-control attempt did not prove rotation and is not a pass. Filter-channel acceptance/removal was not driven beyond its normal confirmation. These limits prevent a claim that every feature/path is fully tested.

## Ownership, restoration and cleanup

Trusted recovery after the earlier host reboot completed without runtime deployment/restart/config changes. Three later screenshot operations revoked sessions with safe `unknown/operation` errors; their underlying causes remain unverified. Ordinary `validation/dump` failures retained ownership and used fallback; they are not app-test failures. Fresh sessions established dedicated-package quiescence before continuation, separately from the old rejected stale releases. A planned phone reboot then legitimately lost transport; the disconnected command revoked its lease and required documented trusted cleanup recovery. No raw ADB bypass was used.

Temporary subscription was removed; source fixtures, list layout, English system-default locale and feature defaults were restored by normal import of the original real synthetic backup. Watch history was explicitly restored OFF; the optimized overlay permission was returned OFF. Wi-Fi was restored ON/mobile data OFF after offline tests. Only dedicated synthetic data was manipulated; no protected package data was cleared or uninstalled.

**Current cleanup is BLOCKED.** The final lease was revoked by genuine reboot transport loss; its guard exited and private token was removed. No successful explicit release, cleanup-to-IDLE or post-reboot app-UID quiescence is established. Documented trusted recovery attempts at 14:04:17, 14:04:54 and 14:05:26 UTC each acknowledged cleaning and then failed; broker remains quarantined. The recovery report identifies USB renumbering and closed DeviceAllow as a plausible operator-repair issue, not a proven root cause. Fleet/device-owner repair is required; this lane made no service restart, deployment/configuration edit, permission bypass or further phone call. See `/home/user/.local/state/fleet/pipepipe-debug-20261029/phone-reboot-recovery-20261031/result.md`. Earlier fresh-session quiescence proofs remain valid only at their recorded times.

Private evidence root: `/home/user/.local/share/pipepipe-device-evidence.K8LETjIj`. Current run directories: `usage82.Bj9Xbqbf` (targeted/full runner bundles and exact backup comparisons), `usage82b.ECztvT62` (remote boundary, modes and performance), `usage82c.d0Qtc1Bw` (layout/default/privacy/history/deletion/error/final restoration). Every operation records UTC start/end, safe reply/disposition/correlation and bounded raw output. The final bounded optimized UID-only log capture was complete and contained no `FATAL EXCEPTION`, `Fatal signal` or `ANR in` match; expected extraction/offline errors remain. This does not claim the entire historical log is error-free.

Review and delivery: independent read-only review of the five parent fixes found two P2 deferred-open races: an old request survives cancellation/another selection, and metadata completion can overwrite a newer Pause with the old autoplay snapshot. A host-only client implementation follow-up is in progress; no second app phone owner exists. The 82-pass candidate has these open findings, and the follow-up will require separate review/build/device execution. Changes are on the user's `muntedcrocodile` forks only, client PR #1 and root PR #2. No merge, automatic enrollment or APK publication was performed.
