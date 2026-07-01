# AlphaAgent vs BetaAgent Skill 资产盘点对比与整合报告

> **生成时间**: 2026-06-20  
> **对比对象**: AlphaAgent 盘点 (financial-ai-skills 私有仓库) vs BetaAgent 盘点 (openclaw-workspace 仓库)  
> **目标**: 识别差异、消除冗余、统一标准、形成唯一可信源

---

## 一、盘点范围对比

| 维度 | AlphaAgent 盘点 | BetaAgent 盘点 | 差异说明 |
|------|-------------|------------|---------|
| **扫描路径** | `/root/.openclaw/workspace/financial-ai-skills/skills` + 工作区已安装 + Agent已安装 + Plugin Skills | `/home/ubuntu/due-diligence/skills` | AlphaAgent扫描了更多来源（Agent、Plugin） |
| **原始文件数** | 283 | ~125 | AlphaAgent扫描范围更广 |
| **去重后Skill** | 153 | 131 | AlphaAgent多22个（主要来自Agent/Plugin） |
| **私有金融仓库** | 90 | - | AlphaAgent专门统计了私有仓库 |
| **工作区/Agent/Plugin** | 63 | - | BetaAgent未区分来源 |

**结论**: AlphaAgent的扫描范围更全面，涵盖了Agent安装和Plugin Skills，这是BetaAgent盘点缺失的部分。

---

## 二、Skill 分层对比

### 2.1 分层定义差异

| 层级 | AlphaAgent 定义 | BetaAgent 定义 | 评价 |
|------|-------------|------------|------|
| **L0** | 原子/连接器Skill：工具、连接器、平台操作 | 基础Skill (Base)：原子功能 | AlphaAgent的L0更强调"连接器"属性，BetaAgent的Base更强调"原子性" |
| **L1** | 基础Skill：单点业务能力 | 知识层 (Knowledge)：领域Skill | BetaAgent的L1更偏向领域知识，AlphaAgent的L1更偏向单点功能 |
| **L2** | 组合Skill：串联2-4个基础能力 | 组合Skill (Composite)：多Skill组合 | 基本一致 |
| **L3** | 组合的组合Skill：端到端场景 | 多Agent Skill (Multi-Agent)：多Agent协同 | BetaAgent的L3更强调多Agent，AlphaAgent的L3更强调场景完整性 |

### 2.2 分层数量对比

| 层级 | AlphaAgent | BetaAgent | 差异 |
|------|---------|--------|------|
| L0/基础 | 23 | 18 | AlphaAgent多5个（主要是Agent/Plugin连接器） |
| L1/知识 | 36 | 77* | BetaAgent的"standard"包含了AlphaAgent的L1+L2部分 |
| L2/组合 | 86 | 13 | BetaAgent分类更保守，AlphaAgent更激进 |
| L3/多Agent | 8 | 17 | BetaAgent将更多Skill归为多Agent |

*注：BetaAgent的77个"standard"中，大部分应属于AlphaAgent的L1或L2

**核心差异**: 
- AlphaAgent的分层更"扁平"，大量Skill被归为L2组合
- BetaAgent的分层更"保守"，大量Skill被归为L1基础或L3多Agent
- **建议**: 采用AlphaAgent的四层定义（L0-L3），但调整分类标准，使分层更一致

---

## 三、Skill 清单差异

### 3.1 只在 AlphaAgent 中的 Skill (51个)

这些Skill主要来自：
1. **Agent安装的通用工具** (15个): browser, computer-use, feishu-doc-manager, feishu-wiki, opencli, summarize, workspace-netdrive 等
2. **私有金融仓库的细分Skill** (25个): aml_rating, audit-sampling, budget_control, cashflow_forecast, churn-recall, claim_review_v2, code_review_skill, collateral-valuation, collection-optimize, compliance_training, credit_collection, expense_audit, fraud_alert, fund-research, insurance_recommend, invoice_check, liquidity-alert, lobby_emotion, lobby_marketing, lobby_queue, operational_risk, performance_attribution, research_notes, securities_research, smart_underwriting, stress_test, suspicious_report, underwriting_v2 等
3. **其他** (11个): Feishu Cloud Drive, Story Writer, contract-review, customer-health, financial_extract 等

**关键发现**:
- AlphaAgent扫描到了大量**Agent安装的基础工具Skill**（browser, computer-use等），这些是BetaAgent遗漏的
- 私有金融仓库中有大量**细分金融Skill**（如aml_rating, claim_review_v2等），是BetaAgent未扫描到的
- 存在**命名差异导致的重复统计**（如`churn-recall` vs `churn_recall`）

### 3.2 只在 BetaAgent 中的 Skill (29个)

这些Skill主要来自：
1. **due-diligence目录的独立Skill** (15个): due_diligence_data_fetcher, report_formatter, risk_analyzer, web_search, feishu_publisher, financial_intelligence, ma_scheme, market_view, meeting_minutes, objection_training, ops_daily_report, product_pricing, roadshow_material, tax_planning, valuation_helper
2. **命名差异** (10个): 与AlphaAgent同名但命名规范不同（如`family_trust` vs `family-trust`）
3. **其他** (4个): global_asset_allocation, ops-daily-report, code_reviewer, contract_review

**关键发现**:
- BetaAgent扫描了`/home/ubuntu/due-diligence/skills`目录，其中有一些AlphaAgent未扫描到的Skill
- **命名规范不统一**导致同一Skill被重复统计（如`churn_recall` vs `churn-recall`）
- 部分Skill在AlphaAgent中属于私有仓库，但在BetaAgent中被归类为工作区安装

### 3.3 共同存在的 Skill (102个)

这些是两个盘点都识别到的Skill，属于"共识资产"。

---

## 四、行业分类对比

### 4.1 分类标准差异

| 维度 | AlphaAgent | BetaAgent |
|------|---------|--------|
| **金融专用** | 73个 | 64个 |
| **跨行业通用** | 63个 | 58个 (general) + 1个 (universal) |
| **可迁移** | 17个 | - |
| **未知/未分类** | - | 6个 |
| **其他** | - | 零售1个 + 医疗1个 |

### 4.2 关键差异

1. **AlphaAgent引入了"行业可迁移"分类**: 17个Skill被标记为可迁移，这是BetaAgent没有的维度
2. **BetaAgent有"未知"分类**: 6个Skill未分类，AlphaAgent全部进行了分类
3. **分类一致性**: 两个盘点对"金融专用"的判定基本一致（73 vs 64），差异主要来自扫描范围

---

## 五、能力域对比

### 5.1 AlphaAgent 的 10 大能力域

| 能力域 | 数量 | 说明 |
|--------|------|------|
| C02 数据分析与洞察 | 36 | 最大能力域，覆盖金融分析、量化、运营等 |
| C09 集成连接器 | 32 | 工具、平台、API连接器 |
| C08 投资/组合/定价 | 17 | 投研、组合管理、定价 |
| C05 风险/合规/安全 | 16 | 风控、合规、反欺诈 |
| C07 客户/营销/服务 | 16 | 营销、客服、客户管理 |
| C04 报告/文档生成 | 12 | 报告、文档、内容生成 |
| C03 知识检索与RAG | 9 | RAG、知识库、搜索 |
| C06 流程编排与路由 | 7 | 编排、路由、工作流 |
| C01 信息提取与结构化 | 5 | 提取、归档、结构化 |
| C10 沉淀归档与治理 | 3 | 归档、治理、审计 |

### 5.2 BetaAgent 的功能类型分类

| 功能类型 | 数量 | 对应AlphaAgent能力域 |
|----------|------|------------------|
| generation (生成) | 82 | C04 + C07部分 |
| knowledge (知识) | 21 | C03 + C10部分 |
| analysis (分析) | 7 | C02部分 |
| audit (审核) | 1 | C05部分 |
| search (搜索) | - | C03 |
| reporting (报告) | - | C04 |
| conversation (对话) | 1 | C07 |
| calculation (计算) | 2 | C02 |
| utility (工具) | - | C09 |

**关键差异**:
- AlphaAgent的能力域分类更**结构化**，按业务领域划分
- BetaAgent的功能类型分类更**技术导向**，按功能类型划分
- **建议**: 采用AlphaAgent的能力域分类作为主线，BetaAgent的功能类型作为辅助标签

---

## 六、企业架构思想对比

### 6.1 AlphaAgent 的架构思想

- **TOGAF**: 统一方法、标准与沟通
- **ArchiMate**: 业务过程/组织/信息流/IT系统/技术基础设施关系可视化
- **LeanIX**: 业务战略、流程、信息与技术对齐，能力地图、资产清单、目标架构、路线图、标准
- **构建块**: ABB (Architecture Building Block) + SBB (Solution Building Block)
- **能力地图**: 10大能力域
- **信息流**: Input → Process → Output → Archive → Audit

### 6.2 BetaAgent 的架构思想

- **4A架构**: 业务架构→场景层、应用架构→编排层、数据架构→知识层、技术架构→基础层
- **构建块**: 标准化、可复用、可组合
- **无差别信息流**: 统一输入→处理→输出模式
- **微服务架构**: 独立部署、独立扩展、独立升级
- **治理体系**: 生命周期管理、质量门禁、版本管理

### 6.3 对比评价

| 维度 | AlphaAgent | BetaAgent | 评价 |
|------|---------|--------|------|
| **架构理论深度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | AlphaAgent引用了更多外部架构理论（TOGAF/ArchiMate/LeanIX） |
| **实践落地性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | BetaAgent提供了更具体的目录结构、接口规范、治理体系 |
| **分层清晰度** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | BetaAgent的四层架构（场景/编排/知识/基础）更清晰 |
| **复用策略** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | BetaAgent提供了构建块复用矩阵和复用原则 |
| **治理体系** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | BetaAgent提供了完整的生命周期、质量门禁、版本管理 |
| **多智能体** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 两者都识别了多智能体场景，AlphaAgent更具体 |

---

## 七、整合建议

### 7.1 统一分层标准

建议采用**AlphaAgent的四层定义**，但调整分类标准：

```
L0 原子/连接器Skill: 工具、连接器、平台操作（不可再分解）
L1 基础Skill: 单点业务能力（只做一件事，有明确输入输出）
L2 组合Skill: 串联多个L0/L1，完成一个业务流程
L3 场景Skill: 面向端到端业务场景，包含多个流程/角色/系统
L4 多AgentSkill: 多个AI Agent协同，存在职责边界和状态传递
```

**关键调整**:
- 将AlphaAgent的L3"组合的组合"改为"场景Skill"
- 新增L4"多AgentSkill"，将BetaAgent的L3多Agent和AlphaAgent的多Agent候选统一
- 明确分层判定标准：是否可独立运行、是否有外部依赖、是否面向用户场景

### 7.2 统一命名规范

发现大量命名不一致问题：

| AlphaAgent | BetaAgent | 建议统一为 |
|---------|--------|-----------|
| `churn-recall` | `churn_recall` | `churn_recall` (snake_case) |
| `family-trust` | `family_trust` | `family_trust` (snake_case) |
| `liquidity-alert` | `liquidity_alert` | `liquidity_alert` (snake_case) |
| `audit-sampling` | `audit_sampling` | `audit_sampling` (snake_case) |
| `ops-daily-report` | `ops_daily_report` | `ops_daily_report` (snake_case) |
| `collateral-valuation` | `collateral_valuation` | `collateral_valuation` (snake_case) |
| `collection-optimize` | `collection_optimize` | `collection_optimize` (snake_case) |
| `compliance-auto` | `compliance_auto` | `compliance_auto` (snake_case) |
| `customer-health` | `customer_health` | `customer_health` (snake_case) |
| `fund-research` | `fund_research` | `fund_research` (snake_case) |
| `lobby_emotion` | - | `lobby_emotion` (snake_case) |
| `lobby_queue` | - | `lobby_queue` (snake_case) |
| `code_review_skill` | `code_reviewer` | `code_reviewer` (统一命名) |
| `contract-review` | `contract_review` | `contract_review` (snake_case) |

**建议**: 统一采用 **snake_case** 命名规范，所有Skill目录和文件名使用下划线分隔。

### 7.3 统一行业分类

建议采用三级分类：

```
行业专用 (Industry-Specific)
├── 金融 (Financial)
│   ├── 银行 (Banking)
│   ├── 证券 (Securities)
│   ├── 保险 (Insurance)
│   ├── 基金 (Fund)
│   └── 信托 (Trust)
├── telecom (Telecom)
├── 政务 (Government)
└── 医疗 (Healthcare)

跨行业通用 (Cross-Industry)
├── 工具 (Tools)
├── 搜索 (Search)
├── 生成 (Generation)
├── 代码 (Code)
├── 数据 (Data)
└── 集成 (Integration)

行业可迁移 (Transferable)
├── 通用业务 (General Business)
└── 通用技术 (General Technology)
```

### 7.4 统一能力域分类

建议采用AlphaAgent的10大能力域，但调整命名和顺序：

```
C01 信息提取与结构化 (Information Extraction)
C02 知识检索与RAG (Knowledge & RAG)
C03 数据分析与洞察 (Data Analysis)
C04 报告/文档生成 (Report Generation)
C05 风险/合规/安全 (Risk & Compliance)
C06 客户/营销/服务 (Customer & Marketing)
C07 投资/组合/定价 (Investment & Pricing)
C08 流程编排与路由 (Orchestration)
C09 集成连接器 (Integration)
C10 沉淀归档与治理 (Governance)
```

### 7.5 统一目录结构

建议采用BetaAgent的目录结构，但增加AlphaAgent的架构文档：

```
repository/
├── skills/                          # Skill代码目录
│   ├── l0-connectors/              # L0 原子/连接器
│   ├── l1-foundation/              # L1 基础Skill
│   ├── l2-composite/               # L2 组合Skill
│   ├── l3-scenario/                # L3 场景Skill
│   └── l4-multi-agent/             # L4 多AgentSkill
├── architecture/                    # 架构文档（不与skills/重叠）
│   ├── skill-architecture/
│   │   ├── 01-enterprise-architecture-principles.md
│   │   ├── 02-skill-layer-taxonomy.md
│   │   ├── 03-skill-inventory.md
│   │   ├── 04-composition-and-information-flow.md
│   │   ├── 05-multi-agent-scenario-skills.md
│   │   ├── 06-cross-industry-vs-industry-specific.md
│   │   ├── 07-governance-and-roadmap.md
│   │   ├── 08-references.md
│   │   └── data/
│   │       ├── skill-inventory.json
│   │       ├── skill-inventory.csv
│   │       └── category-summary.json
│   └── methodology/                # 方法论文档
│       └── skill-development-guide.md
├── docs/                           # 用户文档
└── scripts/                        # 自动化脚本
    ├── inventory-scan.py           # Skill盘点脚本
    └── naming-check.py             # 命名规范检查
```

### 7.6 统一机器可读清单

建议采用JSON格式，包含以下字段：

```json
{
  "name": "skill_name",
  "display_name": "Skill显示名称",
  "version": "1.0.0",
  "level": "L0|L1|L2|L3|L4",
  "industry": "financial|telecom|government|healthcare|universal|transferable",
  "industry_sub": "banking|securities|insurance|fund|trust",
  "capability_domain": "C01|C02|C03|C04|C05|C06|C07|C08|C09|C10",
  "func_type": "search|generation|analysis|audit|reporting|conversation|calculation|utility|knowledge|integration",
  "building_block_type": "SBB|ABB|SolutionBB",
  "description": "Skill描述",
  "dependencies": ["skill1", "skill2"],
  "source": "private_financial|workspace_installed|agent_installed|plugin",
  "path": "绝对路径",
  "has_scripts": true,
  "has_integration": true,
  "multi_agent_candidate": false,
  "multi_agent_note": "",
  "created_at": "2026-01-01",
  "updated_at": "2026-06-20",
  "author": "author_name",
  "tags": ["tag1", "tag2"]
}
```

---

## 八、行动项

### 8.1 立即执行 (P0)

1. **统一命名规范**: 将所有Skill目录名统一为snake_case
2. **合并重复Skill**: 识别并合并命名不同但功能相同的Skill
3. **统一分层标准**: 重新分类所有Skill，确保L0-L4分层一致
4. **统一行业分类**: 将所有Skill标记为"行业专用/跨行业通用/行业可迁移"

### 8.2 短期执行 (P1)

1. **统一机器可读清单**: 生成包含完整字段的JSON/CSV清单
2. **建立唯一可信源**: 确定以哪个仓库为唯一可信源（建议financial-ai-skills）
3. **同步缺失Skill**: 将BetaAgent独有的29个Skill同步到统一仓库
4. **建立治理流程**: 新增Skill必须登记inventory，遵循命名规范

### 8.3 中期执行 (P2)

1. **建立自动化盘点**: 编写inventory-scan.py，定期自动扫描并更新清单
2. **建立质量门禁**: 新增Skill必须通过分层、行业、能力域检查
3. **建立复用度量**: 统计每个Skill的被复用次数，识别高价值构建块
4. **建立路线图**: 基于能力缺口，制定Skill开发优先级

---

## 九、最终结论

**AlphaAgent的盘点更全面**（153 vs 131），覆盖了Agent安装和Plugin Skills，且引入了更丰富的企业架构理论（TOGAF/ArchiMate/LeanIX）。

**BetaAgent的架构更清晰**（四层架构映射到4A架构），提供了更具体的实践规范（目录结构、接口定义、治理体系）。

**整合方向**:
1. 以 **AlphaAgent的扫描结果** 为资产基准（更全面）
2. 以 **BetaAgent的四层架构** 为分层标准（更清晰）
3. 以 **AlphaAgent的能力域** 为分类主线（更结构化）
4. 以 **BetaAgent的治理体系** 为管理规范（更完整）
5. 统一存储在 **financial-ai-skills 私有仓库**（主仓库）
6. 在 **openclaw-workspace** 中引用/同步（工作仓库）

**最终目标**: 形成"一个唯一可信源、一套统一标准、一种自动化治理"的Skill资产管理体系。
