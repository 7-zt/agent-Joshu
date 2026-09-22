import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, dirname, isAbsolute } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

// ---------------------------------------------------------------------------
// memtrace OMP 扩展：
// - 按 .memtrace/（或 .agents/memtrace_config.toml）标记定位项目根
// - 会话开始注入当前任务 + 最近 WAL 摘要（spawnSync 调 CLI）
// - 阶段性提醒记录（每 N 轮用户输入提醒一次）
// - 抓客观元数据（会话开始时 git 变更清单 → WAL，actor=memtrace-hook）
// 规格：grill-memtrace.md「memtrace 规格 v1.0」。
// ---------------------------------------------------------------------------

const MEMTRACE_CONTEXT_TIMEOUT_MS = 5000;
const REMIND_EVERY_N_TURNS = 10;

function findProjectRoot(startDir: string): string | null {
   let current = startDir;
   while (true) {
      if (existsSync(join(current, ".agents", "memtrace_config.toml"))) return current;
      if (existsSync(join(current, ".memtrace"))) return current;
      const parent = dirname(current);
      if (parent === current) break;
      current = parent;
   }
   return null;
}

// 主包仓库位置 = 本扩展文件向上三级（.omp/extensions/memtrace/ → 仓库根）。
// Windows/Linux 通用；避免依赖 OMP 配置里的绝对路径。
function defaultKitRoot(): string {
   // fileURLToPath 处理 Windows 的 file:///C:/...，避免把 /C:/ 当成本地路径。
   const file = fileURLToPath(import.meta.url);
   return dirname(dirname(dirname(file)));
}

function resolvePython(): string {
   // Windows 上 spawnSync("python3") 常失败；Linux 上 python 可能指向 python2。
   // 依次探测 python/python3，探测不到时退回 python3（让报错可见）。
   for (const candidate of ["python", "python3"]) {
      const probe = spawnSync(candidate, ["-c", "import sys; sys.exit(0)"], { timeout: 3000, windowsHide: true });
      if (probe.status === 0) return candidate;
   }
   return "python3";
}

interface CliResult {
   ok: boolean;
   stdout: string;
}

function runCli(projectRoot: string, args: string[]): CliResult {
   const env = {
      ...process.env,
      PYTHONPATH: [defaultKitRoot(), process.env.PYTHONPATH].filter(Boolean).join(process.platform === "win32" ? ";" : ":"),
      PYTHONUTF8: "1",
      PYTHONIOENCODING: "utf-8",
   };
   try {
      const result = spawnSync(resolvePython(), ["-X", "utf8", "-m", "memtrace", ...args], {
         cwd: projectRoot,
         encoding: "utf-8",
         env,
         timeout: MEMTRACE_CONTEXT_TIMEOUT_MS,
         windowsHide: true,
      });
      if (result.error || result.status !== 0) {
         return { ok: false, stdout: "" };
      }
      return { ok: true, stdout: (result.stdout ?? "").trim() };
   } catch {
      return { ok: false, stdout: "" };
   }
}

// ---------------------------------------------------------------------------
// 注入内容构建（直接读文件，避免多进程开销；CLI 仍是权威操作入口）
// ---------------------------------------------------------------------------

interface TaskMeta {
   id: string;
   name: string;
   status: string;
   dirName: string;
   walEntries: number;
   lastWalLine: string;
}

function parseTomlSubset(text: string): Record<string, string> {
   const data: Record<string, string> = {};
   for (const rawLine of text.replace(/^\uFEFF/, "").split(/\r?\n/)) {
      const line = rawLine.trim();
      if (!line || line.startsWith("#") || line.startsWith("[")) continue;
      const eq = line.indexOf("=");
      if (eq < 0) continue;
      const key = line.slice(0, eq).trim();
      let value = line.slice(eq + 1).trim();
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
         value = value.slice(1, -1);
      } else {
         const hash = value.indexOf(" #");
         if (hash >= 0) value = value.slice(0, hash).trim();
      }
      data[key] = value;
   }
   return data;
}

function readTaskMeta(taskDir: string): TaskMeta | null {
   const metaPath = join(taskDir, "memtrace.toml");
   if (!existsSync(metaPath)) return null;
   let meta: Record<string, string>;
   try {
      meta = parseTomlSubset(readFileSync(metaPath, "utf-8"));
   } catch {
      return null;
   }
   if (!meta.id || !meta.name) return null;
   return {
      id: meta.id,
      name: meta.name,
      status: meta.status ?? "planning",
      dirName: taskDir.split(/[\\/]/).pop() ?? taskDir,
      walEntries: 0,
      lastWalLine: "",
   };
}

function collectWalStats(taskDir: string, meta: TaskMeta): TaskMeta {
   const walDir = join(taskDir, "wal");
   if (!existsSync(walDir)) return meta;
   let files: string[];
   try {
      files = readdirSync(walDir).filter((f) => f.endsWith(".md")).sort();
   } catch {
      return meta;
   }
   let entries = 0;
   let lastHeader = "";
   let lastBody = "";
   for (const file of files) {
      let text: string;
      try {
         text = readFileSync(join(walDir, file), "utf-8");
      } catch {
         continue;
      }
      for (const line of text.split(/\r?\n/)) {
         if (line.startsWith("## ") && line.includes(" · ")) {
            entries += 1;
            lastHeader = line.slice(3).trim();
            lastBody = "";
         } else if (entries > 0 && line.trim() && !line.startsWith("#")) {
            lastBody = line.trim();
         }
      }
   }
   meta.walEntries = entries;
   meta.lastWalLine = lastBody || lastHeader;
   return meta;
}

function findTaskRoots(projectRoot: string): string[] {
   const configPath = join(projectRoot, ".agents", "memtrace_config.toml");
   let configuredRoot = ".memtrace";
   try {
      if (existsSync(configPath)) {
         const config = parseTomlSubset(readFileSync(configPath, "utf-8"));
         configuredRoot = config.task_root?.trim() || configuredRoot;
      }
   } catch {
      // CLI 负责报告配置错误；扩展在此场景保持静默。
   }
   const root = isAbsolute(configuredRoot) ? configuredRoot : join(projectRoot, configuredRoot);
   const results: string[] = [];
   const walk = (dir: string, depth: number): void => {
      if (depth > 3) return;
      let entries;
      try {
         entries = readdirSync(dir, { withFileTypes: true });
      } catch {
         return;
      }
      for (const entry of entries) {
         if (!entry.isDirectory()) continue;
         const child = join(dir, entry.name);
         if (existsSync(join(child, "memtrace.toml"))) {
            results.push(child);
         } else {
            walk(child, depth + 1);
         }
      }
   };
   walk(root, 0);
   return results;
}

function buildSessionContext(projectRoot: string): string {
   const taskDirs = findTaskRoots(projectRoot);
   const tasks = taskDirs
      .map((dir) => {
         const meta = readTaskMeta(dir);
         return meta ? collectWalStats(dir, meta) : null;
      })
      .filter((t): t is TaskMeta => t !== null);
   if (tasks.length === 0) return "";

   const open = tasks.filter((t) => t.status !== "closed");
   const recent = open.length > 0 ? open : tasks;
   const lines: string[] = [];

   lines.push(`memtrace：${tasks.length} 个任务（open/planning ${open.length} 个，closed ${tasks.length - open.length} 个）。`);
   for (const task of recent.slice(0, 3)) {
      lines.push(`- ${task.dirName}｜${task.status}｜WAL ${task.walEntries} 条${task.lastWalLine ? `｜最近：${task.lastWalLine.slice(0, 160)}` : ""}`);
   }
   lines.push("继续该任务用 `memtrace read <任务> --wal --full` 拉详情；阶段性进展用 `memtrace log` 写变更/推翻/验证小节。");
   if (open.length > 0) {
      lines.push(`当前未关闭任务：${open[0]!.dirName}`);
   }
   return `<memtrace-context>\n${lines.join("\n")}\n</memtrace-context>`;
}

// ---------------------------------------------------------------------------
// hook 元数据：会话开始抓 git 变更清单（客观事实，不写语义）
// ---------------------------------------------------------------------------

function logHookMetadata(projectRoot: string, sessionId: string | undefined): void {
   let changed: string;
   try {
      const status = spawnSync("git", ["status", "--porcelain"], {
         cwd: projectRoot,
         encoding: "utf-8",
         timeout: 5000,
         windowsHide: true,
      });
      if (status.status !== 0 || !status.stdout) return;
      changed = status.stdout
         .split(/\r?\n/)
         .filter(Boolean)
         .slice(0, 50)
         .map((line) => line.trim())
         .join("; ");
   } catch {
      return;
   }
   if (!changed) return;

   // 找当前 open 任务追加（多 open 时挑最近创建的；无 open 任务则跳过）
   const taskDirs = findTaskRoots(projectRoot);
   const metas = taskDirs
      .map((dir) => {
         const meta = readTaskMeta(dir);
         return meta ? collectWalStats(dir, meta) : null;
      })
      .filter((t): t is TaskMeta => t !== null && t.status !== "closed");
   if (metas.length === 0) return;
   const target = metas[metas.length - 1]!;
   runCli(projectRoot, [
      "log",
      target.dirName,
      "会话开始：工作区状态快照",
      "--actor", "memtrace-hook",
      "--body", `session: ${sessionId ?? "unknown"}\ngit status: ${changed}`,
   ]);
}

// ---------------------------------------------------------------------------
// 扩展入口
// ---------------------------------------------------------------------------

export default function(pi: ExtensionAPI): void {
   let projectRoot: string | null = null;
   let reminderCounter = 0;

   pi.on("session_start", async (_event, ctx) => {
      projectRoot = findProjectRoot(ctx.cwd);
      if (!projectRoot) return; // 非 memtrace 项目：零打扰

      const sessionId = ctx.sessionManager?.getSessionId?.();
      logHookMetadata(projectRoot, sessionId);

      const context = buildSessionContext(projectRoot);
      if (context) {
         await pi.sendMessage({
            customType: "memtrace-session-context",
            content: context,
            display: false,
         });
      }
      ctx.ui.notify("memtrace 任务记录已加载", "info");
   });

   pi.on("input", async (_event, ctx) => {
      if (!projectRoot) {
         projectRoot = findProjectRoot(ctx.cwd);
      }
      if (!projectRoot) return;
      reminderCounter += 1;
      if (reminderCounter % REMIND_EVERY_N_TURNS !== 0) return;

      // 阶段性提醒：仅当存在 open 任务且最近 WAL 很久没写时
      const taskDirs = findTaskRoots(projectRoot);
      const open = taskDirs
         .map((dir) => {
            const meta = readTaskMeta(dir);
            return meta ? collectWalStats(dir, meta) : null;
         })
         .filter((t): t is TaskMeta => t !== null && t.status === "open");
      if (open.length === 0) return;
      ctx.ui.notify(
         `memtrace：任务进行中（${open[0]!.dirName}）。本阶段改动完成的话，用 memtrace log 写一条阶段汇总（变更/推翻/验证）。`,
         "info",
      );
   });
}
