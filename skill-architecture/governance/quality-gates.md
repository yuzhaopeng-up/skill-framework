# Skill 质量门禁流程 (Quality Gates)

**版本**: v1.0
**适用范围**: 五方所有节点向 `openclaw-workspace` 提交Skill
**关键词**: RFC 2119 (MUST/SHOULD/MAY)

---

## 1. 总则

为保障 Skill 资产长期可治理、可复用，所有 Skill 在合入主干（`main` / `develop`）前**必须**通过本文定义的质量门禁。

> 没有质量门禁，整合再多Skill都会随时间退化为"巨大的lint垃圾场"。

## 2. 质量分级

| 等级 | 标记 | 准入门槛 | 用途 |
|------|------|----------|------|
| **🥉 Bronze** | `quality: bronze` | 仅强制项 | 实验性 / 内部探索 |
| **🥈 Silver** | `quality: silver` | 强制项 + 推荐项 | 客户演示可用 |
| **🥇 Gold** | `quality: gold` | 强制项 + 推荐项 + 性能/安全测试 | 生产可用 |

**默认**：未声明等级的 Skill 视为 Bronze。

---

## 3. 七项强制门禁 (MUST，全等级)

### G1. 命名规范
- ✅ 名称 snake_case，正则 `^[a-z][a-z0-9_]*$`
- ✅ 长度 3-64 字符
- ✅ 必须有 LX 层级前缀字段（不强求在文件名里）

### G2. SKILL.md frontmatter 完整
```yaml
---
name: skill_name                  # MUST, snake_case
description: "..."                # MUST, ≥ 20 字, ≤ 200 字
version: 1.0.0                    # MUST, 语义化版本
author: NodeName                  # MUST
license: MIT                      # MUST (or other open license)
layer: L2                         # MUST, L0-L4
capability_domain: [C09]          # MUST, 至少一个
industry: universal               # MUST
metadata:
  hermes:
    tags: [...]                   # SHOULD
    related_skills: [...]         # SHOULD
prerequisites:
  commands: [python3]             # SHOULD
---
```

### G3. 文档完整性
- ✅ SKILL.md ≥ 30 行（仅强制门禁）
- ✅ 必须包含章节：**核心能力 / 输入输出 / 使用示例**
- ✅ 至少 1 个端到端调用示例

### G4. 安全合规
- ✅ 没有硬编码凭据（token/密钥/手机号/身份证）
- ✅ 没有恶意调用（`rm -rf /`, `:(){:|:&};:`, 反弹shell, etc.）
- ✅ 涉及网络请求时**必须**支持 timeout
- ✅ 涉及外部API时**必须**说明所需权限范围

### G5. 接口契约
- ✅ 输入参数有类型/必填/取值范围说明
- ✅ 输出格式明确（schema/示例）
- ✅ 错误处理：明确异常类型与含义

### G6. 可观测
- ✅ 关键步骤产生日志（无强制格式，但需可grep）
- ✅ Skill 调用应可被 trace_id 串联（如发消息要传递 trace_id）

### G7. 与上层L2协议一致
- ✅ 发送消息**必须**遵循 [IM 渠道接口标准](./im-channel-interface-spec.md)
- ✅ 文档处理类**应**调用 `l2_unified_document_pipeline`，不重复造轮子
- ✅ 编排类**应**用 `l2_taskflow_patterns`，不自己写状态机

---

## 4. 三项推荐门禁 (SHOULD，Silver+)

### G8. 单元测试
- ✅ 至少 3 条测试用例（happy / edge / error）
- ✅ 测试不依赖真实外部服务（mock / 录制重放）

### G9. 文档示例
- ✅ 至少 1 张架构/流程图（mermaid 或图片）
- ✅ 至少 1 个完整对话示例

### G10. 跨节点互通
- ✅ 凡涉及 SecureBridge 的 Skill，必须在 metadata 标注 `clawlink.compatible: true`
- ✅ 必须能通过 `unified_skill_inventory.json` 索引到

---

## 5. 两项性能/安全门禁 (MUST for Gold)

### G11. 性能基线
- ✅ P95 延迟有实测数据（在描述中标注典型场景）
- ✅ 高并发（>10 QPS）场景需有压测报告

### G12. 安全审查
- ✅ 红队 prompt 测试通过（禁止越权 / 数据泄露 / 注入）
- ✅ 涉及生产数据的 Skill 必须有最小权限矩阵
- ✅ 高风险操作（资金/删除/外发）必须 human_in_loop

---

## 6. 自动化检查工具

### 6.1 lint 工具：`scripts/skill-lint.py`
- 静态检查 G1, G2, G3, G4 (部分)
- 退出码：0=通过, 1=warn, 2=error

### 6.2 盘点工具：`scripts/inventory-scan.py`
- 校验 G1, G2 + 跨节点对账
- 用法见 `scripts/README.md`

### 6.3 安全扫描（推荐）
- `gitleaks`：扫凭据泄露
- `bandit`：扫Python安全漏洞
- `semgrep`：扫通用安全模式

---

## 7. PR 检查清单

提交 Skill 的 PR **必须**在描述中勾选：

```markdown
## Skill 质量门禁自检
- [ ] G1 名称 snake_case
- [ ] G2 frontmatter 完整（name/description/version/author/license/layer/capability_domain/industry）
- [ ] G3 SKILL.md 包含 核心能力/输入输出/使用示例
- [ ] G4 无硬编码凭据，无恶意调用
- [ ] G5 输入输出契约明确
- [ ] G6 关键步骤有日志
- [ ] G7 遵循 IM 渠道接口标准 / TaskFlow / Document Pipeline
- [ ] (Silver+) G8 至少 3 条单元测试
- [ ] (Silver+) G9 包含架构图/流程图
- [ ] (Silver+) G10 跨节点字段已标注
- [ ] (Gold) G11 性能基线已实测
- [ ] (Gold) G12 红队测试通过

声明等级：[ ] Bronze [ ] Silver [ ] Gold
```

---

## 8. CI 工作流（GitHub Actions 示例）

```yaml
name: skill-quality-gate
on:
  pull_request:
    paths: ["skills/**", "00-methodology/skill-architecture/**"]

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - run: pip install pyyaml
      
      - name: G1+G2 (lint)
        run: python3 00-methodology/skill-architecture/scripts/skill-lint.py --strict
      
      - name: Inventory consistency
        run: python3 00-methodology/skill-architecture/scripts/inventory-scan.py --strict
      
      - name: Secrets scan
        uses: gitleaks/gitleaks-action@v2
      
      - name: Security scan (Python)
        run: pip install bandit && bandit -r skills/ -ll
```

---

## 9. 退化治理

存量 Skill 不一定能立刻达标。采用**渐进式治理**：

### 9.1 当前基线（首次扫描）
- 86 / 208 Skill 落地，其中 ≥ 50% 缺少 frontmatter (G2 不通过)

### 9.2 治理路线
| 季度 | 目标 |
|------|------|
| 2026 Q3 | 强制 G1+G2 全部新提交 Skill；存量补 frontmatter |
| 2026 Q4 | 全部存量 Skill 通过 G1-G7（强制项） |
| 2027 Q1 | 核心 30 Skill 升级 Silver |
| 2027 Q2 | 生产场景关键 Skill 升级 Gold |

### 9.3 豁免机制
对于"暂时无法达标但有业务价值"的 Skill，可在 frontmatter 添加：
```yaml
quality_gate_exempt:
  reason: "存量历史Skill, 计划2026Q4补全frontmatter"
  expires: "2026-12-31"
  approved_by: " Contributor"
```
带豁免的 Skill 在 lint 报告中显式标记，并定期审查。

---

## 10. 变更管理

- 本文档变更**必须**走 PR 评审，至少 1 名 Reviewer 批准
- 新增门禁项：先发布 RFC，60 天预告期再启用
- 撤销门禁项：需说明理由 + 影响评估

---

## 附录 A: 反模式（自动判定为 Fail）

1. 一个 SKILL.md 里塞 5+ 个独立功能 → 拆开
2. 调用了多个 IM 渠道 SDK → 改用 cross_channel_router
3. 自己实现 OCR/PDF 解析 → 改用 unified_document_pipeline
4. 自己实现状态机 → 改用 taskflow_patterns
5. 把凭据/Token写在示例里（即使是测试） → 立即拒绝
6. SKILL.md 全是 LLM 自动生成的废话（没有实际能力描述） → 拒绝
7. 标 layer=L4 但没声明依赖的 L3 → 层级声明失实
