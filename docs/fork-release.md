# Signed fork releases

`.github/workflows/fork-release.yml` publishes installable, R8-optimized releases
of `muntedcrocodile/PipePipe` on every push to `main`, including changes under
`.github/`, documentation changes, and submodule updates. It also supports a fresh
manual `workflow_dispatch` on `main`. Both jobs require this exact repository and
branch, so copying the workflow upstream does not enable upstream publishing.
There are no pull-request triggers, path filters, or cancellation of older builds.

After a client change is merged, update and push the root client gitlink to `main`; a client-only push does not trigger this root workflow.

The root records exact client and extractor commits. CI builds the triggering root SHA and those recorded submodule SHAs with `--checkout`; it never follows `.gitmodules` branch hints or runs `git pull` or `submodule update --remote`. Only build submodules are initialized, avoiding the unrelated wiki. Nested build submodules are pinned recursively. The checked-in FFmpeg AAR and root composite build are used.

## Client version interface

`PipePipeClient/app/build.gradle` accepts optional Gradle project properties `forkVersionCode` and `forkVersionName`. The code is an integer base from 1 through 20,999,999; the name must be nonblank. Builds without overrides retain upstream defaults. CI supplies both, choosing base `1,000,000 + github.run_number` and name `<upstreamMajor>.<upstreamMinor>.<base>`.

The shared version validator in `scripts/fork-release-verify.py` reads the pinned
client's literal default `def appVersionName = "5.5.0"` without executing Gradle.
It requires exactly one declaration with a quoted numeric `MAJOR.MINOR.PATCH`
value and no leading zeroes (single quotes, an optional semicolon, and a trailing
line comment are also accepted). A missing, duplicate, dynamic, or unexpectedly
formatted default fails with a clear error. The major/minor components follow
that default; the patch component is replaced by the allocated base. Version
allocation, signing input validation, and APK verification use the same parser.

The existing ABI codes (`armeabi-v7a=1`, `x86=2`, `x86_64=3`, `arm64-v8a=4`) encode APK version codes as `100 * base + ABI`. The highest supported output is 2,099,999,904. Output metadata, manifest versions, filenames, and stable `BuildConfig.VERSION_CODE` use the overridden base/name. CI checks the actual APKs, so ignored overrides fail verification.

CI calls the existing client wrapper from `PipePipeClient`:

```bash
./gradlew :app:assembleRelease \
  --no-daemon --no-configuration-cache --no-build-cache --console=plain \
  -DskipFormatKtlint -DpackageSuffix=.queue.devicetest \
  -PforkVersionCode=1000001 -PforkVersionName=5.5.1000001
```

Retain the current release build's `minifyEnabled true` and
`proguard-android-optimize.txt`; this invokes R8 optimization. Resource shrinking
remains governed by the existing client build. The workflow requires a nonempty
release R8 `mapping.txt` in addition to the APK checks. JDK 25, SDK platform 37
(`platforms;android-37.0` in Google's current catalog), and Build Tools 37.0.0
are explicitly installed on the GitHub-hosted Ubuntu 24.04 runner. Wrapper
validation requires both wrappers to be present and runs before either executes.

## Signing identity and secrets

Configure these **repository Actions secrets** privately in the fork, using the
existing local signing identity; do not generate a replacement key:

| Secret | Value provided by the owner |
| --- | --- |
| `KEYSTORE_BASE64` | Base64 encoding of the existing signing keystore |
| `KEY_STORE_PASSWORD` | Existing keystore password |
| `KEY_ALIAS` | Existing signing key alias |
| `KEY_PASSWORD` | Existing signing key password |

The workflow decodes the keystore into a mode-600 file under a mode-700 temporary
directory in `RUNNER_TEMP` and exports `KEY_PATH` for the existing signing config.
Passwords and alias reach Gradle only through its existing environment interface,
not command-line arguments or Gradle property files. Shell tracing is disabled.
An EXIT/signal trap removes the keystore and private Gradle home on ordinary
success, build failure, or termination. A forcibly killed hosted job relies on
the disposable GitHub runner's teardown. Configuration/build caching is disabled
and configuration caches are removed; no signing configuration or keystore is
cached or uploaded. Only the build step receives signing secrets. The publisher
runs on a separate runner and receives the automatic `github.token` as `GH_TOKEN`.

Every APK must have exactly this identity:

- Application ID: `InfinityLoop1309.NewPipeEnhanced.queue.devicetest`
- Certificate SHA-256:
  `5644fffef9eebff9f4446e6bbd8844d225f03879511f88bc3502f3a42812eb49`

The release suffix is passed through the existing `-DpackageSuffix` interface.
The debug validation build uses the separate `.queue.devicetest.debug` package
and debug certificate. This optimized release updates the previously distributed
`.queue.devicetest` release using its existing certificate. `apksigner verify --verbose --print-certs` rejects
unsigned APKs, invalid signatures, extra signers, or a different certificate.
The APK manifest must also be non-debuggable and not test-only. Secrets missing
from an enabled fork fail the build; there is no unsigned fallback.

## Versions, reruns, and publication

For GitHub workflow run number `N`:

| Field | Allocation | First run (`N=1`) |
| --- | --- | --- |
| Gradle `forkVersionCode` base | `1000000 + N` | `1000001` |
| Android APK version code | `100 * base + abiCode` | `100000101` through `100000104` |
| Gradle `forkVersionName` | `<upstreamMajor>.<upstreamMinor>.<base>` | `5.5.1000001` |
| Git tag | `v<version_name>` | `v5.5.1000001` |

With the checked-in upstream default `5.5.0`, the first release's version name
`5.5.1000001` is newer than the installed `5.5.0` fork. The tag is the same standard
three-part version with a source-side `v` prefix, which Obtainium can normalize
to match Android's version name. No version extraction override or release-date
pseudo-version is required. Upstream major/minor changes are picked up from each
pinned client commit; retain or advance that prefix on subsequent main updates.

The patch counter and per-ABI Android version codes increase on every new
workflow run. The initial codes exceed the current upstream
`1110 * 100 + abiCode` codes. A base is capped at `20999999`, making the largest
allowed APK code `2099999904`, below the conservative 2,100,000,000 limit. This
leaves 19,999,999 distinct runs. Keep the workflow filename/identity and offset
stable; if its run counter is ever reset or the workflow is replaced, choose a
new offset above every previously published base within this budget.

Rerunning a failed run keeps its existing run number and allocated version. A
failed publisher can reuse its producing build's artifact name even when the
publish attempt changes. Once a tag/release exists, this workflow refuses to
reuse it or replace assets: use a new manual dispatch for a fresh version.
If an upload fails after tag creation, keep that version reserved and dispatch
a new run. API failures stop publication rather than being treated as no releases.

Build jobs run independently, so a newer push does not discard an older build.
Publish jobs use `concurrency.queue: max` to serialize release mutations without
the default single pending job being replaced. GitHub permits at most 100 pending
publish jobs in that group; normal pushes are retained within this service limit.
Since completion/queue order can differ from dispatch order, the publisher compares
all existing tags matching `^v[0-9]+\.[0-9]+\.([0-9]{7,8})$` and explicitly marks a
release latest only when no higher base counter exists. Comparing the captured
counter across all major/minor prefixes preserves run order when an upstream
version changes. Older completed builds still get their own release
without downgrading GitHub's latest release. A failed run needs fixing/rerunning;
an unbuildable push cannot produce an installable release. GitHub's own commit
skip directives and Actions availability also govern whether a push is scheduled.

Only the publish job has `contents: write`. It uses `gh release create` with the
automatic token, explicit repository and root commit target, and a new tag. It
creates a normal published release (no prerelease or draft flag), with no
third-party release action and no asset clobbering. Existing tag names are rejected
even when they have no release, so `--target` cannot accidentally publish a tag
pointing to another commit.

Each release contains exactly four signed standalone ABI APKs, `SHA256SUMS`, and
`release-manifest.json`. Checksums cover the APKs and JSON manifest. The manifest
records package, certificate, root/submodule commits, run URL/attempt, versions,
ABI, APK hashes, and R8 mapping hash. The same files plus release notes are kept
as a workflow artifact for 14 days. The publisher rechecks all file checksums
before uploading. Failed verification stages no files for upload.

For Obtainium, add `https://github.com/muntedcrocodile/PipePipe` as the GitHub source
URL and use normal releases. Matching standard source/APK version formats let
Obtainium detect the installed version without custom version settings. If APK
selection needs narrowing for a device, the ABI asset filter remains
`arm64-v8a.*-release\.apk$` for modern ARM phones. Every update retains the installed
package and certificate, while its version code increases. The public repository's GitHub
Releases assets are the durable update source; workflow artifact retention does
not remove release assets.

## Validation boundary

Debug device validation of feed refresh, Queue, and swipes is sufficient for the
requested functional testing and belongs to the parent task. This workflow builds
an optimized release and verifies its outputs without accessing a phone, emulator,
ADB, or device lease. It makes no claim that the optimized APK received device
testing. A real signed GitHub run still requires the owner-provided secrets and
the parent-integrated Gradle interface; local syntax/static checks cannot prove
those external prerequisites.

Local validation of this implementation: Bash/Python syntax and new-file
whitespace checks passed. Sixteen isolated fixture checks passed for output
staging/checksums, signer/unsigned APK rejection, submodule pins, ignored version
overrides, debuggable/wrong-package APK rejection, missing R8 mapping, temporary
signing-data permissions/cleanup on success and failure, missing signing inputs,
latest-version ordering, existing releases/tags, and GitHub API failure. These
checks used synthetic fixtures and stubbed Android/GitHub commands, with no real
keystore, device, release build, or publication.

The pre-release version-format follow-up passed 27 additional isolated checks:
major/minor extraction from the pinned client, clear failures for unexpected
defaults, increasing versions above the installed `5.5.0`, the existing Android
code ceiling, four-ABI metadata/manifest/checksum alignment, rejection of old or
mismatched versions/tags, signing-wrapper version validation, base-counter
publication ordering across upstream prefixes, duplicate release/tag and API
failure handling, and preservation of the parent's function type hints. All
Android, GitHub, and Gradle commands in these checks were stubs; no real signing
material or external mutations were involved.

Actionlint v1.7.12 parsed the workflow and checked all expressions successfully
with one narrowly scoped schema diagnostic excluded:

```bash
actionlint -shellcheck= \
  -ignore '^unexpected key "queue" for "concurrency" section\.' \
  .github/workflows/fork-release.yml
bash -n scripts/fork-release-build.sh
```

This actionlint release predates support for `concurrency.queue`; GitHub's current
official concurrency reference explicitly supports `queue: max`. The unfiltered
lint reports only that property as an unexpected key. No other lint diagnostic
was excluded. ShellCheck is not installed in the implementation environment.

Action pins were checked against the official releases: [checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1),
[setup-java v6.1.0](https://github.com/actions/setup-java/releases/tag/v6.1.0),
[upload-artifact v7.0.2](https://github.com/actions/upload-artifact/releases/tag/v7.0.2),
[download-artifact v8.0.2](https://github.com/actions/download-artifact/releases/tag/v8.0.2),
and [Gradle wrapper-validation v6.4.1](https://github.com/gradle/actions/releases/tag/v6.4.1).
Protocol references: [GitHub run counters](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts),
[GitHub concurrency queues](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency),
[GitHub CLI release creation](https://cli.github.com/manual/gh_release_create),
[Android versioning](https://developer.android.com/studio/publish/versioning),
[APK manifest analysis](https://developer.android.com/tools/apkanalyzer), and
[APK signature verification](https://developer.android.com/tools/apksigner).
Version detection follows [Obtainium's official app tracking documentation](https://wiki.obtainium.imranr.dev/app_tracking/),
which requires standard matching source and Android version formats and documents
normalization of a source-side `v` prefix.
SDK package names were checked in [Google's SDK repository catalog](https://dl.google.com/android/repository/repository2-3.xml);
the [Android 17 setup guide](https://developer.android.com/about/versions/17/setup-sdk)
uses `compileSdk = 37`.
