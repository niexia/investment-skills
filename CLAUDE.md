# Claude Code entry point

本仓库的规则、证据标准与交付要求全部写在根目录的 `AGENTS.md`。

@AGENTS.md

技能位于 `skills/<name>/SKILL.md`。Claude Code 不读 `.agents/skills`，执行一次
`./scripts/install-skills.sh` 即可装到 `~/.claude/skills`（同时覆盖其他 Agent）。
