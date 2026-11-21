# 目录结构评审：多 Agent 下的 skill 发现

评审日期：2026-11-21。问题是：**同时支持这么多 Agent，目录结构是否会重复、是否合理？**

## 结论先行

1. `skills/` 是唯一源码；`.agents/skills/` 是**唯一提交的项目级发现根目录**。
2. 仓库里**没有复制品**：`.agents/skills/<name>` 是指向 `skills/<name>` 的符号链接，与源目录同一个 inode。
3. 之前的 `.claude/skills → ../skills` 已移除。它不是文件重复，但会让**同时读多个根目录的 Agent** 从两条路径看到同一个 skill。多根优先级没有官方文档保证，所以不做这种赌注。
4. Claude Code 改为**用户级安装**（`~/.claude/skills`），一条命令解决。

## 一、三个不同层面的"重复"

| 层面 | 含义 | 本仓库 |
| --- | --- | --- |
| 文件重复 | 真的存了两份内容，改一处另一处不同步 | ❌ 不存在，全部是链接 |
| 路径重复 | 同一个 skill 能被两条路径发现，Agent 可能列两次 | ⚠️ 只在"多根目录"出现，已消除 |
| 目录重复 | 一个 skill 被装到多个 Agent 目录 | ➖ 用户级安装时可能发生，属于安装策略 |

用户看到的"`.claude/` 里有重复 skill"，属于**路径重复**的观感：8 个条目、名字相同。实际是同一个目录的两种入口。

## 二、谁会读多个根目录

| Agent | 项目级根目录 | 是否多根 |
| --- | --- | --- |
| DSH | `.dsh/skills`、`.agents/skills` | 是（2 个），但本仓库不建 `.dsh/skills` |
| Codex CLI | `.agents/skills` | 否 |
| Cursor | `.agents/skills` 或 `.cursor/skills` | 否（二选一） |
| Gemini CLI | `.agents/skills` 或 `.gemini/skills` | 否（二选一） |
| **Copilot CLI** | `.github/skills`、`.claude/skills`、`.agents/skills` | **是（3 个）** |
| Copilot（VS Code） | `.github/skills` | 否 |
| Windsurf / Devin | `.agents/skills`、`.devin/skills` | 是（2 个） |
| OpenCode | `.agents/skills` | 否 |
| Claude Code | `.claude/skills` | 否 |

只有 **Copilot CLI** 和 **Windsurf/Devin** 会在项目里同时读多个目录。如果仓库里既有 `.agents/skills` 又有 `.claude/skills`，Copilot CLI 就会从两个入口各看到一次。

它们大概率按名字去重或按优先级取一个——但这是**未文档化的行为**，不能写进安装说明当作保证。因此：

> **规则：仓库只提交一个项目级 skill 根目录。**

## 三、为什么是 `.agents/skills` 而不是 `.claude/skills`

- `.agents/skills` 被 Codex、Cursor、Gemini CLI、Copilot CLI、Windsurf/Devin、OpenCode、DSH 读取，覆盖面最大。
- `.claude/skills` 只有 Claude Code 读；为它单独提交一个根目录，收益 1 个 Agent，代价是多根重复。
- Claude Code 用用户级 `~/.claude/skills` 就能解决，且不影响其他 Agent 的项目级发现。

## 四、为什么源码不直接放 `.agents/skills`

- `npx skills` 优先扫描 `skills/`，这是生态里最常见的约定，也是 `skills add` 直接可用的保证。
- `skills/` 是可见目录，便于人类审阅、比较、写文档；`.agents/` 是工具目录。
- 链接层很薄（8 个），且有校验脚本兜底。

代价：符号链接在 Windows 上需要开发者模式；文件被 git 检出为纯文本时链接失效。对策是 `--copy` 与 `check_skills.py`。

## 五、当前结构

```
skills/<name>/SKILL.md                    唯一源码，提交
.agents/skills/<name> -> ../../skills/... 项目级发现层，提交（8 个链接）
CLAUDE.md / GEMINI.md                     @AGENTS.md 指针，提交
AGENTS.md                                 唯一规则文件，提交
~/.claude/skills/<name>                   用户级安装，不提交
~/.agents/skills/<name>                   用户级安装，不提交
```

不提交：`.claude/skills`、`.cursor/skills`、`.gemini/skills`、`.github/skills`、`.devin/skills`（已写进 `.gitignore`）。

## 六、仍需注意

1. **符号链接跟随**：Claude Code 明确支持符号链接的 skill 目录；其他 Agent 未逐一验证。若某个 Agent 不跟随，用 `--copy` 安装到用户级。
2. **全局安装的路径解析**：skill 正文引用 `knowledge/`、`data/` 等相对路径，以仓库根目录为基准。装到用户级后，在别的项目里调用会找不到这些文件；日常请在仓库内工作（`AGENTS.md` 已写明该规则）。
3. **VS Code Copilot** 只读 `.github/skills`，本项目不提交该目录；需要时用 `npx skills add ... --skill '*' -g` 或在本地建链接（已 gitignore）。
4. **新增 Agent 时**：先确认它读哪些根、是否多根。如果它新增一个与 `.agents` 并行的根，**不要**在仓库里加第二个链接目录；写进本文件的矩阵，并评估是否值得为它牺牲"单根"原则。
5. **项目级 `npx skills add` 会覆盖发现层**：实测执行 `npx skills add . --skill '*'` 后，`.agents/skills/<name>` 从符号链接变成真实副本（输出 `(copied)`）。发现层只能由本仓库的脚本维护；误操作后跑 `python3 scripts/check_skills.py --repair`。

## 七、复查清单（结构变更时逐项确认）

- [ ] 仓库里只有一个项目级 skill 根目录
- [ ] 该目录下每个条目都是指向 `skills/` 的链接，没有副本
- [ ] 新增 skill 时同步创建链接，并跑 `python3 scripts/check_skills.py --strict`
- [ ] `.claude/skills` 等本地目录在 `.gitignore` 里
- [ ] 规则文件仍只有 `AGENTS.md` 一份
- [ ] 安装文档中的 Agent 目录与官方文档一致
