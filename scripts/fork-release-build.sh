#!/usr/bin/env bash
# The four signing secrets are provided only to this step, never as CLI arguments.
set +x
set -euo pipefail
umask 077

for name in KEYSTORE_BASE64 KEY_STORE_PASSWORD KEY_ALIAS KEY_PASSWORD FORK_VERSION_CODE FORK_VERSION_NAME; do
    if [[ -z "${!name:-}" ]]; then
        echo "Required signing/version input is missing: $name" >&2
        exit 1
    fi
done
[[ "$FORK_VERSION_CODE" =~ ^[0-9]{7,8}$ ]]
(( FORK_VERSION_CODE >= 1000001 && FORK_VERSION_CODE <= 20999999 ))
expected_version_name=$(python3 scripts/fork-release-verify.py --version-name "$FORK_VERSION_CODE")
if [[ "$FORK_VERSION_NAME" != "$expected_version_name" ]]; then
    echo "Fork version name must match the checked-in client default: $expected_version_name" >&2
    exit 1
fi

private_dir=$(mktemp -d "$RUNNER_TEMP/fork-release-private.XXXXXXXX")
cleanup() {
    # Gradle's configuration can contain signing credentials; never retain/cache it.
    rm -rf -- "$private_dir" PipePipeClient/.gradle/configuration-cache PipePipeExtractor/.gradle/configuration-cache
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

export KEY_PATH="$private_dir/release.keystore"
export GRADLE_USER_HOME="$private_dir/gradle-home"
printf '%s' "$KEYSTORE_BASE64" | base64 --decode > "$KEY_PATH"
unset KEYSTORE_BASE64
[[ -s "$KEY_PATH" ]]

# Run from the current root's composite build, including the pinned extractor/AAR.
# A release mapping must be freshly generated; metadata checks run after secrets
# and the entire private Gradle home have been removed.
(
    cd PipePipeClient
    ./gradlew :app:assembleRelease \
        --no-daemon --no-configuration-cache --no-build-cache --console=plain \
        -DskipFormatKtlint -DpackageSuffix=.queue.devicetest \
        "-PforkVersionCode=$FORK_VERSION_CODE" \
        "-PforkVersionName=$FORK_VERSION_NAME"
)
