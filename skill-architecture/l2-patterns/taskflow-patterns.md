# L2 模式蓝图：TaskFlow 任务编排模式 (TaskFlow Patterns)

**Skill ID**: `l2_taskflow_patterns`
**层级**: L2 组合模式（元模式 / 编排框架）
**能力域**: C03 数据处理 + C09 集成连接 + C07 协作通知（贯穿）
**版本**: v1.0
**状态**: 蓝图

---

## 1. 设计目标

把"多个 Skill 串成一个工单"的编排能力沉淀为**统一的 TaskFlow 引擎**，让所有 L3 场景 Skill 不再各自实现状态机、不再硬编码"先做A再做B"。

**为什么需要它**：
- 五方清单中 L3 场景 Skill 普遍把流程逻辑写死在代码中（switch-case / 一连串 if）
- 同一类工作流模式在多个场景重复出现（审批、流水线、扇出聚合、分支选择）
- 需要可视化、可观察、可中断、可补偿的统一执行底座

---

## 2. 五种核心模式

> 90% 的业务场景能用以下五种模式或其组合表达。

### 2.1 Sequential 顺序流（最常用）
```
Step1 ──▶ Step2 ──▶ Step3 ──▶ End
```
**适用**：审批流、文档流水线、报告生成

### 2.2 Parallel 并行扇出 + Aggregate 聚合
```
        ┌──▶ Step2a ──┐
Step1 ──┼──▶ Step2b ──┼──▶ Aggregate ──▶ End
        └──▶ Step2c ──┘
```
**适用**：尽调（财务/法律/业务并行调查）、多源数据采集、多Agent协作

### 2.3 Branch 条件分支
```
            ┌── if amount > 100w ──▶ 总部审批 ──┐
Step1 ──▶ ──┼── if amount > 10w  ──▶ 部门审批 ──┼──▶ End
            └── else              ──▶ 自动通过 ──┘
```
**适用**：审批分级、风险分级处置、客户分群营销

### 2.4 Loop 循环重试
```
Step1 ──▶ Step2 ──▶ ok? ─yes─▶ End
              ▲             │
              └──── no ─────┘ (最多N次, 退避)
```
**适用**：调用重试、轮询等待、迭代优化

### 2.5 Saga 补偿事务
```
Step1 ──▶ Step2 ──▶ Step3 ──✗
   ▲          ▲          │
   │          │          ▼ 失败
   │          └── compensate2
   └── compensate1
```
**适用**：跨系统事务（订单+库存+支付）、需要回滚的业务流程

---

## 3. 统一编排DSL

```yaml
# flows/contract_signing_v1.yaml
flow_id: contract_signing_v1
name: "合同签署流程"
version: 1
input_schema:
  - {name: contract_doc_token, type: string, required: true}
  - {name: counterparty, type: string, required: true}
  - {name: amount, type: decimal, required: true}

steps:
  # 1. 顺序：先解析合同
  - id: parse_contract
    type: skill_call
    skill: l2_unified_document_pipeline
    params:
      pipeline_id: contract_review_v1
      documents: [{ source: { type: feishu_drive, ref: "${input.contract_doc_token}" } }]
    output: parsed
    on_error: { strategy: retry, max: 2, backoff: 5s }

  # 2. 分支：根据金额走不同审批
  - id: route_approval
    type: branch
    cases:
      - when: "${parsed.amount} > 1000000"
        next: approve_hq
      - when: "${parsed.amount} > 100000"
        next: approve_dept
      - default:
        next: auto_approve

  # 3a. 总部审批（并行：法务 + 财务）
  - id: approve_hq
    type: parallel
    branches:
      - id: legal_review
        skill: l1_legal_review
      - id: finance_review
        skill: l1_finance_review
    aggregate: all_pass             # all_pass | any_pass | first | custom
    next: notify_signing

  # 3b. 部门审批
  - id: approve_dept
    type: skill_call
    skill: l2_approval_workflow
    next: notify_signing

  # 3c. 自动通过
  - id: auto_approve
    type: noop
    next: notify_signing

  # 4. 通知签署
  - id: notify_signing
    type: skill_call
    skill: l2_cross_channel_router
    params:
      message_type: notify
      title: "合同进入签署阶段"
      recipients: { channels: [feishu], targets: ["${input.counterparty}"] }

compensations:                       # Saga 补偿（可选）
  parse_contract: l1_cleanup_temp_files

triggers:                            # 触发器（可选，多种触发方式共存）
  - type: api
  - type: feishu_event
    event: contract_uploaded
  - type: cron
    schedule: "0 9 * * 1"            # 每周一9点

observability:
  trace: true
  store_intermediate: true           # 保留中间产物（用于Debug/审计）
  metrics: ["duration", "success_rate", "step_durations"]

sla:
  total_timeout: 24h
  alert_on_timeout: true
```

---

## 4. 引擎核心能力

| 能力 | 说明 |
|------|------|
| **状态持久化** | 每步状态写入 DB，重启可恢复 |
| **断点续传** | 任意步骤失败可从断点重试，不重做已完成步骤 |
| **超时控制** | 单步超时 / 整体超时，触发告警或补偿 |
| **可观测性** | 每个 flow 实例有唯一 trace_id，可视化执行轨迹 |
| **人工介入** | 任意步骤可设置 `human_in_loop: true`，IM按钮决策 |
| **事件驱动** | 步骤完成发事件，其他 flow 可订阅 |
| **版本管理** | flow 定义版本化，运行中的实例不受新版本影响 |
| **权限控制** | 每个 flow 限定可调用的 Skill 集合（白名单） |

---

## 5. 与其他 L2 的关系

```
┌─────────────────────────────────────────────────────────────┐
│              L2 taskflow_patterns (编排引擎)                │
│                                                             │
│         可作为节点调用以下 L2/L1：                            │
│   ┌──────────────────────┬─────────────────────┐            │
│   ▼                      ▼                     ▼            │
│ l2_unified_document_   l2_alert_engine     l2_cross_        │
│ pipeline                                    channel_router  │
└─────────────────────────────────────────────────────────────┘

L3 场景 Skill = 一组 TaskFlow + 业务上下文
L4 多Agent  = 多个 TaskFlow 通过 SecureBridge 协作
```

L3/L4 全部基于 TaskFlow 实现，避免每个场景都自己写状态机。

---

## 6. Human-in-the-loop 模式

```yaml
- id: manager_approval
  type: human_decision
  prompt:
    channel: feishu
    template: |
      合同 ${parsed.contract_no} 待您审批
      金额：${parsed.amount}
      ✅ 通过  ❌ 驳回  📝 需补充
    timeout: 4h
    on_timeout: { action: escalate, to: "${approver.manager}" }
  output: decision        # decision.choice = "approve" | "reject" | "supplement"
  next:
    - when: "${decision.choice} == 'approve'"
      next: notify_signing
    - when: "${decision.choice} == 'reject'"
      next: notify_rejection
    - default:
      next: request_supplement
```

---

## 7. 治理要求

- 所有 L3 场景 Skill 必须基于 TaskFlow 实现，不再自己写流程控制
- `flows/*.yaml` 走 PR 评审，触发 lint（DSL语法 + Skill引用合法性）
- 高风险操作（资金转账、删除数据）必须设置 `human_in_loop`
- 生产环境运行的 flow 必须开 `trace=true`，30天内可回查

---

## 8. 已规划 TaskFlow 模板（首批 8 个）

1. `contract_signing_v1` 合同签署
2. `expense_reimbursement_v1` 报销审批
3. `customer_onboarding_v1` 客户入网
4. `due_diligence_v1` 企业尽调
5. `marketing_campaign_v1` 营销活动
6. `incident_response_v1` 故障响应
7. `report_generation_v1` 报告生成
8. `data_quality_check_v1` 数据质量稽核

每个模板对应一个 L3 场景 Skill，由 L3 Skill 注入业务参数后执行。
