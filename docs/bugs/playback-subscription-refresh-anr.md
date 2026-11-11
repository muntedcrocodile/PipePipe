# Playback during large subscription refresh: investigation

Status: investigation in progress; no verified fix or push.

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

No device test, lock acquisition, upstream integration, fixed SHA, or remote
push is claimed by this interim record.
