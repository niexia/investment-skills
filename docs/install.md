# 安装与使用

三种入口：**npm / npx**（推荐）、**离线脚本**（无 Node）、**仓库内零安装**（不装）。

## 0. 先看兼容性

### 技能目录

| Agent | 项目级目录 | 用户级目录 | 本仓库零安装 |
| --- | --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | 一条命令（见第 1 节） |
| Codex（桌面端 / CLI / IDE 扩展） | `.agents/skills/` | `~/.agents/skills/` | ✅ |
| Cursor | `.agents/skills/` 或 `.cursor/skills/` | `~/.agents/skills/` 或 `~/.cursor/skills/` | ✅ |
| Gemini CLI | `.agents/skills/` 或 `.gemini/skills/` | `~/.agents/skills/` 或 `~/.gemini/skills/` | ✅ |
| Copilot CLI | `.agents/skills/`、`.claude/skills/`、`.github/skills/` | `~/.copilot/skills/` | ✅ |
| Copilot（VS Code） | `.github/skills/` | — | ⚠️ 用 `npx` 或 `--target copilot` |
| Windsurf / Devin | `.agents/skills/`、`.devin/skills/` | `~/.agents/skills/` | ✅ |
| OpenCode | `.agents/skills/` | `~/.agents/skills/` | ✅ |
| DeepSeek Harness | `.dsh/skills/`、`.agents/skills/` | `~/.dsh/skills/`、`~/.agents/skills/` | ✅ |

`.agents/skills` 是当前的跨 Agent 共同目录，也是本仓库**唯一提交的项目级 skill 根目录**。原因见 [`layout-review.md`](research/layout-review.md)：同时读多个根目录的 Agent（如 Copilot CLI 会看 `.github/`、`.claude/`、`.agents/`）会从两个入口看到同一个 skill。

### 规则文件

| Agent | 读取的文件 | 本仓库 |
| --- | --- | --- |
| Codex / Cursor / Copilot / OpenCode / Devin / DSH | `AGENTS.md` | ✅ 权威来源 |
| Claude Code | `CLAUDE.md`（存在时优先），支持 `@` 导入 | ✅ `CLAUDE.md` → `@AGENTS.md` |
| Gemini CLI | `GEMINI.md`，支持 `@` 导入 | ✅ `GEMINI.md` → `@AGENTS.md` |

规则只维护 `AGENTS.md` 一份；`CLAUDE.md` / `GEMINI.md` 是两行指针，不要往里写规则。

## 1. npm / npx（推荐）

包内自带 CLI，一条命令完成安装。

```bash
# 仓库推到 GitHub 后（不必发布到 npm）
npx github:niexia/investment-skills install

# 发布到 npm 后
npx investment-skills install

# 预览
npx investment-skills install --dry-run
```

| 命令 | 作用 |
| --- | --- |
| `install` | 把 8 个 skill 安装到三个用户级目录；本地克隆链接源码，从 npm / npx 包安装时复制文件 |
| `init <dir>` | 生成完整工作区（skills + knowledge + data + reports + portfolio + AGENTS.md） |
| `list` | 列出当前工作区的 skill |

`install` 的参数与离线脚本一致：`--dry-run`、`--copy`、`--detected`、`--target`、`--force`、`--uninstall`。

**`install` 与 `init` 的分工**：skill 正文用相对路径引用 `knowledge/`、`data/`、`reports/`。`install` 只解决"Agent 能发现 skill"；要让相对路径成立，必须在工作区里工作——`init` 生成一个，或在克隆目录里工作。

发布到 npm 前请先补 `LICENSE`（当前仓库未声明许可证），否则包的使用条款不明确。

## 2. 离线脚本（无 Node）

等价于 `npx investment-skills install`，只依赖 bash：

```bash
./scripts/install-skills.sh
```

默认写入三个用户级目录，覆盖全部支持的 Agent：

| 目录 | Agent |
| --- | --- |
| `~/.agents/skills` | Codex、Cursor、Gemini CLI、Windsurf/Devin、OpenCode、DeepSeek Harness |
| `~/.claude/skills` | Claude Code |
| `~/.copilot/skills` | GitHub Copilot CLI |

只创建指向 `skills/<name>` 的符号链接，重复执行幂等，不复制文件。

| 参数 | 用途 |
| --- | --- |
| `--dry-run` | 只打印会做什么 |
| `--detected` | 只装到本机已存在的 Agent 目录 |
| `--copy` | 复制而非链接（Windows / 不跟随符号链接） |
| `--force` | 目标已存在目录或非本仓库符号链接时，备份后覆盖；默认跳过此类目标 |
| `--target codex,dsh` | 装到旧版目录（`~/.codex/skills`、`~/.dsh/skills`、`~/.cursor/skills`、`~/.gemini/skills`） |
| `--uninstall` | 删除本脚本创建的链接 |

验证：`ls ~/.agents/skills` 应有 8 个条目。

## 3. 仓库内零安装

```bash
git clone https://github.com/niexia/investment-skills.git
cd investment-skills
python3 scripts/check_skills.py
```

在**这个目录**里启动 Agent 即可：

- DSH、Codex、Cursor、Gemini CLI、Copilot CLI、Windsurf/Devin、OpenCode 读 `.agents/skills/`
- Claude Code 不读它：要么执行第 1 或第 2 节的命令，要么本地建 `.claude/skills -> ../skills`（已 gitignore）

`.agents/skills/` 里的 8 个条目全部是指向 `skills/<name>` 的**符号链接**，不是副本；仓库里只有这一个项目级根目录。

## 4. 插件市场与其他渠道（可选）

仓库已带好各家的清单文件。推送到 GitHub 后可直接从市场安装：

| 渠道 | 清单文件 | 命令 |
| --- | --- | --- |
| Claude Code | `.claude-plugin/marketplace.json` | `claude plugin marketplace add niexia/investment-skills`<br>`claude plugin install investment-skills@niexia-investment` |
| Codex | `.agents/plugins/marketplace.json`、`.codex-plugin/plugin.json` | `codex plugin marketplace add niexia/investment-skills`<br>`codex plugin add investment-skills@niexia-investment` |
| Copilot CLI | `.github/plugin/plugin.json` | `/plugin marketplace add niexia/investment-skills`<br>`/plugin install investment-skills@niexia-investment` |
| Antigravity CLI | `plugin.json` | `agy plugin install https://github.com/niexia/investment-skills` |
| 通用 Agent Skills | `skills/` | `npx skills add niexia/investment-skills` |

插件名是 `investment-skills`，市场名是 `niexia-investment`；两者不一致时以上面的 `plugin@marketplace` 写法为准。

### `npx skills` 的参数

**前提：`skills/` 已经推到 GitHub。** 如果 `-l` 返回 `[SKILLS_NO_VALID_SKILLS] No valid skills found`，说明远端没有 skill（未 push，或 frontmatter 无效），不是命令写错。

```bash
npx skills add niexia/investment-skills -l                         # 预览，应输出 8 个
npx skills add niexia/investment-skills --skill '*' -g -a '*' -y   # 装到全部 Agent
npx skills add niexia/investment-skills --skill company-research -g -y
npx skills add niexia/investment-skills --skill '*' -g --copy -y   # 复制而非链接
```

| 参数 | 作用 |
| --- | --- |
| `-g` / `--global` | 装到用户级，不加则装到当前项目 |
| `-a` / `--agent` | 指定 Agent，`'*'` 表示全部检测到的 |
| `-s` / `--skill` | 指定 skill，`'*'` 表示全部 |
| `-l` / `--list` | 只列出，不安装 |
| `--copy` | 复制文件，不做符号链接 |
| `-y` / `--yes` | 跳过确认 |

说明与坑：

- 该 CLI 会跳过符号链接，并优先读 `skills/`，不会因为 `.agents/skills` 里的链接而重复计数。
- **不要在这个仓库内部执行项目级安装**（`npx skills add .` 不加 `-g`）。实测它会把 `.agents/skills/<name>` 的链接替换成真实副本；误操作后执行 `python3 scripts/check_skills.py --repair`。
- 插件市场与全局安装都只解决"在哪被发现"，不改变路径解析：skill 引用 `knowledge/`、`data/` 的相对路径，需要工作区（`init` 或克隆目录）才能成立。
- 从远端安装得到的是快照；仓库更新后执行 `npx skills update`，插件市场则重新安装。

## 5. 验证

```bash
# 通用
ls -l ~/.agents/skills

# Claude Code
ls -l ~/.claude/skills

# 仓库内
python3 scripts/check_skills.py --strict
```

然后在 Agent 里用自然语言触发，例如：

```
研究一下腾讯，重点看游戏和 AI 投入对利润率的影响
```

Codex 可以显式点名：`$company-research 腾讯`。
Claude Code 可以直接说需求，或输入 `/` 查看已加载的 skills。

## 6. 常见问题

**Q：为什么源码在 `skills/`，还要 `.agents/skills/`？**
所有 Agent 都要求 `<root>/<name>/SKILL.md` 且只扫一层。`skills/` 是可读、可审阅的唯一源码；`.agents/skills/` 是发现层链接。链接失效时 skill 会**静默消失**，所以 `scripts/check_skills.py` 是必需的。

**Q：会不会出现重复 skill？**
不会。项目级只提交 `.agents/skills` 一个根目录，每个 Agent 在项目里只会看到一次。
之前提交过 `.claude/skills`，那会让同时读多个入口的 Agent（Copilot CLI 会读 `.github/`、`.claude/`、`.agents/`）从两条路径看到同一个 skill；虽然指向同一个文件，但优先级未文档化，所以已移除。取舍见 [`layout-review.md`](research/layout-review.md)。

**Q：`npx skills` 和我自己的脚本冲突吗？**
会，如果在本仓库内部做项目级安装：实测 CLI 会把 `.agents/skills/<name>` 的链接替换成真实副本，`check_skills.py` 会报 `is not a symlink`。恢复方式：`python3 scripts/check_skills.py --repair`。用户级安装（`-g`）与本脚本互不冲突。

**Q：改了 SKILL.md 要重启吗？**
DSH 会监听目录，下一步即生效（改正文甚至不需要重新发现）。其他 Agent 通常需要新会话。

**Q：Claude Code 看不到 skill。**
Claude Code 只读 `.claude/skills/`，本项目不再提交该目录。执行 `./scripts/install-skills.sh`（默认已包含 `~/.claude/skills`），确认 `ls -l ~/.claude/skills` 有 8 个条目。若你的 Claude Code 版本不支持符号链接，用 `--copy`。

**Q：Windows。**
git 检出符号链接需要开发者模式；否则 `.agents/skills` 会变成普通文本文件。用 `--copy`，或直接用 `npx skills add ... --copy`，并在仓库内改用 WSL。

**Q：`npx github:...` 提示找不到包或无法执行？**
仓库还没推到 GitHub（`npx github:` 是从远端拉取，不读本地未提交文件），或网络不可达。先用离线脚本，或 `git push` 后再试。

**Q：用 npx 装完，skill 里的 `knowledge/...` 路径失效？**
装的是 skill 本身，不是工作区。用 `npx investment-skills init <dir>` 生成工作区并在其中工作，或在克隆目录里运行。

**Q：想发布到 npm。**
包名 `investment-skills` 当前未被占用；发布前先补 `LICENSE`（仓库尚未声明许可证），然后 `npm publish`，用户即可 `npx investment-skills install`。不发布也能用 `npx github:niexia/investment-skills`。

**Q：`npx skills add` 报 `[SKILLS_NO_VALID_SKILLS]`。**
远端没有 `skills/`（还没 push），或 frontmatter 缺 `name`/`description`。先 `npx skills add <repo> -l` 确认能找到 8 个；本地可用 `npx skills add . -l` 排除内容问题。

**Q：加第 9 个 skill。**
```bash
mkdir -p skills/<name>
# 按 knowledge/standards/skill-authoring.md 写 SKILL.md
ln -sfn "../../skills/<name>" ".agents/skills/<name>"
python3 scripts/check_skills.py --strict
```

**Q：想让 skill 出现在 Claude Code 的插件市场。**
需要额外维护 `.claude-plugin/marketplace.json`，当前未提供；`npx skills` 与链接方式已覆盖日常使用。

## 7. 参考文档

- Agent Skills 规范：<https://agentskills.io/specification>
- `skills` CLI：<https://github.com/vercel-labs/skills>
- Claude Code skills：<https://code.claude.com/docs/en/skills>
- Codex skills：<https://learn.chatgpt.com/docs/build-skills>
- Cursor skills：<https://cursor.com/docs/skills>
- Gemini CLI skills：<https://geminicli.com/docs/cli/skills/>
- VS Code agent skills：<https://code.visualstudio.com/docs/agent-customization/agent-skills>
- DSH 技能目录：`@deepseek-ai/dsh-skill-filesystem` 包文档
