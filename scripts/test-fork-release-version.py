#!/usr/bin/env python3
"""Focused release-version contract checks; no Android tools, keys or network."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("release_verify", Path(__file__).with_name("fork-release-verify.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class ReleaseVersionTest(unittest.TestCase):
    def check_source(self, source, base=1000004):
        with tempfile.TemporaryDirectory() as directory:
            previous = Path.cwd()
            try:
                os.chdir(directory)
                path = Path("PipePipeClient/app/build.gradle")
                path.parent.mkdir(parents=True)
                path.write_text(source)
                return verify.expected_version_name(base)
            finally:
                os.chdir(previous)

    def test_prerelease_upstream_keeps_numeric_fork_version(self):
        self.assertEqual("5.6.1000004", self.check_source('def appVersionName = "5.6.0-beta1"'))

    def test_stable_and_quoted_defaults_remain_supported(self):
        for source in ['def appVersionName = "5.5.0"', "def appVersionName = '5.5.0'; // upstream"]:
            with self.subTest(source=source):
                self.assertEqual("5.5.1000004", self.check_source(source))

    def test_dynamic_duplicate_or_malformed_defaults_fail_closed(self):
        for value in ['"05.6.0"', 'project.version', '"5.6"', '"5.6.0-"', '"5.6.0-beta1" + suffix']:
            with self.subTest(value=value), self.assertRaises(SystemExit):
                self.check_source('def appVersionName = ' + value)
        with self.assertRaises(SystemExit):
            self.check_source('def appVersionName = "5.6.0"\ndef appVersionName = "5.7.0"')

    def test_counter_bounds_and_monotonic_android_codes(self):
        source = 'def appVersionName = "5.6.0-beta1"'
        self.assertEqual("5.6.1000005", self.check_source(source, 1000005))
        for base in [1000000, 21000000]:
            with self.subTest(base=base), self.assertRaises(SystemExit):
                self.check_source(source, base)
        self.assertGreater(100 * 1000004 + 4, 100000304)


if __name__ == "__main__":
    unittest.main()
