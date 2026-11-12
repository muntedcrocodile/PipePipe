# Playback/refresh fix release promotion

The user authorized priority promotion to main and a normal signed GitHub Release
on November13 (Sydney), including latest upstream. The earlier scoped branch
pushes correctly did not run the main-only release workflow; they were not CI
release failures. The prior published release was v5.5.1000003.

## Sources

| Source | SHA |
| --- | --- |
| Fork root main before promotion | `88d69d469361a930fe6304e4db202797f295f691` |
| Fork client main before promotion | `0a59c6264a4746efad9d98a5353efab4dab5bc3a` |
| Verified fix root before new upstream integration | `73461508b933efaa05d4d1627c537acb7e301fab` |
| Verified fix client before integration | `639b085f5c16da9d236d5cb048f193fa9db159c8` |
| Latest upstream root main (unchanged, already ancestor) | `3fd38c6dbdfa1d29c97d9d5b1344836347793ec3` |
| Latest upstream client default branch dev | `872c0d6553ec1e4f07501e635332520a534946c9` |
| Latest upstream extractor main | `21995900b94eb78794aa29631fc7325fa22f04dc` |
| Integrated client merge | `0c982c55d345cc242812444baad19dc5d78f36ac` |

Fleet fetched the upstream refs into isolation and supplied local bundles. Root
and client history preserve the earlier contention and retention fixes. Extractor
advances from28a1a5e to21995900 without custom/vendor commits. The prepared local
extractor's old HEAD and pre-existing staged deletions remain untouched; root
records the new gitlink and clean build/CI contexts check out that exact pin.

Client upstream adds the empty-uploader fix, null-safe enqueue player selection,
local-settings cleanup and5.6.0-beta1 version. Merge conflicts were resolved to
preserve the fork's pending-open lifecycle protection, persistent queue feedback
and longpress queue controls. The generic enqueue selection incorporates the
upstream null-safe active mode fallback. Other fork behavior was not rewritten.
Extractor updates include uploader-name fixes and Bilibili short-room/captcha
handling. These are genuine upstream deltas, not claimed unchanged phone-tested
bytes. The prior seven full450/1080p checks establish the fixes before these small
upstream deltas; the exact original multi-GiB/launcher crash cause remains unproven.

The release version parser now accepts a literal prerelease suffix in the upstream
default while allocating the same numeric fork major.minor.counter. Four focused
Python tests cover beta/stable parsing, invalid/dynamic/duplicate declarations,
version limits and increasing ABI codes. Workflow identity, offset, package and
signer are unchanged. No signing secrets were read/exposed or replacement key made.

## Validation and publication boundary

Local parser tests and Bash syntax passed. Fleet performs focused integrated
compilation and existing queue-policy JVM checks; no unchanged phone suite or
extra optimized local build is required. The established GitHub workflow builds
and verifies all four signed optimized APKs before publication. Main promotion
is module-first/root-next with fast-forward ancestry and remote readbacks; one
root main push is the sole release trigger, without a duplicate dispatch.

Expected package `InfinityLoop1309.NewPipeEnhanced.queue.devicetest`, signer
`5644fffef9eebff9f4446e6bbd8844d225f03879511f88bc3502f3a42812eb49`.
The workflow must publish a normal non-draft/non-prerelease latest release with
four ABI APKs, release-manifest.json and SHA256SUMS. Actual run/tag, source pins,
versions, downloaded checksums and APK certificate/manifest verification are
recorded separately in the final release receipt. No release is claimed here
before those terminal checks complete.

Fleet receipt scope: `local/tasks/pipepipe-release-promotion-20261113/`.
No device operation, personal data mutation, unrelated service interaction,
force push, upstream/vendor write, unrelated PR merge or Matrix delivery is part
of this promotion.
