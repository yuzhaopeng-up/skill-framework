# Scripts — 自动化脚本

## inventory-scan.py — Skill 资产盘点工具

扫描各节点 `skills/` 目录的 SKILL.md，与 `unified_skill_inventory.json` 对账，发现：
- **缺失**：清单登记了但仓库找不到
- **孤儿**：仓库有但清单未登记
- **不规范**：命名/frontmatter/层级/能力域不符合标准

### 用法

```bash
# 默认：彩色控制台报告
python3 scripts/inventory-scan.py

# JSON 输出（CI集成）
python3 scripts/inventory-scan.py --json > scan-report.json

# 严格模式（CI门禁）：发现 error 时 exit 2，warn 时 exit 1
python3 scripts/inventory-scan.py --strict

# 指定根目录
python3 scripts/inventory-scan.py --root /path/to/openclaw-workspace
```

### 检测项

| 等级 | 代码 | 含义 |
|------|------|------|
| error | `parse_error` | SKILL.md 解析失败（无frontmatter / YAML语法错） |
| error | `inventory_missing` | 清单文件不存在 |
| warn | `name_not_snake_case` | 名称不符合 snake_case |
| warn | `missing_skill_md` | 目录缺少 SKILL.md |
| warn | `orphan_on_disk` | 仓库有但清单没登记 |
| warn | `missing_on_disk` | 清单标了本节点，但本次扫描未找到 |
| warn | `invalid_layer` / `invalid_domain` | 层级 / 能力域不在白名单 |
| info | `duplicate_across_nodes` | 同名 Skill 在多节点出现 |
| info | `external_only` | 清单标注由外部节点提供 |
| info | `unknown_industry` | 行业字段未识别 |

### 退出码

| 模式 | error | warn | only info / clean |
|------|-------|------|-------------------|
| 默认 | 0 | 0 | 0 |
| `--strict` | 2 | 1 | 0 |

### 当前已知发现（首次运行基线）

- 86 / 208 Skill 落地在 BetaAgent 仓库（其余在 AlphaAgent / DeltaAgent / GammaAgent / EpsilonAgent 节点）
- 大量 Skill 缺少 frontmatter（93 个 parse_error）→ 见质量门禁路线图
- 一批名称仍是 kebab-case 或 raw text → 持续治理迁移到 snake_case

详细报告：`python3 scripts/inventory-scan.py --json | jq` 

### 与 CI 集成

GitHub Actions 示例：

```yaml
name: skill-inventory-scan
on:
  pull_request:
    paths: ["skills/**", "**/unified_skill_inventory.json"]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install pyyaml
      - run: python3 00-methodology/skill-architecture/scripts/inventory-scan.py --strict --no-color
```
