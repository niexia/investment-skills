#!/usr/bin/env node
// CLI entry point: npx investment-skills <command>
//
// The same layout rules as scripts/install-skills.sh:
//   install  -> link skills into agent directories (user level by default)
//   init     -> scaffold a full workspace (skills + knowledge + templates)
//   list     -> print the skills in the current or packaged workspace
//
// Zero dependencies, Node >= 18.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PKG_ROOT = path.resolve(__dirname, '..');

const TARGETS = {
  agents: ['.agents', 'skills'],
  claude: ['.claude', 'skills'],
  copilot: ['.copilot', 'skills'],
  codex: ['.codex', 'skills'],
  dsh: ['.dsh', 'skills'],
  cursor: ['.cursor', 'skills'],
  gemini: ['.gemini', 'skills'],
};
const DEFAULT_TARGETS = ['agents', 'claude', 'copilot'];

const WORKSPACE_MARKERS = ['skills', 'knowledge', 'AGENTS.md'];

function log(msg) {
  process.stdout.write(`${msg}\n`);
}
function fail(msg) {
  process.stderr.write(`error ${msg}\n`);
  process.exit(1);
}

function parseArgs(argv) {
  const opts = {
    command: null,
    dir: null,
    dryRun: false,
    copy: false,
    detected: false,
    force: false,
    uninstall: false,
    targets: null,
    from: null,
    help: false,
  };
  const positional = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') opts.help = true;
    else if (arg === '--dry-run') opts.dryRun = true;
    else if (arg === '--copy') opts.copy = true;
    else if (arg === '--detected') opts.detected = true;
    else if (arg === '--force') opts.force = true;
    else if (arg === '--uninstall') opts.uninstall = true;
    else if (arg === '--target') opts.targets = argv[++i] ?? fail('--target needs a value');
    else if (arg.startsWith('--target=')) opts.targets = arg.slice('--target='.length);
    else if (arg === '--from') opts.from = argv[++i] ?? fail('--from needs a value');
    else if (arg.startsWith('-')) fail(`unknown option: ${arg}`);
    else positional.push(arg);
  }
  opts.command = positional[0] ?? null;
  opts.dir = positional[1] ?? null;
  return opts;
}

function looksLikeWorkspace(dir) {
  return WORKSPACE_MARKERS.every((entry) => fs.existsSync(path.join(dir, entry)));
}

function resolveWorkspace(opts) {
  if (opts.from) {
    const dir = path.resolve(opts.from);
    if (!looksLikeWorkspace(dir)) fail(`${dir} is not a workspace (needs skills/, knowledge/, AGENTS.md)`);
    return dir;
  }
  if (looksLikeWorkspace(process.cwd())) return process.cwd();
  return PKG_ROOT;
}

function listSkills(workspace) {
  const dir = path.join(workspace, 'skills');
  if (!fs.existsSync(dir)) fail(`no skills/ in ${workspace}`);
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function readSkillName(skillFile) {
  try {
    const text = fs.readFileSync(skillFile, 'utf8');
    const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!match) return '';
    const line = match[1].split(/\r?\n/).find((l) => l.startsWith('name:'));
    return line ? line.slice('name:'.length).trim().replace(/^["']|["']$/g, '') : '';
  } catch {
    return '';
  }
}

function readDescription(skillFile) {
  try {
    const text = fs.readFileSync(skillFile, 'utf8');
    const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!match) return '';
    const line = match[1].split(/\r?\n/).find((l) => l.startsWith('description:'));
    return line ? line.slice('description:'.length).trim().replace(/^["']|["']$/g, '') : '';
  } catch {
    return '';
  }
}

function targetPath(name) {
  const parts = TARGETS[name];
  if (!parts) fail(`unknown target: ${name}`);
  return path.join(os.homedir(), ...parts);
}

function resolveTargets(opts) {
  if (opts.targets) {
    const names = opts.targets.split(',').map((s) => s.trim()).filter(Boolean);
    for (const name of names) if (!TARGETS[name]) fail(`unknown target: ${name}`);
    return names;
  }
  if (!opts.detected) return [...DEFAULT_TARGETS];
  const found = DEFAULT_TARGETS.filter((name) => {
    const dir = targetPath(name);
    return fs.existsSync(path.dirname(dir));
  });
  if (found.length === 0) fail('no agent directory detected; run without --detected to create them');
  return found;
}

function ensureDir(dir, dryRun) {
  if (!dryRun) fs.mkdirSync(dir, { recursive: true });
}

function removePath(target, dryRun) {
  if (dryRun) return;
  const stat = fs.lstatSync(target);
  if (stat.isSymbolicLink() || stat.isFile()) fs.unlinkSync(target);
  else fs.rmSync(target, { recursive: true, force: true });
}

function makeLink(src, dest, opts) {
  const stat = (() => {
    try {
      return fs.lstatSync(dest);
    } catch {
      return null;
    }
  })();
  if (stat) {
    if (!stat.isSymbolicLink()) {
      if (!opts.force) {
        log(`warn  skip ${dest} (exists and is not a symlink; use --force)`);
        return false;
      }
      if (!opts.dryRun) fs.renameSync(dest, `${dest}.bak.${Date.now()}`);
    }
    if (!opts.dryRun) fs.unlinkSync(dest);
  }
  if (opts.copy) {
    if (opts.dryRun) return true;
    fs.cpSync(src, dest, { recursive: true });
    return true;
  }
  const type = process.platform === 'win32' ? 'junction' : 'dir';
  try {
    if (!opts.dryRun) fs.symlinkSync(src, dest, type);
    return true;
  } catch (error) {
    log(`warn  cannot symlink ${dest}: ${error.message}`);
    log('      on Windows enable Developer Mode, or rerun with --copy');
    return false;
  }
}

function linkInto(workspace, dir, names, opts) {
  ensureDir(dir, opts.dryRun);
  let done = 0;
  for (const name of names) {
    const src = path.join(workspace, 'skills', name);
    const dest = path.join(dir, name);
    const stat = fs.existsSync(dest) ? fs.lstatSync(dest) : null;
    if (opts.uninstall) {
      if (!stat) continue;
      const ours =
        stat.isSymbolicLink() ||
        (stat.isDirectory() && readSkillName(path.join(dest, 'SKILL.md')) === name);
      if (ours) {
        if (!opts.dryRun) fs.rmSync(dest, { recursive: true, force: true });
        done += 1;
      } else {
        log(`warn  skip ${dest} (not one of our skills)`);
      }
      continue;
    }
    if (makeLink(src, dest, opts)) done += 1;
  }
  if (opts.uninstall) log(`removed ${done} skills <- ${dir}`);
  else log(`installed ${done} skills -> ${dir}`);
}

function installProject(workspace, names, opts) {
  const dir = path.join(workspace, '.agents', 'skills');
  ensureDir(dir, opts.dryRun);
  let done = 0;
  for (const name of names) {
    const src = path.join(workspace, 'skills', name);
    const dest = path.join(dir, name);
    const rel = path.join('..', '..', 'skills', name);
    const stat = fs.existsSync(dest) ? fs.lstatSync(dest) : null;
    if (stat?.isSymbolicLink()) {
      if (!opts.dryRun) fs.unlinkSync(dest);
    } else if (stat) {
      if (!opts.force) {
        log(`warn  skip ${dest} (exists; use --force)`);
        continue;
      }
      removePath(dest, opts.dryRun);
    }
    try {
      if (!opts.dryRun) {
        if (process.platform === 'win32') fs.symlinkSync(src, dest, 'junction');
        else fs.symlinkSync(rel, dest, 'dir');
      }
      done += 1;
    } catch (error) {
      log(`warn  cannot link ${dest}: ${error.message}`);
    }
  }
  log(`installed ${done} skills -> ${dir}`);
}

function cmdInstall(opts) {
  const workspace = resolveWorkspace(opts);
  const names = listSkills(workspace);
  if (opts.uninstall) {
    for (const target of resolveTargets(opts)) linkInto(workspace, targetPath(target), names, opts);
    return;
  }
  if (workspace === PKG_ROOT) {
    log('note  installing packaged skills (copied, not linked: the npm cache is temporary)');
    opts.copy = true;
  }
  for (const target of resolveTargets(opts)) linkInto(workspace, targetPath(target), names, opts);
  log('');
  log('restart the agent (or start a new session) to pick them up.');
  log('verify: python3 scripts/check_skills.py   (inside the workspace)');
}

function cmdInit(opts) {
  const dest = path.resolve(opts.dir ?? 'investment-workspace');
  if (fs.existsSync(dest) && fs.readdirSync(dest).length > 0) {
    fail(`${dest} already exists and is not empty`);
  }
  const include = [
    'skills', 'knowledge', 'data', 'portfolio', 'reports', 'docs', 'scripts',
    'AGENTS.md', 'README.md', 'README.zh-CN.md', 'CLAUDE.md', 'GEMINI.md',
  ];
  if (opts.dryRun) {
    log(`dry-run: create ${dest}`);
    for (const entry of include) log(`dry-run: copy ${entry}`);
    log(`dry-run: link ${listSkills(PKG_ROOT).length} skills -> ${path.join(dest, '.agents', 'skills')}`);
    return;
  }
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of include) {
    const src = path.join(PKG_ROOT, entry);
    if (!fs.existsSync(src)) continue;
    fs.cpSync(src, path.join(dest, entry), {
      recursive: true,
      filter: (from) => !from.includes(`${path.sep}.git${path.sep}`) && !from.endsWith(`${path.sep}.git`),
    });
  }
  for (const empty of [
    'data/companies', 'data/financials', 'data/market',
    'reports/company-research', 'reports/financial-analysis',
    'reports/etf-analysis', 'reports/theses', 'reports/portfolio-review',
  ]) {
    fs.mkdirSync(path.join(dest, empty), { recursive: true });
  }
  const names = listSkills(dest);
  installProject(dest, names, opts);
  log('');
  log(`workspace created: ${dest}`);
  log(`next: cd ${path.relative(process.cwd(), dest) || '.'}`);
  log('      open your agent there, then run: npx investment-skills install');
}

function cmdList(opts) {
  const workspace = resolveWorkspace(opts);
  const names = listSkills(workspace);
  log(`${names.length} skills in ${workspace}`);
  for (const name of names) {
    const desc = readDescription(path.join(workspace, 'skills', name, 'SKILL.md'));
    log(`  ${name.padEnd(20)} ${desc.slice(0, 72)}`);
  }
}

function usage() {
  log(`investment-skills — Agent Skills for US/HK equity research

Usage:
  investment-skills install [options]   link skills into agent directories
  investment-skills init [dir]          scaffold a full workspace
  investment-skills list                list skills
  investment-skills --help

Options:
  --dry-run            print actions without writing
  --copy               copy files instead of symlinking
  --detected           only agent directories already present
  --target a,b         agents,claude,copilot,codex,dsh,cursor,gemini
  --force              back up an existing real directory
  --from <dir>         workspace to install from (default: cwd)
  --uninstall          remove links created by this tool`);
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help || !opts.command) {
    usage();
    return;
  }
  if (opts.command === 'install') return cmdInstall(opts);
  if (opts.command === 'init') return cmdInit(opts);
  if (opts.command === 'list' || opts.command === 'ls') return cmdList(opts);
  fail(`unknown command: ${opts.command} (try --help)`);
}

main();
