import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "dependency-audit.py"
CLEAN = {"advisories": {}, "metadata": {"vulnerabilities": {"low": 0, "moderate": 0, "high": 0, "critical": 0}}}
VULNERABLE = {"advisories": {"1": {"module_name": "left-pad", "severity": "high", "title": "Prototype pollution"}},
              "metadata": {"vulnerabilities": {"low": 0, "moderate": 0, "high": 1, "critical": 0}}}


class DependencyAuditTest(unittest.TestCase):
    """A fake pnpm stands in for the npm audit endpoint."""

    def audit(self, stdout="", stderr="", code=0, sleep=0, args=(), **env):
        with tempfile.TemporaryDirectory() as tmp:
            for name, text in (("out", stdout), ("err", stderr)):
                Path(tmp, name).write_text(text)
            pnpm = Path(tmp, "pnpm")
            pnpm.write_text(f'#!/bin/sh\necho "$*" > "{tmp}/args"\nsleep {sleep}\ncat "{tmp}/out"\n'
                            f'cat "{tmp}/err" >&2\nexit {code}\n')
            pnpm.chmod(0o755)
            output = Path(tmp, "github_output")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=30,
                env={"PATH": f"{tmp}:/usr/bin:/bin", "GITHUB_OUTPUT": str(output), **env})
            result.args_seen = Path(tmp, "args").read_text() if Path(tmp, "args").exists() else ""
            result.github_output = output.read_text() if output.exists() else ""
            return result

    def test_clean_audit_passes(self):
        result = self.audit(json.dumps(CLEAN))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("audit --json", result.args_seen)
        self.assertIn("audit=ok", result.github_output)

    def test_vulnerability_is_red_even_when_soft(self):
        result = self.audit(json.dumps(VULNERABLE), code=1, args=["--soft-unavailable"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("left-pad", result.stdout + result.stderr)
        self.assertIn("audit=vulnerable", result.github_output)

    def test_timeout_is_unavailable(self):
        strict = self.audit(json.dumps(CLEAN), sleep=3, AUDIT_TIMEOUT="1")
        self.assertEqual(strict.returncode, 3)
        self.assertIn("unavailable", strict.stderr)
        soft = self.audit(json.dumps(CLEAN), sleep=3, args=["--soft-unavailable"], AUDIT_TIMEOUT="1")
        self.assertEqual(soft.returncode, 0)
        self.assertIn("audit=unavailable", soft.github_output)
        self.assertIn("::warning", soft.stdout)

    def test_endpoint_5xx_and_network_errors_are_unavailable(self):
        for err in ("ERR_PNPM_AUDIT_BAD_RESPONSE  The audit endpoint (at https://registry.npmjs.org/-/npm/v1/security/audits/quick) responded with 503: Service Unavailable",
                    json.dumps({"error": {"code": "ERR_PNPM_AUDIT_BAD_RESPONSE", "message": "responded with 504: Gateway Timeout"}}),
                    "request to https://registry.npmjs.org/-/npm/v1/security/advisories/bulk failed, reason: connect ETIMEDOUT",
                    "getaddrinfo EAI_AGAIN registry.npmjs.org"):
            with self.subTest(err=err[:40]):
                self.assertEqual(self.audit(stderr=err, code=1).returncode, 3)

    def test_other_failures_fail_closed(self):
        for err in ("ERR_PNPM_AUDIT_BAD_RESPONSE  The audit endpoint responded with 401: Unauthorized",
                    "ERR_PNPM_LOCKFILE_MISSING  no pnpm-lock.yaml", ""):
            with self.subTest(err=err[:40]):
                result = self.audit(stderr=err, code=1, args=["--soft-unavailable"])
                self.assertEqual(result.returncode, 1)
                self.assertIn("audit=failed", result.github_output)

    def test_extra_args_reach_pnpm(self):
        result = self.audit(json.dumps(CLEAN), args=["--", "--audit-level=high", "--prod"])
        self.assertIn("audit --json --audit-level=high --prod", result.args_seen)


if __name__ == "__main__":
    unittest.main()
