# Skill 治理 30 天补全计划

**生成日期**: 2026-06-20
**基线 lint run**: GitHub Actions run `27874270398` (Skill Quality Gate, develop)
**目标**: 30 天内 errors **230 → 0**

---

## 1. 现状基线（真实 lint 数据）

| 指标 | 数量 |
|---|---|
| 扫描 Skill 总数 | **127** |
| 有 errors 的 Skill 数 | **88** |
| 总 errors | **230** |
| 总 warnings | 536 |
| 总 info | 8 |

### 1.1 Errors 分布（按规则码）

| Rule | Count | 严重度 | 类别 |
|---|---|---|---|
| `G2_missing_field` | 137 | High | frontmatter 缺 `version` (44) / `author` (48) / `license` (45) |
| `G1_name_format` | 83 | High | frontmatter 中 `name` 字段非 snake_case |
| `G4_potential_secret` | 10 | **误报** | 全部是教学示例占位符（`your_token`、`API_KEY="your-...here"`、示例身份证号） |

### 1.2 错误叠加情况

| Bucket | 描述 | 数量 |
|---|---|---|
| **A** | G1 + G2 双错（命名 + 缺字段） | **49** |
| **B** | 仅 G1（命名问题） | **34** |
| **C** | 仅 G2（缺字段） | **5** |
| **D** | G4（占位符误报） | **5**（与 A/B 重叠） |
| **总 unique 待修 Skill** | — | **88** |

### 1.3 来源拆分

全部 88 个 Skill 都在本仓 `skills/` 下（`BetaAgent` 来源），不涉及 AlphaAgent 私有仓。

---

## 2. 修复策略

### 2.1 自动化优先

**G1 (83 errors)** —— 80% 是 AlphaAgent Phase 5 sync 时 frontmatter 的 `name` 字段没改成 snake_case，目录名其实已经合规。可写脚本自动转换：

```python
# 伪代码
for skill_dir in skills/:
    fm = parse_frontmatter(skill_dir / "SKILL.md")
    if fm.get("name") and not is_snake_case(fm["name"]):
        fm["name"] = to_snake_case(fm["name"])
        write_frontmatter(skill_dir / "SKILL.md", fm)
```

**预计自动修复: 70+/83**，剩余少数（含中文标题、特殊符号）人工处理。

**G2 (137 errors)** —— 复用现有 `00-methodology/skill-architecture/scripts/backfill-frontmatter.py`，扩展支持 `version` / `author` / `license` 三个字段：

| 字段 | 默认填充策略 |
|---|---|
| `version` | 从 git log 第一个 commit 推 `0.1.0`，否则 `0.1.0` |
| `author` | git log 最早 author（去 email 后） |
| `license` | 仓内统一默认 `MIT`（可配置） |

**预计自动修复: 137/137**（默认值兜底）

**G4 (10 误报)** —— 全部是教学占位符，直接改成更显眼的"假密钥"格式：

```diff
- API_KEY="your-key-here"
+ API_KEY="${YOUR_API_KEY}"  # set via env var
```

身份证号示例改为 `XXXXXXXXXXXXXXXXXX` 或全 0。**预计修复: 10/10**

### 2.2 lint 规则改进（同步进行）

把"明显占位"加入 G4 的 allow-list，避免误报：

```python
# skill-lint.py G4 检查可加 allowlist
PLACEHOLDER_TOKENS = {
    "your-key-here", "your_token", "your_api_key",
    "<YOUR_API_KEY>", "${YOUR_API_KEY}",
    "XXXXXXXXXXXXXXXXXX",
}
```

可以在 G4 命中后做二次过滤：值匹配占位模式 → 降级为 warn 而非 error。

---

## 3. 30 天日程

### 第 1 周（Week 1, 06-21 ~ 06-27）— 基础设施 + 自动化

| Day | 任务 | 产出 |
|---|---|---|
| D1 | 扩展 `backfill-frontmatter.py` 支持 `version`/`author`/`license` | PR #1 |
| D2 | 写 `normalize-skill-names.py` 自动 snake_case 化 frontmatter `name` 字段 | PR #2 |
| D3 | lint G4 占位 allow-list 改造 | PR #3 |
| D4-D5 | 三个工具 dry-run 全仓扫描，校对结果 | dry-run 报告 |
| D6-D7 | 在 `.github/workflows/skill-quality-gate.yml` 加 PR 报告评论 | PR #4 |

**Week 1 出口标准**：3 个治理工具上线，lint 误报降为 0。

### 第 2 周（Week 2, 06-28 ~ 07-04）— Bucket D + Bucket A 前半

| Day | 任务 | 期望剩余 errors |
|---|---|---|
| D8 | **Bucket D (5 skill)**：手工修 10 个 G4 占位符 | 230 → 220 |
| D9-D10 | **Bucket A 前 25 个**：跑 normalize + backfill，逐个 PR review | 220 → ~150 |
| D11-D12 | **Bucket A 后 24 个**：同上 | 150 → ~85 |
| D13-D14 | 修复过程中 lint 工具迭代（处理边界 case） | — |

**Week 2 出口标准**：errors ≤ 90。

### 第 3 周（Week 3, 07-05 ~ 07-11）— Bucket B + Bucket C

| Day | 任务 | 期望剩余 errors |
|---|---|---|
| D15-D17 | **Bucket B (34 skill, 仅 G1)**：批量跑 normalize 脚本 + 人工 review | 90 → ~25 |
| D18-D19 | **Bucket C (5 skill, 仅 G2)**：跑 backfill 脚本 | 25 → ~5 |
| D20-D21 | 修复脚本未覆盖的 corner case（含中文标题、特殊符号 skill 名） | 5 → 0 |

**Week 3 出口标准**：errors ≤ 5。

### 第 4 周（Week 4, 07-12 ~ 07-20）— 验收 + 升级 gate

| Day | 任务 | 产出 |
|---|---|---|
| D22-D24 | 处理残余 errors + nightly artifact 复盘 | errors → 0 |
| D25 | warnings 选择性消化（不强制，目标 ≤ 200） | warns 536 → ≤200 |
| D26-D27 | 升级 quality-gate：把 push 模式 `full sweep soft` 改回 `full sweep strict` | PR #N |
| D28-D30 | 全仓 nightly run 验证连续 3 天无 error 复发 | 验收报告 |

**Week 4 出口标准**：
- errors = 0 ✅
- nightly 全量 strict gate 连续 3 天绿
- quality-gate push 模式恢复全量 strict

---

## 4. 风险与回滚

| 风险 | 缓解措施 |
|---|---|
| normalize-skill-names.py 把合理的 PascalCase（如 `OpenClaw`）改坏 | 加 dry-run + diff review；保留 allow-list |
| backfill 注入的 author 与历史 git blame 不符 | 使用 `git log --follow --format='%an' SKILL.md` 取最早作者 |
| 升级到 strict gate 后偶发 error 卡推送 | nightly 跑 7 天通过率 ≥ 99% 才升级 |

回滚策略：所有修复都是单 Skill 级 PR，可独立 revert。

---

## 5. 责任与跟踪

- **数据源**: `governance/remediation-plan-data.json`（含 88 个 Skill 的逐项分类，机器可读）
- **每日跟踪**: nightly artifact `skill-lint-report.json` 的 errors 数趋势
- **里程碑通报**: 每周日推送进度到 BetaAgent Brain 飞书群

## 6. 附录 — Bucket 概览

实际 88 个 Skill 的逐项清单见 `governance/remediation-plan-data.json`。文档中只列代表性 5 个：

**Bucket A (G1+G2, 49 项, 例)**: `Feishu-Cloud-Drive`, `Grammar`, `agent-browser`, `agile-product-owner`, `api-test-automation`, ...

**Bucket B (G1 only, 34 项, 例)**: `ai-contract-review-cn`, `audit_sampling`, `churn_recall`, `customer_health`, `liquidity_alert`, ...

**Bucket C (G2 only, 5 项, 全部)**: `copywriter`, `github`, `newman`, `ontology`, `weather`

**Bucket D (G4 误报, 5 项, 全部)**: `Feishu-Cloud-Drive`, `application-material-checker`, `byted-seedream-image-generate`, `byted-teamproject-image-generate`, `tavily-search`
