#!/usr/bin/env python3
"""Unit tests for the text parsers behind Maintenance → Repair / History and Logging → Journal.

No root, no GUI, no network: sample text in, parsed result out. Run from the repo root:
    python3 -m unittest tests/test_parsers.py
"""

import os
import sys
import tempfile
import types
import unittest

APP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "usr", "share", "archlinux-tweak-tool")
sys.path.insert(0, APP_DIR)

# functions.py pulls in GTK and reads the running system; the parsers only log through it
sys.modules["functions"] = types.SimpleNamespace(
    log_info=lambda *a, **k: None, log_warn=lambda *a, **k: None, log_error=lambda *a, **k: None,
    log_subsection=lambda *a, **k: None, debug_print=lambda *a, **k: None, GLib=None, Gdk=None)

import journal_view  # noqa: E402
import pkg_history  # noqa: E402
import pkg_repair  # noqa: E402


class TestRepairParser(unittest.TestCase):
    """pacman -Qkk warnings → packages with damaged or wrong-permission files."""

    QKK = "\n".join([
        "warning: nano: /usr/share/nano/c.nanorc (No such file or directory)",
        "warning: lshw: /usr/share/applications/gtk-lshw.desktop (SHA256 checksum mismatch)",
        "warning: lshw: /usr/share/applications/gtk-lshw.desktop (Size mismatch)",
        "warning: lshw: /usr/share/applications/gtk-lshw.desktop (Modification time mismatch)",
        "warning: foo: /usr/bin/foo (Permissions mismatch)",
        "backup file: pacman: /etc/pacman.conf (SHA256 checksum mismatch)",
        "warning: tuned: /etc/tuned/ppd_base_profile (SHA256 checksum mismatch)",
        "warning: libvirt: /var/log/swtpm/libvirt/qemu (GID mismatch)",
        "warning: intel-ucode: /boot/intel-ucode.img (No such file or directory)",
        "warning: filesystem: /usr/lib/os-release (SHA256 checksum mismatch)",
        "warning: libutempter: /usr/lib/utempter/utempter (Permissions mismatch)",
        "warning: opera: /usr (Permissions mismatch)",
        "warning: cups: /usr/lib/cups/backend/ipp (SHA256 checksum mismatch)",
        "warning: bar: /usr/bin/bar (Modification time mismatch)",
        "nano: 192 total files, 1 altered file",
    ])

    def test_real_damage_is_found(self):
        problems = pkg_repair.parse_qkk(self.QKK)
        self.assertEqual(problems["nano"]["damaged"], ["/usr/share/nano/c.nanorc"])
        # several reasons for one file count once
        self.assertEqual(problems["lshw"]["damaged"], ["/usr/share/applications/gtk-lshw.desktop"])
        self.assertEqual(problems["foo"]["permissions"], ["/usr/bin/foo"])

    def test_intentional_changes_are_skipped(self):
        problems = pkg_repair.parse_qkk(self.QKK)
        # backup files, /etc, /var, /boot, os-release, utempter, directories, noisy packages, mtime only
        for pkg in ("pacman", "tuned", "libvirt", "intel-ucode", "filesystem", "libutempter", "opera", "cups", "bar"):
            self.assertNotIn(pkg, problems, pkg)
        self.assertEqual(sorted(problems), ["foo", "lshw", "nano"])

    def test_hook_targets_are_skipped(self):
        output = "\n".join([
            "warning: niri: /usr/share/wayland-sessions/niri.desktop (SHA256 checksum mismatch)",
            "warning: archlinux-appstream-data: /usr/share/swcatalog/icons/a.jxl (Size mismatch)",
            "warning: nano: /usr/share/nano/c.nanorc (No such file or directory)",
        ])
        problems = pkg_repair.parse_qkk(output, ["/usr/share/wayland-sessions/niri.desktop"],
                                        {"archlinux-appstream-data"})
        self.assertEqual(sorted(problems), ["nano"])

    def test_untranslated_output_only(self):
        # pacman in Dutch: the scan forces LC_ALL=C, so translated lines must never be read as findings
        self.assertEqual(pkg_repair.parse_qkk("waarschuwing: nano: /usr/share/nano/c.nanorc (Bestand bestaat niet)"),
                         {})

    def test_only_kiro_hooks_count(self):
        with tempfile.TemporaryDirectory() as hooks:
            files = {
                "kiro-hide-session.hook": "[Trigger]\nType = Path\nTarget = usr/share/wayland-sessions/x.desktop\n",
                "kiro-jxl.hook": "[Trigger]\nType = Package\nTarget = archlinux-appstream-data\nTarget = !skip\n",
                "30-systemd-udev.hook": "[Trigger]\nType = Path\nTarget = usr/lib/udev/rules.d/*\n",
                "bootloader-systemd-boot.hook": "[Trigger]\nType = Package\nTarget = systemd\n",
            }
            for name, text in files.items():
                with open(os.path.join(hooks, name), "w") as hook:
                    hook.write(text)
            patterns, packages = pkg_repair.hook_targets((hooks,))
        self.assertEqual(patterns, ["/usr/share/wayland-sessions/x.desktop"])
        self.assertEqual(packages, {"archlinux-appstream-data"})


class TestHistoryParser(unittest.TestCase):
    """pacman.log → transactions, and older versions in the package cache."""

    LOG = [
        "[2026-11-26T06:39:20+0100] [PACMAN] Running 'pacman -Syyu'",
        "[2026-11-26T06:39:20+0100] [ALPM] transaction started",
        "[2026-11-26T06:39:21+0100] [ALPM] upgraded zstd (1.5.7-3 -> 1.6.0-1)",
        "[2026-11-26T06:39:21+0100] [ALPM] removed oldpkg (2.0-1)",
        "[2026-11-26T06:39:22+0100] [ALPM-SCRIPTLET] some scriptlet output",
        "[2026-11-26T06:39:22+0100] [ALPM] transaction completed",
        "[2026-11-26T06:40:00+0100] [PACMAN] Running 'pacman -S broken'",
        "[2026-11-26T06:40:00+0100] [ALPM] transaction started",
        "[2026-11-26T06:40:01+0100] [ALPM] transaction failed",
        "[2026-11-26T06:44:26+0100] [PACMAN] Running 'pacman -U /tmp/nano-9.2-1-x86_64.pkg.tar.zst'",
        "[2026-11-26T06:44:26+0100] [ALPM] transaction started",
        "[2026-11-26T06:44:26+0100] [ALPM] downgraded nano (9.3-1 -> 9.2-1)",
        "[2026-11-26T06:44:26+0100] [ALPM] transaction completed",
    ]

    def test_transactions_newest_first(self):
        transactions = pkg_history.parse_log(self.LOG)
        self.assertEqual(len(transactions), 2)  # the failed, empty one is dropped
        self.assertEqual(transactions[0]["command"], "pacman -U /tmp/nano-9.2-1-x86_64.pkg.tar.zst")
        self.assertEqual(transactions[1]["time"], "2026-11-26 06:39")

    def test_entries(self):
        older = pkg_history.parse_log(self.LOG)[1]["entries"]
        self.assertEqual(older[0], {"action": "upgraded", "pkg": "zstd", "old": "1.5.7-3", "new": "1.6.0-1"})
        self.assertEqual(older[1], {"action": "removed", "pkg": "oldpkg", "old": "2.0-1", "new": "2.0-1"})

    def test_limit(self):
        self.assertEqual(len(pkg_history.parse_log(self.LOG, limit=1)), 1)

    def test_cache_lookup(self):
        with tempfile.TemporaryDirectory() as cache:
            for name in ("zstd-1.5.7-3-x86_64.pkg.tar.zst", "zstd-1.5.7-3-x86_64.pkg.tar.zst.sig",
                         "python-requests-2.32.0-1-any.pkg.tar.zst", "python-requests-file-2.1.0-3-any.pkg.tar.zst",
                         "vim-2:9.1.0-1-x86_64.pkg.tar.zst"):
                open(os.path.join(cache, name), "w").close()
            index = pkg_history.cache_index([cache])
        self.assertTrue(pkg_history.find_cached("zstd", "1.5.7-3", index).endswith("zstd-1.5.7-3-x86_64.pkg.tar.zst"))
        self.assertIsNone(pkg_history.find_cached("zstd", "1.6.0-1", index))
        # a package whose name starts like another must not pick the other's file
        self.assertTrue(pkg_history.find_cached("python-requests", "2.32.0-1", index).endswith(
            "python-requests-2.32.0-1-any.pkg.tar.zst"))
        self.assertIsNone(pkg_history.find_cached("python-requests", "2.1.0-3", index))
        self.assertIsNotNone(pkg_history.find_cached("vim", "2:9.1.0-1", index))


class TestJournalParser(unittest.TestCase):
    """journalctl -o json lines → table rows."""

    def test_parse_line(self):
        entry = journal_view.parse_line(
            '{"MESSAGE":"Failed to start","PRIORITY":"3","_SYSTEMD_UNIT":"bluetooth.service",'
            '"SYSLOG_IDENTIFIER":"bluetoothd","__REALTIME_TIMESTAMP":"1795673645801431"}')
        self.assertEqual(entry["priority"], 3)
        self.assertEqual(entry["service"], "bluetooth.service")
        self.assertEqual(entry["message"], "Failed to start")
        self.assertIsNotNone(entry["time"])

    def test_service_fallbacks(self):
        self.assertEqual(journal_view.parse_line('{"SYSLOG_IDENTIFIER":"sudo","MESSAGE":"x"}')["service"], "sudo")
        self.assertEqual(journal_view.parse_line('{"_COMM":"xyz","MESSAGE":"x"}')["service"], "xyz")
        self.assertEqual(journal_view.parse_line('{"MESSAGE":"x"}')["service"], "kernel")

    def test_byte_list_message(self):
        # journalctl writes a message that is not valid UTF-8 as a list of bytes
        entry = journal_view.parse_line('{"MESSAGE":[104,105,255],"PRIORITY":"4"}')
        self.assertEqual(entry["message"], "hi�")

    def test_bad_input(self):
        self.assertIsNone(journal_view.parse_line("not json"))
        self.assertEqual(journal_view.parse_line('{"PRIORITY":"x","MESSAGE":"y"}')["priority"], 6)

    def test_summary_and_text(self):
        entries = [journal_view.parse_line(line) for line in (
            '{"MESSAGE":"b","PRIORITY":"4","SYSLOG_IDENTIFIER":"two","__REALTIME_TIMESTAMP":"1795673645000002"}',
            '{"MESSAGE":"a","PRIORITY":"3","SYSLOG_IDENTIFIER":"one","__REALTIME_TIMESTAMP":"1795673645000001"}',
        )]
        self.assertEqual(journal_view.summarize(entries), (1, 1, 2))
        text = journal_view.as_text(entries).splitlines()
        # newest-first rows are copied oldest first, like journalctl prints them
        self.assertTrue(text[0].endswith("error one: a"))
        self.assertTrue(text[1].endswith("warning two: b"))


class TestReportProblemPath(unittest.TestCase):
    """kiro-report lives in /usr/local/bin, which pkexec leaves out of ATT's PATH (the button vanished on picard)."""

    def test_found_outside_pkexec_path(self):
        import report_problem
        with tempfile.TemporaryDirectory() as local_bin:
            script = os.path.join(local_bin, "kiro-report")
            with open(script, "w") as fake:
                fake.write("#!/bin/sh\n")
            os.chmod(script, 0o755)
            saved_path, saved_local = os.environ.get("PATH", ""), report_problem.LOCAL_PATH
            os.environ["PATH"] = "/usr/sbin:/usr/bin:/sbin:/bin:/root/bin"
            report_problem.LOCAL_PATH = local_bin
            try:
                self.assertEqual(report_problem._kiro_report(), script)
            finally:
                os.environ["PATH"], report_problem.LOCAL_PATH = saved_path, saved_local

    def test_real_location_is_searched(self):
        import report_problem
        self.assertIn("/usr/local/bin", report_problem.LOCAL_PATH.split(":"))


class TestReportRedaction(unittest.TestCase):
    """att_report.redact() — the report is pasted on a public issue tracker."""

    def redact(self, text):
        import att_report
        return att_report.redact(text, "archlinux", "alice")

    def test_private_values_removed(self):
        text = self.redact("alice@archlinux /home/alice/x 192.168.1.20 aa:bb:cc:dd:ee:ff fe80::1 "
                           "4f2a9e1c-1111-2222-3333-444455556666 0123456789abcdef0123456789abcdef end 10.0.0.5.")
        self.assertEqual(text, "<user>@<host> /home/<user>/x <ip> <mac> <ipv6> <uuid> <machine-id> end <ip>.")

    def test_lookalikes_survive(self):
        # Arch's default hostname is "archlinux": the package name must not become "<host>-tweak-tool"
        for keep in ("archlinux-tweak-tool 26.11-35", "libva 2.23.0-1", "sddm-git 0.21.0.123.gd7f8b02-1",
                     "0000:03:00.0 VGA", "Calamares::Job", "alicebob"):
            self.assertEqual(self.redact(keep), keep)


if __name__ == "__main__":
    unittest.main()
