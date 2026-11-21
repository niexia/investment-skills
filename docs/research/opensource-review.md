# 开源项目调研

核查日期：2026-11-21。以下结论来自仓库 API、README 与目录结构，**不是转述推荐文**。

## 先说一个更正

原推荐里的 `sinmentis/ai-berkshire-generic` **确实存在**，但它是 [`xbtlin/ai-berkshire`](https://github.com/xbtlin/ai-berkshire) 的 fork（19 个 skill，MIT，0 star），不是独立项目。
`sinmentis/ai-berkshire` 只是改名后的重定向，指向同一个 fork。

要研究就研究上游：`xbtlin/ai-berkshire`，17,201 star，2026-11-21 仍在更新，22 个 skill。

## 五个项目的核查结果

| 项目 | 真实性 | 许可证 | 内容 | 运行时 | 数据依赖 | 结论 |
| --- | --- | --- | --- | --- | --- | --- |
| [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire) | ✅ 17.2k★，活跃 | MIT | 22 个 skill + `financial_rigor.py` + 2,294 份报告 | Claude Code、Codex | 无付费数据面，靠 agent 联网检索 | **主要方法论来源** |
| [finterm-ai/investment-skills](https://github.com/finterm-ai/investment-skills) | ✅ | MIT | 65 张决策卡 / 8 模块 / 3 工作流 + Python 路由与校验 | 任意 Agent Skills 运行时 | 无 | **主要结构来源** |
| [agentii-ai/agentii-investment-intelligence](https://github.com/agentii-ai/agentii-investment-intelligence) | ✅ 211★ | Apache-2.0 | 80 个 skill / 14 个垂直领域 + 托管 MCP | Claude Code、Codex 等；**不支持 DSH** | **付费**：$19.90/月起，托管数据面与 MCP | **不采用** |
| [davidalmeida90/finance-agent-kit](https://github.com/davidalmeida90/finance-agent-kit) | ✅ 3★ | MIT + Apache-2.0 | 7 个 skill + SEC/market-data 两个 MCP | **原生支持 DSH**（cordis patch、`.dsh/skills`）、Claude Code | 无密钥，但需 SEC 身份；yfinance 非官方 | **只读源码参考** |
| [R1s-t/stock-analysis-skill](https://github.com/R1s-t/stock-analysis-skill) | ✅ 0★ | **无许可证** | 1 个 20KB 的 SKILL.md | Claude Code | 依赖联网检索 | **不能复制**（无授权） |

补充：`sinmentis/ai-berkshire-generic` 是上述第一项的 fork，落后上游约 4 个月，唯一增量是把 skill 改成 agent 中立措辞以支持 GitHub Copilot CLI。可以直接忽略。

## 值得吸收的五件事

### 1. 证据边界（来自 investment-skills）

它的 65 张卡片每张都有固定契约：决策问题、适用条件、分析动作、可观察输出、**限制**、来源。
结论只允许 `supported / challenged / unresolved` 三种。

我们落地为：`knowledge/standards/research-protocol.md` 的三分法 + 置信度标注 + 留白原则；结论四档制。

### 2. 路由 + 卡片上限（来自 investment-skills）

它的 `scripts/framework.py` 是**确定性路由**：同样意图永远加载同一组卡片，且一次最多 12 张，明确把上下文当预算。

我们落地为：8 个 skill 的单一职责 + `company-research` 按步骤编排 + 每个 skill 只读自己需要的 knowledge 文件。没有照搬卡片机制，因为 8 个 skill 还不需要。

### 3. 四视角对抗（来自 ai-berkshire）

四个大师不是"四个 prompt 拼在一起"，而是设计来互相挑战：段永平说好生意，芒格问怎么会死；巴菲特说便宜，李录问十年后还在吗。

我们落地为：`knowledge/investors/` 四份框架 + `investment-thesis` 的强制反方论证 + 顺序规则（先过芒格风险关，再谈巴菲特价格关）。

### 4. 金融严谨性（来自 ai-berkshire）

它的 `financial_rigor.py` 全部用 `decimal.Decimal`，提供市值验算、多源交叉验证、三情景、Benford 检测。

我们落地为：`AGENTS.md` 的计算规则（禁止心算、市值必须校验、单位显式）+ 估值 skill 的复算附录要求。**尚未**实现同等强度的工具脚本，这是阶段 2 的候选。

### 5. 论点追踪（来自 ai-berkshire 的 thesis-tracker / thesis-drift）

买入后持续跟踪论点是否被证伪，并对比两版论点的差异。

我们落地为：`investment-thesis` 的"支柱状态 + 与上版差异 + 决策日志"，文件不覆盖，按日期留存。

## 明确不采用的

| 做法 | 原因 |
| --- | --- |
| 整包安装 agentii | 订阅制 + 托管数据面 + 引用指向厂商域名，与"本地、可复现、无订阅"目标冲突 |
| 复制 stock-analysis-skill 的 31 条规则 | 无许可证，法律上不可再分发 |
| 直接使用 ai-berkshire 的 22 个 skill 原文 | 为 Claude Code 定制（TeamCreate 等），且与我们的港美股数据规范不一致；更适合作为方法论读物 |
| 混合 12 位大师风格 | 风格混用会产生互相矛盾的判断标准，不如四个框架分工明确 |
| 引入 MCP 数据面 | 现阶段数据量小，手动取数 + 事实卡足够；引入 MCP 会增加密钥与可用性依赖 |

## 如果后续要装外部 skill

只在**全局**装，不装进本仓库，避免与自有 skill 抢触发：

```bash
# 仅作为知识补充，不替代 company-research
npx skills add finterm-ai/investment-skills --skill buffett-investment-framework -g --yes
```

装之前确认：① 许可证允许；② 不要求 API key；③ 触发词不与本仓库 8 个 skill 重叠。

## 兼容性矩阵（2026-11 核对）

| 能力 | DSH | Codex | Claude Code | Cursor | Gemini CLI | Copilot | Windsurf/Devin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 项目级 skill 目录 | `.dsh/skills`、`.agents/skills` | `.agents/skills` | `.claude/skills` | `.agents/skills`、`.cursor/skills` | `.agents/skills`、`.gemini/skills` | `.agents/skills`、`.claude/skills`、`.github/skills` | `.agents/skills`、`.devin/skills` |
| 用户级 skill 目录 | `~/.dsh/skills`、`~/.agents/skills` | `~/.agents/skills` | `~/.claude/skills` | `~/.agents/skills` | `~/.agents/skills` | `~/.copilot/skills` | `~/.agents/skills` |
| 扫描深度 | 一层 | 一层 | 一层 | 一层 | 一层 | 一层 | 一层 |
| frontmatter | `name`、`description` 必需 | 同 | 同 | 同 | 同 | 同 | 同 |
| 项目规则文件 | `AGENTS.md` | `AGENTS.md` | `CLAUDE.md`（可 `@AGENTS.md`） | `AGENTS.md` | `GEMINI.md`（可 `@AGENTS.md`） | `AGENTS.md` 或 `.github/copilot-instructions.md` | `AGENTS.md` |
| 跨 Agent 安装器 | `npx skills`（写各 Agent 目录） | 同 | 同 | 同 | 同 | 同 | 同 |

结论：

- **`SKILL.md` 与方法论可以共用一份**，`skills/<name>/SKILL.md` 是当前事实标准。
- **发现目录不能共用一份**：`.agents/skills` 覆盖最多，但 Claude Code 只认 `.claude/skills`，VS Code Copilot 只认 `.github/skills`。用安装器或用户级链接解决，不要复制文件；本仓库只提交 `.agents/skills` 一个项目级根目录，避免多根重复（见 [`layout-review.md`](layout-review.md)）。
- **安装方式已标准化**：`npx skills add <repo> --skill '*' -g` 会自动写入各 Agent 目录，代价是需要 Node ≥ 22.20 且仓库已在 GitHub 上。
- 工具调用、子 Agent 调度、MCP 配置**不能假设一致**，各自运行时分别验证。
