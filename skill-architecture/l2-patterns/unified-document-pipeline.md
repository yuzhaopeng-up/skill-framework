# L2 模式蓝图：统一文档流水线 (Unified Document Pipeline)

**Skill ID**: `l2_unified_document_pipeline`
**层级**: L2 组合模式
**能力域**: C04 文档处理 + C03 数据处理 + C09 集成连接
**版本**: v1.0
**状态**: 蓝图

---

## 1. 设计目标

将"文档进、结构化数据出"的全部场景（合同审核、报销单审核、立项审批、招投标分析、客户尽调、报告解析）统一抽象为**一条可配置的文档流水线**，避免每个业务方各自重新实现 OCR + 解析 + 校验 + 入库逻辑。

**解决的痛点**：
- AlphaAgent + DeltaAgent 五方清单中至少 18 个 Skill 在重复造文档解析轮子
- 文档来源各异（PDF/Word/Excel/扫描件/拍照），下游 Skill 不应感知格式差异
- 解析规则分散在各 Skill 内部，无法治理

---

## 2. 流水线七阶段

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 1. 接入  │──▶│ 2. 预处理 │──▶│ 3. 识别  │──▶│ 4. 提取  │──▶│ 5. 校验  │──▶│ 6. 入库  │──▶│ 7. 通知  │
│ Ingest   │   │ Preprocess│   │ Recognize│   │ Extract  │   │ Validate │   │ Persist  │   │ Notify   │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

| 阶段 | 责任 | 复用 L0/L1 Skill |
|------|------|------------------|
| 1. Ingest | 文档接入：飞书/企微/邮件/网盘/本地 | `l0_file_fetch`, `l0_imap_pull`, `l0_feishu_drive_download` |
| 2. Preprocess | 格式归一化：扫描件转 PDF、PDF 切页、Excel 转 CSV、压缩包解压 | `l1_format_normalize`, `l1_pdf_split`, `l1_archive_extract` |
| 3. Recognize | OCR / 版面分析 / 表格还原 | `l1_ocr_paddle`, `l1_layout_detect`, `l1_table_recover` |
| 4. Extract | 字段提取：规则 / LLM / 模板 | `l1_llm_field_extract`, `l1_template_match`, `l1_regex_extract` |
| 5. Validate | 业务校验：必填、格式、跨字段、外部对账 | `l1_schema_validate`, `l1_cross_field_check`, `l1_external_lookup` |
| 6. Persist | 落库：飞书多维表格 / 企微表格 / DB / Excel | `l0_bitable_write`, `l0_db_insert`, `l0_excel_append` |
| 7. Notify | 结果通知：调用 L2 跨渠道路由器 | `l2_cross_channel_router` |

---

## 3. 统一输入输出契约

### 3.1 输入 (PipelineRequest)

```yaml
pipeline_id: contract_review_v1     # 流水线模板ID
documents:                          # 待处理文档（1..N）
  - source:
      type: feishu_drive            # feishu_drive | wecom_msg | email | local | url
      ref: "doc_token_xxxx"
    hint:
      doc_type: contract            # contract | invoice | proposal | report | unknown
      sensitivity: confidential     # public | internal | confidential | secret
context:                            # 业务上下文
  initiator: "ou_xxxx"
  org: "南昌分公司"
  ticket_id: "T20260620-001"
options:
  ocr_engine: paddle                # paddle | tesseract | aliyun | tencent
  llm_provider: doubao              # doubao | kimi | gpt-4o | local
  validate_strictness: medium       # low | medium | high
  output_format: bitable            # bitable | excel | json | webhook
```

### 3.2 输出 (PipelineResult)

```yaml
status: success                     # success | partial | failed
documents:
  - doc_id: "d_001"
    source_ref: "doc_token_xxxx"
    extracted:                      # 字段提取结果（schema由模板定义）
      contract_no: "HT-2026-0620-001"
      party_a: "Operator-ARegion-A分公司"
      party_b: "XX科技有限公司"
      amount: 1280000.00
      sign_date: "2026-06-15"
    validations:                    # 校验结果
      - field: amount
        rule: "single_amount_limit"
        passed: false
        reason: "单笔金额超过 100 万需走特批流程"
        severity: warning
    persistence:
      target: "bitable://app_xxx/tbl_yyy"
      record_id: "recXYZ"
    artifacts:                      # 中间产物（可审计）
      ocr_text_uri: "..."
      preview_pdf_uri: "..."
metrics:
  total_pages: 24
  ocr_confidence: 0.94
  llm_tokens: 18230
  total_duration_ms: 14200
trace_id: "tr_20260620_xxxx"        # 全链路追踪ID
```

---

## 4. 模板机制（重点）

不同业务通过 **DocTemplate** 配置文件接入，无需写代码：

```yaml
# templates/contract_review_v1.yaml
template_id: contract_review_v1
doc_type: contract
schema:
  - {name: contract_no, type: string, required: true, regex: "^HT-\\d{4}-.*"}
  - {name: party_a, type: string, required: true}
  - {name: party_b, type: string, required: true}
  - {name: amount, type: decimal, required: true, min: 0}
  - {name: sign_date, type: date, required: true}
  - {name: term_months, type: int, required: false}
extract_strategy:
  primary: llm                      # 优先LLM提取
  fallback: regex                   # 失败回落到正则
  llm_prompt_ref: prompts/contract_extract.md
validations:
  - rule: single_amount_limit
    expr: "amount <= 1000000"
    severity: warning
  - rule: party_a_must_be_telecom
    expr: "party_a contains 'Operator-A'"
    severity: error
persistence:
  target_type: bitable
  app_token: "${BITABLE_APP_CONTRACT}"
  table_id: "${BITABLE_TBL_CONTRACT}"
notify:
  on_warning: ["ou_legal_team"]
  on_error: ["ou_legal_team", "ou_initiator"]
  channel: feishu
```

**已规划模板**（首批 6 个）：
1. `contract_review_v1` 合同审核
2. `expense_invoice_v1` 报销发票
3. `project_proposal_v1` 项目立项
4. `bid_document_v1` 招投标文件
5. `due_diligence_report_v1` 尽调报告
6. `customer_kyc_v1` 客户KYC材料

---

## 5. 容错与降级

| 异常 | 降级策略 |
|------|----------|
| OCR 引擎不可用 | 切换到备用引擎（aliyun → tencent → paddle 本地） |
| LLM 提取超时 | 回落到正则/模板匹配 |
| 字段缺失 | 标记 `partial`，写入飞书表格的"待人工补全"分类 |
| 外部对账接口失败 | 跳过该校验项，记录 warning，不阻塞流水线 |
| 入库失败 | 落到本地缓存 + 重试队列（最多3次，指数退避） |

---

## 6. 调用方式

### 6.1 同步调用（小文档）
```python
from skills.l2 import unified_document_pipeline as udp

result = udp.run({
    "pipeline_id": "contract_review_v1",
    "documents": [{"source": {"type": "feishu_drive", "ref": doc_token}}],
    "context": {"initiator": user_id, "org": "南昌分公司"},
})
```

### 6.2 异步调用（大文档/批量）
```python
job_id = udp.submit({...})
status = udp.poll(job_id)           # queued | running | done | failed
result = udp.get_result(job_id)
```

### 6.3 触发器调用（IM 消息）
```yaml
# 当用户在飞书发送文件并 @bot
trigger:
  channel: feishu
  event: file_uploaded_with_mention
action:
  skill: l2_unified_document_pipeline
  pipeline_id: auto_detect          # 根据文件名/内容自动选模板
```

---

## 7. 性能与配额

| 指标 | 目标 | 实测基线（参考） |
|------|------|------------------|
| 单页 PDF 端到端延迟 | < 8 s | 5.2 s（paddle + doubao） |
| 10 页合同延迟 | < 30 s | 21 s |
| 字段提取准确率 | > 92% | 94.1%（contract模板） |
| 并发能力 | 50 文档/分钟 | 依赖 LLM 配额 |

---

## 8. 与其他 L2 模式的协作

```
[L2 unified_document_pipeline]
        │
        ├── 触发 ──▶ [L2 alert_engine]            # 高风险文档触发告警
        ├── 写入 ──▶ [L2 cross_channel_router]    # 结果通知多渠道
        ├── 编排 ──◀ [L2 taskflow_patterns]       # 作为节点嵌入任务编排
        └── 记录 ──▶ [L0 audit_log]               # 全链路审计
```

---

## 9. 治理要求

- 所有文档处理必须留存 `trace_id` 和原始件URI（满足审计）
- 敏感级文档（confidential+）必须走脱敏流水线 → 输出前去除身份证/账号
- 模板变更需走审批：`templates/*.yaml` 受保护分支管控
- 月度抽样 5% 文档做人工复核，准确率 < 90% 触发模板优化
