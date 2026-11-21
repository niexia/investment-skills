# Skill 编写规范

目标：**一份 `SKILL.md` 同时被 DeepSeek Harness（DSH）与 Codex 正确加载**，不出现两套文案。

## 1. 目录与发现路径

```
skills/<name>/SKILL.md          ← 唯一源码（本仓库）
.agents/skills/<name> -> ../../skills/<name>   ← 唯一提交的项目级发现根目录
CLAUDE.md / GEMINI.md                          ← 两行指针，@AGENTS.md
```

`.claude/skills`、`.cursor/skills`、`.gemini/skills`、`.github/skills` 都属于**本地安装目录**，不提交；原因见 [`layout-review.md`](../../docs/research/layout-review.md)。

运行时行为（2026-11 核对）：

| 运行时 | 项目级路径 | 用户级路径 | 扫描深度 |
| --- | --- | --- | --- |
| DSH | `.dsh/skills`（优先）、`.agents/skills` | `~/.dsh/skills`、`~/.agents/skills` | 一层 |
| Codex（桌面端 / CLI / IDE 扩展） | `.agents/skills` | `~/.agents/skills` | 一层 |
| Cursor | `.agents/skills`、`.cursor/skills` | `~/.agents/skills`、`~/.cursor/skills` | 一层 |
| Gemini CLI | `.agents/skills`、`.gemini/skills` | `~/.agents/skills` | 一层 |
| Copilot CLI | `.agents/skills`、`.claude/skills`、`.github/skills` | `~/.copilot/skills` | 一层 |
| Windsurf / Devin | `.agents/skills`、`.devin/skills` | `~/.agents/skills` | 一层 |
| Claude Code | `.claude/skills` | `~/.claude/skills` | 一层 |
| Copilot（VS Code） | `.github/skills` | — | 一层 |

推论（必须遵守）：

- **不能**依赖嵌套路径发现，例如 `skills/value/company-research/SKILL.md` 在多数运行时不会被发现。
- 目录名必须与 frontmatter 的 `name` 完全一致，且为 kebab-case（规范要求 1–64 字符，仅 `a-z0-9-`，不能有首尾或连续连字符）。
- 新增 skill 必须同时建 `.agents/skills/<name>` 链接；不要在仓库里新增第二个项目级根目录（如 `.claude/skills`），否则同时读多个根的 Agent 会重复发现同一个 skill。
- 链接失效时 skill 会**静默消失**，所以 `scripts/check_skills.py` 是必需的。

## 2. Frontmatter

只写两个字段，保证最大兼容性：

```yaml
---
name: company-research
description: 对美股或港股上市公司做完整基本面研究时使用；输出带来源与证伪条件的投资备忘录。触发：研究一下 X、值不值得投、深度研究、护城河。
---
```

规则：

- `name`：kebab-case，与目录同名，≤ 64 字符。
- `description`：**一行**，先写"什么时候用"，再写"产出什么"，最后给 3–5 个触发词。控制在 120 字以内——DSH 会把描述截断进上下文，太长会丢关键触发词。
- 不要写 `version`、`author`、`license` 等自定义字段：Codex 与 DSH 对未知字段的容忍度不同，写在正文里更安全。
- 不要用多行 YAML（`>` / `|`），减少解析差异。

## 3. 正文必备章节

按顺序，缺一节就不合格：

1. `# <标题>` — 一句话说明这个 skill 解决什么问题
2. `## 何时使用` — 触发场景 + **不适用场景**（防止误触发）
3. `## 输入` — 必需 / 可选；缺失时怎么办
4. `## 流程` — 编号步骤，每步有可执行动作和产出
5. `## 输出` — 写到哪个路径、用哪个模板、包含哪些章节
6. `## 质量门` — 交付前必须通过的检查项
7. `## 交接` — 上游读什么、下游交给谁
8. `## 禁止` — 本 skill 特有的红线

## 4. 写作约束

- **单一职责**：一个 skill 只回答一类问题。需要别的能力就调用别的 skill，不复制逻辑。
- **不重复全局规则**：证据、计算、命名规则在 `AGENTS.md`；正文只写本 skill 特有的内容，用链接引用。
- **可执行**：每一步都要能落成动作（读哪个文件、查哪个来源、算什么），不写"深入分析"这类空指令。
- **给判断标准**：写"满足 A 且 B 视为通过"，不写"综合评估"。
- **控制长度**：单个 SKILL.md 建议 80–160 行。超过 200 行说明该拆分。

## 5. 验证

```bash
python3 scripts/check_skills.py          # frontmatter、命名、必备章节、链接
python3 scripts/check_skills.py --strict # 额外检查描述长度与禁止字段
```

在 DSH 中验证是否被发现：新开一个位于本仓库的会话，检查 skill 目录里是否出现该名称，或直接说触发词看是否加载。

## 6. 变更流程

1. 改 `skills/<name>/SKILL.md`。
2. 跑校验脚本。
3. 在 `docs/changelog.md` 记一行：改了什么、为什么。
4. 若改动影响输出结构，同步更新 `knowledge/standards/output-contract.md` 与 `reports/_template/`。
5. 若改动影响流程或产出，同步更新两张架构图（`docs/assets/architecture.svg` 与 `architecture.zh-CN.svg`）和中英 README。
