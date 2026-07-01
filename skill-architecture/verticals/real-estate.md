# 垂直行业蓝图：房地产 (Real Estate)

**Industry Code**: `real_estate`
**版本**: v1.0
**状态**: 蓝图

---

## 1. 行业特征与约束

| 维度 | 特征 | 对Skill设计的影响 |
|------|------|-------------------|
| **业态多元** | 开发/销售/租赁/中介/物管/资管 | Skill按业态分组 |
| **强地理属性** | 城市/区域/地段差异巨大 | 必须有地理坐标和POI能力 |
| **数据来源散** | 房源/楼盘/客户/合同/物业/商圈 | L0连接器矩阵宽 |
| **客户决策长** | 看房→比对→谈判→签约→贷款，周期数周-数月 | 需长周期跟进+多触点 |
| **政策敏感** | 限购/限贷/预售/网签政策频繁调整 | 政策知识库+规则引擎 |
| **集成方** | CRM、楼盘管理、网签系统、ERP、物业系统、贝壳/链家/安居客 | L0连接器 |

---

## 2. 核心场景地图

| 场景 | 描述 | L2复用 | L3 SkillID |
|------|------|--------|-------------|
| 智能客户接待 | 客户咨询→意向判断+楼盘推荐 | cross_channel + taskflow | `l3_smart_reception` |
| 房源智能匹配 | 客户画像→TOP-N房源+对比报告 | document_pipeline | `l3_house_matching` |
| 看房路线规划 | 多套意向房源→最优看房路线+预约 | taskflow | `l3_visit_planning` |
| 价格智能评估 | 房源信息→市场参考价区间+对标房源 | document_pipeline | `l3_price_estimation` |
| 合同智能审签 | 购房/租赁合同→风险条款+电子签 | document_pipeline | `l3_contract_signing` |
| 客户长周期跟进 | 客户阶段→自动跟进话术+触达 | taskflow + cross_channel | `l3_customer_followup` |
| 楼盘日报/周报 | 多楼盘销售数据→管理日报 | document_pipeline + taskflow | `l3_sales_report` |
| 物业报修工单 | 业主报修→工单分派+回访闭环 | taskflow + cross_channel | `l3_property_repair` |
| 商圈洞察 | 区域POI/竞品/租金→商圈研究报告 | document_pipeline | `l3_market_research` |
| 资产估值 | 楼宇资产数据→估值模型+定期报告 | document_pipeline + alert_engine | `l3_asset_valuation` |

---

## 3. L0/L1 行业专用Skill需求

### L0 连接器
- `l0_beike_listings` 贝壳/链家房源（公开数据爬取/合规接入）
- `l0_anjuke_listings` 安居客房源
- `l0_amap_poi` 高德POI/路线/地理编码
- `l0_real_estate_crm` 房产CRM适配（明源/思源/红圈通）
- `l0_signing_system` 网签系统适配（按城市住建局）
- `l0_property_system` 物业管理系统（万翼/极致/嘉乐）
- `l0_loan_calculator` 贷款计算器（房贷利率/公积金/组合贷）

### L1 基础能力
- `l1_property_normalize` 房源信息归一化（户型/朝向/楼层/装修标准化）
- `l1_house_match_score` 房源匹配评分（多因子加权）
- `l1_price_comp_analysis` 同小区/同户型对标分析
- `l1_policy_check` 限购/限贷资格核查
- `l1_geo_distance` 地理距离/通勤时间计算
- `l1_floor_plan_parse` 户型图解析（OCR+结构化）
- `l1_tenant_credit_score` 租户信用评分（适用于租赁）

---

## 4. 标杆场景：智能客户接待 + 房源匹配（详设）

### 4.1 业务价值
售楼处客户接待时长从 30-45 分钟缩短到 15 分钟，初步意向客户转化率提升。

### 4.2 流程设计

```yaml
flow_id: smart_reception_matching_v1
input_schema:
  - {name: customer_id, type: string, required: false}
  - {name: channel, type: enum, values: [wecom, weixin_mp, h5, on_site_h5]}
  - {name: project_id, type: string, required: false}

steps:
  - id: customer_dialogue
    type: human_decision
    prompt:
      channel: "${input.channel}"
      template: dynamic_question_flow
      questions:
        - "您是首次置业还是改善型购房？"
        - "您的预算大致在什么区间？"
        - "您主要考虑哪几个区域？"
        - "几口人居住？是否需要学区？"
        - "首付资金到位情况？是否需要贷款？"
      timeout: 20m
    output: profile

  - id: load_customer_history
    type: skill_call
    skill: l0_real_estate_crm
    params: { action: get_customer, customer_id: "${input.customer_id}" }
    output: history

  - id: build_customer_portrait
    type: skill_call
    skill: l1_customer_portrait_build      # 通用L1
    params:
      dialogue: "${profile}"
      history: "${history}"
    output: portrait

  - id: policy_check
    type: skill_call
    skill: l1_policy_check
    params: { city: "${portrait.target_city}", customer: "${portrait}" }
    output: policy

  - id: branch_qualified
    type: branch
    cases:
      - when: "${policy.qualified} == false"
        next: explain_policy
      - default:
        next: match_houses

  - id: explain_policy
    type: skill_call
    skill: l2_cross_channel_router
    params:
      message_type: notify
      title: "限购政策说明"
      content: "${policy.explanation}"
      recipients: { channels: ["${input.channel}"], targets: ["${input.customer_id}"] }
    next: end

  - id: match_houses
    type: parallel
    branches:
      - id: own_inventory
        skill: l1_house_match_score
        params: { source: own_inventory, portrait: "${portrait}" }
      - id: market_listings
        skill: l1_house_match_score
        params: { source: market, portrait: "${portrait}" }
    aggregate: merge_top_n
    params: { top_n: 5 }
    output: matches

  - id: comparison_report
    type: skill_call
    skill: l1_house_compare_report
    params: { houses: "${matches}", portrait: "${portrait}" }
    output: report

  - id: schedule_visit
    type: skill_call
    skill: l3_visit_planning
    params:
      customer_id: "${input.customer_id}"
      houses: "${matches}"
    output: visit_plan

  - id: deliver_to_customer
    type: skill_call
    skill: l2_cross_channel_router
    params:
      message_type: report
      title: "为您推荐 ${matches.count} 套房源"
      attachments: ["${report.pdf_uri}"]
      buttons:
        - {text: "预约看房", action: "${visit_plan.confirm_url}"}
        - {text: "联系顾问", action: "transfer_to_agent"}
      recipients: { channels: ["${input.channel}"], targets: ["${input.customer_id}"] }

  - id: notify_agent
    type: skill_call
    skill: l2_cross_channel_router
    params:
      message_type: notify
      title: "新意向客户已生成报告，请跟进"
      recipients: { channels: [wecom], targets: ["agent_${portrait.assigned_agent}"] }
```

---

## 5. 多Agent协作场景（L4）

| 场景 | 参与Agent | 模式 |
|------|-----------|------|
| **客户全旅程** | 接待Agent + 销售Agent + 贷款Agent + 签约Agent + 物业Agent | 状态机+交接 |
| **资产管理** | 估值Agent + 出租Agent + 物业Agent + 财务Agent | 周期+并行 |
| **跨城置业** | 本地Agent + 目标城市Agent + 政策Agent | 协商+共识 |

---

## 6. 治理红线

1. **房源信息真实性**：禁止虚假房源/虚假报价（违反房地产管理条例）
2. **限购合规**：政策核查必须基于最新法规，结果可追溯
3. **客户隐私**：客户联系方式严格分级授权，禁止外泄
4. **不做投资建议**：AI不预测房价、不诱导投资决策
5. **广告合规**：营销文案必须避免"绝版"、"稳赚"等违规用语

---

## 7. 实施路线

| 阶段 | 周期 | 内容 |
|------|------|------|
| Phase 1 | 1-2月 | 房源连接器 + L1归一化/匹配 + L3客户接待 |
| Phase 2 | 3-4月 | 政策核查 + 估值 + L3跟进/报告 |
| Phase 3 | 5-6月 | 物业 + 商圈 + L4客户全旅程 |
