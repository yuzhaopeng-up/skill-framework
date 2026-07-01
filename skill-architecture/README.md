# Skill 架构总览

> 五方节点（BetaAgent / AlphaAgent / GammaAgent / DeltaAgent / EpsilonAgent）共建的 Skill 资产架构。
> 本目录是**唯一权威源**，所有节点对齐这里的标准。

## 📂 目录结构

```
00-methodology/skill-architecture/
├─ README.md                                  # 本文件（总览）
├─ SKILL-ARCHITECTURE-v1.0.md                # 架构主文档（990行，L1-L4 + 治理）
│
├─ l2-patterns/                              # L2 模式蓝图（4个核心模式）
│   ├─ README.md
│   ├─ cross-channel-router.md               # 跨渠道路由（解决渠道硬编码瓶颈）
│   ├─ unified-document-pipeline.md          # 统一文档流水线（OCR/解析/校验）
│   ├─ alert-engine.md                        # 告警引擎（监测→处置→闭环）
│   └─ taskflow-patterns.md                   # TaskFlow 编排（5种工作流模式）
│
├─ l3-scenarios/                             # L3 场景 Skill
│   └─ scenario-skills-supplement.md         # 10 个场景 (S301-S310)
│
├─ l4-multi-agent/                           # L4 多Agent Skill
│   └─ multi-agent-skills-supplement.md      # 7 个多Agent场景 (A401-A407)
│
├─ verticals/                                # 4 个垂直行业蓝图
│   ├─ README.md
│   ├─ healthcare.md                          # 医疗
│   ├─ legal.md                               # 法律
│   ├─ real-estate.md                         # 房地产
│   └─ education.md                           # 教育
│
├─ governance/                               # 治理规范
│   ├─ im-channel-interface-spec.md          # IM 渠道接口标准（强制规范）
│   └─ quality-gates.md                       # 质量门禁（Bronze/Silver/Gold）
│
├─ scripts/                                  # 自动化工具
│   ├─ README.md
│   ├─ inventory-scan.py                      # 资产盘点（清单 vs 仓库对账）
│   └─ skill-lint.py                          # Skill 静态检查（G1-G5）
│
├─ roadmap/                                  # 演进路线
│   └─ skill-roadmap.md                       # 6 季度路线图（2026Q3-2027Q4）
│
├─ unified_skill_inventory.json              # 208 Skill 统一清单（机器可读）
├─ unified_skill_inventory.csv               # 同上（表格版）
│
└─ 整合报告（历史归档）
    ├─ ARKCLAW-HERMES-INTEGRATION-REPORT.md
    ├─ TRIPARTITE-INTEGRATION-REPORT-v1.0.md
    └─ QUADRIPARTITE-INTEGRATION-REPORT-v1.0.md
```

## 🎯 五层模型 (L0-L4)

| 层级 | 数量 | 定义 | 例子 |
|------|------|------|------|
| **L0** 原子/连接器 | 23 | 单一外部资源/协议适配 | l0_feishu_im, l0_db_query |
| **L1** 基础Skill | 77 | 单一职责的功能模块 | l1_pdf_parse, l1_legal_ner |
| **L2** 组合模式 | 104 | 业务模式 + 编排骨架 | l2_cross_channel_router, l2_alert_engine |
| **L3** 场景Skill | 12 | 完整业务场景 | l3_smart_reception, l3_contract_review |
| **L4** 多Agent | 10 | 跨Agent协作 | a401_research_team, a403_customer_service |

## 🏭 11 个能力域 (C01-C11)

C01 自然语言理解 / C02 内容生成 / C03 数据处理 / C04 文档处理 /
C05 推理决策 / C06 视觉/影像 / C07 协作通知 / C08 知识管理 /
C09 集成连接 / C10 安全合规 / C11 垂直行业

## 🌐 行业分类

universal / financial / telecom / transferable / general /
healthcare / legal / real_estate / education

## 📚 阅读顺序建议

### 我是新加入的开发者
1. `SKILL-ARCHITECTURE-v1.0.md` — 看主文档，了解 L0-L4
2. `l2-patterns/README.md` — 看 4 个模式蓝图（最常被复用）
3. `governance/quality-gates.md` — 知道写 Skill 的红线
4. `scripts/README.md` — 跑一下盘点工具看现状

### 我要写一个新 Skill
1. `governance/quality-gates.md` — 强制门禁清单
2. `governance/im-channel-interface-spec.md` — 任何发消息的 Skill 必读
3. 找最接近的 L2 模式蓝图，复用而非重写
4. 写完 → `python3 scripts/skill-lint.py path/to/your/skill`

### 我是行业专家想拓展新行业
1. `verticals/README.md` — 看蓝图模板
2. 选一个新蓝图作参考（医疗/法律/房地产/教育）
3. 按 7 章节模板写自己行业的蓝图
4. 提 PR 走架构评审

### 我是项目负责人
1. `roadmap/skill-roadmap.md` — 6 季度路线图
2. `unified_skill_inventory.json` — 当前家底
3. 季度评审用 `scripts/inventory-scan.py --json` 出报告

## 🔧 常用命令

```bash
# 盘点：仓库 vs 清单对账
python3 scripts/inventory-scan.py

# Lint：检查所有 Skill 是否符合质量门禁
python3 scripts/skill-lint.py --strict

# 检查指定 Skill
python3 scripts/skill-lint.py skills/some_skill --quality silver

# 出 JSON 报告（CI 集成）
python3 scripts/inventory-scan.py --json > scan.json
python3 scripts/skill-lint.py --json > lint.json
```

## 📊 当前里程碑

- ✅ P0：L2 跨渠道路由器 + 12 个 L3 场景 + 10 个 L4 多Agent
- ✅ P1：4 个 L2 模式蓝图 + 4 个垂直行业蓝图 + IM 渠道接口标准
- ✅ P2：盘点脚本 + 质量门禁 + 6 季度路线图
- 🚧 下一步：质量治理 + 标杆场景上线（参见路线图 Phase 1）

## 🤝 贡献

1. 任何修改先开 PR
2. 新增 Skill 跑通 `skill-lint.py --strict`
3. 涉及架构变更：写 RFC 走评审
4. 命名永远 snake_case，永远 L0-L4 标层级
