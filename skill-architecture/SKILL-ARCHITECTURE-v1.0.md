# DemoBankAI Skill 架构体系 v1.0

> **定位**: 基于企业架构思想（4A架构、构建块、无差别信息流）的Skill系统化梳理  
> **目标**: 形成可复用、可编排、可治理的Skill模块体系，减少开发时间，提升复用性  
> **适用**: 金融、telecom、政务等多行业AI Skill工程化  
> **版本**: v1.0 | 2026-06-20

---

## 一、架构思想引入

### 1.1 4A架构映射

| 企业架构层级 | 传统定义 | Skill架构映射 | 示例 |
|-------------|---------|-------------|------|
| **业务架构 (BA)** | 业务流程、组织能力、价值链 | **场景层 (Scenario Layer)** | 企业尽调、财富管理、风控合规 |
| **应用架构 (AA)** | 应用系统、组件、接口 | **编排层 (Orchestration Layer)** | 多Agent工作流、Skill网关、路由编排 |
| **数据架构 (DA)** | 数据模型、存储、流转 | **知识层 (Knowledge Layer)** | RAG知识库、数据提取、报告生成 |
| **技术架构 (TA)** | 技术组件、基础设施 | **基础层 (Foundation Layer)** | 搜索、TTS、代码生成、浏览器自动化 |

### 1.2 构建块 (Building Block) 思想

```
┌─────────────────────────────────────────────────────────────┐
│                    业务场景 (Business Scenario)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ 企业尽调    │  │ 财富管理    │  │ 风控合规    │       │
│  │ (Composite) │  │ (Composite) │  │ (Composite) │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         │                │                │               │
│         └────────────────┴────────────────┘               │
│                          │                                │
│              ┌───────────┴───────────┐                   │
│              │    编排层 (编排层)      │                   │
│              │  ┌─────────────────┐   │                   │
│              │  │ 多Agent工作流   │   │                   │
│              │  │ 统一入口网关    │   │                   │
│              │  │ 意图识别路由    │   │                   │
│              │  └─────────────────┘   │                   │
│              └───────────┬───────────┘                   │
│                          │                                │
│         ┌────────────────┼────────────────┐               │
│         │                │                │               │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐      │
│  │ 知识层      │  │ 知识层      │  │ 知识层      │      │
│  │ RAG检索     │  │ 报告生成    │  │ 数据分析    │      │
│  │ 知识库问答  │  │ 内容创作    │  │ 智能审核    │      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │
│         │                │                │               │
│         └────────────────┴────────────────┘               │
│                          │                                │
│              ┌───────────┴───────────┐                   │
│              │    基础层 (Foundation)  │                   │
│              │  ┌─────────────────┐   │                   │
│              │  │ 搜索、TTS、代码   │   │                   │
│              │  │ 浏览器、测试     │   │                   │
│              │  └─────────────────┘   │                   │
│              └─────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 无差别信息流 (Information Flow)

所有Skill遵循统一的信息流模式：

```
输入 (Input) → 处理 (Process) → 输出 (Output)
     ↓              ↓              ↓
  结构化        业务逻辑         标准化
  非结构化      算法模型         可消费
  多模态        规则引擎         可追踪
```

---

## 二、Skill 四层架构

### 2.1 第一层：基础层 (Foundation Layer) — 原子Skill

**定义**: 不可再分解的最小功能单元，单一职责，独立运行

**特征**:
- 输入输出标准化（JSON/Markdown/结构化数据）
- 无外部Skill依赖
- 可独立测试和部署
- 跨行业通用

#### 2.1.1 搜索类 (Search)

| Skill | 功能 | 输入 | 输出 | 行业 |
|-------|------|------|------|------|
| **web_search** | 通用Web搜索 | 查询词 | 搜索结果列表 | 通用 |
| **multi-search-engine** | 多引擎聚合搜索 | 查询词+引擎选择 | 聚合结果 | 通用 |
| **tavily-search** | Tavily深度搜索 | 查询词+深度参数 | 结构化结果 | 通用 |
| **research_rag** | 研报RAG检索 | 问题+知识库 | 相关段落+来源 | 金融 |

#### 2.1.2 生成类 (Generation)

| Skill | 功能 | 输入 | 输出 | 行业 |
|-------|------|------|------|------|
| **content-creator-cn** | 中文内容创作 | 主题+风格 | 文章/文案 | 通用 |
| **copywriter** | 营销文案生成 | 产品+卖点 | 广告文案 | 通用 |
| **meeting_minutes** | 会议纪要生成 | 录音/文字 | 结构化纪要 | 通用 |
| **edge-tts** | 文本转语音 | 文本+音色 | 音频文件 | 通用 |
| **byted-text-to-speech** | 字节TTS | 文本+参数 | 音频文件 | 通用 |

#### 2.1.3 代码类 (Code)

| Skill | 功能 | 输入 | 输出 | 行业 |
|-------|------|------|------|------|
| **code_reviewer** | 代码审查 | 代码片段 | 审查意见 | 通用 |
| **senior-backend** | 后端开发 | 需求描述 | 代码+文档 | 通用 |
| **senior-devops** | DevOps脚本 | 场景描述 | 脚本/配置 | 通用 |
| **vite-react-tailwind** | 前端开发 | 设计需求 | 前端代码 | 通用 |
| **api-test-automation** | API测试 | API定义 | 测试用例 | 通用 |
| **py-test-creator** | 测试生成 | 代码/需求 | 测试代码 | 通用 |
| **clean-pytest** | 测试清理 | 测试代码 | 优化后代码 | 通用 |

#### 2.1.4 工具类 (Utility)

| Skill | 功能 | 输入 | 输出 | 行业 |
|-------|------|------|------|------|
| **agent-browser** | 浏览器自动化 | URL+操作 | 页面内容/截图 | 通用 |
| **video-editor** | 视频编辑 | 素材+脚本 | 编辑后视频 | 通用 |
| **video-to-prompt** | 视频转提示词 | 视频 | 描述文本 | 通用 |
| **byted-seedance-video-generate** | 视频生成 | 提示词 | 视频 | 通用 |
| **byted-seedream-image-generate** | 图像生成 | 提示词 | 图像 | 通用 |
| **getdesign-md** | 设计文档生成 | 需求 | 设计文档 | 通用 |
| **ontology** | 知识图谱 | 实体关系 | 图谱结构 | 通用 |
| **Grammar** | 语法检查 | 文本 | 修正建议 | 通用 |
| **humanizer** | 去AI化 | AI文本 | 自然文本 | 通用 |
| **humanizer-academic-zh** | 学术去AI化 | 学术文本 | 自然学术文本 | 通用 |

#### 2.1.5 数据类 (Data)

| Skill | 功能 | 输入 | 输出 | 行业 |
|-------|------|------|------|------|
| **data-analysis-skill** | 数据分析 | 数据+问题 | 分析结果 | 通用 |
| **report_formatter** | 报告格式化 | 原始数据 | 格式化报告 | 通用 |
| **newman** | Postman测试 | API集合 | 测试结果 | 通用 |
| **model-healthcheck** | 模型健康检查 | 模型配置 | 健康报告 | 通用 |

### 2.2 第二层：知识层 (Knowledge Layer) — 领域Skill

**定义**: 基于基础层构建，面向特定业务领域的Skill，包含领域知识和业务规则

**特征**:
- 依赖基础层Skill
- 包含领域知识库或规则引擎
- 行业专用或跨行业通用
- 可独立使用，也可被上层编排

#### 2.2.1 金融知识类 (Financial Knowledge)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **regulatory-policy-rag** | 监管政策RAG | web_search, research_rag | 金融 |
| **research-report** | 研报生成 | content-creator-cn, data-analysis-skill | 金融 |
| **market_view** | 市场观点 | research_rag, content-creator-cn | 金融 |
| **fund_research** | 基金研究 | data-analysis-skill, web_search | 金融 |
| **regulatory_reporting** | 监管报送 | report_formatter, data-analysis-skill | 金融 |

#### 2.2.2 金融分析类 (Financial Analysis)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **risk-compliance** | 风控合规 | data-analysis-skill, regulatory-policy-rag | 金融 |
| **financial-intelligence** | 金融智能中枢 | 多Skill组合 | 金融 |
| **collateral_valuation** | 抵押物估值 | data-analysis-skill, valuation_helper | 金融 |
| **tax_planning** | 税务筹划 | data-analysis-skill, content-creator-cn | 金融 |
| **product_pricing** | 产品定价 | data-analysis-skill, quant_backtest | 金融 |
| **liquidity_alert** | 流动性预警 | data-analysis-skill, report_formatter | 金融 |
| **valuation_helper** | 估值核算 | data-analysis-skill | 金融 |
| **trade_optimize** | 交易优化 | data-analysis-skill, quant_backtest | 金融 |

#### 2.2.3 金融审核类 (Financial Audit)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **contract_review** | 合同审查 | content-creator-cn, Grammar | 金融 |
| **application-material-checker** | 进件材料核对 | data-analysis-skill, Grammar | 金融 |
| **compliance_auto** | 合规检查 | risk-compliance, regulatory-policy-rag | 金融 |
| **audit_sampling** | 审计抽样 | data-analysis-skill | 金融 |
| **fraud_detection** | 反欺诈 | data-analysis-skill, risk-compliance | 金融 |

#### 2.2.4 保险类 (Insurance)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **claim_analysis** | 理赔分析 | data-analysis-skill, content-creator-cn | 保险 |
| **policy_management** | 保单管理 | data-analysis-skill, report_formatter | 保险 |
| **smart_underwriting** | 智能核保 | data-analysis-skill, risk-compliance | 保险 |
| **actuarial_model** | 精算模型 | data-analysis-skill, quant_backtest | 保险 |

#### 2.2.5 信贷类 (Credit)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **credit_approval** | 信用审批 | data-analysis-skill, risk-compliance | 金融 |
| **collection_optimize** | 催收优化 | data-analysis-skill, customer_health | 金融 |
| **churn_recall** | 流失召回 | data-analysis-skill, customer_health | 金融 |
| **customer_health** | 客户健康度 | data-analysis-skill | 金融 |

#### 2.2.6 投资类 (Investment)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **quant_backtest** | 量化回测 | data-analysis-skill | 金融 |
| **quant_fund** | 量化基金 | data-analysis-skill, quant_backtest | 金融 |
| **portfolio_management** | 组合管理 | data-analysis-skill, quant_backtest | 金融 |
| **rebalance** | 再平衡 | data-analysis-skill, portfolio_management | 金融 |
| **fof_portfolio** | FOF组合 | data-analysis-skill, fund_research | 金融 |
| **fund_compare** | 基金对比 | data-analysis-skill, web_search | 金融 |
| **fund_manager_profile** | 基金经理画像 | data-analysis-skill, web_search | 金融 |
| **dca_calculator** | 定投计算 | data-analysis-skill | 金融 |
| **options_strategy** | 期权策略 | data-analysis-skill, quant_backtest | 金融 |
| **margin_trading** | 融资融券 | data-analysis-skill, risk-compliance | 金融 |
| **block_trade** | 大宗交易 | data-analysis-skill, market_view | 金融 |
| **fixed_income_plus** | 固收+ | data-analysis-skill, portfolio_management | 金融 |
| **global-asset-allocation** | 全球配置 | data-analysis-skill, portfolio_management | 金融 |
| **esg_research** | ESG研究 | research_rag, content-creator-cn | 金融 |

#### 2.2.7 投行类 (Investment Banking)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **enterprise-due-diligence** | 企业尽调 | 多Skill组合 | 金融 |
| **ma_scheme** | 并购方案 | content-creator-cn, data-analysis-skill | 金融 |
| **ipo_analysis** | IPO分析 | data-analysis-skill, content-creator-cn | 金融 |
| **roadshow_material** | 路演材料 | content-creator-cn, getdesign-md | 金融 |
| **corp_account_opening** | 对公开户 | data-analysis-skill, application-material-checker | 金融 |

#### 2.2.8 财富管理类 (Wealth Management)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **family-trust** | 家族信托 | content-creator-cn, data-analysis-skill | 金融 |
| **robo_advisor** | 智能投顾 | data-analysis-skill, portfolio_management | 金融 |
| **wealth-management** | 财富管理 | 多Skill组合 | 金融 |

#### 2.2.9 供应链金融类 (Supply Chain)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **supply_chain_finance** | 供应链金融 | data-analysis-skill, risk-compliance | 金融 |
| **trade_finance** | 贸易融资 | data-analysis-skill, risk-compliance | 金融 |
| **cross_border_biz** | 跨境业务 | data-analysis-skill, regulatory-policy-rag | 金融 |
| **supply_chain** | 供应链方案 | data-analysis-skill | 金融 |
| **cash_management** | 现金管理 | data-analysis-skill | 金融 |

#### 2.2.10 营销客服类 (Marketing & Service)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **customer-marketing** | 营销话术 | content-creator-cn, customer-persona | 金融 |
| **smart_marketing** | 智能营销 | content-creator-cn, data-analysis-skill | 金融 |
| **smart_customer_service** | 智能客服 | content-creator-cn, knowledge_base | 金融 |
| **customer-persona** | 客户画像 | data-analysis-skill | 金融 |
| **objection_training** | 异议训练 | content-creator-cn | 金融 |

#### 2.2.11 运营类 (Operations)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **ops-daily-report** | 运营日报 | data-analysis-skill, report_formatter | 通用 |
| **ops_daily_report** | 运营日报v2 | data-analysis-skill, report_formatter | 通用 |
| **branch_analysis** | 网点分析 | data-analysis-skill | 金融 |
| **kpi_performance** | KPI考核 | data-analysis-skill | 通用 |
| **alm** | 资产负债管理 | data-analysis-skill, quant_backtest | 金融 |

#### 2.2.12 内容创作类 (Content Creation)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **story-cog** | 故事创作 | content-creator-cn | 通用 |
| **Story-Writer-Bilingual-Enhanced-Edition** | 双语故事 | content-creator-cn | 通用 |
| **douyin-creator-cn** | 抖音创作 | content-creator-cn, video-editor | 通用 |
| **content-strategy** | 内容策略 | content-creator-cn, data-analysis-skill | 通用 |

#### 2.2.13 设计与前端类 (Design & Frontend)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **frontend-design** | 前端设计 | getdesign-md | 通用 |
| **no-code-frontend-builder** | 无代码前端 | frontend-design, getdesign-md | 通用 |
| **product-manual-rag** | 产品手册RAG | research_rag | 通用 |

#### 2.2.14 产品管理类 (Product Management)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **prd-developer** | PRD开发 | content-creator-cn, getdesign-md | 通用 |
| **product-manager-toolkit** | 产品工具包 | content-creator-cn, data-analysis-skill | 通用 |
| **agile-product-owner** | 敏捷PO | content-creator-cn | 通用 |

#### 2.2.15 项目管理类 (Project Management)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **arkclaw-team-project-builder** | 项目构建 | content-creator-cn, code_reviewer | 通用 |
| **XUA-auto** | 自动化 | code_reviewer | 通用 |

#### 2.2.16 发布与集成类 (Publishing & Integration)

| Skill | 功能 | 依赖基础层 | 行业 |
|-------|------|-----------|------|
| **wecom-template-card** | 企微卡片 | content-creator-cn | 通用 |
| **feishu_publisher** | 飞书发布 | content-creator-cn | 通用 |
| **Feishu-Cloud-Drive** | 飞书云盘 | 无 | 通用 |
| **openclaw-feishu-docs-perm-auto** | 飞书权限 | 无 | 通用 |

### 2.3 第三层：编排层 (Orchestration Layer) — 组合Skill

**定义**: 将多个知识层Skill组合，通过工作流编排实现复杂业务场景

**特征**:
- 依赖知识层和基础层Skill
- 包含业务逻辑编排（串行/并行/条件分支）
- 统一入口和出口
- 状态管理和错误处理

#### 2.3.1 多Agent工作流 (Multi-Agent Workflow)

| Skill | 功能 | 组成Skill | 行业 |
|-------|------|----------|------|
| **enterprise-due-diligence** | 企业尽调引擎 | 数据采集→分析→报告→审核 | 金融 |
| **self-improvement** | 自我改进 | 学习→反思→优化→验证 | 通用 |
| **skill-creator** | Skill创建器 | 需求→设计→编码→测试→部署 | 通用 |
| **cyber-owasp-review** | 安全审查 | 扫描→分析→修复建议→验证 | 通用 |
| **mlops-automation-cn** | MLOps自动化 | 训练→部署→监控→回滚 | 通用 |
| **modified-code-review** | 修改代码评审 | 差异分析→影响评估→建议 | 通用 |

#### 2.3.2 统一入口网关 (Gateway)

| Skill | 功能 | 路由规则 | 行业 |
|-------|------|---------|------|
| **financial_intelligence** | 金融智能中枢 | 意图识别→路由→聚合 | 金融 |
| **wealth-management** | 财富管理网关 | 需求分析→方案匹配→执行 | 金融 |
| **customer-marketing** | 营销网关 | 客户识别→话术匹配→渠道选择 | 金融 |

### 2.4 第四层：场景层 (Scenario Layer) — 业务场景

**定义**: 面向最终用户的完整业务场景，包含多个编排层Skill的协同

**特征**:
- 面向具体业务场景（如"企业开户"、"财富管理"）
- 包含用户交互界面（企微/飞书/网页）
- 端到端流程闭环
- 可审计、可追踪

#### 2.4.1 金融场景 (Financial Scenarios)

| 场景 | 组成Skill | 用户 | 渠道 |
|------|----------|------|------|
| **企业开户** | corp_account_opening + application-material-checker + compliance_auto | 企业客户 | 企微/网页 |
| **财富管理** | wealth-management + robo_advisor + portfolio_management + risk-compliance | 高净值客户 | 企微/APP |
| **企业尽调** | enterprise-due-diligence + research_rag + market_view | 投行/风控 | 企微/网页 |
| **智能投顾** | robo_advisor + portfolio_management + fund_research + market_view | 零售客户 | APP/小程序 |
| **风控合规** | risk-compliance + compliance_auto + regulatory-policy-rag + fraud_detection | 合规人员 | 企微/网页 |
| **智能客服** | smart_customer_service + knowledge_base + escalation | 所有客户 | 企微/APP/电话 |
| **营销话术** | customer-marketing + smart_marketing + customer-persona | 客户经理 | 企微 |
| **研报生成** | research-report + research_rag + market_view + data-analysis-skill | 研究员 | 企微/网页 |
| **监管报送** | regulatory_reporting + data-analysis-skill + report_formatter | 合规人员 | 企微/网页 |
| **理赔处理** | claim_analysis + policy_management + smart_underwriting | 保险客户 | 企微/APP |
| **信贷审批** | credit_approval + collateral_valuation + risk-compliance + fraud_detection | 信贷员 | 企微/网页 |
| **IPO辅导** | ipo_analysis + enterprise-due-diligence + roadshow_material | 企业/投行 | 企微/网页 |
| **并购顾问** | ma_scheme + enterprise-due-diligence + valuation_helper | 投行/企业 | 企微/网页 |
| **家族信托** | family-trust + tax_planning + wealth-management | 高净值客户 | 企微/私人银行 |
| **供应链金融** | supply_chain_finance + trade_finance + risk-compliance | 企业/银行 | 企微/网页 |
| **跨境业务** | cross_border_biz + regulatory-policy-rag + compliance_auto | 企业/银行 | 企微/网页 |
| **量化投资** | quant_backtest + quant_fund + portfolio_management + rebalance | 投资经理 | 网页/终端 |
| **固收+管理** | fixed_income_plus + portfolio_management + risk-compliance | 投资经理 | 网页/终端 |
| **ESG投资** | esg_research + portfolio_management + research_rag | 投资经理 | 网页/终端 |
| **全球配置** | global-asset-allocation + portfolio_management + fund_research | 投资经理 | 网页/终端 |
| **网点运营** | branch_analysis + kpi_performance + ops-daily-report | 运营经理 | 企微/网页 |
| **审计合规** | audit_sampling + compliance_auto + regulatory-policy-rag | 审计/合规 | 企微/网页 |
| **反欺诈** | fraud_detection + risk-compliance + data-analysis-skill | 风控 | 企微/网页 |
| **客户召回** | churn_recall + customer_health + smart_marketing | 营销经理 | 企微 |
| **催收优化** | collection_optimize + customer_health + risk-compliance | 催收经理 | 企微 |
| **路演支持** | roadshow_material + market_view + research-report | 投行/企业 | 企微/网页 |
| **对公开户** | corp_account_opening + application-material-checker + compliance_auto | 企业 | 企微/网页 |
| **产品定价** | product_pricing + data-analysis-skill + market_view | 产品经理 | 企微/网页 |
| **流动性管理** | liquidity_alert + cash_management + alm | 财务/资金 | 企微/网页 |
| **税务筹划** | tax_planning + family-trust + wealth-management | 高净值客户 | 企微/私人银行 |
| **保险核保** | smart_underwriting + claim_analysis + actuarial_model | 保险/客户 | 企微/APP |
| **精算分析** | actuarial_model + data-analysis-skill + risk-compliance | 精算师 | 网页/终端 |
| **大宗交易** | block_trade + market_view + data-analysis-skill | 交易员 | 网页/终端 |
| **期权策略** | options_strategy + quant_backtest + risk-compliance | 交易员 | 网页/终端 |
| **融资融券** | margin_trading + risk-compliance + liquidity_alert | 交易员 | 网页/终端 |
| **FOF管理** | fof_portfolio + fund_research + fund_compare + fund_manager_profile | 投资经理 | 网页/终端 |
| **定投管理** | dca_calculator + fund_research + portfolio_management | 零售客户 | APP/小程序 |
| **估值核算** | valuation_helper + data-analysis-skill + report_formatter | 财务/会计 | 企微/网页 |
| **交易优化** | trade_optimize + data-analysis-skill + market_view | 交易员 | 网页/终端 |
| **抵押估值** | collateral_valuation + data-analysis-skill + risk-compliance | 信贷/评估 | 企微/网页 |

#### 2.4.2 通用场景 (Universal Scenarios)

| 场景 | 组成Skill | 用户 | 渠道 |
|------|----------|------|------|
| **内容创作** | content-creator-cn + copywriter + humanizer + Grammar | 营销/编辑 | 企微/网页 |
| **视频制作** | video-editor + byted-seedance-video-generate + video-to-prompt | 营销/创作者 | 企微/网页 |
| **代码开发** | senior-backend + senior-devops + code_reviewer + api-test-automation | 开发者 | IDE/网页 |
| **测试自动化** | py-test-creator + clean-pytest + api-test-automation + newman | 测试工程师 | IDE/网页 |
| **知识管理** | research_rag + regulatory-policy-rag + ontology + product-manual-rag | 知识管理员 | 企微/网页 |
| **会议管理** | meeting_minutes + content-creator-cn + report_formatter | 所有员工 | 企微/APP |
| **日报周报** | ops-daily-report + data-analysis-skill + report_formatter | 所有员工 | 企微 |
| **数据分析** | data-analysis-skill + report_formatter + web_search | 分析师 | 企微/网页 |
| **搜索聚合** | multi-search-engine + tavily-search + web_search + research_rag | 研究员 | 企微/网页 |
| **文档生成** | getdesign-md + prd-developer + product-manager-toolkit | 产品经理 | 企微/网页 |
| **前端开发** | vite-react-tailwind + no-code-frontend-builder + frontend-design | 前端开发 | IDE/网页 |
| **后端开发** | nodejs-backend-patterns + senior-backend + api-test-automation | 后端开发 | IDE/网页 |
| **DevOps** | senior-devops + openclaw-docker + model-healthcheck | DevOps | 终端/网页 |
| **安全审查** | cyber-owasp-review + code_reviewer + contract_review | 安全/合规 | 企微/网页 |
| **项目管理** | arkclaw-team-project-builder + agile-product-owner + XUA-auto | 项目经理 | 企微/网页 |
| **产品管理** | prd-developer + product-manager-toolkit + agile-product-owner | 产品经理 | 企微/网页 |
| **MLOps** | mlops-automation-cn + model-healthcheck + data-analysis-skill | ML工程师 | 终端/网页 |
| **自动化** | XUA-auto + openclaw-docker + api-test-automation | 自动化工程师 | 终端/网页 |
| **文本优化** | humanizer + humanizer-academic-zh + Grammar + content-creator-cn | 编辑/作者 | 企微/网页 |
| **语音合成** | edge-tts + byted-text-to-speech + content-creator-cn | 营销/客服 | 企微/APP |
| **浏览器自动化** | agent-browser + web_search + data-analysis-skill | 分析师/运营 | 终端/网页 |
| **抖音运营** | douyin-creator-cn + content-strategy + video-editor | 运营/创作者 | 企微/网页 |
| **故事创作** | story-cog + Story-Writer-Bilingual-Enhanced-Edition + content-creator-cn | 创作者 | 企微/网页 |
| **设计文档** | getdesign-md + frontend-design + prd-developer | 设计师/产品 | 企微/网页 |
| **知识图谱** | ontology + research_rag + data-analysis-skill | 知识工程师 | 网页/终端 |
| **飞书集成** | Feishu-Cloud-Drive + feishu_publisher + openclaw-feishu-docs-perm-auto | 所有员工 | 飞书 |
| **企微集成** | wecom-template-card + smart_customer_service + customer-marketing | 所有员工 | 企微 |
| **GitHub集成** | github + XUA-auto + code_reviewer | 开发者 | IDE/网页 |
| **Self-Improvement** | self-improvement + skill-creator + code_reviewer | AI工程师 | 终端/网页 |
| **Skill创建** | skill-creator + self-improvement + code_reviewer | AI工程师 | 终端/网页 |

---

## 三、跨行业通用 vs 行业专用

### 3.1 跨行业通用Skill (Universal Skills)

**定义**: 不依赖特定行业知识，可在任何行业复用

| 类别 | Skill列表 | 复用度 |
|------|----------|--------|
| **搜索** | web_search, multi-search-engine, tavily-search | ⭐⭐⭐⭐⭐ |
| **生成** | content-creator-cn, copywriter, meeting_minutes, edge-tts, byted-text-to-speech | ⭐⭐⭐⭐⭐ |
| **代码** | code_reviewer, senior-backend, senior-devops, vite-react-tailwind, api-test-automation, py-test-creator, clean-pytest | ⭐⭐⭐⭐⭐ |
| **工具** | agent-browser, video-editor, video-to-prompt, byted-seedance-video-generate, byted-seedream-image-generate, getdesign-md, ontology, Grammar, humanizer, humanizer-academic-zh | ⭐⭐⭐⭐⭐ |
| **数据** | data-analysis-skill, report_formatter, newman, model-healthcheck | ⭐⭐⭐⭐⭐ |
| **设计** | frontend-design, no-code-frontend-builder, getdesign-md | ⭐⭐⭐⭐⭐ |
| **产品** | prd-developer, product-manager-toolkit, agile-product-owner | ⭐⭐⭐⭐⭐ |
| **项目** | arkclaw-team-project-builder, XUA-auto | ⭐⭐⭐⭐⭐ |
| **发布** | wecom-template-card, feishu_publisher, Feishu-Cloud-Drive, openclaw-feishu-docs-perm-auto | ⭐⭐⭐⭐⭐ |
| **元能力** | self-improvement, skill-creator | ⭐⭐⭐⭐⭐ |
| **测试** | api-test-automation, newman, py-test-creator, clean-pytest, modified-code-review | ⭐⭐⭐⭐⭐ |
| **DevOps** | senior-devops, openclaw-docker, mlops-automation-cn | ⭐⭐⭐⭐⭐ |
| **内容** | content-creator-cn, copywriter, story-cog, Story-Writer-Bilingual-Enhanced-Edition, douyin-creator-cn, content-strategy | ⭐⭐⭐⭐⭐ |
| **搜索增强** | multi-search-engine, tavily-search, web_search | ⭐⭐⭐⭐⭐ |
| **浏览器** | agent-browser | ⭐⭐⭐⭐⭐ |
| **视频** | video-editor, video-to-prompt, byted-seedance-video-generate | ⭐⭐⭐⭐⭐ |
| **图像** | byted-seedream-image-generate, getdesign-md | ⭐⭐⭐⭐⭐ |
| **语音** | edge-tts, byted-text-to-speech | ⭐⭐⭐⭐⭐ |
| **文本优化** | humanizer, humanizer-academic-zh, Grammar | ⭐⭐⭐⭐⭐ |
| **知识图谱** | ontology | ⭐⭐⭐⭐⭐ |
| **GitHub** | github | ⭐⭐⭐⭐⭐ |
| **Node.js** | nodejs-backend-patterns | ⭐⭐⭐⭐⭐ |
| **前端框架** | vite-react-tailwind | ⭐⭐⭐⭐⭐ |
| **后端模式** | senior-backend, nodejs-backend-patterns | ⭐⭐⭐⭐⭐ |
| **代码质量** | code_reviewer, modified-code-review, clean-pytest | ⭐⭐⭐⭐⭐ |
| **测试生成** | py-test-creator, api-test-automation | ⭐⭐⭐⭐⭐ |
| **模型健康** | model-healthcheck | ⭐⭐⭐⭐⭐ |
| **MLOps** | mlops-automation-cn | ⭐⭐⭐⭐⭐ |
| **安全** | cyber-owasp-review | ⭐⭐⭐⭐⭐ |
| **自动化** | XUA-auto | ⭐⭐⭐⭐⭐ |
| **日报** | ops-daily-report, ops_daily_report | ⭐⭐⭐⭐⭐ |
| **KPI** | kpi_performance | ⭐⭐⭐⭐⭐ |
| **会议** | meeting_minutes | ⭐⭐⭐⭐⭐ |
| **飞书** | Feishu-Cloud-Drive, feishu_publisher, openclaw-feishu-docs-perm-auto | ⭐⭐⭐⭐⭐ |
| **企微** | wecom-template-card | ⭐⭐⭐⭐⭐ |

**总计**: 约 60+ 个跨行业通用Skill

### 3.2 金融行业专用Skill (Financial Skills)

**定义**: 依赖金融专业知识、监管规则、业务流程

| 子行业 | Skill列表 | 专业度 |
|--------|----------|--------|
| **风控合规** | risk-compliance, compliance_auto, regulatory-policy-rag, regulatory_reporting, audit_sampling, fraud_detection | ⭐⭐⭐⭐⭐ |
| **信贷** | credit_approval, collateral_valuation, collection_optimize, churn_recall, customer_health | ⭐⭐⭐⭐⭐ |
| **投资/投研** | quant_backtest, quant_fund, portfolio_management, rebalance, fof_portfolio, fund_research, fund_compare, fund_manager_profile, dca_calculator, options_strategy, margin_trading, block_trade, fixed_income_plus, global-asset-allocation, esg_research, market_view, research-report, research_rag | ⭐⭐⭐⭐⭐ |
| **投行** | enterprise-due-diligence, ma_scheme, ipo_analysis, roadshow_material, corp_account_opening, valuation_helper | ⭐⭐⭐⭐⭐ |
| **财富管理** | wealth-management, robo_advisor, family-trust, tax_planning | ⭐⭐⭐⭐⭐ |
| **保险** | claim_analysis, policy_management, smart_underwriting, actuarial_model | ⭐⭐⭐⭐⭐ |
| **供应链金融** | supply_chain_finance, trade_finance, cross_border_biz, supply_chain, cash_management | ⭐⭐⭐⭐⭐ |
| **营销客服** | customer-marketing, smart_marketing, smart_customer_service, customer-persona, objection_training | ⭐⭐⭐⭐⭐ |
| **运营** | ops-daily-report, ops_daily_report, branch_analysis, kpi_performance, alm | ⭐⭐⭐⭐⭐ |
| **产品** | product_pricing, liquidity_alert | ⭐⭐⭐⭐⭐ |
| **监管** | regulatory-policy-rag, regulatory_reporting, compliance_auto | ⭐⭐⭐⭐⭐ |
| **交易** | trade_optimize, block_trade, options_strategy, margin_trading | ⭐⭐⭐⭐⭐ |
| **财务** | valuation_helper, tax_planning, cash_management, alm, liquidity_alert | ⭐⭐⭐⭐⭐ |
| **核保理赔** | smart_underwriting, claim_analysis, policy_management, actuarial_model | ⭐⭐⭐⭐⭐ |
| **尽调** | enterprise-due-diligence, research_rag, market_view | ⭐⭐⭐⭐⭐ |
| **开户** | corp_account_opening, application-material-checker | ⭐⭐⭐⭐⭐ |
| **路演** | roadshow_material, market_view, research-report | ⭐⭐⭐⭐⭐ |
| **并购** | ma_scheme, enterprise-due-diligence, valuation_helper | ⭐⭐⭐⭐⭐ |
| **IPO** | ipo_analysis, enterprise-due-diligence, roadshow_material | ⭐⭐⭐⭐⭐ |
| **信托** | family-trust, tax_planning, wealth-management | ⭐⭐⭐⭐⭐ |
| **税务** | tax_planning, family-trust | ⭐⭐⭐⭐⭐ |
| **精算** | actuarial_model, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **ALM** | alm, liquidity_alert, cash_management | ⭐⭐⭐⭐⭐ |
| **ESG** | esg_research, research_rag | ⭐⭐⭐⭐⭐ |
| **全球配置** | global-asset-allocation, portfolio_management, fund_research | ⭐⭐⭐⭐⭐ |
| **固收+** | fixed_income_plus, portfolio_management, risk-compliance | ⭐⭐⭐⭐⭐ |
| **FOF** | fof_portfolio, fund_research, fund_compare, fund_manager_profile | ⭐⭐⭐⭐⭐ |
| **量化** | quant_backtest, quant_fund, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **大宗** | block_trade, market_view, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **期权** | options_strategy, quant_backtest, risk-compliance | ⭐⭐⭐⭐⭐ |
| **两融** | margin_trading, risk-compliance, liquidity_alert | ⭐⭐⭐⭐⭐ |
| **定投** | dca_calculator, fund_research, portfolio_management | ⭐⭐⭐⭐⭐ |
| **基金研究** | fund_research, fund_compare, fund_manager_profile | ⭐⭐⭐⭐⭐ |
| **基金经理** | fund_manager_profile, fund_research | ⭐⭐⭐⭐⭐ |
| **基金对比** | fund_compare, fund_research, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **客户健康** | customer_health, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **流失召回** | churn_recall, customer_health, smart_marketing | ⭐⭐⭐⭐⭐ |
| **催收** | collection_optimize, customer_health, risk-compliance | ⭐⭐⭐⭐⭐ |
| **网点分析** | branch_analysis, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **KPI** | kpi_performance, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **审计抽样** | audit_sampling, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **合规检查** | compliance_auto, risk-compliance, regulatory-policy-rag | ⭐⭐⭐⭐⭐ |
| **反欺诈** | fraud_detection, risk-compliance, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **合同审查** | contract_review, content-creator-cn, Grammar | ⭐⭐⭐⭐⭐ |
| **材料核对** | application-material-checker, data-analysis-skill, Grammar | ⭐⭐⭐⭐⭐ |
| **监管报送** | regulatory_reporting, data-analysis-skill, report_formatter | ⭐⭐⭐⭐⭐ |
| **政策RAG** | regulatory-policy-rag, web_search, research_rag | ⭐⭐⭐⭐⭐ |
| **研报RAG** | research_rag, web_search, content-creator-cn | ⭐⭐⭐⭐⭐ |
| **市场观点** | market_view, research_rag, content-creator-cn | ⭐⭐⭐⭐⭐ |
| **运营日报** | ops-daily-report, data-analysis-skill, report_formatter | ⭐⭐⭐⭐⭐ |
| **产品定价** | product_pricing, data-analysis-skill, market_view | ⭐⭐⭐⭐⭐ |
| **流动性** | liquidity_alert, data-analysis-skill, alm | ⭐⭐⭐⭐⭐ |
| **现金管理** | cash_management, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **供应链金融** | supply_chain_finance, data-analysis-skill, risk-compliance | ⭐⭐⭐⭐⭐ |
| **贸易融资** | trade_finance, data-analysis-skill, risk-compliance | ⭐⭐⭐⭐⭐ |
| **跨境业务** | cross_border_biz, data-analysis-skill, regulatory-policy-rag | ⭐⭐⭐⭐⭐ |
| **供应链** | supply_chain, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **对公开户** | corp_account_opening, application-material-checker, compliance_auto | ⭐⭐⭐⭐⭐ |
| **路演材料** | roadshow_material, content-creator-cn, getdesign-md | ⭐⭐⭐⭐⭐ |
| **营销话术** | customer-marketing, content-creator-cn, customer-persona | ⭐⭐⭐⭐⭐ |
| **智能营销** | smart_marketing, content-creator-cn, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **智能客服** | smart_customer_service, content-creator-cn, knowledge_base | ⭐⭐⭐⭐⭐ |
| **客户画像** | customer-persona, data-analysis-skill | ⭐⭐⭐⭐⭐ |
| **异议训练** | objection_training, content-creator-cn | ⭐⭐⭐⭐⭐ |
| **金融智能中枢** | financial_intelligence, financial-intelligence, 多Skill组合 | ⭐⭐⭐⭐⭐ |

**总计**: 约 70+ 个金融行业专用Skill

### 3.3 telecom industrySkill (Telecom Skills)

**当前状态**: 正在开发中（Region-Atelecom课程项目）

| 场景 | 对应Skill | 状态 |
|------|----------|------|
| 信息提取与归档 | l1-01-info-extractor-archiver | ✅ 已开发 |
| 日报/周报生成 | l1-02-daily-weekly-report-generator | ✅ 已开发 |
| 资料审核 | l1-03-material-audit-assistant | ✅ 已开发 |
| 知识库问答 | l1-04-kb-qa-assistant | ✅ 已开发 |
| 权限自查 | l1-05-permission-self-checklist | ✅ 已开发 |
| 消息联动 | l1-06-channel-message-linker | ✅ 已开发 |
| 统一入口网关 | l2-01-unified-entry-gateway | ✅ 已开发 |
| 多Agent投诉流 | l2-02-multi-agent-complaint-flow | ✅ 已开发 |
| 智能数据查询 | l3-01-intelligent-data-query | ✅ 已开发 |

**特点**: 基于金融Skill方法论，适配telecom business场景

---

## 四、Skill 依赖关系图谱

### 4.1 核心依赖关系

```
基础层 (Foundation)
├── web_search ──┬──> multi-search-engine
│               ├──> tavily-search
│               ├──> research_rag
│               └──> 所有需要搜索的Skill
│
├── content-creator-cn ──┬──> copywriter
│                       ├──> meeting_minutes
│                       ├──> customer-marketing
│                       ├──> smart_marketing
│                       ├──> smart_customer_service
│                       ├──> roadshow_material
│                       ├──> regulatory_reporting
│                       ├──> research-report
│                       ├──> market_view
│                       ├──> story-cog
│                       ├──> douyin-creator-cn
│                       ├──> content-strategy
│                       └──> 所有需要文本生成的Skill
│
├── data-analysis-skill ──┬──> report_formatter
│                        ├──> quant_backtest
│                        ├──> quant_fund
│                        ├──> portfolio_management
│                        ├──> risk-compliance
│                        ├──> customer_health
│                        ├──> branch_analysis
│                        ├──> kpi_performance
│                        ├──> ops-daily-report
│                        ├──> ops_daily_report
│                        ├──> product_pricing
│                        ├──> liquidity_alert
│                        ├──> valuation_helper
│                        ├──> trade_optimize
│                        ├──> collateral_valuation
│                        ├──> collection_optimize
│                        ├──> churn_recall
│                        ├──> audit_sampling
│                        ├──> compliance_auto
│                        ├──> fraud_detection
│                        ├──> credit_approval
│                        ├──> claim_analysis
│                        ├──> policy_management
│                        ├──> smart_underwriting
│                        ├──> actuarial_model
│                        ├──> alm
│                        ├──> dca_calculator
│                        ├──> fund_research
│                        ├──> fund_compare
│                        ├──> fund_manager_profile
│                        ├──> esg_research
│                        ├──> global-asset-allocation
│                        ├──> fixed_income_plus
│                        ├──> rebalance
│                        ├──> fof_portfolio
│                        ├──> block_trade
│                        ├──> options_strategy
│                        ├──> margin_trading
│                        ├──> supply_chain_finance
│                        ├──> trade_finance
│                        ├──> cross_border_biz
│                        ├──> supply_chain
│                        ├──> cash_management
│                        ├──> enterprise-due-diligence
│                        ├──> ma_scheme
│                        ├──> ipo_analysis
│                        ├──> family-trust
│                        ├──> tax_planning
│                        ├──> wealth-management
│                        ├──> robo_advisor
│                        ├──> corp_account_opening
│                        ├──> product_pricing
│                        └──> 几乎所有金融Skill
│
├── code_reviewer ──┬──> senior-backend
│                  ├──> senior-devops
│                  ├──> modified-code-review
│                  └──> 所有代码相关Skill
│
├── agent-browser ──┬──> vite-react-tailwind
│                  └──> no-code-frontend-builder
│
├── edge-tts ──┬──> byted-text-to-speech
│             └──> 所有需要语音的Skill
│
└── ontology ──┬──> research_rag
              └──> regulatory-policy-rag
```

### 4.2 组合关系

```
知识层 (Knowledge)
├── risk-compliance ──┬──> compliance_auto
│                    ├──> collection_optimize
│                    ├──> fraud_detection
│                    ├──> credit_approval
│                    ├──> smart_underwriting
│                    ├──> collateral_valuation
│                    ├──> margin_trading
│                    ├──> options_strategy
│                    ├──> block_trade
│                    ├──> fixed_income_plus
│                    ├──> supply_chain_finance
│                    ├──> trade_finance
│                    ├──> cross_border_biz
│                    ├──> wealth-management
│                    ├──> enterprise-due-diligence
│                    └──> 几乎所有金融场景
│
├── research_rag ──┬──> research-report
│                 ├──> market_view
│                 ├──> regulatory-policy-rag
│                 ├──> esg_research
│                 └──> enterprise-due-diligence
│
├── portfolio_management ──┬──> rebalance
│                         ├──> fof_portfolio
│                         ├──> global-asset-allocation
│                         ├──> fixed_income_plus
│                         ├──> robo_advisor
│                         └──> wealth-management
│
├── customer_health ──┬──> churn_recall
│                    └──> collection_optimize
│
└── application-material-checker ──┬──> corp_account_opening
                                  └──> compliance_auto
```

### 4.3 编排层组合

```
编排层 (Orchestration)
├── enterprise-due-diligence ──┬──> research_rag
│                             ├──> market_view
│                             ├──> regulatory-policy-rag
│                             ├──> data-analysis-skill
│                             └──> content-creator-cn
│
├── wealth-management ──┬──> robo_advisor
│                      ├──> portfolio_management
│                      ├──> risk-compliance
│                      ├──> family-trust
│                      └──> tax_planning
│
├── financial_intelligence ──┬──> 几乎所有金融Skill
│                           └──> 统一路由网关
│
├── customer-marketing ──┬──> smart_marketing
│                       ├──> customer-persona
│                       └──> content-creator-cn
│
└── self-improvement ──┬──> skill-creator
                      └──> code_reviewer
```

---

## 五、Skill 复用策略

### 5.1 构建块复用 (Building Block Reuse)

```
┌─────────────────────────────────────────────────────────────┐
│                    构建块 (Building Blocks)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ 搜索块      │  │ 生成块      │  │ 分析块      │       │
│  │ web_search  │  │ content-    │  │ data-       │       │
│  │ tavily      │  │ creator-cn  │  │ analysis-   │       │
│  │ research_rag│  │ copywriter  │  │ skill       │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         │                │                │               │
│         └────────────────┴────────────────┘               │
│                          │                                │
│              ┌───────────┴───────────┐                   │
│              │     组合块 (Composites)  │                   │
│              │  ┌─────────────────┐   │                   │
│              │  │ risk-compliance │   │                   │
│              │  │ portfolio_mgmt  │   │                   │
│              │  │ customer-health │   │                   │
│              │  └─────────────────┘   │                   │
│              └───────────┬───────────┘                   │
│                          │                                │
│              ┌───────────┴───────────┐                   │
│              │    场景块 (Scenarios)    │                   │
│              │  ┌─────────────────┐   │                   │
│              │  │ 企业尽调        │   │                   │
│              │  │ 财富管理        │   │                   │
│              │  │ 智能客服        │   │                   │
│              │  └─────────────────┘   │                   │
│              └─────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 复用矩阵

| 基础Skill | 被复用次数 | 主要复用方 |
|-----------|-----------|-----------|
| data-analysis-skill | 50+ | 几乎所有金融Skill |
| content-creator-cn | 40+ | 报告、营销、客服、内容创作 |
| web_search | 20+ | 搜索、研究、尽调 |
| research_rag | 15+ | 研报、政策、ESG、尽调 |
| report_formatter | 15+ | 日报、监管报送、运营报告 |
| code_reviewer | 10+ | 代码开发、安全审查 |
| risk-compliance | 20+ | 风控、信贷、保险、交易 |
| portfolio_management | 10+ | 投顾、组合、全球配置 |

### 5.3 复用原则

1. **单一职责**: 基础Skill只做一件事，做好一件事
2. **标准接口**: 统一输入输出格式（JSON/Markdown）
3. **无状态**: Skill不保存状态，状态由编排层管理
4. **可替换**: 同类Skill可互换（如web_search ↔ tavily-search）
5. **可组合**: 通过编排层自由组合，形成新场景

---

## 六、Skill 治理体系

### 6.1 生命周期管理

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  规划   │ → │  开发   │ → │  测试   │ → │  部署   │ → │  退役   │
│ Plan    │    │ Develop │    │ Test    │    │ Deploy  │    │ Retire  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │              │
     ↓              ↓              ↓              ↓              ↓
  需求分析      编码实现       单元测试       灰度发布       下线通知
  架构设计      代码审查       集成测试       监控告警       数据迁移
  资源评估      文档编写       性能测试       回滚策略       归档保存
```

### 6.2 质量门禁

| 层级 | 检查项 | 工具 | 标准 |
|------|--------|------|------|
| **基础层** | 单元测试覆盖率 | pytest | ≥80% |
| | 代码复杂度 | radon | ≤10 |
| | 安全扫描 | bandit | 无高危漏洞 |
| **知识层** | 集成测试 | pytest | 核心路径100% |
| | 性能测试 | locust | RT ≤ 5s |
| | 数据质量 | 自定义 | 准确率 ≥ 90% |
| **编排层** | 端到端测试 | 自定义 | 全链路通过 |
| | 并发测试 | locust | 支持100并发 |
| | 故障注入 | chaos | 自动恢复 |
| **场景层** | UAT测试 | 人工 | 业务验收通过 |
| | 灰度监控 | 自定义 | 错误率 ≤ 1% |
| | 回滚测试 | 自定义 | 5分钟内回滚 |

### 6.3 版本管理

```
主版本.次版本.修订号 (Major.Minor.Patch)

示例: v2.3.1
- Major (2): 不兼容的API变更
- Minor (3): 新增功能，向后兼容
- Patch (1): Bug修复，向后兼容

版本策略:
- 基础层: 保守升级，Major变更需全量回归
- 知识层: 按需升级，Minor变更需集成测试
- 编排层: 快速迭代，Patch可热更新
- 场景层: 业务驱动，版本与业务版本对齐
```

---

## 七、Skill 开发规范

### 7.1 目录结构规范

```
skill-name/
├── SKILL.md              # Skill定义文档（必须）
├── _meta.json            # 元数据（名称、版本、作者、标签）
├── README.md             # 使用说明（可选）
├── engines/              # 引擎实现
│   ├── __init__.py
│   └── skill_engine.py   # 主引擎
├── scripts/              # CLI脚本
│   ├── __init__.py
│   └── skill_cli.py      # 命令行入口
├── tests/                # 测试用例
│   ├── __init__.py
│   └── test_skill.py
├── knowledge_base/       # 知识库（RAG类Skill）
│   └── ...
├── templates/            # 模板文件
│   └── ...
├── wecom_integration.py  # 企微集成（可选）
└── references/           # 参考文档
    └── ...
```

### 7.2 SKILL.md 规范

```markdown
---
name: "skill-name"
display_name: "Skill显示名称"
version: "1.0.0"
level: "L1"  # L1=基础, L2=组合, L3=多Agent
industry: "financial"  # financial/telecom/healthcare/retail/universal
description: "一句话描述"
author: "作者"
tags: ["tag1", "tag2"]
dependencies: ["web_search", "data-analysis-skill"]  # 依赖的基础Skill
---

# Skill名称

## 功能概述

## 输入参数

## 输出格式

## 使用示例

## 依赖关系

## 版本历史
```

### 7.3 接口规范

```python
# 统一接口定义
class SkillEngine:
    """Skill引擎基类"""
    
    def __init__(self, config: dict):
        self.config = config
        self.name = config.get('name', 'unnamed')
        self.version = config.get('version', '1.0.0')
    
    async def execute(self, input_data: dict) -> dict:
        """
        执行Skill
        
        Args:
            input_data: 标准化输入数据
            
        Returns:
            标准化输出数据
            {
                "status": "success|partial|error",
                "data": {},
                "metadata": {
                    "skill_name": "...",
                    "version": "...",
                    "execution_time_ms": 1234,
                    "timestamp": "2026-06-20T10:30:00Z"
                },
                "error": null  # 或错误信息
            }
        """
        raise NotImplementedError
    
    def health_check(self) -> dict:
        """健康检查"""
        return {"status": "healthy", "timestamp": "..."}
```

---

## 八、附录

### 8.1 Skill完整清单

详见 [skills_inventory.json](./skills_inventory.json) 和 [skills_detailed.json](./skills_detailed.json)

### 8.2 依赖关系图

详见 [skills_dependencies.json](./skills_dependencies.json)

### 8.3 术语表

| 术语 | 定义 |
|------|------|
| **Skill** | 可独立运行、可复用的AI功能单元 |
| **基础Skill (L1)** | 原子功能，不可再分解 |
| **组合Skill (L2)** | 多个基础Skill的组合，通过编排实现复杂功能 |
| **多Agent Skill (L3)** | 多个AI Agent协同工作，实现端到端业务场景 |
| **编排层** | 负责Skill之间的调度、路由、状态管理 |
| **知识层** | 包含领域知识和业务规则的Skill层 |
| **场景层** | 面向最终用户的完整业务场景 |
| **构建块** | 可复用的标准化功能单元 |
| **无差别信息流** | 统一的信息输入-处理-输出模式 |
| **RAG** | Retrieval-Augmented Generation，检索增强生成 |
| **企微集成** | 与企业微信的对接能力 |
| **飞书集成** | 与飞书的对接能力 |

### 8.4 参考架构

- **TOGAF**: The Open Group Architecture Framework
- **4A架构**: 业务架构、应用架构、数据架构、技术架构
- **微服务架构**: 独立部署、独立扩展、独立升级
- **构建块方法**: 标准化、可复用、可组合

---

*文档版本: v1.0*  
*更新日期: 2026-06-20*  
*作者: BetaAgent Agent*  
*适用范围: DemoBankAI Skill体系*
