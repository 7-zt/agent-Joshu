from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from memtrace import config, store
from memtrace import cli as cli_mod
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

    def test_git_policy_controls_gitignore(self) -> None:
        cases = {
            "ignore": "ignore",
            "track": "track",
            "none": "none",
        }
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for policy, expected in cases.items():
                with self.subTest(policy=policy):
                    target = base / policy
                    target.mkdir()
                    self.write_config(target, policy)
                    if policy == "track":
                        (target / ".gitignore").write_text(
                            "# 追加到项目 .gitignore 的内容\n.memtrace/\n",
                            encoding="utf-8",
                            newline="\n",
                        )
                    before = (
                        (target / ".gitignore").read_bytes()
                        if (target / ".gitignore").is_file()
                        else None
                    )

                    code, output, error = self.run_cli("bootstrap", str(target))

                    self.assertEqual((code, error), (0, ""))
                    gitignore = target / ".gitignore"
                    if expected == "ignore":
                        self.assertIn(".memtrace/", gitignore.read_text(encoding="utf-8"))
                    elif expected == "track":
                        self.assertEqual(gitignore.read_bytes(), before)
                        self.assertIn("git_policy=track 与现有 .memtrace/ 忽略规则冲突", output)
                    else:
                        self.assertFalse(gitignore.exists())
                        self.assertIn("git_policy=none：已跳过追加 .gitignore", output)

    def test_commented_and_invalid_git_policy_use_default_ignore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name, config_text, warning in (
                (
                    "commented",
                    '# git_policy = "track"\n',
                    None,
                ),
                (
                    "invalid",
                    'git_policy = "sometimes"\n',
                    "警告：git_policy=sometimes 无效，按默认 ignore 处理",
                ),
            ):
                with self.subTest(name=name):
                    target = base / name
                    target.mkdir()
                    config_path = target / ".agents" / "memtrace_config.toml"
                    config_path.parent.mkdir()
                    config_path.write_text(config_text, encoding="utf-8", newline="\n")

                    code, output, error = self.run_cli("bootstrap", str(target))

                    self.assertEqual((code, error), (0, ""))
                    self.assertIn(
                        ".memtrace/",
                        (target / ".gitignore").read_text(encoding="utf-8"),
                    )
                    if warning:
                        self.assertIn(warning, output)

    def test_track_and_none_dry_run_skip_gitignore_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for policy in ("track", "none"):
                with self.subTest(policy=policy):
                    target = base / policy
                    target.mkdir()
                    self.write_config(target, policy)
                    before = self.snapshot(target)

                    code, output, error = self.run_cli(
                        "bootstrap",
                        str(target),
                        "--dry-run",
                    )

                    self.assertEqual((code, error), (0, ""))
                    self.assertIn(f"git_policy={policy}：将跳过追加 .gitignore", output)
                    self.assertEqual(self.snapshot(target), before)

    def test_bootstrap_succeeds_without_git_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "gitless-project"
            target.mkdir()

            code, output, error = self.run_cli("bootstrap", str(target))

            self.assertEqual((code, error), (0, ""))
            self.assertIn("bootstrap 完成", output)
            self.assertIn(
                ".memtrace/",
                (target / ".gitignore").read_text(encoding="utf-8"),
            )

    def test_init_prints_policy_hint_only_on_first_init(self) -> None:
        expected = {
            "ignore": "按默认策略留在本地（git_policy=ignore）",
            "track": "git_policy=track：任务过程将进项目 git",
            "none": "git_policy=none：不管理 git 策略",
        }
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for policy, message in expected.items():
                with self.subTest(policy=policy):
                    target = base / policy
                    target.mkdir()

                    def write_config(root: Path, selected: str = policy) -> Path:
                        path = config.config_path(root)
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(
                            f'git_policy = "{selected}"\n',
                            encoding="utf-8",
                            newline="\n",
                        )
                        return path

                    stdout = io.StringIO()
                    with patch.object(cli_mod.config_mod, "write_config", side_effect=write_config):
                        with redirect_stdout(stdout):
                            self.assertEqual(cli_mod.init_project(target), 0)
                    self.assertIn(message, stdout.getvalue())

                    stdout = io.StringIO()
                    with redirect_stdout(stdout):
                        self.assertEqual(cli_mod.init_project(target), 0)
                    self.assertIn("已存在：.agents/memtrace_config.toml", stdout.getvalue())
                    self.assertNotIn(message, stdout.getvalue())

    @staticmethod
    def write_config(target: Path, policy: str) -> None:
        path = target / ".agents" / "memtrace_config.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f'git_policy = "{policy}"\n',
            encoding="utf-8",
            newline="\n",
        )

    @staticmethod
    def snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }


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
