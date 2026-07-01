# L2 模式蓝图：告警引擎 (Alert Engine)

**Skill ID**: `l2_alert_engine`
**层级**: L2 组合模式
**能力域**: C03 数据处理 + C09 集成连接 + C07 协作通知
**版本**: v1.0
**状态**: 蓝图

---

## 1. 设计目标

将"监测 → 评估 → 告警 → 处置 → 闭环"这条共性链路抽象为**统一告警引擎**，业务方只需提供"指标 + 阈值 + 处置策略"，无需各自重复造监控/通知系统。

**典型业务场景**：
- 风控监测（异常交易、合规告警）
- 数据质量监测（指标偏移、数据延迟）
- 系统健康监测（接口超时、错误率）
- 业务KPI监测（合同到期、客户流失风险）
- 设备/网络监测（telecom故障、设备宕机）

**避免的重复造轮子**：
五方清单中至少 14 个 Skill 在各自实现告警逻辑（包括去重、抑制、升级、值班路由），统一引擎可一次解决。

---

## 2. 核心架构

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Alert Engine                                 │
│                                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│  │ Collector│──▶│ Evaluator│──▶│ Suppressor│──▶│ Dispatcher│         │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘           │
│       ▲             │              │              │                  │
│       │             ▼              ▼              ▼                  │
│   data sources   rule store   alert state    channel router          │
│  (DB/API/log)    (yaml/UI)    (redis/db)     (l2_cross_channel)      │
│                                                                      │
│  ┌──────────────────── Escalator (升级) ──────────────────────┐       │
│  │ Acknowledger (认领) │ Closer (闭环) │ Postmortem (复盘)   │       │
│  └────────────────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. 五个核心组件

### 3.1 Collector 数据采集
- **拉模式**：定时调用 SQL / API / Webhook
- **推模式**：接收上游 push（Kafka/Webhook/MQ）
- **复用**：`l0_db_query`, `l0_http_get`, `l0_log_tail`

### 3.2 Evaluator 规则评估
支持 4 类规则：
| 规则类型 | 表达式示例 | 适用场景 |
|----------|------------|----------|
| 阈值 | `error_rate > 0.05` | KPI、错误率 |
| 同比/环比 | `today vs yesterday > 30%` | 业务波动 |
| 缺失 | `last_seen > 5min` | 心跳/数据延迟 |
| 复合 | `(amount > 100w) AND (counterparty.risk > 0.7)` | 风控复合规则 |

### 3.3 Suppressor 告警抑制
防止告警风暴的三道闸：
1. **去重**：同一指纹 N 分钟内只发一次
2. **依赖抑制**：上游告警触发时，下游不再独立通知
3. **静默期**：维护窗口/夜间静默配置

### 3.4 Dispatcher 路由分发
**调用 `l2_cross_channel_router` 落地多渠道分发**，自身专注于：
- 值班表查询（按时段、按团队）
- 升级路径（L1 → L2 → L3，每级超时未响应自动升级）
- 渠道偏好（紧急走电话/短信，一般走IM）

### 3.5 Escalator 升级 + Acknowledger 认领 + Closer 闭环
- 告警发出后等待"认领"（IM按钮 / 命令 / API）
- 超时未认领自动升级到上级
- 闭环要求填写"原因 + 处置 + 复盘"，写入告警库

---

## 4. 统一规则配置

```yaml
# rules/risk_anomaly_transaction.yaml
rule_id: risk_anomaly_transaction_v1
name: "异常大额交易告警"
enabled: true
severity: high                       # info | low | medium | high | critical

collect:
  type: sql
  source: risk_db
  query: |
    SELECT txn_id, amount, counterparty, risk_score
    FROM transactions
    WHERE created_at > now() - interval '5 minutes'
      AND status = 'pending'
  schedule: "*/5 * * * *"           # cron 表达式

evaluate:
  expr: "row.amount > 1000000 AND row.risk_score > 0.7"
  group_by: ["counterparty"]
  fingerprint: "{rule_id}:{counterparty}"

suppress:
  dedup_window: 10m
  silence_periods: ["00:00-06:00 weekdays"]
  depends_on: []

dispatch:
  on_call_team: risk_team
  escalation:
    - {after: 0m, level: L1, contact: ["@duty_l1"]}
    - {after: 10m, level: L2, contact: ["@risk_manager"]}
    - {after: 30m, level: L3, contact: ["@cro", "phone:+8613800000000"]}
  channels: [feishu, wecom, sms_for_critical]
  template: templates/alert_risk_zh.md

close:
  require_fields: ["root_cause", "action_taken", "lessons_learned"]
  auto_close_after: 24h
```

---

## 5. 告警生命周期

```
firing ──▶ acknowledged ──▶ investigating ──▶ resolved ──▶ closed
   │              │                                            ▲
   │              └─ timeout ──▶ escalated ─────────────────────┘
   │
   └─ suppressed (去重/静默/依赖抑制)
```

每次状态变更写入 `alert_events` 表，支持完整审计回溯。

---

## 6. 输出消息标准

调用 `l2_cross_channel_router` 的统一消息：

```yaml
message_type: alert
priority: high
title: "[L1风控告警] 异常大额交易"
content: |
  规则：异常大额交易告警
  时间：2026-06-20 14:32:18
  对手方：XX科技有限公司
  金额：1,280,000.00 元
  风险评分：0.83
  
  请在 10 分钟内认领并初步处置。
metadata:
  alert_id: "alert_20260620_001"
  rule_id: risk_anomaly_transaction_v1
  fingerprint: "risk_anomaly_transaction_v1:XX科技"
  ack_url: "https://.../ack?alert_id=alert_20260620_001"
  details_url: "https://.../alert/alert_20260620_001"
recipients:
  channels: [feishu, wecom]
  targets: ["@duty_l1"]
schedule:
  send_at: now
  expire_at: now+10m
```

---

## 7. 治理与SLA

| 指标 | 目标 |
|------|------|
| 告警发出延迟（采集 → 收到通知） | P95 < 30s |
| 误报率 | < 5% |
| 漏报率 | < 1%（基于回测） |
| MTTA（平均认领时间） | high级 < 10min |
| MTTR（平均处置时间） | high级 < 1h |
| 告警闭环率 | > 98% |

---

## 8. 与其他 L2 的协作

| 上游 | 关系 |
|------|------|
| `l2_unified_document_pipeline` | 文档审核发现高风险 → 告警 |
| `l2_cross_channel_router` | 用作下游分发 |
| `l2_taskflow_patterns` | 告警可作为 taskflow 触发器 |
| `l4_multi_agent_*` | 多Agent场景中风控Agent调用告警引擎 |

---

## 9. 已规划告警规则集（首批）

1. **金融风控**：异常交易、可疑账户、超额贷款、合规偏离
2. **数据质量**：报表延迟、指标缺失、跨表对账偏离
3. **系统健康**：API错误率、超时率、队列堆积
4. **业务KPI**：合同到期、客户流失、转化率下降
5. **telecom运维**：基站告警、链路中断、投诉量突增
6. **安全合规**：异常登录、权限变更、敏感数据访问
