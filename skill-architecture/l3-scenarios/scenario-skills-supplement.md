# L3 场景Skill补充清单

> **层级**: L3 场景Skill  
> **目标**: 补充10个典型场景，覆盖金融、telecom、通用领域  
> **版本**: v1.0  

---

## 一、补充场景总览

| 编号 | 场景名称 | 行业 | 能力域 | 组成Skill | 优先级 |
|------|----------|------|--------|----------|--------|
| S301 | 智能投研工作台 | 金融 | C03/C04/C08 | research_rag + market_view + report_formatter | P0 |
| S302 | 客户360视图 | 金融 | C07 | customer_persona + customer_health + churn_recall | P0 |
| S303 | 智能风控指挥中心 | 金融 | C05 | risk_compliance + fraud_detection + regulatory_policy_rag | P0 |
| S304 | 财富管理顾问 | 金融 | C08 | robo_advisor + portfolio_management + fund_research | P1 |
| S305 | 智能客服中枢 | 通用 | C07 | smart_customer_service + faq_knowledge + sentiment_monitor | P0 |
| S306 | 企业尽调报告工厂 | 金融 | C01/C04 | enterprise_due_diligence + research_report + contract_review | P1 |
| S307 | 运营智能驾驶舱 | 通用 | C03/C04 | ops_daily_report + data_analysis_skill + branch_analysis | P1 |
| S308 | 智能营销工作台 | 通用 | C07 | customer_marketing + smart_marketing + content_creator_cn | P1 |
| S309 | telecom故障智能诊断 | telecom | C03/C06 | fault_diagnosis + data_analysis_skill + knowledge_rag | P0 |
| S310 | 智能培训助手 | 通用 | C04 | training_plan + content_creator_cn + meeting_minutes | P2 |

---

## 二、场景详细设计

### S301 智能投研工作台 (Intelligent Research Workbench)

**行业**: 金融  
**能力域**: C03数据分析 + C04报告生成 + C08投资组合定价  
**目标用户**: 研究员、投资经理  

#### 输入
- 研究标的（股票代码/行业/公司名）
- 研究类型（宏观/行业/公司/策略）
- 输出格式（简报/深度报告/数据包）

#### 处理流程
```
用户输入研究标的
    ↓
L1: multi-search-engine → 收集多源数据
L1: research_rag → 检索内部研报知识库
L1: tavily-search → 检索外部最新资讯
    ↓
L2: data_analysis_skill → 数据清洗、计算指标
L2: market_view → 生成市场观点
    ↓
L1: report_formatter → 格式化报告
L1: content_creator_cn → 生成文字描述
    ↓
L2: cross_channel_router → 发送到飞书/邮件
    ↓
输出: 完整投研报告（PDF/Markdown）
```

#### 输出
- 研究报告（摘要+数据分析+观点+风险提示）
- 数据包（Excel/CSV）
- 可视化图表

---

### S302 客户360视图 (Customer 360 View)

**行业**: 金融  
**能力域**: C07客户营销服务渠道  
**目标用户**: 客户经理、营销经理  

#### 输入
- 客户ID/手机号
- 查询维度（画像/健康度/流失风险/营销建议）

#### 处理流程
```
用户输入客户ID
    ↓
L1: customer_persona → 生成客户画像
L1: customer_health → 计算健康度评分
L1: churn_recall → 评估流失风险
    ↓
L2: data_analysis_skill → 聚合分析
    ↓
L1: content_creator_cn → 生成营销话术
L1: report_formatter → 格式化视图
    ↓
输出: 客户360视图报告
```

#### 输出
- 客户画像卡片
- 健康度热力图
- 流失风险等级
- 个性化营销建议

---

### S303 智能风控指挥中心 (Intelligent Risk Control Center)

**行业**: 金融  
**能力域**: C05风险合规安全  
**目标用户**: 风控经理、合规专员  

#### 输入
- 监控对象（交易/客户/产品/市场）
- 告警阈值
- 响应策略

#### 处理流程
```
实时监控数据流
    ↓
L1: risk_compliance → 风险评估
L1: fraud_detection → 欺诈检测
L1: regulatory_policy_rag → 政策合规检查
    ↓
L2: alert_engine → 生成告警
    ↓
L2: cross_channel_router → 多渠道告警（企微+钉钉）
L1: report_formatter → 生成风控日报
    ↓
输出: 告警通知 + 风控报告
```

#### 输出
- 实时告警通知
- 风控日报/周报
- 风险趋势分析
- 合规检查报告

---

### S304 财富管理顾问 (Wealth Management Advisor)

**行业**: 金融  
**能力域**: C08投资组合定价  
**目标用户**: 高净值客户、理财经理  

#### 输入
- 客户资产情况
- 风险偏好（保守/稳健/积极）
- 投资目标（保值/增值/传承）

#### 处理流程
```
用户输入资产+风险偏好
    ↓
L1: robo_advisor → 生成配置建议
L1: portfolio_management → 组合优化
L1: fund_research → 基金筛选
L1: risk_compliance → 风险检查
    ↓
L2: data_analysis_skill → 收益预测
L1: report_formatter → 生成方案书
    ↓
输出: 财富管理方案
```

#### 输出
- 资产配置方案
- 产品推荐清单
- 收益预测报告
- 风险揭示书

---

### S305 智能客服中枢 (Intelligent Customer Service Hub)

**行业**: 通用  
**能力域**: C07客户营销服务渠道  
**目标用户**: 客服团队、客户  

#### 输入
- 客户问题（文本/语音）
- 客户ID（可选）
- 渠道来源（企微/APP/网页）

#### 处理流程
```
客户输入问题
    ↓
L1: smart_customer_service → 意图识别
L1: faq_knowledge → FAQ检索
L1: product_manual_rag → 产品手册检索
    ↓
L2: sentiment_monitor → 情绪分析
    ↓
如果情绪负面/问题复杂:
    L2: cross_channel_router → 转人工（高优先级）
否则:
    L1: content_creator_cn → 生成回复
    L2: cross_channel_router → 自动回复
    ↓
输出: 客服回复
```

#### 输出
- 自动回复（80%常见问题）
- 人工转接（复杂/投诉）
- 客服质检报告
- 知识库更新建议

---

### S306 企业尽调报告工厂 (Due Diligence Report Factory)

**行业**: 金融  
**能力域**: C01信息提取 + C04报告生成  
**目标用户**: 投行、风控、投资经理  

#### 输入
- 目标企业名称/代码
- 尽调类型（财务/法律/业务/技术）
- 报告深度（标准/深度）

#### 处理流程
```
用户输入目标企业
    ↓
L1: enterprise_due_diligence → 数据采集
L1: web_search → 公开信息检索
L1: research_rag → 内部研报检索
    ↓
L2: data_analysis_skill → 财务分析
L1: contract_review → 合同审查
    ↓
L1: research_report → 生成报告
L1: report_formatter → 格式化
    ↓
输出: 尽调报告
```

#### 输出
- 尽调报告（PDF/Word）
- 财务分析表
- 风险提示清单
- 估值建议

---

### S307 运营智能驾驶舱 (Operations Intelligence Cockpit)

**行业**: 通用  
**能力域**: C03数据分析 + C04报告生成  
**目标用户**: 运营经理、管理层  

#### 输入
- 运营数据源（数据库/Excel/API）
- 分析维度（日报/周报/月报）
- 关注指标（自定义）

#### 处理流程
```
连接数据源
    ↓
L1: data_analysis_skill → 数据提取
L1: ops_daily_report → 日报生成
L1: branch_analysis → 网点分析
    ↓
L2: data_analysis_skill → 趋势分析
L1: report_formatter → 可视化
    ↓
L2: cross_channel_router → 定时推送
    ↓
输出: 运营驾驶舱
```

#### 输出
- 运营日报/周报
- 数据可视化看板
- 异常预警
- 趋势预测

---

### S308 智能营销工作台 (Intelligent Marketing Workbench)

**行业**: 通用  
**能力域**: C07客户营销服务渠道  
**目标用户**: 营销经理、客户经理  

#### 输入
- 营销目标（拉新/促活/转化）
- 目标客户群
- 产品信息

#### 处理流程
```
用户输入营销目标
    ↓
L1: customer_marketing → 话术生成
L1: smart_marketing → 策略推荐
L1: customer_persona → 画像分析
    ↓
L2: content_creator_cn → 内容生成
L2: cross_channel_router → 多渠道投放
    ↓
L1: sentiment_monitor → 效果监控
    ↓
输出: 营销方案+执行报告
```

#### 输出
- 营销话术库
- 投放策略
- 执行报告
- 效果分析

---

### S309 telecom故障智能诊断 (Telecom Fault Intelligent Diagnosis)

**行业**: telecom  
**能力域**: C03数据分析 + C06流程编排  
**目标用户**: 运维工程师、客服  

#### 输入
- 故障现象描述
- 设备/区域信息
- 日志文件（可选）

#### 处理流程
```
用户输入故障信息
    ↓
L1: fault_diagnosis → 根因分析
L1: data_analysis_skill → 日志分析
L1: knowledge_rag → 知识库检索
    ↓
L2: alert_engine → 生成工单
    ↓
L2: cross_channel_router → 通知运维
    ↓
输出: 诊断报告+修复方案
```

#### 输出
- 故障根因分析
- 修复步骤
- 工单自动创建
- 预防建议

---

### S310 智能培训助手 (Intelligent Training Assistant)

**行业**: 通用  
**能力域**: C04报告文档生成  
**目标用户**: 培训师、HR、员工  

#### 输入
- 培训主题
- 目标学员
- 培训时长

#### 处理流程
```
用户输入培训主题
    ↓
L1: training_plan → 计划生成
L1: content_creator_cn → 内容生成
L1: meeting_minutes → 纪要生成
    ↓
L2: data_analysis_skill → 效果评估
    ↓
输出: 培训方案+材料
```

#### 输出
- 培训计划
- 课件材料
- 考核方案
- 效果评估

---

## 三、场景与L2构建块的关系

```
L3 场景Skill
├── S301 智能投研工作台
│   ├── L2: cross-channel-router (发送报告)
│   ├── L2: data_analysis_skill (数据分析)
│   └── L1: research_rag, market_view, report_formatter
│
├── S302 客户360视图
│   ├── L2: cross-channel-router (发送视图)
│   ├── L2: data_analysis_skill (聚合分析)
│   └── L1: customer_persona, customer_health, churn_recall
│
├── S303 智能风控指挥中心
│   ├── L2: cross-channel-router (多渠道告警)
│   ├── L2: alert_engine (告警生成)
│   └── L1: risk_compliance, fraud_detection, regulatory_policy_rag
│
├── S305 智能客服中枢
│   ├── L2: cross-channel-router (回复路由)
│   ├── L2: sentiment_monitor (情绪分析)
│   └── L1: smart_customer_service, faq_knowledge, product_manual_rag
│
└── ... (其他场景)
```

---

## 四、实施路线图

| 阶段 | 时间 | 场景 | 说明 |
|------|------|------|------|
| **Phase 1** | 1-2周 | S301, S302, S303 | 金融核心场景 |
| **Phase 2** | 2-3周 | S305, S309 | 通用+telecom场景 |
| **Phase 3** | 3-4周 | S304, S306, S307 | 金融深度场景 |
| **Phase 4** | 4-5周 | S308, S310 | 通用扩展场景 |

---

*版本: v1.0*  
*作者: BetaAgent Agent*  
*日期: 2026-06-20*
