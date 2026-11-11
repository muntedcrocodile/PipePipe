# Full extraction during 1080p playback: continuation

The user clarified the original scenario: approximately 450 subscriptions, fast/RSS
fetching disabled, and 1080p playback. They reported whole-phone slowdown and
occasional launcher crashes and authorized a plausible narrow fix if the exact
crash cannot be recreated. These symptoms suggest investigating memory pressure;
they do not establish a memory cause by themselves.

The earlier [contention investigation](playback-subscription-refresh-anr.md) remains
valid for its tested RSS scenario. Its 13 passes do not establish full-extraction
or original multi-GiB crash resolution. The previously published root
`9815dd0345d7571a04833e9f5ecc8c6928c79bef` and client
`d78aa788c4cae92fe57a44687174881d6fa3b1ff` are preserved ancestors.

## Source-supported retention paths

The manual FeedLoadService ignores the list returned by FeedLoadManager. However,
the loader collects every stored batch with `toList()` and flattens it at the end.
Thus every completed channel's stream list and computed new-stream list remain
reachable until the entire refresh completes. This grows with subscription and
entry counts, rather than just active work.

Full extraction previously called the UI ExtractorHelper channel/tab wrappers
with `forceLoad=true`. That bypasses cache reads but still inserts fresh results
in the shared navigation cache. The cache has a 60-entry count limit, not a byte
budget. Full extraction data can therefore remain reachable after persistence
and can displace playback/navigation entries. This is a bounded cache contribution,
not evidence that it accounts for the original multi-GiB footprint. The current
extractor's channel link handlers are not assumed to retain raw JSON merely
because an older FeedUpdateInfo comment mentions that possibility.

Default RxJava hand-off prefetch can also retain completed channel results while
SQLite writes are slower than extraction. The extraction rail count is six.

## Narrow candidate

Manual service refresh sets `retainResults=false`: storage, errors, progress and
post-processing still run, but stored batches are discarded before collection.
The notification worker retains its existing results, including new-stream lists.
Full channel/tab loads use the same extractor entry points directly without the
navigation cache wrappers. Existing cache entries are not globally cleared.
Sequential merge and main/I/O hand-offs each use prefetch one. Extraction still
uses six rails and channel-atomic writes from the prior fix.

This trades some producer/consumer overlap and navigation-cache warming for lower
retained extraction data. It does not reduce playback resolution, change queue
semantics, drop streams, impose subscription limits, or alter extractor code.
Notification callers still retain results; error aggregation also remains.

## Validation plan and limits

Test-only baseline `3f0e0797f6` adds synthetic full browse JSON parsed by the real
ChannelInfo and ChannelTabInfo implementations. The full fixture seeds 450 unique
subscriptions with 100 stream entries/channel for UI diagnostics and expects 900
browse requests per cycle. Playback uses the actual MainActivity/PlayerService,
network video, real refresh service, injected input and view recreation. An
explicit decoded video-format height check requires 1080p; setting the preference
alone is insufficient. Memory and heartbeat observations are diagnostic, not a
controlled performance comparison or a license to claim exact crash reproduction.

Separate regressions check full extraction/cache behavior and stored stream/new
video notification correctness with and without retained results. Test data and
preferences belong only to a fresh `.queue.devicetest.refresh` package and a
uniquely named reversible database. Fleet is the sole remote/device operator,
using the installed broker contract and an exclusive renewable lease.

No personal subscription lists, backups, original raw logs or viewing data are
part of the fixture or this document. Hardware and synthetic response-size limits
remain relevant to the original Google-device crash.

The initial fixture failed on localized relative-date parsing, before the cache
assertion. Diagnostic baseline `8ec4e8eb73` exposed `Could not get upload date` /
`Unable to parse the date: 1 minute ago`. Corrected test-only baseline
`41215d965d` uses the existing ISO-date fallback, parsed without partial errors,
and failed at the expected navigation-cache retention assertion. Production source
for these baselines remains identical to d78.

The baseline UI attempt could not resolve `www.youtube.com` during live stream
extraction. It reached neither 1080p decoding nor subscription refresh and is not
an application reproduction. Its fresh packages/processes/instrumentation were
removed, and its lease explicitly released to idle.

Fixed client `62e5a35ca32c3808ea3617ca1fcba0f502e00d60` subsequently established
decoded 1080p and passed both full-extraction UI cycles, with advancing playback,
injected input and view recreation. Two memory regressions and three routing
checks passed; debug and optimized release compilation passed. The baseline DNS
failure was not repeated as an app failure or counted as a before/after memory
comparison. The final client adds only a separate 450-channel persistence test;
its production app bytes match the UI-tested build. Final provenance and cleanup
receipts were audited before the scoped publication instruction.

## Exact source and artifacts

| Revision | SHA |
| --- | --- |
| Root before continuation | `9815dd0345d7571a04833e9f5ecc8c6928c79bef` |
| Client before continuation | `d78aa788c4cae92fe57a44687174881d6fa3b1ff` |
| Corrected test-only baseline | `41215d965dbf7352bbe17bb50a34067dc537f8e7` |
| UI/release-tested client | `62e5a35ca32c3808ea3617ca1fcba0f502e00d60` |
| Final client, additional test only | `639b085f5c16da9d236d5cb048f193fa9db159c8` |
| Extractor, unchanged | `28a1a5ee889fadb36a435c43e0bc9483b59bb3bf` |

The upstream integration and before/upstream/integrated SHAs from the earlier
report remain ancestors; no upgrade, rewrite or vendor change was added here.
Worktree `/home/user/.t3/fleet-dev-0.1.2/worktrees/PipePipe/t3-3d5de02e`, root branch
`t3/fix-playback-subscription-refresh`, client branch
`fix/playback-subscription-refresh`. The pre-existing dirty extractor was preserved.

Device: Samsung SM-G960F/starlte, Android 17/API 37, server1 normal UID1000 through
Fleet alone. Fresh app `InfinityLoop1309.NewPipeEnhanced.queue.devicetest.refresh`
and instrumentation `.refresh.test`; versionCode111004/versionName5.5.0,
targetSDK36/compileSDK37. Debug signer SHA256
`bfadb6be9109016e35054c9591542ffc14df0c360eb8d635b595b1716ae043ce`.

| ARM64 artifact | SHA256 |
| --- | --- |
| Baseline debug app (prior fixed contention binary) | `94b8790f532de6af49d1227f8b3b6b2d1d80a3d74a0f3b52c573d120404d96b4` |
| New fixed debug app, identical at62e5/639b | `8ab9e033d158eb1e687c2a6da81c2a894a09f202e9487cb718fad6c19c4a3798` |
| UI-tested62e5 instrumentation | `481c5c0f1d51ba39471b3c0966237dc6c1116c8ffccd36e4f6010503b737fe42` |
| Final639b instrumentation | `6ea25c5d7807848acdf3bb502243356de98d20bbaff1fc86c801dcebef426180` |
| Optimized unsigned release | `43307c82981805bdeb8c9a57343ea901b2007c24b91f38edc66d5c52f74aa56d` |

## Terminal outcomes and commands

Seven scoped checks passed across separate runs, not a single seven-test suite:

| Check | Outcome / JUnit time |
| --- | --- |
| Full-extraction cache + persistence/new-video notification regressions | 2/2,4.153s |
| Actual MainActivity/full450/1080p UI, two cycles | 1/1,321.226s |
| Refresh routing | 3/3,0.045s |
| Additional manual450 full-extraction persistence | 1/1,130.658s |

The UI run asserted900browse requests/cycle (1800total), advancing playback,
swipes and feed/detail view recreation. It used100entries/channel, full extraction,
unique on-disk Room with synchronous=FULL, cycles=2, require1080p=true and
cycleTimeoutSeconds=600. Decoded1080p was observed about21seconds into the run.
The additional non-playback check asserted900requests,45000stored streams,
terminal success without channel errors and zero retained result entries.

55 UI target-process samples: maximum sampledRSS899792KiB, PSS727623KiB,
observedVmHWM946860KiB, maximum148threads. Main heartbeat assertions passed:
1500ms acknowledgement bound, scheduled every1second. No measured worst-frame
latency or controlled memory-reduction comparison is claimed. Aggregate memory
availability was collected; Android denied `/proc/pressure/memory`. The original
multi-GiB profile, whole-phone slowdown and launcher crash were not reproduced.

Builds used Bash/JDK25/SDK37 and the same offline Gradle options documented in the
prior report. Debug app+instrumentation:86tasks on frozen62e5 (start=endSHA).
Final instrumentation-only build:68tasks on frozen639b, apphash unchanged.
Optimized release:56tasks, source start=end62e5, exit0. No signing inputs were
available; it remained unsigned and was not installed, delivered or distributed.

```bash
bash ./gradlew --no-daemon --offline --console=plain --max-workers=2 \
  -Dorg.gradle.jvmargs=-Xmx4g -DdebugPackageSuffix=.queue.devicetest.refresh \
  :app:assembleDebug :app:assembleDebugAndroidTest
bash ./gradlew --no-daemon --offline --console=plain --max-workers=2 \
  -Dorg.gradle.jvmargs=-Xmx4g -DpackageSuffix=.queue.devicetest.refresh \
  :app:assembleRelease
```

Broker-mediated instrumentation selectors, package runner
`.refresh.test/androidx.test.runner.AndroidJUnitRunner`:
`org.schabi.newpipe.local.feed.service.FullExtractionMemoryTest` (first two checks
at62e5, new450method at639b), `FeedRefreshRoutingTest`, and
`MainActivityRefreshReproTest#actualPlayerAndFeedRepeatedRefreshWithInputAndViewRecreation`
(all in the same service package). No unchanged broad suite or additional reviewer
was run; production changes were self-reviewed and the previous independent
fixture review was not represented as a new production review.

## Current-session cleanup and publication scope

Corrected baseline session6a7f4d76:1acquire/1successfulrenew; fixed UI/regression
sessionec60e158:1acquire/4renews; final450session5123367b:1acquire/2renews.
Same-session continuity is supported by saved operation ledgers. Every session
explicitly released with exit0, reached idle, removed its token, verified target
processes/subprocesses and active instrumentation absent, and uninstalled both
fresh packages with absence checked. No lease is held. Original apps, subscriptions,
history and original remote checkout remained untouched. Earlier failed fixture
sessions also have their own release/quiescence receipts; stale state is not used
as current release proof.

Sanitized receipts live under Fleet
`local/tasks/pipepipe-playback-refresh-20261111/full-extraction/final-handoff/`:
summary, JUnit/build/APK/source records, bounded samples, actual acquire/renew and
explicit release/quiescence records. No original private attachment was copied.

GitHub identity and existing scoped fork refs were checked as muntedcrocodile,
clientd78/root9815. Publication updates only client
`refs/heads/fix/playback-subscription-refresh` followed by root
`refs/heads/t3/fix-playback-subscription-refresh`, with exact remote readbacks and
gitlink verification recorded separately. No force push, main/upstream/vendor
write, PR, merge, Matrix, APK delivery or release publication is included.

This is a source-supported memory-retention mitigation with meaningful regression
and requested-path validation. It is not a proven diagnosis or complete resolution
of the original Google-device memory/launcher crash. The user explicitly accepted
a plausible narrow fix when exact original-crash reproduction was unavailable.
