# L2 模式蓝图索引

L2 是**组合层**，把 L0/L1 原子/基础Skill按业务模式组合成可复用的"骨架"。
L3 场景Skill和L4多Agent都建立在L2之上，避免重复造轮子。

## 4 大核心模式

| 蓝图 | 文件 | 解决的问题 |
|------|------|-----------|
| **跨渠道路由** | [`cross-channel-router.md`](./cross-channel-router.md) | 一次发送，多渠道分发；解决"L3硬编码渠道"瓶颈 |
| **统一文档流水线** | [`unified-document-pipeline.md`](./unified-document-pipeline.md) | 文档进、结构化数据出；OCR/解析/校验/入库统一框架 |
| **告警引擎** | [`alert-engine.md`](./alert-engine.md) | 监测→评估→告警→处置→闭环全链路 |
| **TaskFlow 任务编排** | [`taskflow-patterns.md`](./taskflow-patterns.md) | 五种通用工作流模式（顺序/并行/分支/循环/Saga） |

## 设计原则

1. **协议统一**：四个模式都遵循《IM渠道接口标准》中的统一消息格式
2. **可组合**：L2 之间可以互相调用（taskflow 调 router、document 调 alert）
3. **可观测**：每个模式都强制 trace_id 与生命周期事件
4. **可治理**：模板/规则/DSL 受版本控制，走 PR 评审
5. **可降级**：每个模式都有明确的容错与降级策略

## 与上下层的关系

```
L4 多Agent      ─── 调用多个L3，跨节点协作
                       ▼
L3 场景Skill    ─── 基于 TaskFlow 编排 + 调用 L2 模式
                       ▼
L2 模式蓝图     ─── 4个：router / document / alert / taskflow
                       ▼
L1 基础Skill    ─── 单一职责的功能模块
                       ▼
L0 原子/连接器  ─── DB/API/IM/文件等底层连接
```

## 实施优先级

| 优先级 | 蓝图 | 节点负责 |
|--------|------|----------|
| P0 | cross-channel-router | BetaAgent（已设计） |
| P0 | unified-document-pipeline | BetaAgent + DeltaAgent（实现） |
| P1 | alert-engine | GammaAgent（设计） + AlphaAgent（金融规则） |
| P1 | taskflow-patterns | BetaAgent（引擎） + 全节点（注册flow） |
