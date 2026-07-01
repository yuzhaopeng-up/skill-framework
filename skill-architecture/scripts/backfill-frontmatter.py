#!/usr/bin/env python3
"""
backfill-frontmatter.py — 给存量 SKILL.md 智能补全 YAML frontmatter

策略:
  1. 从目录名提取 name (snake_case)
  2. 从 H1 提取标题, 用作 raw_name 和补充描述
  3. 从"概述"/"简介"/"用途"段提取 description (前 200 字, 截断到句号)
  4. 推断 layer/capability_domain/industry:
     - layer: 目录里有 multi-agent/orchestrate 等关键词 → L4; 调用 ≥3 个其他Skill → L3;
              文档/数据/查询 → L2; 单一职能 → L1; 仅是连接器 → L0;
              默认 L2(组合层)
     - capability_domain: 关键词匹配 11 大能力域
     - industry: 路径或关键词匹配 (financial_*, telecom_*, generic)
  5. version 默认 1.0.0; license 默认 MIT; author 从 git log 推断, 失败则用 'OpenClaw Team'
  6. 写入 frontmatter, body 保持原样

安全:
  - 不修改已有 frontmatter 的文件
  - 写入前打印 dry-run 摘要; --apply 才落盘
  - 备份原文件到 .bak（可关闭 --no-backup）

用法:
  backfill-frontmatter.py --dry-run                    # 预览
  backfill-frontmatter.py --apply                      # 真写
  backfill-frontmatter.py --apply --skill skills/alm   # 只处理一个
"""
import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────
# 推断规则
# ─────────────────────────────────────────────────────

LAYER_HINTS = [
    (re.compile(r"(multi[_-]?agent|orchestrat|协同|集群|联防)", re.I), "L4"),
    (re.compile(r"(workflow|pipeline|workbench|场景|工作台|驾驶舱|中枢)", re.I), "L3"),
    (re.compile(r"(router|engine|aggregator|integrator|批处理|路由|引擎)", re.I), "L2"),
    (re.compile(r"(connector|adapter|client|sdk|webhook|连接器|适配器)", re.I), "L0"),
]

DOMAIN_HINTS = [
    (re.compile(r"(NLP|nlu|意图|分类|情感|语义|理解)", re.I), "C01"),
    (re.compile(r"(generate|writer|creator|生成|写作|内容)", re.I), "C02"),
    (re.compile(r"(data|分析|报表|统计|指标|数据)", re.I), "C03"),
    (re.compile(r"(document|pdf|word|excel|ocr|文档|合同|发票)", re.I), "C04"),
    (re.compile(r"(reasoning|decide|推理|决策|策略|风控|评估)", re.I), "C05"),
    (re.compile(r"(image|video|vision|影像|图片|视觉)", re.I), "C06"),
    (re.compile(r"(notify|alert|chat|消息|通知|告警|协作)", re.I), "C07"),
    (re.compile(r"(kb|knowledge|knowledge_base|rag|知识库|知识|检索)", re.I), "C08"),
    (re.compile(r"(integration|api|connector|adapter|连接|集成|对接)", re.I), "C09"),
    (re.compile(r"(security|compliance|audit|合规|审计|权限|安全)", re.I), "C10"),
    (re.compile(r"(insurance|bank|wealth|fund|loan|医疗|法律|教育|地产|金融|银行|保险|证券)", re.I), "C11"),
]

INDUSTRY_HINTS = [
    (re.compile(r"(bank|loan|wealth|fund|insurance|securit|invest|alm|risk|信贷|理财|基金|银行|保险|证券|资产|风控|金融)", re.I), "financial"),
    (re.compile(r"(telecom|5g|宽带|基站|工单|装维|telecom|通信)", re.I), "telecom"),
    (re.compile(r"(medical|health|diagnos|emr|fhir|hl7|医疗|诊断)", re.I), "healthcare"),
    (re.compile(r"(legal|contract|law|律师|法律|合同|合规)", re.I), "legal"),
    (re.compile(r"(estate|property|housing|房产|楼盘|物业)", re.I), "real_estate"),
    (re.compile(r"(school|teach|课程|教学|学生|教育)", re.I), "education"),
]


# ─────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────

def to_snake_case(s: str) -> str:
    s = re.sub(r"[-\s]+", "_", s.strip())
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()
    s = re.sub(r"[^a-z0-9_]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def extract_h1(body: str):
    """提取首个 # 标题."""
    for line in body.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return m.group(1).strip()
    return None


def extract_description(body: str, max_chars: int = 180) -> str:
    """从'概述/简介/用途/Overview'段抽 description."""
    # 找'## 概述' 或类似
    section_pat = re.compile(
        r"^##\s*(?:概述|简介|用途|Overview|Description|功能|核心能力|介绍)\s*\n+(.*?)(?=\n##|\Z)",
        re.M | re.S,
    )
    m = section_pat.search(body)
    if m:
        text = m.group(1).strip()
    else:
        # 退化：取 H1 之后的第一段非空文字
        lines = body.splitlines()
        text = ""
        in_body = False
        for line in lines:
            if line.startswith("# "):
                in_body = True
                continue
            if in_body and line.strip() and not line.startswith("#"):
                text = line.strip()
                break

    # 清理 markdown 标记，截断到第一个句号
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # 表格/分隔符/列表符号会污染 yaml 描述，剔除
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"^[\s>•\-*]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    # 截断
    if len(text) > max_chars:
        # 尝试在标点处截断
        cut = text[:max_chars]
        for sep in ["。", "！", ".", "；", ";"]:
            idx = cut.rfind(sep)
            if idx > max_chars // 2:
                cut = cut[: idx + 1]
                break
        text = cut.rstrip("，,、 ") + ("…" if not text.endswith(("。", "！", ".")) else "")

    if not text:
        text = "Skill module (auto-generated frontmatter; please refine description)"
    return text


def infer_layer(name: str, body: str) -> str:
    target = f"{name} {body[:1000]}"
    for pat, layer in LAYER_HINTS:
        if pat.search(target):
            return layer
    return "L1"  # 保守估计：单职能基础Skill


def infer_domains(name: str, body: str):
    target = f"{name} {body[:2000]}"
    domains = []
    for pat, dom in DOMAIN_HINTS:
        if pat.search(target):
            if dom not in domains:
                domains.append(dom)
    return domains[:3] if domains else ["C09"]  # 默认归到集成连接


def infer_industry(name: str, body: str, path: Path) -> str:
    target = f"{path} {name} {body[:2000]}"
    for pat, ind in INDUSTRY_HINTS:
        if pat.search(target):
            return ind
    return "universal"


def get_git_author(file_path: Path) -> str:
    """从 git log 里读最后一个 author，失败时返回默认值."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%an", "--", str(file_path)],
            cwd=file_path.parent,
            capture_output=True, text=True, timeout=5,
        )
        author = result.stdout.strip()
        if author:
            return author
    except Exception:
        pass
    return "OpenClaw Team"


# ─────────────────────────────────────────────────────
# 主补全
# ─────────────────────────────────────────────────────

def build_frontmatter(skill_dir: Path, body: str) -> dict:
    raw_name = extract_h1(body) or skill_dir.name
    name = to_snake_case(skill_dir.name)
    description = extract_description(body)
    layer = infer_layer(skill_dir.name, body)
    domains = infer_domains(skill_dir.name, body)
    industry = infer_industry(skill_dir.name, body, skill_dir)
    author = get_git_author(skill_dir / "SKILL.md")

    return {
        "name": name,
        "description": description,
        "version": "1.0.0",
        "author": author,
        "license": "MIT",
        "layer": layer,
        "capability_domain": domains,
        "industry": industry,
        "metadata": {
            "raw_title": raw_name,
            "auto_generated": True,
            "auto_generated_at": datetime.now().strftime("%Y-%m-%d"),
        },
    }


def render_frontmatter(fm: dict) -> str:
    """渲染 YAML frontmatter (固定字段顺序，可读)."""
    lines = ["---"]
    lines.append(f'name: {fm["name"]}')
    # description 加引号防止特殊字符
    desc = fm["description"].replace('"', '\\"')
    lines.append(f'description: "{desc}"')
    lines.append(f'version: {fm["version"]}')
    lines.append(f'author: {fm["author"]}')
    lines.append(f'license: {fm["license"]}')
    lines.append(f'layer: {fm["layer"]}')
    domains = fm["capability_domain"]
    lines.append(f"capability_domain: [{', '.join(domains)}]")
    lines.append(f'industry: {fm["industry"]}')
    lines.append("metadata:")
    raw = fm["metadata"]["raw_title"].replace('"', '\\"')
    lines.append(f'  raw_title: "{raw}"')
    lines.append(f'  auto_generated: {str(fm["metadata"]["auto_generated"]).lower()}')
    lines.append(f'  auto_generated_at: "{fm["metadata"]["auto_generated_at"]}"')
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def has_frontmatter(text: str) -> bool:
    if not text.startswith("---"):
        return False
    parts = text.split("---", 2)
    return len(parts) >= 3


def process_skill(skill_dir: Path, apply: bool, backup: bool):
    """处理一个 Skill 目录. 返回 (status, info)."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return "skipped_no_md", None

    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if has_frontmatter(text):
        return "skipped_has_fm", None

    # 处理纯空文件
    if not text.strip():
        return "skipped_empty", None

    fm = build_frontmatter(skill_dir, text)
    fm_text = render_frontmatter(fm)
    new_text = fm_text + text

    if apply:
        if backup:
            bak = skill_md.with_suffix(".md.bak")
            bak.write_text(text, encoding="utf-8")
        skill_md.write_text(new_text, encoding="utf-8")
        return "applied", fm
    return "dry_run", fm


def main():
    parser = argparse.ArgumentParser(description="智能补全 SKILL.md frontmatter")
    parser.add_argument("--root", default="skills",
                        help="Skill 根目录 (默认 skills/)")
    parser.add_argument("--skill", action="append",
                        help="只处理指定 Skill 目录 (可多次)")
    parser.add_argument("--apply", action="store_true",
                        help="真正写入文件; 否则 dry-run 仅打印")
    parser.add_argument("--no-backup", action="store_true",
                        help="不生成 .md.bak")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"[FATAL] root not found: {root}", file=sys.stderr)
        sys.exit(2)

    targets = []
    if args.skill:
        for s in args.skill:
            p = Path(s).resolve()
            if (p / "SKILL.md").exists():
                targets.append(p)
            else:
                print(f"[WARN] no SKILL.md in {p}", file=sys.stderr)
    else:
        for sub in sorted(root.iterdir()):
            if sub.is_dir() and (sub / "SKILL.md").exists():
                targets.append(sub)

    counts = {"applied": 0, "dry_run": 0, "skipped_has_fm": 0,
              "skipped_empty": 0, "skipped_no_md": 0}
    samples = []
    for skill in targets:
        status, fm = process_skill(skill, args.apply, not args.no_backup)
        counts[status] = counts.get(status, 0) + 1
        if status == "dry_run" and len(samples) < 5:
            samples.append((skill.name, fm))

    print(f"━━━ backfill-frontmatter ({'APPLY' if args.apply else 'DRY-RUN'}) ━━━")
    print(f"Total skills scanned : {len(targets)}")
    print(f"Already have FM       : {counts['skipped_has_fm']}")
    print(f"Empty SKILL.md        : {counts['skipped_empty']}")
    if args.apply:
        print(f"Applied (FM written)  : {counts['applied']}")
    else:
        print(f"Would write FM        : {counts['dry_run']}")

    if samples and not args.apply:
        print("\nSample frontmatter (first 5 dry-run):")
        for name, fm in samples:
            print(f"\n[{name}]")
            for k, v in fm.items():
                if k == "metadata":
                    continue
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
