# Playback during large subscription refresh: investigation

Status: upstream integrated; bounded standalone fixture passes; actual MainActivity
diagnostics in progress. Original ANR acceptance incomplete; no verified fix or push.

## Scope and starting source

Dedicated test package: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest`.
Reproduce playback concurrently with refresh of a genuinely large synthetic
subscription list. Preserve personal apps, subscriptions, and watch history.
Fleet owns remote collection and device tests; no overlapping device worker.

Prepared worktree: `/home/user/.t3/fleet-dev-0.1.2/worktrees/PipePipe/t3-3d5de02e`.
Root branch: `t3/fix-playback-subscription-refresh`.
Root starting commit: `7f8d030f6f04ca97c95d57bddcf62cee3352433a`.
Client starting gitlink: `da54421e6878aef59520e80b21dfb5539bcef530`.
Extractor starting gitlink: `a1aa6841e7868c72c39bf119bf992dc83b5176b1`.
Prepared extractor HEAD was already `28a1a5ee889fadb36a435c43e0bc9483b59bb3bf`,
with an empty worktree and staged deletions. This pre-existing state was preserved.
Client was initially uninitialized, then cloned from the local original client
repository into this worktree on `fix/playback-subscription-refresh` at its
starting gitlink. The original checkout was not changed.

## Attachment evidence (sanitized)

Private attachment original name: `Error in PipePipe .queue.devicetest 272d2de259c9.txt`.
Raw attachment is not committed or copied into this repository. SHA-256:
`596f738cd4a05e45ce17244f1515407f0d7e151d0dc0c2b7661ae38c129eace8`.

- Lines 1–15: ANR, versionCode `100000304`, target SDK 36. Input dispatch
  timeout after 5,000 ms waiting for `FocusEvent(hasFocus=false)`.
- Lines 19–32: earlier input timeout for a MotionEvent, another process PID,
  approximately 218 seconds before this event.
- Lines 11–14: RSS 6,867,632 KiB, high-water RSS 7,782,760 KiB,
  anonymous RSS 6,652,484 KiB. These establish severe memory use, not its cause.
- Lines 34–388: target PID 23166; initial collection at
  `2026-11-11 19:52:21 +1100`. Tombstoned reports failure at line 39 and
  a failed status response at line 242. Only waiting-channel entries with
  `ptrace_stop` appear for the app; **there is no app Java stack trace**.
- Lines 18641–18648: ANR summary confirms the target activity and timeout.
  Stacks from other processes elsewhere in the attachment are not app stacks.

The filename's abbreviated revision is a provenance lead, not verified source
identity. Candidate `272d2de259c9` is absent from the local client object store.
The historical Nov 5 APK is not assumed to match this attachment.

## Source synchronization

Fleet fetched current remote source and supplied local bundles. Current fork root
`88d69d469361a930fe6304e4db202797f295f691` was merged without rewriting history,
yielding root `44dd8a28a13d2c80b17f44d466ebbd55f7f2059c`.
Latest upstream root `3fd38c6dbdfa1d29c97d9d5b1344836347793ec3` is already an
ancestor of that fork root. Client advanced to current fork
`0a59c6264a4746efad9d98a5353efab4dab5bc3a`, then merged latest upstream
`118ffc86baa811edae4d5659bbba7835f8ba6a92`, yielding
`d115054f4716b142950e9a7dbce009935f02f4a9`. No merge conflicts.
Extractor origin main remains `28a1a5ee889fadb36a435c43e0bc9483b59bb3bf`;
the newer fork root already pins that revision.

Release metadata for `v5.5.1000003` matches the attachment's versionCode, package,
and target ABI and points to root `88d69d4` / client `0a59c626` / extractor
`28a1a5e`. Its arm64 APK hash is
`d54822461699e895a0e9a7ceff4b765a5ab8aa5bd959bcf7ea4e61b344f7f843`.
This is a source-provenance inference from matching version metadata, not a hash
match to the original failing APK. The filename suffix remains unresolved.

One initial local root-bundle import unexpectedly triggered Git's recursive
client fetch from GitHub. It was read-only; subsequent bundle imports explicitly
disabled recursion. Remote server/device access remained exclusively with Fleet.

## Reproduction fixture

Client fixture tip `4142337e4174f84ece07cc62f12e08c418341918` adds tests only
(initial fixture commit `d99fc7ea97280314ac62976989126cbb44cdc4dd`).
`SabrPlaybackSmokeTest#playbackDuringLargeSubscriptionRefresh` performs real
online YouTube extraction and production SABR resolution, waits for decoded video
and advancing audio, then invokes the production feed manager over 1,000 distinct
synthetic RSS channels with 20 entries each. It asserts playback advances during
refresh and successful results for every channel. A periodic main-looper
heartbeat must be acknowledged within 1.5 seconds; all 20,000 distinct parsed
entries and empty extraction-error lists are verified. All other downloader requests,
including streaming SABR bodies, are delegated unchanged.

The fixture refuses any application ID except `.queue.devicetest.refresh` and
uses an in-memory Room database, restoring the previous singleton, downloader,
and changed RSS preference afterward. It does not load personal subscription
data. This exercises dedicated RSS extraction, not full channel-tab extraction,
and cannot by itself prove the original ANR's cause or resolution.

Fleet preflight found Samsung SM-G960F (`starlte`), Android 17 / API 37, security
patch `2026-10-01`. This differs from the attachment's Google `blazer` device.
Neither existing dedicated app process was running. Installed diagnostic release
versionCode `100000204` differs from the attachment. Read-only preflight acquired
and renewed its exclusive lease, explicitly released it, confirmed broker idle,
and removed its token; existing app data was untouched. These are preflight
receipts, **not application-test passes**.

The initial SDK37 absence report was corrected by Fleet: the installed platform
directory is `android-37.0`, rather than `android-37`. No SDK installation was
needed. Both baseline and integrated debug app/test APKs compiled successfully with:

```bash
bash ./gradlew --no-daemon --offline --console=plain --max-workers=2 \
  -Dorg.gradle.jvmargs=-Xmx4g \
  -DdebugPackageSuffix=.queue.devicetest.refresh \
  :app:assembleDebug :app:assembleDebugAndroidTest
```

Baseline production source is `0a59c626` with test-only patch SHA-256
`d7c06f84d40d7284830f82787aab782e3f4268a69bf7970f7850617c12e50d78`;
integrated source is `4142337e`. Each build used 86 Gradle tasks, with no compile
failure. Baseline production-only compilation also passed (19 tasks).
These are compile results, not executed application tests.

Package: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.refresh`, ABI arm64,
versionCode `111004`; debug certificate SHA-256
`bfadb6be9109016e35054c9591542ffc14df0c360eb8d635b595b1716ae043ce`.

| Build | App APK SHA-256 | Instrumentation APK SHA-256 |
| --- | --- | --- |
| Baseline | `9d7b1de3eadedeace5085e45dd1ededc9347f96069d022c3f476136ab998566e` | `8f04ca68f1b45acdfd3bae35c81b57d45db8a4d87c6eccaccf63c992117945a1` |
| Integrated | `ff9632a28d4c48f9d49c3239aa67c311e02d77f3e096f7c0e95f08700c6179a6` | `1cb38c4555e0204d278365cb395d8986f465091a4826da57f9136157327986a5` |

One independent read-only review found gaps in the initial fixture: net playback
advancement could hide an input stall; parsed entry/error counts were unchecked;
and cleanup could stop at the first exception. The reviewed follow-up adds a
main-looper heartbeat, checks parsed results, and rolls back constructor failure
with nested-finally restoration. Remaining limitation: playback uses standalone
ExoPlayer/SurfaceTexture and does not recreate the original MainActivity input
window or embedded player UI. No review of an application fix is claimed.

The first device harness attempt failed at its pre-install `pm path` probe because
the fresh diagnostic package was absent (exit 1, empty output, retained session).
No app test ran in that attempt. It explicitly released and confirmed idle;
Fleet handled expected absence and retried. Phase 1 completed:

- Baseline standalone stress: **1/1 passed**, 90.239 seconds.
- Integrated standalone stress: **1/1 passed**; its log verifies 1,000 distinct
  subscriptions, 20,000 entries, 1,000 results, refresh elapsed 42,364 ms.
- Integrated `FeedLoadIsolationTest`: **3/3 passed**.
- Integrated `FeedRefreshRoutingTest`: **3/3 passed**.
- Seventeen memory/thread samples per stress run. Baseline sampled maximum
  meminfo RSS 541,884 KiB and PSS 385,105 KiB; integrated RSS 537,512 KiB and
  PSS 379,968 KiB. Each reached 121 observed threads. These are sampled maxima,
  not continuous peak measurements or a performance comparison.

The original 6,867,632 KiB RSS and input ANR were **not reproduced before upstream**.
Standalone fixture passes do not verify upstream resolution of the reported bug.

Fleet's authoritative phase-1 completion session explicitly released successfully
at `2026-11-11 09:31:36 UTC` (exit 0, `status:cleaning`), reached idle at
`09:31:37 UTC`, and removed its token. Supported process queries confirmed no
fresh task process/instrumentation remained; both fresh test packages were
removed and absence confirmed. Earlier staging timeout/stale-release evidence
is retained and is not used as explicit-release proof. Existing diagnostic and
personal data were preserved. Sanitized Fleet receipts are in its scoped local
task directory (`PHASE1-RECEIPT.md`, `explicit-release-quiescence-proof.json`).

## Actual MainActivity continuation

Same implementation owner continues; no extra implementation worker or review.
Test-only client `0695e9de27` adds `MainActivityRefreshReproTest` and production
queue-table initialization to the isolated Room callback. The next controlled
scenario uses the actual MainActivity, VideoDetailFragment and PlayerService,
the actual feed refresh button/service, five refresh cycles of 1,000 synthetic
RSS subscriptions, injected swipe input during refresh, and feed/detail view
recreation. It records Java/native memory and the main thread's stack on a
heartbeat stall. This test must compile and execute before any result claim.
RSS extraction remains a material limitation if the original user used full
channel-tab extraction. No production behavior has been changed.

Source retention/contention investigation so far:

- `FeedLoadManager` buffers database writes by 20, then `toList()` retains all
  `FeedUpdateInfo`/stream lists until completion and flattens them. This scales
  with total extracted results even for foreground refresh, whose subscriber
  discards the result. It is a measurable retention lead, **not the proven ANR
  cause**. NotificationWorker separately needs new-stream results.
- `FeedUpdateInfo` copies lightweight metadata instead of holding ChannelInfo,
  while `InfoCache` bounds entries at 60. Full channel tabs can still carry
  larger raw response payloads than synthetic RSS.
- FeedViewModel throttles progress/database updates; feed queries limit visible
  streams to 500. The UI and service lifecycle must be observed under repeated
  refresh rather than inferred from standalone ExoPlayer.
- Six extraction rails and scheduler switches bound extraction concurrency;
  blocking network extraction and main-thread event delivery remain contention
  leads. No app blocked stack has yet connected those leads to the original ANR.

## Pending evidence and gates

1. Fleet: refresh current source/device owner metadata and provide candidate
   provenance plus latest fork/upstream root, client, and extractor source.
2. Record upstream SHAs and integrate into isolated branches without losing
   fork features. Reproduce before integration where feasible, then retest.
3. Collect target thread/memory evidence during playback and large refresh.
   Result retention and extraction concurrency are investigation leads only.
4. Make a causal fix if still needed, with a meaningful regression test.
5. Fleet: verify on actual device using the current broker skill, renewable
   exclusive lock, serialized commands, reversible synthetic dataset; record
   device, APK/source hashes, results, cleanup, lock release and quiescence.
6. Push only verified commits to the correct fork refs (module before root),
   with identity and remote-ref verification. No push while verification blocked.

No application device-test pass, verified causal fix, or remote push is claimed
by this interim record. Local whitespace checks pass in root and client.
