# Unavailable-service feed hotfix — 5 November 2026 (UTC)

Client: `0a59c6264a4746efad9d98a5353efab4dab5bc3a`. Tested source tree: `fa4da02a05a9b5d51df6b645db58cc60417b8764`.

The published `5.5.1000002` release reproduced the reported What’s New error on the physical Samsung phone when a service-3 subscription was included with working YouTube subscriptions. REPORT confirmed `ExtractionException: There's no service with the id = "3"`. ID 3 is reserved for the PeerTube plugin.

Service lookup ran before the per-subscription error boundary. The fix defers service lookup/scheduling/extraction within that boundary and reports failures with their subscription ID and original cause. Successful channels continue. Failed subscriptions are retained for a later plugin installation/retry. Database errors remain visible as refresh failures.

**127/127 instrumentation tests passed on Android 17/API 37, zero failures/errors/skips**, including three new real-registry/RSS-extractor regressions. **8/8 JVM tests passed**. The new regressions passed separately too. The target debug APK SHA-256 is `99c3f6356e0d52616dce0167ccf54c7d980f2ba1f109cc32f87dad9e33e023a3`; test APK is `72d1937b9f27dd3a432272ba0ac3a3bfce021fe1decda2acaf3a38028d16ad7a`.

The owner requested immediate publication after these passes. Additional manual refresh/export checks were curtailed; no live mixed-database success is claimed for this corrected candidate. Original diagnostic data is restored and device ownership released separately from CI. The optimized release is built and verified by the existing main-push workflow; no optimized-device pass is required under AGENTS.md.

Private evidence: `/home/user/.local/share/pipepipe-service-isolation.k0rox8i7`. Historical failures and earlier candidate evidence remain preserved.
