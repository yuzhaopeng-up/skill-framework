#!/usr/bin/env python3
"""
skill-lint.py — Skill 强制门禁静态检查

检查项 (对应 governance/quality-gates.md):
  G1 名称 snake_case
  G2 frontmatter 完整 (必填: name, description, version, author, license, layer,
                       capability_domain, industry)
  G3 SKILL.md 文档骨架 (核心能力/输入输出/使用示例)
  G4 无硬编码凭据 (token / 密钥 / 手机号 / 身份证)
  G5 输入输出契约关键词存在

用法:
  skill-lint.py [PATH ...]            # 检查指定路径，默认 skills/
  skill-lint.py --strict              # 任何 fail 即 exit 1
  skill-lint.py --json                # 输出JSON
  skill-lint.py --quality silver      # 同时检查 Silver+ 级别项
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[FATAL] need PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# ─────────────────────────────────────────────────────
# 检查规则
# ─────────────────────────────────────────────────────

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
VALID_LAYERS = {"L0", "L1", "L2", "L3", "L4"}

REQUIRED_FRONTMATTER = [
    "name", "description", "version", "author", "license"
]
RECOMMENDED_FRONTMATTER = [
    "layer", "capability_domain", "industry"
]

# 必备文档章节关键词
REQUIRED_SECTIONS = [
    ["核心能力", "Core Capabilities", "Capabilities", "能力"],
    ["输入", "Input", "输入输出", "Input/Output", "Inputs"],
    ["示例", "Example", "Usage", "使用示例", "示范"],
]

# 凭据泄露模式
SECRET_PATTERNS = [
    (re.compile(r"(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
     "hardcoded credential"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GitHub PAT"),
    (re.compile(r"\b1[3-9]\d{9}\b"), "China mobile number (PII)"),
    (re.compile(r"\b\d{17}[\dXx]\b"), "China ID (PII, 18-digit)"),
]
# 通过白名单：示例/占位符
SECRET_WHITELIST = [
    "your_token_here", "<TOKEN>", "${TOKEN}", "REDACTED", "xxxx", "13800138000",
    "11111111111111111X", "1234567890",
]


# ─────────────────────────────────────────────────────
# 检查器
# ─────────────────────────────────────────────────────

class Issue:
    __slots__ = ("level", "code", "message", "line")

    def __init__(self, level, code, message, line=None):
        self.level = level    # error | warn | info
        self.code = code
        self.message = message
        self.line = line

    def to_dict(self):
        return {"level": self.level, "code": self.code,
                "message": self.message, "line": self.line}


def lint_skill(skill_dir: Path, quality: str = "bronze"):
    """对单个 Skill 目录执行 lint."""
    issues = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        issues.append(Issue("error", "G3_no_skill_md",
                            f"missing SKILL.md in {skill_dir}"))
        return issues, None

    text = skill_md.read_text(encoding="utf-8", errors="replace")

    # G2: frontmatter
    if not text.startswith("---"):
        issues.append(Issue("error", "G2_no_frontmatter",
                            "SKILL.md must start with YAML frontmatter (---)"))
        return issues, None

    parts = text.split("---", 2)
    if len(parts) < 3:
        issues.append(Issue("error", "G2_malformed_frontmatter",
                            "frontmatter not closed (need second ---)"))
        return issues, None

    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        issues.append(Issue("error", "G2_yaml_error", f"YAML error: {e}"))
        return issues, None

    body = parts[2]

    # G2: 必填字段
    for k in REQUIRED_FRONTMATTER:
        if not fm.get(k):
            issues.append(Issue("error", "G2_missing_field",
                                f"frontmatter missing required field: {k}"))
    # 推荐字段
    for k in RECOMMENDED_FRONTMATTER:
        if not fm.get(k):
            issues.append(Issue("warn", "G2_missing_recommended",
                                f"frontmatter missing recommended field: {k}"))

    # G1: 名称
    name = fm.get("name", "")
    if name and not NAME_RE.match(str(name)):
        issues.append(Issue("error", "G1_name_format",
                            f"name '{name}' is not snake_case"))

    # G2: 版本号
    if fm.get("version") and not SEMVER_RE.match(str(fm["version"])):
        issues.append(Issue("warn", "G2_version_format",
                            f"version '{fm['version']}' is not semver"))

    # G2: layer 合法性
    layer = fm.get("layer")
    if layer and layer not in VALID_LAYERS:
        issues.append(Issue("error", "G2_invalid_layer",
                            f"layer '{layer}' not in {sorted(VALID_LAYERS)}"))

    # G2: description 长度
    desc = fm.get("description", "")
    if 0 < len(desc) < 20:
        issues.append(Issue("warn", "G2_description_short",
                            f"description too short ({len(desc)} chars, need ≥20)"))
    elif len(desc) > 200:
        issues.append(Issue("warn", "G2_description_long",
                            f"description too long ({len(desc)} chars, ≤200)"))

    # G3: 必备章节
    for keywords in REQUIRED_SECTIONS:
        if not any(k in body for k in keywords):
            issues.append(Issue("warn", "G3_missing_section",
                                f"missing section: any of {keywords}"))

    # G3: 文档行数
    if body.count("\n") < 30:
        issues.append(Issue("info", "G3_short_doc",
                            f"document body has only {body.count(chr(10))} lines"))

    # G4: 凭据扫描（在 body 中扫，frontmatter 例外）
    for line_no, line in enumerate(body.splitlines(), start=1):
        for pattern, label in SECRET_PATTERNS:
            m = pattern.search(line)
            if m:
                snippet = m.group(0)
                if any(w in snippet for w in SECRET_WHITELIST):
                    continue
                issues.append(Issue("error", "G4_potential_secret",
                                    f"{label}: {snippet[:50]}", line=line_no))

    # G5: 输入输出契约关键词（弱检查）
    if "输入" not in body and "Input" not in body and "input" not in body:
        issues.append(Issue("warn", "G5_no_input_spec",
                            "no input specification found"))

    # Silver+: G8 测试 / G9 图
    if quality in ("silver", "gold"):
        has_tests = (skill_dir / "tests").exists() or (skill_dir / "test").exists() \
                    or any(f.name.startswith("test_") for f in skill_dir.glob("*.py"))
        if not has_tests:
            issues.append(Issue("warn", "G8_no_tests",
                                "Silver+ requires tests/ directory or test_*.py"))
        if "```mermaid" not in body and "![" not in body:
            issues.append(Issue("warn", "G9_no_diagram",
                                "Silver+ recommends architecture/flow diagram"))

    return issues, fm


# ─────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Skill quality gate linter")
    parser.add_argument("paths", nargs="*",
                        help="Skill directories or parent directories (default: skills/)")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 on any error/warn")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--quality", default="bronze",
                        choices=["bronze", "silver", "gold"],
                        help="Quality level to enforce (default: bronze)")
    args = parser.parse_args()

    # 解析路径
    targets = []
    if args.paths:
        for p in args.paths:
            path = Path(p).resolve()
            if (path / "SKILL.md").exists():
                targets.append(path)
            elif path.is_dir():
                # 父目录, 找下一层的 SKILL.md
                for sub in sorted(path.iterdir()):
                    if sub.is_dir() and (sub / "SKILL.md").exists():
                        targets.append(sub)
    else:
        # 默认扫 ./skills/
        default = Path("skills").resolve()
        if default.exists():
            for sub in sorted(default.iterdir()):
                if sub.is_dir() and (sub / "SKILL.md").exists():
                    targets.append(sub)

    if not targets:
        print("[skill-lint] no Skill targets found", file=sys.stderr)
        sys.exit(0)

    all_results = []
    n_err = n_warn = n_info = 0
    for skill in targets:
        issues, fm = lint_skill(skill, quality=args.quality)
        for i in issues:
            if i.level == "error":
                n_err += 1
            elif i.level == "warn":
                n_warn += 1
            else:
                n_info += 1
        all_results.append({
            "skill": str(skill),
            "name": (fm or {}).get("name", skill.name),
            "issues": [i.to_dict() for i in issues],
        })

    if args.json:
        print(json.dumps({
            "scanned": len(targets),
            "errors": n_err, "warnings": n_warn, "info": n_info,
            "quality_level": args.quality,
            "results": all_results,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"━━━ skill-lint @ quality={args.quality} ━━━")
        print(f"Scanned: {len(targets)} skills")
        print(f"Errors:  {n_err}")
        print(f"Warns:   {n_warn}")
        print(f"Info:    {n_info}\n")
        for r in all_results:
            if not r["issues"]:
                continue
            print(f"  [{r['name']}]  ({r['skill']})")
            for i in r["issues"][:5]:
                sym = {"error": "✗", "warn": "⚠", "info": "ℹ"}[i["level"]]
                line_str = f" L{i['line']}" if i.get("line") else ""
                print(f"    {sym} [{i['code']}]{line_str} {i['message']}")
            if len(r["issues"]) > 5:
                print(f"    ... and {len(r['issues']) - 5} more")

    if args.strict:
        if n_err > 0:
            sys.exit(2)
        if n_warn > 0:
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
