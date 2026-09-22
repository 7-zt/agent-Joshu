from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from memtrace import config, store
from memtrace.cli import main


class BootstrapTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_full_install_and_idempotent_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            code, output, error = self.run_cli("bootstrap", str(target))
            self.assertEqual((code, error), (0, ""))
            self.assertIn("bootstrap 完成", output)
            self.assertTrue((target / "agent-joshu" / "memtrace" / "__init__.py").is_file())
            self.assertTrue((target / ".omp" / "extensions" / "memtrace" / "index.ts").is_file())
            self.assertEqual(
                len(list((target / ".omp" / "skills").iterdir())),
                8,
            )
            self.assertTrue((target / ".agents" / "memtrace_config.toml").is_file())
            self.assertTrue((target / ".memtrace").is_dir())
            manifest_path = target / "agent-joshu" / "bootstrap-manifest.json"
            first_manifest = manifest_path.read_bytes()

            decision = target / "agent-joshu" / "adr" / "decision" / "local.md"
            decision.write_text("project decision\n", encoding="utf-8", newline="\n")
            skill = target / ".omp" / "skills" / "memtrace" / "SKILL.md"
            original_skill = skill.read_text(encoding="utf-8")
            skill.write_text(original_skill + "\nproject edit\n", encoding="utf-8", newline="\n")

            code, output, error = self.run_cli("bootstrap", str(target))
            self.assertEqual((code, error), (0, ""))
            self.assertEqual(decision.read_text(encoding="utf-8"), "project decision\n")
            self.assertTrue((skill.with_name("SKILL.md.new")).is_file())
            self.assertTrue(skill.read_text(encoding="utf-8").endswith("project edit\n"))
            self.assertIn("已更新 agent-joshu/bootstrap-manifest.json", output)
            second_manifest = manifest_path.read_bytes()

            code, output, error = self.run_cli("bootstrap", str(target))
            self.assertEqual((code, error), (0, ""))
            self.assertIn("bootstrap-manifest.json 无变化", output)
            self.assertEqual(manifest_path.read_bytes(), second_manifest)
            self.assertTrue(first_manifest)

    def test_skills_filter_and_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()

            code, output, error = self.run_cli(
                "bootstrap",
                str(target),
                "--skills",
                "architect,memtrace",
                "--dry-run",
            )
            self.assertEqual((code, error), (0, ""))
            self.assertIn("预览完成", output)
            self.assertEqual(list(target.iterdir()), [])

            code, _, error = self.run_cli(
                "bootstrap",
                str(target),
                "--skills",
                "architect,memtrace",
                "--skip-init",
            )
            self.assertEqual((code, error), (0, ""))
            self.assertEqual(
                sorted(path.name for path in (target / ".omp" / "skills").iterdir()),
                ["architect", "memtrace"],
            )
            self.assertFalse((target / ".agents").exists())
            manifest = json.loads(
                (target / "agent-joshu" / "bootstrap-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["skills"], ["architect", "memtrace"])

    def test_e1_to_e4(self) -> None:
        source_root = Path(__file__).resolve().parents[1]
        code, _, error = self.run_cli("bootstrap", str(source_root))
        self.assertEqual(code, 1)
        self.assertIn("不能是主包自身或其子目录", error)

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            missing = base / "missing"
            code, _, error = self.run_cli("bootstrap", str(missing))
            self.assertEqual(code, 1)
            self.assertIn("不存在或不是目录", error)

            target = base / "project"
            target.mkdir()
            code, _, error = self.run_cli("bootstrap", str(target), "--skills", "unknown")
            self.assertEqual(code, 2)
            self.assertIn("有效名字", error)

            (target / "agent-joshu").mkdir()
            code, _, error = self.run_cli("bootstrap", str(target))
            self.assertEqual(code, 1)
            self.assertIn("缺少 VERSION", error)


class FindTaskTests(unittest.TestCase):
    def test_directory_slug_and_id_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config.write_config(root)
            task_dir = root / ".memtrace" / "2026" / "09" / "22-02--bootstrap-project"
            task_dir.mkdir(parents=True)
            meta = {
                "schema_version": 1,
                "id": "01a0c7f6-83c4-7999-8989-0497ef43f8ec",
                "name": "bootstrap project",
                "status": "planning",
                "created_at": "2026-09-22T15:13:36+08:00",
                "depends_on": [],
                "related_to": [],
            }
            (task_dir / "memtrace.toml").write_text(
                store.dump_meta(meta),
                encoding="utf-8",
                newline="\n",
            )
            cfg = config.load_config(root)

            for ref in (
                "22-02--bootstrap-project",
                "bootstrap-project",
                "22-02",
                "01a0c7f6",
            ):
                with self.subTest(ref=ref):
                    task = store.find_task(root, cfg, ref)
                    self.assertEqual(task.id, meta["id"])


if __name__ == "__main__":
    unittest.main()
