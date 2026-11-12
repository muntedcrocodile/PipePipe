#!/usr/bin/env python3
"""Verify only newly built public outputs; never open signing keys or secrets."""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile


PACKAGE = "InfinityLoop1309.NewPipeEnhanced.queue.devicetest"
CERT_SHA256 = "5644fffef9eebff9f4446e6bbd8844d225f03879511f88bc3502f3a42812eb49"
ABI_CODES = {"armeabi-v7a": 1, "x86": 2, "x86_64": 3, "arm64-v8a": 4}
ANDROID = "{http://schemas.android.com/apk/res/android}"


def require(condition: object, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def certificate_sha256(signature: str) -> set[str]:
    # Build Tools 37 changed human-readable signer labels. Hash the emitted
    # certificate DER instead; scheme-specific reports may repeat the same cert.
    require(
        re.findall(r"^Number of signers: ([0-9]+)$", signature, re.MULTILINE) == ["1"],
        "Expected exactly one APK signer",
    )
    certificates = re.findall(
        r"-----BEGIN CERTIFICATE-----\s*([A-Za-z0-9+/=\s]+?)\s*-----END CERTIFICATE-----",
        signature,
    )
    require(certificates, "Missing APK signing certificate PEM")
    return {
        hashlib.sha256(base64.b64decode(re.sub(r"\s+", "", cert), validate=True)).hexdigest()
        for cert in certificates
    }


def expected_version_name(base: int) -> str:
    require(1000001 <= base <= 20999999, "Invalid base version code")
    source = Path("PipePipeClient/app/build.gradle")
    try:
        defaults = re.findall(
            r"^[ \t]*def[ \t]+appVersionName[ \t]*=[ \t]*([^\r\n]*)",
            source.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    except OSError as error:
        raise SystemExit(f"Cannot read checked-in client default version: {source}") from error
    message = (
        f"Expected exactly one literal def appVersionName = \"MAJOR.MINOR.PATCH\" in {source}; "
        "use three numeric components without leading zeroes and an optional prerelease suffix"
    )
    require(len(defaults) == 1, message)
    match = re.fullmatch(
        r"""(["'])(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?\1[ \t]*;?[ \t]*(?://[^\r\n]*)?""",
        defaults[0],
    )
    if match is None:
        raise SystemExit(message)
    return f"{match[2]}.{match[3]}.{base}"


def main() -> None:
    base = int(os.environ["FORK_VERSION_CODE"])
    version = os.environ["FORK_VERSION_NAME"]
    tag = os.environ["FORK_RELEASE_TAG"]
    expected_version = expected_version_name(base)
    require(
        version == expected_version and tag == f"v{expected_version}",
        f"Version/tag mismatch: expected APK {expected_version} and tag v{expected_version}",
    )
    require(run("git", "rev-parse", "HEAD") == os.environ["GITHUB_SHA"], "Root commit mismatch")
    statuses = subprocess.check_output(
        ["git", "submodule", "status", "--recursive", "--", "PipePipeClient", "PipePipeExtractor"], text=True
    ).splitlines()
    require(statuses and all(line.startswith(" ") for line in statuses), "Submodule pin mismatch")

    sdk = Path(os.environ["ANDROID_HOME"])
    apksigner = sdk / "build-tools/37.0.0/apksigner"
    analyzer = sdk / "cmdline-tools/latest/bin/apkanalyzer"
    output = Path("PipePipeClient/app/build/outputs/apk/release")
    metadata = json.loads((output / "output-metadata.json").read_text())
    require(metadata["applicationId"] == PACKAGE, "Gradle output package mismatch")
    require(metadata["variantName"] == "release", "Expected the release variant")
    elements = metadata["elements"]
    require(len(elements) == len(ABI_CODES), "Expected all four ABI release APKs")
    mapping = Path("PipePipeClient/app/build/outputs/mapping/release/mapping.txt")
    require(mapping.is_file() and mapping.stat().st_size > 0, "Missing R8 release mapping")

    dist = Path("fork-release-dist")
    require(not dist.exists(), "Refusing to mix this run with previous release outputs")
    records = []
    files = []
    seen = set()
    for element in elements:
        filters = element["filters"]
        require(len(filters) == 1 and filters[0]["filterType"] == "ABI", "Unexpected APK split")
        abi = filters[0]["value"]
        require(abi in ABI_CODES and abi not in seen, "Unknown/duplicate ABI")
        seen.add(abi)
        filename = element["outputFile"]
        require(Path(filename).name == filename and filename.endswith("-release.apk"), "Unexpected APK name")
        require("unsigned" not in filename, "Unsigned APK output")
        apk = output / filename
        code = base * 100 + ABI_CODES[abi]
        require(element["versionCode"] == code and element["versionName"] == version, "Gradle version mismatch")

        signature = run(str(apksigner), "verify", "--verbose", "--print-certs-pem", str(apk))
        require(certificate_sha256(signature) == {CERT_SHA256}, "APK signing certificate mismatch")
        manifest = ET.fromstring(run(str(analyzer), "manifest", "print", str(apk)))
        require(manifest.get("package") == PACKAGE, "APK manifest package mismatch")
        require(manifest.get(ANDROID + "versionCode") == str(code), "APK manifest version code mismatch")
        require(manifest.get(ANDROID + "versionName") == version, "APK manifest version name mismatch")
        app = manifest.find("application")
        require(app is not None and app.get(ANDROID + "debuggable", "false") == "false", "APK is debuggable")
        require(app.get(ANDROID + "testOnly", "false") == "false", "APK is test-only")
        with zipfile.ZipFile(apk) as archive:
            native_abis = {p.split("/")[1] for p in archive.namelist() if p.startswith("lib/") and p.endswith(".so")}
        require(native_abis == {abi}, "APK native libraries do not match its ABI")

        with apk.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        files.append(apk)
        records.append({"file": filename, "abi": abi, "version_code": code, "sha256": digest})

    require(seen == set(ABI_CODES), "Missing ABI release")
    require({apk.name for apk in output.glob("*.apk")} == {apk.name for apk in files}, "Unexpected extra APK output")
    # Nothing is staged/uploaded until every APK passes verification.
    dist.mkdir()
    for apk in files:
        shutil.copyfile(apk, dist / apk.name)
    report = {
        "tag": tag,
        "version_name": version,
        "base_version_code": base,
        "package": PACKAGE,
        "certificate_sha256": CERT_SHA256,
        "root_commit": os.environ["GITHUB_SHA"],
        "submodules": statuses,
        "run_url": f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
        "run_attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]),
        "r8_mapping_sha256": hashlib.sha256(mapping.read_bytes()).hexdigest(),
        "debuggable": False,
        "apks": sorted(records, key=lambda item: item["abi"]),
    }
    (dist / "release-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    checksums = []
    for path in sorted(dist.iterdir()):
        with path.open("rb") as stream:
            checksums.append(f"{hashlib.file_digest(stream, 'sha256').hexdigest()}  {path.name}\n")
    (dist / "SHA256SUMS").write_text("".join(checksums))
    (dist / "release-notes.md").write_text(
        f"Signed, R8-optimized fork release `{version}`.\n\n"
        f"Package: `{PACKAGE}`\n\nCertificate SHA-256: `{CERT_SHA256}`\n\n"
        f"Root commit: `{report['root_commit']}`\n\n[Build and pinned sources]({report['run_url']})\n\n"
        "Select the APK matching your device ABI; use the `arm64-v8a` asset for modern ARM phones. "
        "SHA256SUMS covers all APKs and release-manifest.json.\n\n"
        "Device validation uses the separately tested debug build. This optimized release is "
        "checked for package, signer, versions, ABI, and non-debuggable status; it has no device-test claim.\n"
    )
    print(f"Verified {len(records)} signed R8 release APKs for {PACKAGE} ({version}).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version-name", type=int, metavar="BASE", help="Print the expected APK version for this base")
    args = parser.parse_args()
    if args.version_name is not None:
        print(expected_version_name(args.version_name))
    else:
        main()
