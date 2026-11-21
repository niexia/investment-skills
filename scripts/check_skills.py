#!/usr/bin/env python3
"""Validate the repository's SKILL.md files and the .agents/skills links.

Checks:
  * frontmatter exists and is closed
  * `name` and `description` present; name is kebab-case and matches the directory
  * required sections exist
  * each documented report type has a starter template
  * `.agents/skills/<name>` is a symlink that resolves to `skills/<name>`
  * no orphan links that point into `skills/` but no longer resolve

Usage:
  python3 scripts/check_skills.py [--strict] [--repair]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
LINKS = ROOT / ".agents" / "skills"
CLAUDE_LINK = ROOT / ".claude" / "skills"
POINTER_FILES = ["CLAUDE.md", "GEMINI.md"]

REQUIRED_SECTIONS = ["何时使用", "输入", "流程", "输出", "质量门", "交接", "禁止"]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_KEYS = {
    "name",
    "description",
    "whenToUse",
    "metadata",
    "user-invocable",
    "disable-model-invocation",
}
MAX_DESC = 160
STRICT_MAX_DESC = 120
MAX_LINES = 220


def read_frontmatter(path: Path) -> tuple[dict[str, str] | None, str, str | None]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, "missing opening '---'"
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, text, "frontmatter not closed by '---'"
    data: dict[str, str] = {}
    for raw in lines[1:end]:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            return None, text, f"cannot parse frontmatter line: {raw!r}"
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data, "\n".join(lines[end + 1 :]), None


def check_skill(skill_dir: Path, strict: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    name = skill_dir.name
    skill_file = skill_dir / "SKILL.md"

    if not skill_file.is_file():
        return [f"missing {skill_file.relative_to(ROOT)}"], warnings

    meta, body, err = read_frontmatter(skill_file)
    if err:
        return [f"{name}: {err}"], warnings
    assert meta is not None

    for key in ("name", "description"):
        if not meta.get(key):
            errors.append(f"{name}: frontmatter missing required key '{key}'")

    fm_name = meta.get("name", "")
    if fm_name and fm_name != name:
        errors.append(f"{name}: frontmatter name '{fm_name}' != directory '{name}'")
    if fm_name and not NAME_RE.match(fm_name):
        errors.append(f"{name}: name is not kebab-case")

    desc = meta.get("description", "")
    if desc:
        if len(desc) > MAX_DESC:
            errors.append(f"{name}: description is {len(desc)} chars (max {MAX_DESC})")
        elif strict and len(desc) > STRICT_MAX_DESC:
            warnings.append(
                f"{name}: description is {len(desc)} chars (strict budget {STRICT_MAX_DESC})"
            )

    extra = set(meta) - ALLOWED_KEYS
    if extra:
        msg = f"{name}: non-portable frontmatter keys {sorted(extra)}"
        (errors if strict else warnings).append(msg)

    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^##\s+{re.escape(section)}", body, re.MULTILINE):
            errors.append(f"{name}: missing section '## {section}'")

    n_lines = len(skill_file.read_text(encoding="utf-8").splitlines())
    if n_lines > MAX_LINES:
        warnings.append(f"{name}: {n_lines} lines (recommended <= {MAX_LINES})")

    link = LINKS / name
    if not link.is_symlink():
        errors.append(
            f"{name}: .agents/skills/{name} is not a symlink "
            f"(a copy? run `python3 scripts/check_skills.py --repair`)"
        )
    else:
        target = Path(os.path.realpath(link))
        expected = Path(os.path.realpath(skill_dir))
        if target != expected:
            errors.append(
                f"{name}: link points to {target} instead of {expected}"
            )
        elif not link.exists():
            errors.append(f"{name}: link is broken")

    return errors, warnings


def repair_links(names: set[str]) -> None:
    LINKS.mkdir(parents=True, exist_ok=True)
    for name in sorted(names):
        link = LINKS / name
        wanted = Path("..") / ".." / "skills" / name
        if link.is_symlink() and Path(os.path.realpath(link)) == Path(
            os.path.realpath(SKILLS / name)
        ):
            continue
        if link.is_symlink() or link.is_file():
            link.unlink()
        elif link.is_dir():
            shutil.rmtree(link)
        link.symlink_to(wanted)
        print(f"repaired: .agents/skills/{name} -> {wanted}")
    for link in sorted(LINKS.iterdir()):
        if link.name in names or not link.is_symlink():
            continue
        if not link.exists() and "skills" in os.readlink(link):
            link.unlink()
            print(f"removed orphan: .agents/skills/{link.name}")


def check_compat_files() -> tuple[list[str], list[str]]:
    """Check the optional cross-agent entry points (Claude Code, Gemini CLI)."""
    errors: list[str] = []
    warnings: list[str] = []

    # The repository deliberately commits only one project-level skill root
    # (.agents/skills). A local .claude/skills link is allowed but should not be
    # committed; see docs/research/layout-review.md.
    if CLAUDE_LINK.is_symlink() or CLAUDE_LINK.exists():
        if CLAUDE_LINK.is_symlink() and Path(os.path.realpath(CLAUDE_LINK)) == Path(
            os.path.realpath(SKILLS)
        ):
            warnings.append(
                "local .claude/skills link present (fine for local use, keep it out of git)"
            )
        else:
            warnings.append(
                ".claude/skills exists but does not point at skills/; "
                "prefer ./scripts/install-skills.sh (installs every agent)"
            )

    for name in POINTER_FILES:
        path = ROOT / name
        if not path.is_file():
            warnings.append(f"missing {name} (some agents will not load AGENTS.md)")
        elif "AGENTS.md" not in path.read_text(encoding="utf-8"):
            warnings.append(f"{name} does not reference AGENTS.md")

    return errors, warnings


MANIFESTS = [
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".github/plugin/plugin.json",
    "plugin.json",
    "package.json",
]
MARKETPLACES = [
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
]


def check_manifests() -> tuple[list[str], list[str]]:
    """Keep plugin manifests and the npm package on the same name and version."""
    errors: list[str] = []
    warnings: list[str] = []
    pkg_path = ROOT / "package.json"
    if not pkg_path.is_file():
        warnings.append("missing package.json (npm/npx install unavailable)")
        return errors, warnings
    try:
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"package.json is not valid JSON: {exc}"], warnings
    name, version = pkg.get("name"), pkg.get("version")

    for rel in MANIFESTS:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing manifest {rel}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel} is not valid JSON: {exc}")
            continue
        if data.get("name") != name:
            errors.append(f"{rel}: name '{data.get('name')}' != package.json '{name}'")
        if rel != "package.json" and data.get("version") != version:
            errors.append(f"{rel}: version '{data.get('version')}' != '{version}'")
        if rel == "plugin.json" and not data.get("$schema"):
            errors.append("plugin.json: missing $schema")

    for rel in MARKETPLACES:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing manifest {rel}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{rel} is not valid JSON: {exc}")
            continue
        for plugin in data.get("plugins", []):
            if plugin.get("version") != version:
                errors.append(
                    f"{rel}: plugin '{plugin.get('name')}' version "
                    f"'{plugin.get('version')}' != '{version}'"
                )

    if not (ROOT / "LICENSE").exists() and not pkg.get("license"):
        warnings.append("no LICENSE file and no license field; choose one before npm publish")
    return errors, warnings


ARCH_EN = ROOT / "docs" / "assets" / "architecture.svg"
ARCH_ZH = ROOT / "docs" / "assets" / "architecture.zh-CN.svg"
REPORT_TEMPLATES = {
    "company-research": "company-research.md",
    "financial-analysis": "financial-analysis.md",
    "etf-analysis": "etf-analysis.md",
    "theses": "thesis.md",
    "portfolio-review": "portfolio-review.md",
}


def check_report_templates() -> tuple[list[str], list[str]]:
    """Every report type documented by the repository must have a starter template."""
    errors: list[str] = []
    templates_dir = ROOT / "reports" / "_template"
    for report_type, template in REPORT_TEMPLATES.items():
        path = templates_dir / template
        if not path.is_file():
            errors.append(f"missing report template for {report_type}: {path.relative_to(ROOT)}")
    return errors, []


def _diagram_shape(path: Path) -> tuple[int, int]:
    root = ET.parse(path).getroot()
    texts = sum(1 for el in root.iter() if el.tag.endswith("text"))
    rects = sum(1 for el in root.iter() if el.tag.endswith("rect"))
    return texts, rects


def check_diagrams() -> tuple[list[str], list[str]]:
    """The English and Chinese architecture diagrams must stay structurally identical."""
    errors: list[str] = []
    warnings: list[str] = []
    if not ARCH_EN.is_file() or not ARCH_ZH.is_file():
        missing = [str(p.relative_to(ROOT)) for p in (ARCH_EN, ARCH_ZH) if not p.is_file()]
        errors.append(f"missing architecture diagram(s): {', '.join(missing)}")
        return errors, warnings
    try:
        en = _diagram_shape(ARCH_EN)
        zh = _diagram_shape(ARCH_ZH)
    except ET.ParseError as exc:
        return [f"architecture diagram is not valid XML: {exc}"], warnings
    if en != zh:
        warnings.append(
            f"architecture diagrams differ in structure (text/rect en={en}, zh={zh}); update both"
        )
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat style warnings as errors")
    parser.add_argument("--repair", action="store_true", help="recreate broken .agents/skills links")
    args = parser.parse_args()

    if not SKILLS.is_dir():
        print(f"error: {SKILLS} not found", file=sys.stderr)
        return 1

    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    if not skill_dirs:
        print("error: no skills found", file=sys.stderr)
        return 1

    names = {p.name for p in skill_dirs}
    if args.repair:
        repair_links(names)

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for skill_dir in skill_dirs:
        errors, warnings = check_skill(skill_dir, args.strict)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    compat_errors, compat_warnings = check_compat_files()
    all_errors.extend(compat_errors)
    all_warnings.extend(compat_warnings)

    manifest_errors, manifest_warnings = check_manifests()
    all_errors.extend(manifest_errors)
    all_warnings.extend(manifest_warnings)

    diagram_errors, diagram_warnings = check_diagrams()
    all_errors.extend(diagram_errors)
    all_warnings.extend(diagram_warnings)

    template_errors, template_warnings = check_report_templates()
    all_errors.extend(template_errors)
    all_warnings.extend(template_warnings)

    if LINKS.is_dir():
        for link in sorted(LINKS.iterdir()):
            if link.name not in names:
                all_warnings.append(f"orphan link: .agents/skills/{link.name}")

    for warning in all_warnings:
        print(f"warn  {warning}")
    for error in all_errors:
        print(f"error {error}", file=sys.stderr)

    if all_errors:
        print(f"\nFAILED: {len(all_errors)} error(s)", file=sys.stderr)
        return 1

    print(f"\n{len(skill_dirs)} skills OK ({len(all_warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
