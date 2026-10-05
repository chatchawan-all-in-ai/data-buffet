import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.source = Path(__file__).parent
        self.temp = tempfile.TemporaryDirectory(prefix=".nm-command-test-", dir=self.source)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache = self.root / "cache"
        self.output = self.root / "outputs"
        self.output.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        (self.cache / "node_modules/@dataform/core").mkdir(parents=True)
        (self.cache / "node_modules/@dataform/core/package.json").write_text('{"version":"3.0.0"}')
        (self.cache / "package.json").write_text('{"private":true}')
        (self.cache / ".dataform-version").write_text("3.0.0\n")
        (self.cache / ".bigquery-version").write_text("3.25.0\n")
        self.executable(self.bin / "npm", "raise SystemExit('unexpected installation')\n")
        self.executable(self.bin / "git", """
import os
import sys
if "merge-base" in sys.argv:
    print("base")
elif "--name-only" in sys.argv:
    print(os.environ["NM_TEST_CHANGED"])
""")
        self.executable(self.cache / "node_modules/.bin/dataform", """
import json
import sys
from pathlib import Path
if "--version" in sys.argv:
    print("3.0.0")
else:
    graph = json.loads((Path(sys.argv[2]) / "includes/graph.json").read_text())
    if graph.get("compile_error"):
        raise SystemExit(1)
    print(json.dumps(graph))
""")
        self.executable(self.cache / "venv/bin/python", """
import argparse
import json
import os
import time
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument("script")
parser.add_argument("--compile")
parser.add_argument("--changed")
parser.add_argument("--mode")
args = parser.parse_args()
evidence = Path(os.environ["NM_TEST_EVIDENCE"])
name = os.environ["NM_TEST_NAME"]
if os.environ.get("NM_TEST_BLOCK") == "1":
    (evidence / "ready").touch()
    deadline = time.monotonic() + 10
    while not (evidence / "release").exists():
        if time.monotonic() >= deadline:
            raise SystemExit("release timeout")
        time.sleep(0.01)
graph = json.loads(Path(args.compile).read_text())
record = {
    "compile": args.compile, "changed": args.changed,
    "selection": Path(args.changed).read_text().splitlines(),
    "mode": args.mode, "origin": graph["origin"],
}
(evidence / (name + ".json")).write_text(json.dumps(record))
raise SystemExit(1 if graph["invalid"] else 0)
""")

    def executable(self, path, body):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!" + sys.executable + "\n" + body)
        path.chmod(0o755)

    def worktree(self, name, *, invalid=False, compile_error=False):
        project = self.root / name
        (project / "scripts").mkdir(parents=True)
        for file in ("_nm-env.sh", "nm-test.sh", "nm-lint.sh", "nm_dryrun.py"):
            shutil.copyfile(self.source / file, project / "scripts" / file)
        (project / "definitions").mkdir()
        (project / "includes").mkdir()
        (project / "workflow_settings.yaml").write_text("dataformCoreVersion: 3.0.0\n")
        graph = {"origin": name, "invalid": invalid, "compile_error": compile_error, "tables": [{}]}
        (project / "includes/graph.json").write_text(json.dumps(graph))
        return project

    def environment(self, name, *, block=False):
        return {
            **os.environ,
            "PATH": str(self.bin) + ":" + os.environ["PATH"],
            "NM_ENV_DIR": str(self.cache),
            "TMPDIR": str(self.output),
            "NM_TEST_EVIDENCE": str(self.evidence),
            "NM_TEST_NAME": name,
            "NM_TEST_CHANGED": f"definitions/{name}.sqlx",
            "NM_TEST_BLOCK": "1" if block else "0",
        }

    def test_concurrent_commands_keep_graphs_and_selections_together(self):
        first_project = self.worktree("invalid", invalid=True)
        second_project = self.worktree("valid")
        for first_args in ([], ["--all"]):
            for second_args in (["scripts/nm-test.sh"], ["scripts/nm-lint.sh"], ["scripts/nm-lint.sh", "--all"]):
                with self.subTest(first=first_args, second=second_args):
                    for name in ("ready", "release", "invalid.json", "valid.json"):
                        (self.evidence / name).unlink(missing_ok=True)
                    first = subprocess.Popen(
                        ["bash", "scripts/nm-lint.sh", *first_args], cwd=first_project,
                        env=self.environment("invalid", block=True), stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True,
                    )
                    try:
                        deadline = time.monotonic() + 10
                        while not (self.evidence / "ready").exists():
                            if first.poll() is not None or time.monotonic() >= deadline:
                                self.fail("first lint did not reach the dry-run reader")
                            time.sleep(0.01)
                        second = subprocess.run(
                            ["bash", *second_args], cwd=second_project,
                            env=self.environment("valid"), stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, timeout=10,
                        )
                        (self.evidence / "release").touch()
                        first_output, _ = first.communicate(timeout=10)
                    finally:
                        (self.evidence / "release").touch()
                        if first.poll() is None:
                            first.kill()
                            first.communicate()
                    self.assertEqual(second.returncode, 0, second.stdout)
                    self.assertEqual(first.returncode, 1, first_output)
                    record = json.loads((self.evidence / "invalid.json").read_text())
                    self.assertEqual(record["origin"], "invalid")
                    self.assertEqual(record["selection"], [] if first_args else ["definitions/invalid.sqlx"])
                    self.assertEqual(record["mode"], "all" if first_args else "changed")
                    directory = Path(record["compile"]).parent
                    self.assertEqual(directory, Path(record["changed"]).parent)
                    self.assertFalse(directory.exists())
                    if "scripts/nm-lint.sh" in second_args:
                        other = json.loads((self.evidence / "valid.json").read_text())
                        self.assertEqual(other["origin"], "valid")
                        self.assertNotEqual(other["compile"], record["compile"])
                        self.assertNotEqual(other["changed"], record["changed"])
                    self.assertEqual(list(self.output.iterdir()), [])
                    self.assertEqual(list(self.cache.glob("project.*")), [])
                    self.assertFalse((self.cache / "compile.json").exists())
                    self.assertFalse((self.cache / "changed.txt").exists())

    def test_compile_failures_clean_up_outputs_in_both_commands(self):
        project = self.worktree("compile_error", compile_error=True)
        for script in ("scripts/nm-test.sh", "scripts/nm-lint.sh"):
            with self.subTest(script=script):
                result = subprocess.run(
                    ["bash", script], cwd=project, env=self.environment("compile_error"),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10,
                )
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertFalse((self.evidence / "compile_error.json").exists())
                self.assertEqual(list(self.output.iterdir()), [])
                self.assertEqual(list(self.cache.glob("project.*")), [])


if __name__ == "__main__":
    unittest.main()
