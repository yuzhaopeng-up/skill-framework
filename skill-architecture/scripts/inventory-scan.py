#!/usr/bin/env python3
"""
inventory-scan.py — 五方Skill资产自动盘点工具

用途:
  1. 扫描各节点的 skills/ 目录，提取SKILL.md frontmatter
  2. 与 unified_skill_inventory.json 对账，发现：
     - 缺失（清单里有，仓库找不到）
     - 孤儿（仓库里有，清单未登记）
     - 不一致（命名/层级/能力域漂移）
  3. 输出报告：增量/告警/统计

用法:
  python inventory-scan.py [--root PATH] [--json] [--strict]

输出:
  默认: 控制台彩色报告
  --json: 机器可读JSON, 便于CI集成
  --strict: 发现问题时exit 1（CI门禁）
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    import yaml  # PyYAML
except ImportError:
    print("[FATAL] need PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ─────────────────────────────────────────────────────────────────────────
# 1. 配置
# ─────────────────────────────────────────────────────────────────────────

DEFAULT_ROOT = Path(__file__).resolve().parents[1]  # 00-methodology/skill-architecture/
INVENTORY_JSON = DEFAULT_ROOT / "unified_skill_inventory.json"

# 节点 → Skill仓库根目录 (相对于workspace根)
NODE_SKILL_ROOTS = {
    "BetaAgent": "skills",
    "AlphaAgent": "../Workspace/financial-ai-skills/skills",  # AlphaAgent私有仓
    # EpsilonAgent / DeltaAgent / GammaAgent 不在此workspace，靠清单维护
}

VALID_LAYERS = {"L0", "L1", "L2", "L3", "L4"}
VALID_CAPABILITY_DOMAINS = {f"C{i:02d}" for i in range(1, 12)}  # C01-C11
VALID_INDUSTRIES = {"universal", "financial", "telecom", "transferable", "general",
                    "healthcare", "legal", "real_estate", "education"}

SKILL_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")  # snake_case


# ─────────────────────────────────────────────────────────────────────────
# 2. 数据结构
# ─────────────────────────────────────────────────────────────────────────

class ScanResult:
    def __init__(self):
        self.skills_on_disk = {}        # name -> dict (来自SKILL.md)
        self.skills_in_inventory = {}   # name -> dict (来自unified_skill_inventory.json)
        self.errors = []                # [{level, code, target, message}]
        self.stats = defaultdict(int)

    def err(self, level, code, target, message):
        self.errors.append({
            "level": level,        # info | warn | error
            "code": code,
            "target": target,
            "message": message
        })

    def to_dict(self):
        # 按level归一统计
        by_level = defaultdict(int)
        for e in self.errors:
            by_level[e["level"]] += 1
        return {
            "scanned_at": datetime.now().isoformat(timespec="seconds"),
            "stats": dict(self.stats),
            "issues_by_level": dict(by_level),
            "issues": self.errors,
            "summary": {
                "skills_on_disk": len(self.skills_on_disk),
                "skills_in_inventory": len(self.skills_in_inventory),
            }
        }


# ─────────────────────────────────────────────────────────────────────────
# 3. 解析器
# ─────────────────────────────────────────────────────────────────────────

def parse_skill_md(path: Path):
    """解析 SKILL.md frontmatter, 返回 dict 或 None."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"read_error: {e}"

    if not text.startswith("---"):
        return None, "no_frontmatter"

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "malformed_frontmatter"

    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return None, f"yaml_error: {e}"

    return fm or {}, None


def normalize_name(raw):
    """归一化Skill名: kebab-case / camelCase / 中文 → snake_case 占位."""
    if not raw:
        return ""
    s = str(raw).strip()
    s = re.sub(r"[-\s]+", "_", s)
    s = re.sub(r"([a-z])([A-Z])", r"\1_\2", s).lower()
    return s


# ─────────────────────────────────────────────────────────────────────────
# 4. 扫描器
# ─────────────────────────────────────────────────────────────────────────

def scan_disk(workspace_root: Path, result: ScanResult):
    """扫描各节点的 skills/ 目录."""
    for node, rel in NODE_SKILL_ROOTS.items():
        skill_root = (workspace_root / rel).resolve()
        if not skill_root.exists():
            result.err("info", "node_root_missing", node,
                       f"Skill root not found: {skill_root}")
            continue

        for skill_dir in sorted(skill_root.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                result.err("warn", "missing_skill_md", str(skill_dir),
                           f"directory has no SKILL.md")
                continue

            fm, err = parse_skill_md(skill_md)
            if err:
                result.err("error", "parse_error", str(skill_md), err)
                continue

            raw_name = fm.get("name") or skill_dir.name
            name = normalize_name(raw_name)
            try:
                rel_path = str(skill_md.relative_to(workspace_root))
            except ValueError:
                rel_path = str(skill_md)
            entry = {
                "name": name,
                "raw_name": raw_name,
                "path": rel_path,
                "node": node,
                "version": fm.get("version", ""),
                "description": fm.get("description", ""),
                "tags": ((fm.get("metadata") or {}).get("hermes") or {}).get("tags", []),
            }

            # 命名规范检查
            if not SKILL_NAME_RE.match(name):
                result.err("warn", "name_not_snake_case", name,
                           f"raw_name={raw_name} 不符合 snake_case 规范")

            # 重复检测（跨节点）
            if name in result.skills_on_disk:
                result.err("info", "duplicate_across_nodes", name,
                           f"已在 {result.skills_on_disk[name]['node']}, 又在 {node}")
            else:
                result.skills_on_disk[name] = entry
                result.stats[f"on_disk_{node}"] += 1


def load_inventory(inventory_path: Path, result: ScanResult):
    """加载统一Skill清单."""
    if not inventory_path.exists():
        result.err("error", "inventory_missing", str(inventory_path),
                   "unified_skill_inventory.json not found")
        return
    try:
        data = json.loads(inventory_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        result.err("error", "inventory_parse", str(inventory_path), f"json error: {e}")
        return

    skills = data.get("skills", []) if isinstance(data, dict) else data
    if not isinstance(skills, list):
        result.err("error", "inventory_format", str(inventory_path),
                   f"expected list of skills, got {type(skills).__name__}")
        return

    for s in skills:
        if not isinstance(s, dict):
            continue
        name = normalize_name(s.get("name") or s.get("skill_id"))
        if not name:
            continue
        result.skills_in_inventory[name] = s
        result.stats["in_inventory"] += 1

        # 字段校验
        layer = s.get("layer") or s.get("level")
        if layer and layer not in VALID_LAYERS:
            result.err("warn", "invalid_layer", name, f"layer={layer}")

        domains = s.get("capability_domain") or s.get("domains") or []
        if isinstance(domains, str):
            domains = [domains]
        for d in domains:
            if d not in VALID_CAPABILITY_DOMAINS:
                result.err("warn", "invalid_domain", name, f"domain={d}")

        industry = s.get("industry") or "universal"
        if industry not in VALID_INDUSTRIES:
            result.err("info", "unknown_industry", name, f"industry={industry}")


def reconcile(result: ScanResult):
    """对账：清单 vs 磁盘."""
    on_disk = set(result.skills_on_disk.keys())
    in_inv = set(result.skills_in_inventory.keys())

    only_on_disk = on_disk - in_inv
    only_in_inv = in_inv - on_disk

    for name in sorted(only_on_disk):
        result.err("warn", "orphan_on_disk", name,
                   f"仓库有但清单未登记 (node={result.skills_on_disk[name]['node']})")

    for name in sorted(only_in_inv):
        # 清单可能记录了多源Skill但实际仓库在其他节点
        sources = result.skills_in_inventory[name].get("sources", [])
        if any(src in NODE_SKILL_ROOTS for src in sources):
            result.err("warn", "missing_on_disk", name,
                       f"清单标注 {sources} 但本次扫描未找到")
        else:
            result.err("info", "external_only", name,
                       f"仅记录在外部节点 {sources}，本workspace无")

    result.stats["only_on_disk"] = len(only_on_disk)
    result.stats["only_in_inventory"] = len(only_in_inv)
    result.stats["matched"] = len(on_disk & in_inv)


# ─────────────────────────────────────────────────────────────────────────
# 5. 渲染
# ─────────────────────────────────────────────────────────────────────────

COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "info": "\033[36m",       # cyan
    "warn": "\033[33m",       # yellow
    "error": "\033[31m",      # red
    "ok": "\033[32m",         # green
}


def render_console(result: ScanResult, no_color: bool = False):
    def c(level, text):
        if no_color:
            return text
        return f"{COLORS.get(level, '')}{text}{COLORS['reset']}"

    print(c("bold", "═" * 70))
    print(c("bold", "  Skill Inventory Scan Report"))
    print(c("bold", f"  scanned at: {datetime.now().isoformat(timespec='seconds')}"))
    print(c("bold", "═" * 70))

    print(f"\n📦 Skills on disk    : {len(result.skills_on_disk)}")
    print(f"📋 Skills in inventory: {len(result.skills_in_inventory)}")
    print(f"✅ Matched (both)    : {result.stats.get('matched', 0)}")
    print(f"🚧 Only on disk      : {result.stats.get('only_on_disk', 0)}")
    print(f"🚧 Only in inventory : {result.stats.get('only_in_inventory', 0)}")

    by_level = defaultdict(int)
    for e in result.errors:
        by_level[e["level"]] += 1
    n_err = by_level["error"]
    n_warn = by_level["warn"]
    n_info = by_level["info"]
    print("\n📊 Issues: "
          + c("error", f"errors={n_err}") + " | "
          + c("warn", f"warnings={n_warn}") + " | "
          + c("info", f"info={n_info}"))

    if not result.errors:
        print(c("ok", "\n  ✓ No issues found."))
        return

    print("\n" + c("bold", "Issues (top 30):"))
    for e in result.errors[:30]:
        sym = {"error": "✗", "warn": "⚠", "info": "ℹ"}.get(e["level"], "·")
        line = f"  {c(e['level'], sym)} [{e['code']}] {e['target']}: {e['message']}"
        print(line)
    if len(result.errors) > 30:
        print(f"  ... and {len(result.errors) - 30} more (use --json for full list)")


# ─────────────────────────────────────────────────────────────────────────
# 6. 主入口
# ─────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Skill 资产自动盘点")
    parser.add_argument("--root", default=None,
                        help="workspace 根目录 (默认: openclaw-workspace)")
    parser.add_argument("--inventory", default=None,
                        help="清单JSON路径 (默认: unified_skill_inventory.json)")
    parser.add_argument("--json", action="store_true", help="输出JSON而非控制台报告")
    parser.add_argument("--strict", action="store_true",
                        help="任何 error/warn 即 exit 1（用于CI）")
    parser.add_argument("--no-color", action="store_true", help="关闭彩色输出")
    args = parser.parse_args()

    workspace_root = Path(args.root).resolve() if args.root \
        else DEFAULT_ROOT.parents[1]    # 退到 openclaw-workspace/
    inventory_path = Path(args.inventory).resolve() if args.inventory else INVENTORY_JSON

    result = ScanResult()
    scan_disk(workspace_root, result)
    load_inventory(inventory_path, result)
    reconcile(result)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        render_console(result, no_color=args.no_color)

    # CI 退出码
    if args.strict:
        has_error = any(e["level"] == "error" for e in result.errors)
        has_warn = any(e["level"] == "warn" for e in result.errors)
        if has_error:
            sys.exit(2)
        if has_warn:
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
