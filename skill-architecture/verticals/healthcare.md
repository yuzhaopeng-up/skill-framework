# 垂直行业蓝图：医疗 (Healthcare)

**Industry Code**: `healthcare`
**版本**: v1.0
**状态**: 蓝图（设计层，不含实现）

---

## 1. 行业特征与约束

| 维度 | 特征 | 对Skill设计的影响 |
|------|------|-------------------|
| **数据敏感性** | 极高（PHI/PII，受HIPAA/《个人信息保护法》《医疗数据安全管理办法》约束） | 默认脱敏；最小授权；全链路审计 |
| **数据格式** | 结构化（HL7/FHIR）+ 非结构化（病历/影像/检验报告） | 必备DICOM/PDF/影像识别能力 |
| **业务实时性** | 急诊/ICU高实时；门诊/管理低实时 | Skill按延迟分级 |
| **错误代价** | 极高（误诊/漏诊） | 必须有"AI建议+医生确认"模式，禁止全自动决策 |
| **合规要求** | 医疗器械软件可能受NMPA监管 | 算法决策需可解释，留存依据 |
| **集成方** | HIS/LIS/PACS/EMR/CDR/区域卫生平台 | L0连接器矩阵需扩展 |

---

## 2. 核心场景地图

| 场景 | 描述 | L2复用 | L3 SkillID（建议） |
|------|------|--------|---------------------|
| 智能预问诊 | 患者就诊前对话采集 → 结构化主诉 | document_pipeline + cross_channel | `l3_pre_consultation` |
| 病历智能生成 | 医生口述 → SOAP结构化病历草稿 | document_pipeline | `l3_emr_drafting` |
| 检验报告解读 | LIS报告→患者可读解读 + 异常标注 | document_pipeline | `l3_lab_report_explainer` |
| 用药安全核查 | 处方→相互作用/剂量/过敏检查 | alert_engine | `l3_medication_safety` |
| 影像辅助诊断（建议层） | DICOM→AI建议→医生复核 | document_pipeline + taskflow | `l3_imaging_assist` |
| 临床路径辅助 | 病种→标准路径→偏离告警 | taskflow + alert_engine | `l3_clinical_pathway` |
| 患者随访 | 出院/手术后定期随访问答 | cross_channel + taskflow | `l3_follow_up` |
| 医保结算辅助 | 病案首页→DRG/DIP分组建议 | document_pipeline | `l3_drg_dip_assist` |
| 药械合规检查 | 文献/产品资料→法规符合性核查 | document_pipeline + alert_engine | `l3_compliance_check` |
| 慢病管理 | 患者数据→风险评分→个性化方案 | taskflow + alert_engine | `l3_chronic_management` |

---

## 3. L0/L1 行业专用Skill需求

### L0 连接器
- `l0_hl7_v2_parser` HL7 v2 消息解析
- `l0_fhir_client` FHIR REST 调用
- `l0_dicom_reader` DICOM影像读取（pydicom）
- `l0_his_adapter` HIS系统适配（国内主流：东软/卫宁/东华）
- `l0_pacs_query` PACS影像查询
- `l0_drug_database` 药品数据库（说明书/相互作用/医保目录）

### L1 基础能力
- `l1_phi_deidentify` PHI脱敏（姓名/身份证/电话/住址/病历号）
- `l1_medical_ner` 医学命名实体识别（症状/疾病/药品/检查/部位）
- `l1_icd_coding` ICD-10/ICD-11 编码建议
- `l1_drug_interaction_check` 药物相互作用核查
- `l1_dosage_check` 剂量合理性核查（按年龄/体重/肝肾功能）
- `l1_clinical_term_normalize` 临床术语标准化（SNOMED-CT / 中文医学知识图谱）

---

## 4. 标杆场景：智能预问诊（详设）

### 4.1 业务价值
门诊医生平均接诊时间 5-8 分钟，预问诊可把"采集主诉"前置到候诊环节，把医生时间用于诊断与决策。

### 4.2 流程设计（基于 taskflow_patterns）

```yaml
flow_id: pre_consultation_v1
input_schema:
  - {name: patient_id, type: string, required: true}
  - {name: department, type: string, required: true}
  - {name: appointment_id, type: string, required: true}

steps:
  - id: load_patient_history
    type: skill_call
    skill: l1_patient_history_load
    output: history

  - id: choose_question_set
    type: skill_call
    skill: l1_question_set_select       # 按科室+主诉选题
    params: { department: "${input.department}" }
    output: questions

  - id: dialogue_loop
    type: human_decision                # 与患者多轮对话
    prompt:
      channel: wecom_h5                  # H5对话框（医院公众号嵌入）
      template: dynamic_question_flow
      timeout: 30m
    output: answers

  - id: structure_chief_complaint
    type: skill_call
    skill: l1_medical_ner
    params: { text: "${answers.raw}" }
    output: structured

  - id: phi_deidentify
    type: skill_call
    skill: l1_phi_deidentify
    params: { data: "${structured}" }
    output: deidentified

  - id: write_to_emr
    type: skill_call
    skill: l0_his_adapter
    params:
      action: create_pre_visit_note
      patient_id: "${input.patient_id}"
      content: "${deidentified}"

  - id: notify_doctor
    type: skill_call
    skill: l2_cross_channel_router
    params:
      message_type: notify
      title: "预问诊已完成（${input.appointment_id}）"
      recipients: { channels: [his_inbox, wecom], targets: ["doctor_${input.department}"] }
```

### 4.3 安全与合规
- 全程在医院内网/专网完成（LLM私有化部署）
- 患者每条回答先脱敏再入库
- 患者可随时退出，已采集数据可一键删除
- 留存"AI辅助生成"标识，医生确认后才入正式病历

---

## 5. 多Agent协作场景（L4建议）

| 场景 | 参与Agent | 模式 |
|------|-----------|------|
| **MDT会诊辅助** | 各科室专科Agent + 主持Agent + 记录Agent | 轮询发言 + 共识 |
| **影像-病理-临床联诊** | 影像Agent + 病理Agent + 临床Agent + 审核医生 | 并行 + 聚合 + 人审 |
| **慢病多团队管理** | 医生Agent + 营养师Agent + 康复师Agent + 患者Agent | 状态机 + 周期触发 |

---

## 6. 治理红线

1. **不得做最终诊断决策**：AI仅出"建议"，医生确认后才生效
2. **可解释性**：每条建议必须留存依据（文献/规则/相似病例）
3. **数据本地化**：医疗数据不出院、不上云（除非合规云）
4. **审计**：每次AI调用记录 prompt + response + 用户/患者ID
5. **算法版本管理**：算法/模型变更需备案，可回滚

---

## 7. 实施路线（建议）

| 阶段 | 周期 | 内容 |
|------|------|------|
| Phase 1 | 1-2月 | L0连接器 + L1脱敏/NER + 1个L3场景（预问诊或检验解读） |
| Phase 2 | 3-4月 | 补全L1医疗能力 + 3个L3场景（病历/用药/随访） |
| Phase 3 | 5-6月 | 影像辅助 + 临床路径 + 1个L4多Agent场景（MDT） |
| Phase 4 | 持续 | 合规认证 + 真实院内试点 + 效果评估 |
