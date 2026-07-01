# 垂直行业蓝图：法律 (Legal)

**Industry Code**: `legal`
**版本**: v1.0
**状态**: 蓝图

---

## 1. 行业特征与约束

| 维度 | 特征 | 对Skill设计的影响 |
|------|------|-------------------|
| **文本密集** | 输入输出几乎全是法律文本 | 文档流水线是核心 |
| **准确性要求** | 极高（一字之差结果迥异） | 必须留出处引用、不可幻觉 |
| **保密性** | 律师-当事人特权（attorney-client privilege） | 严格隔离，按案件分仓 |
| **法规时效** | 法规会修订、判例会更新 | 知识库需版本化 + 时效标记 |
| **专业分工** | 公司法/诉讼/IP/合规/劳动 | Skill需按专业域组织 |
| **集成方** | 法律检索（北大法宝/威科/Westlaw）、案件管理系统、电子签 | L0连接器 |

---

## 2. 核心场景地图

| 场景 | 描述 | L2复用 | L3 SkillID |
|------|------|--------|-------------|
| 合同审查 | 合同→风险点+修改建议+对照标准模板 | document_pipeline + alert_engine | `l3_contract_review` |
| 合同起草 | 业务要点→合同初稿→条款对照 | taskflow + document_pipeline | `l3_contract_drafting` |
| 法律检索 | 自然语言→法条+判例+学术观点 | cross_channel | `l3_legal_search` |
| 案例分析 | 案情→相似判例+判决预测+论点 | document_pipeline + taskflow | `l3_case_analysis` |
| 尽职调查 | 目标公司→法律风险报告 | taskflow + document_pipeline | `l3_legal_due_diligence` |
| 合规审查 | 业务方案→法规符合性核查 | document_pipeline + alert_engine | `l3_compliance_review` |
| 诉讼文书生成 | 案情+依据→起诉状/答辩状/代理词 | document_pipeline | `l3_litigation_drafting` |
| 法务工单分流 | 业务咨询→自动分类+分配律师 | cross_channel | `l3_legal_intake` |
| 监管动态监测 | 法规新规→影响评估+合规通知 | alert_engine + cross_channel | `l3_regulation_watch` |
| 知识产权管理 | 商标/专利→申请/续展/侵权监测 | alert_engine | `l3_ip_management` |

---

## 3. L0/L1 行业专用Skill需求

### L0 连接器
- `l0_pkulaw_search` 北大法宝检索
- `l0_wkinfo_search` 威科先行检索
- `l0_court_publish` 中国裁判文书网（公开案例）
- `l0_credit_china` 信用中国（行政处罚信息）
- `l0_qichacha` 企查查/天眼查（企业工商）
- `l0_e_signature` 电子签（法大大/e签宝）
- `l0_case_management` 案件管理系统适配

### L1 基础能力
- `l1_legal_ner` 法律命名实体识别（主体/法条/案由/金额/日期/法院）
- `l1_law_citation_parse` 法条引用解析（"《民法典》第577条"→标准化引用）
- `l1_clause_classify` 条款分类（争议解决/保密/违约/不可抗力/...）
- `l1_clause_compare` 条款对照（与标准模板/历史合同对比）
- `l1_risk_grading` 法律风险分级（重大/重要/一般/提示）
- `l1_legal_summary` 法律文书摘要（判决/合同/法规）
- `l1_judgment_features` 判决要素提取（裁判要点/争议焦点/裁判依据）

---

## 4. 标杆场景：合同审查（详设）

### 4.1 业务价值
传统合同审查 1 份 1-3 小时，AI 辅助审查 5-15 分钟，律师只需复核 AI 标注的高风险点。

### 4.2 流程设计

```yaml
flow_id: contract_review_v1
input_schema:
  - {name: contract_doc, type: file, required: true}
  - {name: contract_type, type: enum, values: [purchase, service, lease, employment, nda, ...], required: true}
  - {name: party_role, type: enum, values: [甲方, 乙方], required: true}
  - {name: industry, type: string, required: false}

steps:
  - id: parse_contract
    type: skill_call
    skill: l2_unified_document_pipeline
    params:
      pipeline_id: legal_contract_v1
      documents: [{ source: { type: upload, ref: "${input.contract_doc}" } }]
    output: parsed

  - id: classify_clauses
    type: skill_call
    skill: l1_clause_classify
    params: { contract: "${parsed}" }
    output: clauses

  - id: parallel_checks
    type: parallel
    branches:
      - id: missing_clauses_check
        skill: l1_missing_clauses
        params:
          contract_type: "${input.contract_type}"
          party_role: "${input.party_role}"
          actual_clauses: "${clauses}"

      - id: risk_clauses_check
        skill: l1_risk_clauses_detect    # 不平等条款/对己方不利

      - id: compliance_check
        skill: l1_legal_compliance_check
        params: { industry: "${input.industry}" }

      - id: template_compare
        skill: l1_clause_compare
        params:
          template_ref: "templates/${input.contract_type}_${input.party_role}.docx"
    aggregate: collect_all
    output: findings

  - id: generate_review_report
    type: skill_call
    skill: l1_legal_review_report
    params:
      parsed: "${parsed}"
      findings: "${findings}"
    output: report

  - id: high_risk_alert
    type: branch
    cases:
      - when: "${report.has_high_risk}"
        next: alert_lawyer
      - default:
        next: deliver_report

  - id: alert_lawyer
    type: skill_call
    skill: l2_alert_engine
    params:
      severity: high
      title: "合同存在重大风险条款，需律师确认"
    next: deliver_report

  - id: deliver_report
    type: skill_call
    skill: l2_cross_channel_router
    params:
      message_type: report
      attachments: ["${report.docx_uri}"]
      recipients: { channels: [feishu], targets: ["${input.requester}"] }
```

### 4.3 输出报告示例（结构化）
```yaml
contract_no: "HT-2026-0001"
overall_risk: medium
findings:
  - clause_no: "第8.2条"
    issue: "违约金过高"
    risk_level: high
    explanation: "本条约定违约金30%，超过《民法典》第585条..."
    citations: ["《民法典》第585条", "(2023)京01民终1234号"]
    suggested_revision: "建议改为合同金额的5%-15%"
  - ...
checklist:
  - {item: "争议解决条款", present: true, sufficient: true}
  - {item: "保密条款", present: false, severity: warning}
  - ...
```

---

## 5. 多Agent协作场景（L4）

| 场景 | 参与Agent | 模式 |
|------|-----------|------|
| **复杂合同协同审查** | 公司法Agent + IP-Agent + 劳动法Agent + 主审律师 | 并行+聚合 |
| **跨境合规** | 中国法Agent + 海外法Agent + 翻译Agent | 流水线 |
| **诉讼协作** | 调研Agent + 起草Agent + 审核Agent + 客户对接Agent | 流水线+迭代 |

---

## 6. 治理红线

1. **不出具法律意见**：AI不能替代律师签字，最终意见必须律师审核
2. **必须出处可追溯**：每条结论必须给出法条/判例引用
3. **拒绝幻觉**：找不到依据宁可说"无法判断"，不得编造
4. **案件隔离**：每个案件独立知识库分区，不可跨案件检索
5. **法规时效**：引用的法条必须标注是否现行有效

---

## 7. 实施路线

| 阶段 | 周期 | 内容 |
|------|------|------|
| Phase 1 | 1-2月 | 法律检索连接器 + L1法律NER/引用解析 + 1个L3（合同审查） |
| Phase 2 | 3-4月 | 补全L1（风险分级/条款对照） + 3个L3（起草/检索/案例分析） |
| Phase 3 | 5-6月 | 尽调 + 合规 + 1个L4（复杂合同协同审查） |
