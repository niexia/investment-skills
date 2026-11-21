# 变更记录

只记**影响行为**的改动：skill 流程、输出结构、规则、数据源与安装行为。

## 2026-11-21 · 研究流程与独立报告模板校正

- 校正研究顺序与双语架构图，补齐财报和 ETF 报告模板，收紧税务、配置政策与护城河证据边界，并加固安装器的链接保护。

## 2026-11-21 · 中文架构图与同步规则

- 新增 `docs/assets/architecture.zh-CN.svg`，与英文版结构一一对应；中文 README 改用中文图。
- `AGENTS.md` 增加"文档同步"规则与交付自检项：流程、产出或结构变化时必须同时更新两张图。
- `skill-authoring.md` 的变更流程补上架构图同步。

## 2026-11-21 · 架构图与 README 产品化

- 新增 `docs/assets/architecture.svg`：输入 → 六步流水线 → 三份产出 → 下次财报反馈，底部证据层。
- README 中英两版用同一张图，并把"工作方式"从 ASCII 草图改为三段说明：执行顺序、逐步交接、三份文件与反馈。
- 删除 README 中的实现说明与渠道对比，安装只保留三条入口。

## 2026-11-21 · 插件市场清单

- 新增 6 个分发清单：`.claude-plugin/marketplace.json`、`.claude-plugin/plugin.json`、`.agents/plugins/marketplace.json`、`.codex-plugin/plugin.json`、`.github/plugin/plugin.json`、根目录 `plugin.json`（agent-plugins.org schema）。
- 覆盖 Claude Code、Codex、Copilot CLI、Antigravity CLI 四家市场，与已有 `npx skills` 并存。
- `check_skills.py` 增加清单校验：JSON 可解析、名称与 `package.json` 一致、版本同步，缺 LICENSE 时提示。
- `docs/install.md` 增加渠道对照表（渠道 → 清单文件 → 命令）。

## 2026-11-21 · 增加 npm / npx 安装入口

- 新增 `package.json` 与 `bin/cli.mjs`（零依赖，Node ≥ 18）：`install` / `init` / `list`。
- 分发方式对齐 Chrome `modern-web-guidance`：包内自带 CLI，`npx` 一条命令安装。
- `install` 在克隆目录内链接实时文件；从 npm/npx 运行时自动改为复制，避免链接到临时缓存。
- 新增 `init`：生成含 skills、knowledge、data、portfolio、reports 的完整工作区，解决"只装 skill 导致相对路径失效"。
- `uninstall` 只删除符号链接或带同名 frontmatter 的目录，不误删其他 skill。
- README 与 `docs/install.md` 主入口改为 npm/npx，脚本保留为无 Node 方案。

## 2026-11-21 · 安装简化为一条命令

- `scripts/install-skills.sh` 默认装到三个用户级根目录：`~/.agents/skills`、`~/.claude/skills`、`~/.copilot/skills`，覆盖全部支持的 Agent。
- 移除 `--all`（现为默认）；新增 `--detected`（只装已安装的 Agent）；保留 `--target` 作为旧版目录的逃生口。
- 选择三个根目录的原因：`~/.codex`、`~/.cursor`、`~/.gemini`、`~/.dsh` 与 `~/.agents` 覆盖同一批 Agent，同时写入会造成重复发现。
- README 与 `docs/install.md` 重排：安装章节压缩为"一条命令 + 一张三行目录表"，其余移入文档。

## 2026-11-21 · 修正安装说明与恢复机制

- 实测 `npx skills add niexia/investment-skills -l`：远端只有初始提交时返回 `[SKILLS_NO_VALID_SKILLS]`；README 原用 `<owner>` 占位，无法直接执行，已改为具体仓库并加前置检查。
- 安装方式重排：仓库内零安装 → 离线脚本（现在可用）→ `npx skills`（推送后可选）。
- 实测并记录：在本仓库内部执行项目级 `npx skills add .` 会把 `.agents/skills` 的符号链接**替换成真实副本**。
- `check_skills.py --repair` 支持从"目录副本"恢复为链接（此前只处理链接与缺失）。
- 新增排错项：`SKILLS_NO_VALID_SKILLS` 的两种成因。

## 2026-11-21 · 默认英文 + 目录结构收敛

- README 默认改为英文：`README.md`（English）/ `README.zh-CN.md`（中文），切换链接同步更新。
- **移除提交的 `.claude/skills` 链接**。原因：Copilot CLI 等项目级会同时读 `.github/`、`.claude/`、`.agents/`，两个根目录会让同一个 skill 被发现两次，而多根优先级未文档化。
- 项目级 skill 根目录收敛为唯一一个：`.agents/skills`。Claude Code 改为用户级安装（`./scripts/install-skills.sh --target claude`）。
- `.gitignore` 增加 `.claude/skills`、`.cursor/skills`、`.gemini/skills`、`.github/skills`、`.devin/skills`，防止本地安装目录被误提交。
- 新增 [`docs/research/layout-review.md`](research/layout-review.md)：多 Agent 下的重复来源分析、单根决策与复查清单。
- `AGENTS.md` 增加两条：相对路径以仓库根目录为基准；不得新增第二个项目级 skill 根目录。

## 2026-11-21 · 跨 Agent 安装与双语 README

- README 增加中英切换：`README.md`（中文）/ `README.en.md`（English）。
- 新增 `CLAUDE.md`、`GEMINI.md` 两个 `@AGENTS.md` 指针，以及 `.claude/skills → ../skills` 链接，覆盖 Claude Code 与 Gemini CLI 的项目级发现。
- 安装方式改为三层：仓库内零安装 → `npx skills` 跨 Agent 安装 → 离线脚本。
- `scripts/install-skills.sh` 重写：支持 `--target`、`--all`，目标扩展到 `agents / claude / codex / copilot / dsh / cursor / gemini` 七个用户级根目录。
- `scripts/check_skills.py` 增加兼容文件校验（`.claude/skills` 链接、指针文件是否引用 `AGENTS.md`）。
- 实测：`npx skills` 1.9.0 从本仓库识别 8 个 skill，且不因 `.agents/skills` 链接重复计数。
- 结论：`.agents/skills` 是当前跨 Agent 共同目录，但 Claude Code 只认 `.claude/skills`、VS Code Copilot 只认 `.github/skills`，用链接而非复制解决。

## 2026-11-21 · 初始版本

- 建立仓库结构与全局规则 `AGENTS.md`。
- 8 个 skill：`company-research`、`financial-analysis`、`moat-analysis`、`intrinsic-valuation`、`investment-thesis`、`growth-analysis`、`etf-analysis`、`portfolio-review`。
- 双运行时发现：`skills/` 为源码，`.agents/skills/` 为符号链接（DSH 与 Codex 共用）。
- 规范层：研究协议、输出契约、skill 编写规范。
- 知识层：巴菲特 / 芒格 / 段永平 / 李录框架，一票否决清单，买入前六关，美股港股差异手册。
- 数据层：数据原则、来源登记表、公司与财务模板。
- 组合层：持仓模板、配置政策（默认值待确认）。
- 工具：`scripts/check_skills.py`、`scripts/install-skills.sh`。
- 调研：五个开源项目的核查结论（见 `docs/research/opensource-review.md`），决定不整包安装。
