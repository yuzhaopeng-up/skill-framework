# IM 渠道接口标准 v1.0

**文档ID**: `IM-CHANNEL-INTERFACE-SPEC-v1.0`
**适用范围**: 所有需要发送/接收消息的Skill（L0/L1/L2/L3/L4）
**版本**: v1.0
**状态**: 强制规范 (MUST)
**关键词遵循**: RFC 2119（MUST/SHOULD/MAY）

---

## 1. 目的

统一EnterpriseAI集群所有节点（AlphaAgent / BetaAgent / GammaAgent / DeltaAgent / EpsilonAgent / TeleAgent）发送和接收 IM 消息的接口标准，让上层 Skill **不再感知具体渠道**（飞书/企微/微信/钉钉/Discord/Slack/Telegram 等），所有渠道差异由 L0 适配器吸收。

## 2. 核心原则

1. **统一消息模型**：所有渠道共享一套 `Message` 数据结构
2. **能力声明**：每个渠道明确声明自己支持/不支持哪些能力（cards/buttons/files/voice等）
3. **优雅降级**：上层使用富格式时，渠道不支持则自动降级（例：卡片 → 纯文本+链接）
4. **入站/出站对称**：消息发送（outbound）与接收（inbound）使用同一个数据模型
5. **可观测**：每条消息有 `message_id` + `trace_id` + `idempotency_key`

---

## 3. 已纳入渠道矩阵（v1.0）

| 渠道 | 渠道码 | L0 适配器 SkillID | 主要场景 |
|------|--------|-------------------|----------|
| 飞书 Lark | `feishu` | `l0_feishu_im_adapter` | 内部协作 |
| 企业微信 | `wecom` | `l0_wecom_im_adapter` | 客户/员工触达 |
| 个人微信 | `weixin` | `l0_weixin_im_adapter` | 个人触达（合规边界严格） |
| 钉钉 | `dingtalk` | `l0_dingtalk_im_adapter` | 企业协作（备选） |
| Discord | `discord` | `l0_discord_im_adapter` | 海外/社区 |
| Slack | `slack` | `l0_slack_im_adapter` | 海外企业 |
| Telegram | `telegram` | `l0_telegram_im_adapter` | 海外公开 |
| 短信 | `sms` | `l0_sms_im_adapter` | 紧急通知 |
| 邮件 | `email` | `l0_email_im_adapter` | 正式通知/报告 |

> 新增渠道时**必须**实现本规范定义的所有 MUST 接口；MAY 接口按实际能力实现。

---

## 4. 统一消息模型

### 4.1 出站消息 (OutboundMessage) — MUST

```yaml
# 必填字段
message_id: "msg_20260620_xxxx"      # ULID/UUID，全局唯一
trace_id: "tr_xxxx"                  # 关联调用链
idempotency_key: "..."               # 用于幂等去重，相同key SHOULD 不重复发送
created_at: "2026-06-20T14:32:18+08:00"
sender:
  skill_id: "l3_smart_reception"     # 谁发的（Skill ID）
  agent: "BetaAgent"                    # 哪个节点

message_type: text                   # 见 §4.3
priority: normal                     # critical | high | normal | low
content:
  # 见 §4.3 各类型的schema

recipients:
  channel: feishu                    # 单渠道（routing 由上层 cross_channel_router 决定）
  targets:                           # 收件人，至少1个
    - { type: user, id: "ou_xxxx" }
    - { type: group, id: "oc_xxxx", thread_id: "tid_yyy" }
    - { type: chat, id: "chat_xxx" }

# 可选字段
schedule:
  send_at: "now"                     # now | ISO8601 | "+5m"
  expire_at: "2026-06-20T15:00:00"   # 过期不发

reply_to: "msg_yyyy"                 # 回复某条消息（如渠道支持）
metadata:                            # 透传业务上下文
  business_id: "..."
  source: "..."
```

### 4.2 入站消息 (InboundMessage) — MUST

```yaml
message_id: "msg_xxxx"               # 渠道方原始ID
received_at: "2026-06-20T14:32:18+08:00"
channel: feishu                      # 来自哪个渠道
sender:
  type: user                         # user | bot | system
  id: "ou_xxxx"
  name: " Contributor"
  attributes:                        # 渠道特定属性（可选）
    is_external: false
    org_id: "telecom_jx"

chat:
  type: group                        # private | group | channel
  id: "oc_xxxx"
  thread_id: "tid_xxx"               # 飞书话题/Discord thread/Slack thread
  name: "EnterpriseAI集群AI团队"

message_type: text                   # 同 §4.3
content:
  # 同 §4.3

mentions:                            # 被@的人/机器人
  - { type: bot, id: "cli_a95d07a6df3adcb1" }
  - { type: user, id: "ou_xxxx" }

reply_to: "msg_yyyy"                 # 是否回复某消息
attachments:                         # 附件（如有）
  - { type: file, name: "合同.pdf", size: 1024000, url: "..." }
```

### 4.3 消息类型 (message_type)

| 类型 | 说明 | 出站 schema 字段 |
|------|------|-------------------|
| `text` | 纯文本（支持 Markdown） | `content.text` |
| `card` | 富文本卡片（标题/内容/按钮/图片） | `content.title`, `content.body`, `content.buttons`, `content.images` |
| `notify` | 通知（标题+正文，强调样式） | `content.title`, `content.body`, `content.severity` |
| `alert` | 告警（high/critical 优先级，强样式） | 同 notify + `content.alert_id`, `content.ack_url` |
| `report` | 报告（带附件） | `content.title`, `content.summary`, `content.attachments[]` |
| `file` | 单文件传输 | `content.file_uri`, `content.filename` |
| `image` | 图片 | `content.image_uri`, `content.alt` |
| `voice` | 语音 | `content.voice_uri`, `content.duration_sec` |
| `video` | 视频 | `content.video_uri`, `content.duration_sec` |
| `location` | 位置 | `content.lat`, `content.lng`, `content.address` |
| `quick_reply` | 快捷回复（按钮选项） | `content.text`, `content.options[]` |
| `human_decision` | 人工决策请求（与 taskflow 配合） | `content.prompt`, `content.choices[]`, `content.callback_url` |

---

## 5. 适配器接口契约 (L0)

每个 L0 渠道适配器**必须**实现以下接口：

### 5.1 send (MUST)

```python
def send(message: OutboundMessage) -> SendResult:
    """
    发送消息。
    返回:
      SendResult{
        status: "sent" | "queued" | "failed",
        channel_message_id: str,    # 渠道侧的消息ID（用于后续撤回/编辑）
        sent_at: datetime,
        error: str | None,
        retry_after: int | None     # 失败时建议的重试时间（秒）
      }
    幂等性: 当 message.idempotency_key 已存在时, MUST 返回上次的 SendResult, 不重复发送
    """
```

### 5.2 receive_webhook (MUST，对支持webhook的渠道)

```python
def receive_webhook(raw_event: dict) -> InboundMessage | None:
    """
    把渠道原生事件转换为 InboundMessage。返回 None 表示忽略该事件。
    实现要求:
      - 验证签名 (MUST)
      - 处理重复事件 (基于 channel_message_id 去重)
      - 把@、引用、附件全部归一化
    """
```

### 5.3 capabilities (MUST)

```python
def capabilities() -> dict:
    """
    声明本渠道支持的能力，上层据此降级。
    {
      "supports": {
        "card": true,
        "buttons": true,
        "image": true,
        "voice": true,
        "file": true,
        "thread": true,
        "edit_message": true,
        "delete_message": true,
        "reaction": true,
        "mention": true,
        "markdown": "full",         # full | basic | none
        "max_text_length": 30000,
        "max_buttons_per_card": 5
      },
      "rate_limits": {
        "per_minute": 100,
        "per_hour": 1000
      }
    }
    """
```

### 5.4 可选接口 (SHOULD/MAY)

| 方法 | 等级 | 说明 |
|------|------|------|
| `edit(channel_message_id, new_content)` | SHOULD | 编辑已发送消息 |
| `delete(channel_message_id)` | SHOULD | 撤回消息 |
| `react(channel_message_id, emoji)` | MAY | 加表情反应 |
| `upload_file(file_uri) -> file_token` | MUST 当渠道需要预上传 | 文件预上传 |
| `resolve_user(query) -> user_id` | SHOULD | 用户名/手机/邮箱 → 渠道用户ID |
| `list_groups()` | MAY | 列出可发送的群 |

---

## 6. 降级矩阵

当 `cross_channel_router` 调用某渠道时，若该渠道 capabilities 不支持当前消息类型，**必须**按下表降级：

| 原始类型 | 渠道不支持 | 降级到 | 备注 |
|----------|-----------|--------|------|
| `card` | 不支持卡片 | `text`（带emoji分隔 + URL） | 按钮转链接 |
| `card.buttons` | 不支持按钮 | `text` 末尾追加可点击 URL | |
| `voice` | 不支持语音 | `file`（音频附件） | |
| `voice` | 也不支持文件 | `text` + 转写文字（如有） | |
| `image` | 不支持 | `text` + image URL | |
| `human_decision` | 不支持按钮 | `text` + 编号选项 + "回复编号" | |
| Markdown `full` | 仅 `basic` | strip 高级语法 | |
| 长文本超限 | 超 `max_text_length` | 拆分多条 + 末尾标注 (1/3) | |

---

## 7. 安全与合规要求

| 要求 | 等级 | 说明 |
|------|------|------|
| 签名验证 | MUST | 入站 webhook 必须验证渠道签名/Token |
| 凭据隔离 | MUST | 每个渠道凭据存于 `secrets/`，禁止硬编码 |
| 消息体加密 | SHOULD | 涉及敏感数据时使用渠道侧 E2EE 或先脱敏 |
| 个人微信合规 | MUST | 个人微信仅限"用户已主动触达"或"明示同意"场景 |
| 短信合规 | MUST | 必须有运营商签名 + 退订通道（按工信部要求） |
| 邮件合规 | MUST | 发件域 SPF/DKIM/DMARC 配置完整 |
| 审计日志 | MUST | 每次 send 记录 sender/recipient/message_id/trace_id |
| 频控 | MUST | 不同渠道有不同频控，超限时入队列等待 |
| 退订/拒收 | SHOULD | 用户可退订营销/通知类消息 |

---

## 8. 错误码规范

```yaml
error_code: string                   # 见下表
error_message: string                # 用户可读
retry_after: int                     # 建议重试时间（秒），可选
```

| 错误码 | 含义 | 上层处理 |
|--------|------|----------|
| `RATE_LIMITED` | 渠道限频 | 退避重试 |
| `INVALID_RECIPIENT` | 收件人不存在/已退出 | 不重试，记录 |
| `PERMISSION_DENIED` | 没有发送权限 | 告警 + 检查配置 |
| `CONTENT_REJECTED` | 内容被渠道屏蔽（违规） | 不重试，告警 |
| `MESSAGE_TOO_LARGE` | 超过大小限制 | 拆分后重试 |
| `CHANNEL_UNAVAILABLE` | 渠道API不可用 | 退避+切换备用渠道 |
| `AUTH_EXPIRED` | 凭据过期 | 刷新token后重试 |
| `IDEMPOTENT_RETURN` | 幂等key已发送过 | 视为成功（不报错） |

---

## 9. 测试与验收

新接入一个渠道适配器**必须**通过以下契约测试：

1. ✅ 发送 text/card/notify/alert/file/image 6 种基础类型
2. ✅ 接收 webhook 事件并转换为 InboundMessage
3. ✅ capabilities 准确（实测 vs 声明一致）
4. ✅ 幂等性（重复 idempotency_key 不重复发送）
5. ✅ 频控（达到限频后正确退避）
6. ✅ 错误码映射（5种以上错误正确报告）
7. ✅ 签名验证（伪造签名被拒绝）
8. ✅ 降级（不支持的能力正确降级）
9. ✅ 审计日志（一条消息从发送到送达全链路可查）
10. ✅ 长文本/长附件边界（超限正确拆分或拒绝）

通过后，更新 `00-methodology/skill-architecture/scripts/channel_capabilities.json` 注册。

---

## 10. 与 L2 cross-channel-router 的关系

L2 路由器**不直接调用渠道API**，所有发送动作通过本规范定义的 L0 适配器完成：

```
[Skill]                            
   │ OutboundMessage
   ▼
[L2 cross_channel_router] ─── 路由决策（多渠道/优先级/降级）
   │ 拆分为 N 条 OutboundMessage(channel固定)
   ▼
[L0 l0_<channel>_im_adapter] ─── 调用渠道API
   │
   ▼
[Channel SDK / HTTP API]
```

---

## 11. 版本演进

- v1.0（本版本）：定义统一模型 + 9 个渠道 + 12 种消息类型
- v1.1（计划）：补充 video / interactive_form / payment_request 类型
- v2.0（计划）：引入消息模板系统（独立于业务Skill）
- 重大变更走 RFC 流程，向后兼容保留 ≥ 2 个版本

---

## 12. 实施清单（接入新Skill必读）

✅ 上层 Skill **不要**直接调用渠道 API
✅ 发送时构造 `OutboundMessage` → 调 `l2_cross_channel_router`
✅ 接收时订阅 `InboundMessage` 事件，不要解析 raw event
✅ 涉及富格式优先用 `card` / `notify`，让降级矩阵处理跨渠道
✅ 凡是高优先级/告警 → `priority: high|critical`，路由器自动多渠道
✅ 任何回执需求都用 `idempotency_key` + 业务 `metadata`
✅ 加新渠道前先实现 `send/receive_webhook/capabilities` 三件套
