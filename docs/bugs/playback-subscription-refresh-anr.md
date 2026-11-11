# Playback during subscription refresh: verified contention fix

The controlled MainActivity playback/refresh freeze was reproduced and the narrow
fix passed device validation. **The original attachment's exact blocked stack and
multi-GiB memory profile remain unconfirmed.** No claim is made that its memory
cause was identified or that upstream alone resolved it.

## Cause and change

The baseline main thread was captured waiting in two paths during real playback
and a large refresh:

- RecyclerView layout -> `StreamInfoItemHolder.updateFromItem:109` ->
  `HistoryRecordManager.loadStreamState(...).blockingGet()` -> RxJava latch.
- Player progress/lifecycle -> `PersistentQueuePlayerController.checkpoint:164`
  -> `PersistentPlayQueue.setRecovery` -> `PersistentQueueStore.save:61` ->
  `SQLiteConnectionPool.waitForConnection`. Feed storage held the same database
  writer across 20 independent channel updates.

Video rows now load history asynchronously, cancel obsolete requests, reject stale
results, and handle recycled/detached/cached-reattached views. Existing progress,
duration, paid/live-row display and queue durability semantics are preserved.
Feed storage now commits each channel atomically and releases the writer between
channels. More frequent commits are a throughput/battery tradeoff; validation
checks responsiveness and correctness, not a speed improvement.

These captured row/feed/checkpoint source files were identical between production
baseline `0a59c626` and upstream-integrated `d115054f`. Upstream integration alone
did not change these contention paths. Queue format/checkpoint durability was not
rewritten. No extractor implementation, unrelated feature or visual design changed.

## Worktree and source provenance

Worktree: `/home/user/.t3/fleet-dev-0.1.2/worktrees/PipePipe/t3-3d5de02e`.
Root branch: `t3/fix-playback-subscription-refresh`.
Client branch: `fix/playback-subscription-refresh`.

| Source | Revision |
| --- | --- |
| Local root before work | `7f8d030f6f04ca97c95d57bddcf62cee3352433a` |
| Local client before work | `da54421e6878aef59520e80b21dfb5539bcef530` |
| Current fork / inferred report root | `88d69d469361a930fe6304e4db202797f295f691` |
| Current fork / inferred report client | `0a59c6264a4746efad9d98a5353efab4dab5bc3a` |
| Fetched upstream root | `3fd38c6dbdfa1d29c97d9d5b1344836347793ec3` |
| Fetched upstream client | `118ffc86baa811edae4d5659bbba7835f8ba6a92` |
| Integrated root merge | `44dd8a28a13d2c80b17f44d466ebbd55f7f2059c` |
| Integrated client before fix | `d115054f4716b142950e9a7dbce009935f02f4a9` |
| Latest collected extractor / final gitlink | `28a1a5ee889fadb36a435c43e0bc9483b59bb3bf` |
| Final client including regressions | `d78aa788c4cae92fe57a44687174881d6fa3b1ff` |

Fleet fetched source and provided local bundles; integration used merges, without
reset, rebase or history rewrite. The upstream root was already an ancestor of the
current fork root. Client integration preserved fork features and merged cleanly.
The original client checkout was untouched. The prepared extractor already had
HEAD `28a1a5e`, an empty worktree and staged deletions, versus starting root gitlink
`a1aa6841e7868c72c39bf119bf992dc83b5176b1`; that pre-existing state was preserved.
No vendor push is required. One initial local root-bundle import unexpectedly
triggered a read-only recursive GitHub client fetch; subsequent imports explicitly
disabled recursive fetching. Server/device access remained exclusively with Fleet.

The original filename suffix `272d2de259c9` did not resolve to a scoped source ref
or APK inventory hash. Release `v5.5.1000003` matches versionCode `100000304` and maps
to the fork revisions above; its ARM64 APK hash is
`d54822461699e895a0e9a7ceff4b765a5ab8aa5bd959bcf7ea4e61b344f7f843`.
That association is inferred from version metadata, not verified against original
APK bytes. The historical Nov 5 APK was not used as the failing baseline.

## Sanitized original evidence

Private attachment: `Error in PipePipe .queue.devicetest 272d2de259c9.txt`,
1,260,888 bytes; SHA-256
`596f738cd4a05e45ce17244f1515407f0d7e151d0dc0c2b7661ae38c129eace8`.
Raw logs were not copied into this repository or published.

- Lines 1-15: ANR in `InfinityLoop1309.NewPipeEnhanced.queue.devicetest`, target
  SDK 36, versionCode `100000304`, 5,000 ms input timeout for
  `FocusEvent(hasFocus=false)`. RSS 6,867,632 KiB; high-water RSS 7,782,760 KiB.
- Lines 19-32: earlier MotionEvent ANR in another PID, about 218 seconds earlier.
- Lines 34-388: target PID 23166, initial collection at
  `2026-11-11 19:52:21 +1100`. Tombstoned failures at lines 39 and 242; only
  waiting-channel `ptrace_stop` entries, **no app Java stack**.
- Lines 18641-18648: target activity and input-timeout summary. Other processes'
  stacks elsewhere in the attachment were not treated as app stacks.

## Device scenario and results

Fleet was the sole remote/device operator. No duplicate app worker or phone lease
was started. Device: Samsung SM-G960F (`starlte`), Android 17 / API 37, security
patch `2026-10-01`; this differs from the attachment's Google `blazer` hardware.
The installed old diagnostic APK was not used as source provenance.

Fresh packages: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.refresh` and
`.refresh.test`. Existing diagnostic/personal packages, subscriptions and history
were not replaced, cleared or used. The fixture creates 1,000 distinct synthetic
subscription identities, supplies 100 RSS entries each, and uses a uniquely named
Room file with production `synchronous=FULL` and the production queue-table
callback. It deletes its own database and restores changed preferences/globals.

The final test uses actual MainActivity -> VideoDetailFragment -> PlayerService,
real online YouTube/SABR playback, the real feed refresh button/service, injected
swipe input and feed/detail view recreation. Five refresh cycles each assert 1,000
current requests, successful completion, advancing playback and heartbeat checks.
Fresh-package onboarding/announcement dialogs are excluded to model a returning
user. This is synthetic **RSS**, not a full channel-tab extraction fixture.

| Check | Result |
| --- | --- |
| Early standalone playback/RSS baseline and integrated probes | 1/1 each; negative original reproduction, not acceptance |
| Actual UI in-memory baseline | Main-thread row-read and checkpoint stalls captured |
| Actual UI disk/FULL baseline, 100 entries/channel | Repeated main-thread checkpoint writer waits; no completed cycle |
| Delayed history regressions before fix | 3 expected failures: mini 521 ms, regular 507 ms, grid 503 ms against 250 ms bound |
| Fixed row responsiveness | 3/3 passed |
| Fixed stale-result/recycle/error behavior | 3/3 passed |
| Fixed actual UI, disk/FULL, five current cycles | 1/1 passed; JUnit 1,493.053 seconds; 5,000 RSS requests |
| Fixed feed isolation and refresh routing | 3/3 + 3/3 passed |
| Debug app/instrumentation compilation | Passed, 86 Gradle tasks |
| Optimized release compilation | Passed, 56 tasks, 4m 2s; unsigned, not distributed |

The final UI run used `c441268e36d0274134f694567a4cfd816098c4a7`; final binder
checks used `d78aa788c4cae92fe57a44687174881d6fa3b1ff`. Production app source and
ARM64 app bytes are identical to `5a75619167d120969f257de76749c7f3f8b7d700`, which
also passed the feed/responsiveness checks and release compilation. Only Android
instrumentation files changed afterward. No unchanged broad suite was rerun.

The UI run collected 257 external samples and 43 bounded rolling log chunks.
Sampled maximum RSS was 729,856 KiB, PSS 550,902 KiB; observed VmHWM 797,816 KiB,
maximum 150 threads. These are sampled observations, not continuous peaks or a
controlled performance verdict. Heartbeat assertions passed at the 1,500 ms test
threshold; retained logs had zero `MAIN_STALL` markers. One cycle log timestamp
was absent from bounded captures, so elapsed times across that gap are not claimed.
The original multi-GiB profile was not recreated.

## Commands and immutable artifacts

Host build (Bash, isolated server1 snapshots):

```bash
bash ./gradlew --no-daemon --offline --console=plain --max-workers=2 \
  -Dorg.gradle.jvmargs=-Xmx4g -DdebugPackageSuffix=.queue.devicetest.refresh \
  :app:assembleDebug :app:assembleDebugAndroidTest
bash ./gradlew --no-daemon --offline --console=plain --max-workers=2 \
  -Dorg.gradle.jvmargs=-Xmx4g -DpackageSuffix=.queue.devicetest.refresh \
  :app:assembleRelease
```

Fleet launched instrumentation through the installed ForkKeeper broker under its
exclusive renewable lease. UI selector:
`org.schabi.newpipe.local.feed.service.MainActivityRefreshReproTest#actualPlayerAndFeedRepeatedRefreshWithInputAndViewRecreation`.
Arguments: `diskDatabase=true entriesPerChannel=100 cycleTimeoutSeconds=600`;
bounded host runner 4,000 seconds. Row tests used default in-memory arguments:
`org.schabi.newpipe.info_list.holder.StreamRowHistoryResponsivenessTest` and
`org.schabi.newpipe.info_list.holder.StreamProgressBinderTest`. Feed selectors:
`org.schabi.newpipe.local.feed.service.FeedLoadIsolationTest` and
`org.schabi.newpipe.local.feed.service.FeedRefreshRoutingTest`.

ARM64 debug package versionCode `111004`, versionName `5.5.0`; debug certificate
SHA-256 `bfadb6be9109016e35054c9591542ffc14df0c360eb8d635b595b1716ae043ce`.

| Artifact | SHA-256 |
| --- | --- |
| Baseline ARM64 debug app | `9d7b1de3eadedeace5085e45dd1ededc9347f96069d022c3f476136ab998566e` |
| Verified ARM64 debug app | `94b8790f532de6af49d1227f8b3b6b2d1d80a3d74a0f3b52c573d120404d96b4` |
| Final d78 instrumentation APK | `1a62ee5fa434810a86d0ee8e5c0402ef8f97a0f2803afd7ea32d60ee0b09a585` |
| Optimized ARM64 release, unsigned | `4e10be7e8a85a4a733b7fdd719d7718238cf4e8b6d60eb6e0d9a1db1b1cb7626` |

The d78 debug build started/ended at d78 with a clean source tree; the separately
timestamped post-build readback confirms it. Release start/end were both 5a.
No signing material was available in scoped Fleet configuration; no key was
created and no unsigned APK was published, delivered or installed.

## Cleanup, review and remaining limits

Final UI session `b50c5e95d4863f277ca2f70fa928b8eb` and final binder session
`4d2ca1f61fa67786b69a1003ed230bf5` explicitly released successfully, reached idle,
and removed tokens. Supported queries verified no fresh target process/subprocess
or active instrumentation; both fresh packages were removed and absence checked.
Existing apps/data were preserved. Saved acquire/renew/release operations, source
and APK provenance are in Fleet's scoped
`local/tasks/pipepipe-playback-refresh-20261111/main-ui/final-handoff/` receipts.
No device lease is held after testing.

Earlier failed package-existence probes/staging timeout/stale release were not
used as final cleanup proof. Fixture-only failures (premature Room/service teardown,
cached success replay, accidental UI arguments in helper checks, and circular
indeterminate-only progress widget) were corrected and their failed outcomes
retained. They were not reported as application causes or waived passes.

One independent read-only review covered the initial reproduction fixture; its
responsiveness/count/cleanup findings were addressed. No second reviewer or
implementation owner was started. Final production changes were self-reviewed
and validated by the scoped checks above.

The user subsequently answered: about 450 subscriptions, fast/RSS disabled and
1080p playback, with whole-phone slowdown and occasional launcher crashes. See
[the full-extraction continuation](full-extraction-refresh-memory.md). The actual
attachment's bytes/source association and Google-device memory behavior remain
limits on linking this verified contention fix to every aspect of that report.

Fork publication targets are client `fix/playback-subscription-refresh` and root
`t3/fix-playback-subscription-refresh`, module first, root gitlink second. GitHub
login was verified as `muntedcrocodile`; both refs were absent at preflight. No
main/upstream/vendor branch, PR, release publication, Matrix or APK delivery is
part of this change. Exact final pushed refs are verified separately by Fleet.
