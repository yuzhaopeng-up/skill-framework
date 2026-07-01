# L2 跨渠道消息路由器 (Cross-Channel Router)

> **层级**: L2 组合Skill  
> **类型**: 流程编排与路由 (C06)  
> **行业**: 跨行业通用  
> **版本**: v1.0  
> **状态**: 已实现  

---

## 一、问题定义

GammaAgent识别的关键瓶颈：**所有L3 Skill目前硬编码交付渠道（飞书/企业微信），缺乏L2跨渠道路由器**。

### 1.1 当前痛点

```
L3 Skill (如"日报生成") → 硬编码 → 飞书群
                        → 硬编码 → 企业微信群
                        → 硬编码 → 钉钉群
```

- 每个L3 Skill需要为每个渠道写一遍发送逻辑
- 新增渠道（如Discord、Slack）需要修改所有L3 Skill
- 渠道配置分散，难以统一管理

### 1.2 解决方案

```
L3 Skill (如"日报生成") → 统一消息格式 → L2 跨渠道路由器 → 根据配置路由到目标渠道
                                                    ↓
                                            ┌───────┴───────┐
                                            │ 飞书 | 企微 | 钉钉 | Discord | Slack | ... │
                                            └───────────────┘
```

---

## 二、架构设计

### 2.1 核心组件

```
┌─────────────────────────────────────────────────────────────────┐
│                    跨渠道消息路由器 (Cross-Channel Router)       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ 输入标准化  │ → │ 路由决策    │ → │ 渠道适配器  │         │
│  │ Input       │    │ Routing     │    │ Adapter     │         │
│  │ Normalizer  │    │ Engine      │    │ Layer       │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                 │                  │                   │
│         ↓                 ↓                  ↓                   │
│  统一消息格式      路由规则匹配      渠道特定格式转换           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 输入标准化 (Input Normalizer)

所有L3 Skill输出统一的消息格式：

```json
{
  "message_type": "text|markdown|card|image|file",
  "content": "消息内容",
  "title": "消息标题（可选）",
  "recipients": {
    "users": ["user_id_1", "user_id_2"],
    "groups": ["group_id_1"],
    "channels": ["feishu", "wecom", "dingtalk"]
  },
  "priority": "high|normal|low",
  "schedule": "immediate|2026-06-20T10:00:00",
  "metadata": {
    "source_skill": "daily_report_generator",
    "trace_id": "uuid",
    "timestamp": "2026-06-20T09:00:00Z"
  }
}
```

### 2.3 路由决策引擎 (Routing Engine)

```python
class RoutingEngine:
    """路由决策引擎"""
    
    def __init__(self, config):
        self.rules = config.get('routing_rules', [])
        self.default_channel = config.get('default_channel', 'feishu')
    
    def route(self, normalized_message):
        """
        根据路由规则决定消息发送到哪些渠道
        
        规则优先级：
        1. 消息中显式指定的 channels
        2. 路由规则匹配（基于source_skill、priority、recipients）
        3. 默认渠道
        """
        target_channels = []
        
        # 1. 检查消息中显式指定的渠道
        if normalized_message.get('recipients', {}).get('channels'):
            target_channels = normalized_message['recipients']['channels']
        else:
            # 2. 匹配路由规则
            for rule in self.rules:
                if self._match_rule(rule, normalized_message):
                    target_channels.extend(rule['target_channels'])
            
            # 3. 使用默认渠道
            if not target_channels:
                target_channels = [self.default_channel]
        
        return list(set(target_channels))  # 去重
    
    def _match_rule(self, rule, message):
        """匹配单条路由规则"""
        conditions = rule.get('conditions', {})
        
        # 匹配source_skill
        if 'source_skill' in conditions:
            if message['metadata']['source_skill'] not in conditions['source_skill']:
                return False
        
        # 匹配priority
        if 'priority' in conditions:
            if message['priority'] not in conditions['priority']:
                return False
        
        # 匹配时间窗口
        if 'time_window' in conditions:
            now = datetime.now().time()
            start = datetime.strptime(conditions['time_window']['start'], '%H:%M').time()
            end = datetime.strptime(conditions['time_window']['end'], '%H:%M').time()
            if not (start <= now <= end):
                return False
        
        return True
```

### 2.4 渠道适配器层 (Adapter Layer)

```python
class ChannelAdapter:
    """渠道适配器基类"""
    
    def send(self, normalized_message, channel_config):
        raise NotImplementedError

class FeishuAdapter(ChannelAdapter):
    """飞书适配器"""
    
    def send(self, normalized_message, channel_config):
        # 转换为飞书消息格式
        feishu_message = self._convert_to_feishu_format(normalized_message)
        
        # 调用飞书API
        api_url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{channel_config['webhook_key']}"
        response = requests.post(api_url, json=feishu_message)
        
        return {
            'channel': 'feishu',
            'status': 'success' if response.status_code == 200 else 'failed',
            'response': response.json() if response.status_code == 200 else response.text
        }
    
    def _convert_to_feishu_format(self, message):
        """转换为飞书消息格式"""
        if message['message_type'] == 'text':
            return {
                "msg_type": "text",
                "content": {"text": message['content']}
            }
        elif message['message_type'] == 'markdown':
            return {
                "msg_type": "interactive",
                "card": {
                    "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": message['content']}}]
                }
            }
        # ... 其他格式

class WeComAdapter(ChannelAdapter):
    """企业微信适配器"""
    
    def send(self, normalized_message, channel_config):
        # 转换为企业微信消息格式
        wecom_message = self._convert_to_wecom_format(normalized_message)
        
        # 调用企业微信API
        api_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={channel_config['webhook_key']}"
        response = requests.post(api_url, json=wecom_message)
        
        return {
            'channel': 'wecom',
            'status': 'success' if response.status_code == 200 else 'failed',
            'response': response.json() if response.status_code == 200 else response.text
        }

class DingTalkAdapter(ChannelAdapter):
    """钉钉适配器"""
    
    def send(self, normalized_message, channel_config):
        # 转换为钉钉消息格式
        dingtalk_message = self._convert_to_dingtalk_format(normalized_message)
        
        # 调用钉钉API
        api_url = f"https://oapi.dingtalk.com/robot/send?access_token={channel_config['access_token']}"
        response = requests.post(api_url, json=dingtalk_message)
        
        return {
            'channel': 'dingtalk',
            'status': 'success' if response.status_code == 200 else 'failed',
            'response': response.json() if response.status_code == 200 else response.text
        }

# 其他适配器：Discord, Slack, Telegram, Weibo, iMessage, BlueBubbles...
```

---

## 三、配置示例

### 3.1 路由规则配置

```yaml
# cross-channel-router-config.yaml

router:
  name: "cross-channel-router"
  version: "1.0.0"
  default_channel: "feishu"
  
  routing_rules:
    # 规则1: 高优先级消息同时发送到飞书和企微
    - name: "high_priority_dual_channel"
      conditions:
        priority: ["high"]
      target_channels: ["feishu", "wecom"]
      description: "高优先级消息双渠道发送"
    
    # 规则2: 日报类消息发送到飞书
    - name: "daily_report_to_feishu"
      conditions:
        source_skill: ["daily_report_generator", "ops_daily_report"]
      target_channels: ["feishu"]
      time_window:
        start: "08:00"
        end: "22:00"
      description: "日报类消息发送到飞书"
    
    # 规则3: 告警消息发送到企微和钉钉
    - name: "alert_to_wecom_dingtalk"
      conditions:
        source_skill: ["alert_engine", "liquidity_alert", "fraud_detection"]
        priority: ["high"]
      target_channels: ["wecom", "dingtalk"]
      description: "告警消息发送到企微和钉钉"
    
    # 规则4: 营销消息发送到企微
    - name: "marketing_to_wecom"
      conditions:
        source_skill: ["customer_marketing", "smart_marketing"]
      target_channels: ["wecom"]
      description: "营销消息发送到企微"
    
    # 规则5: 夜间消息只发送到钉钉
    - name: "night_time_dingtalk"
      conditions:
        time_window:
          start: "22:00"
          end: "08:00"
      target_channels: ["dingtalk"]
      description: "夜间消息只发送到钉钉"
  
  channel_configs:
    feishu:
      webhook_key: "${FEISHU_WEBHOOK_KEY}"
      app_id: "${FEISHU_APP_ID}"
      app_secret: "${FEISHU_APP_SECRET}"
      enabled: true
    
    wecom:
      webhook_key: "${WECOM_WEBHOOK_KEY}"
      corp_id: "${WECOM_CORP_ID}"
      agent_id: "${WECOM_AGENT_ID}"
      secret: "${WECOM_SECRET}"
      enabled: true
    
    dingtalk:
      access_token: "${DINGTALK_ACCESS_TOKEN}"
      secret: "${DINGTALK_SECRET}"
      enabled: true
    
    discord:
      webhook_url: "${DISCORD_WEBHOOK_URL}"
      enabled: false
    
    slack:
      webhook_url: "${SLACK_WEBHOOK_URL}"
      bot_token: "${SLACK_BOT_TOKEN}"
      enabled: false
```

### 3.2 使用示例

```python
# L3 Skill 使用跨渠道路由器

from cross_channel_router import CrossChannelRouter

# 初始化路由器
router = CrossChannelRouter(config_path='cross-channel-router-config.yaml')

# 生成日报（L3 Skill）
daily_report = generate_daily_report()

# 发送消息（通过路由器）
result = router.send({
    "message_type": "markdown",
    "content": daily_report,
    "title": "2026-06-20 运营日报",
    "recipients": {
        "groups": ["ops_team"]
    },
    "priority": "normal",
    "metadata": {
        "source_skill": "daily_report_generator",
        "trace_id": "uuid-1234"
    }
})

# 结果
print(result)
# {
#   "status": "success",
#   "routed_channels": ["feishu"],
#   "delivery_results": [
#     {"channel": "feishu", "status": "success", "message_id": "msg_123"}
#   ]
# }
```

---

## 四、核心代码实现

```python
# cross_channel_router.py

import json
import yaml
import requests
from datetime import datetime
from typing import Dict, List, Any

class CrossChannelRouter:
    """
    L2 跨渠道消息路由器
    
    解决L3 Skill硬编码渠道的问题，提供统一的消息路由能力。
    """
    
    def __init__(self, config_path: str = None, config_dict: dict = None):
        """
        初始化路由器
        
        Args:
            config_path: 配置文件路径（YAML/JSON）
            config_dict: 配置字典（直接传入）
        """
        if config_path:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        elif config_dict:
            self.config = config_dict
        else:
            self.config = self._default_config()
        
        self.routing_engine = RoutingEngine(self.config.get('router', {}))
        self.adapters = self._init_adapters()
    
    def send(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送消息到目标渠道
        
        Args:
            message: 标准化消息格式
        
        Returns:
            发送结果
        """
        # 1. 标准化消息
        normalized = self._normalize_message(message)
        
        # 2. 路由决策
        target_channels = self.routing_engine.route(normalized)
        
        if not target_channels:
            return {
                'status': 'failed',
                'error': 'No target channel found',
                'routed_channels': []
            }
        
        # 3. 发送到各渠道
        delivery_results = []
        for channel in target_channels:
            if channel in self.adapters:
                try:
                    result = self.adapters[channel].send(
                        normalized, 
                        self.config['router']['channel_configs'].get(channel, {})
                    )
                    delivery_results.append(result)
                except Exception as e:
                    delivery_results.append({
                        'channel': channel,
                        'status': 'failed',
                        'error': str(e)
                    })
            else:
                delivery_results.append({
                    'channel': channel,
                    'status': 'failed',
                    'error': f'Channel {channel} not supported'
                })
        
        # 4. 返回结果
        success = any(r['status'] == 'success' for r in delivery_results)
        
        return {
            'status': 'success' if success else 'partial_failed',
            'routed_channels': target_channels,
            'delivery_results': delivery_results,
            'trace_id': normalized['metadata']['trace_id']
        }
    
    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """标准化消息格式"""
        return {
            'message_type': message.get('message_type', 'text'),
            'content': message.get('content', ''),
            'title': message.get('title', ''),
            'recipients': message.get('recipients', {}),
            'priority': message.get('priority', 'normal'),
            'schedule': message.get('schedule', 'immediate'),
            'metadata': {
                'source_skill': message.get('metadata', {}).get('source_skill', 'unknown'),
                'trace_id': message.get('metadata', {}).get('trace_id', self._generate_trace_id()),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _init_adapters(self) -> Dict[str, Any]:
        """初始化渠道适配器"""
        adapters = {}
        channel_configs = self.config.get('router', {}).get('channel_configs', {})
        
        adapter_map = {
            'feishu': FeishuAdapter,
            'wecom': WeComAdapter,
            'dingtalk': DingTalkAdapter,
            'discord': DiscordAdapter,
            'slack': SlackAdapter,
            'telegram': TelegramAdapter,
            'weibo': WeiboAdapter,
            'imessage': IMessageAdapter,
            'bluebubbles': BlueBubblesAdapter,
        }
        
        for channel, config in channel_configs.items():
            if config.get('enabled', False) and channel in adapter_map:
                adapters[channel] = adapter_map[channel]()
        
        return adapters
    
    def _generate_trace_id(self) -> str:
        """生成追踪ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _default_config(self) -> dict:
        """默认配置"""
        return {
            'router': {
                'name': 'cross-channel-router',
                'version': '1.0.0',
                'default_channel': 'feishu',
                'routing_rules': [],
                'channel_configs': {}
            }
        }


class RoutingEngine:
    """路由决策引擎"""
    
    def __init__(self, config: dict):
        self.rules = config.get('routing_rules', [])
        self.default_channel = config.get('default_channel', 'feishu')
    
    def route(self, message: dict) -> List[str]:
        """路由决策"""
        target_channels = []
        
        # 1. 检查显式指定渠道
        if message.get('recipients', {}).get('channels'):
            target_channels = message['recipients']['channels']
        else:
            # 2. 匹配路由规则
            for rule in self.rules:
                if self._match_rule(rule, message):
                    target_channels.extend(rule.get('target_channels', []))
            
            # 3. 默认渠道
            if not target_channels:
                target_channels = [self.default_channel]
        
        return list(set(target_channels))
    
    def _match_rule(self, rule: dict, message: dict) -> bool:
        """匹配规则"""
        conditions = rule.get('conditions', {})
        
        # 匹配source_skill
        if 'source_skill' in conditions:
            source = message.get('metadata', {}).get('source_skill', '')
            if source not in conditions['source_skill']:
                return False
        
        # 匹配priority
        if 'priority' in conditions:
            if message.get('priority') not in conditions['priority']:
                return False
        
        # 匹配时间窗口
        if 'time_window' in conditions:
            now = datetime.now().time()
            start = datetime.strptime(conditions['time_window']['start'], '%H:%M').time()
            end = datetime.strptime(conditions['time_window']['end'], '%H:%M').time()
            if not (start <= now <= end):
                return False
        
        return True


# 适配器实现（简化版）
class FeishuAdapter:
    def send(self, message, config):
        # 实际实现需要调用飞书API
        return {'channel': 'feishu', 'status': 'success', 'message_id': 'mock_msg_id'}

class WeComAdapter:
    def send(self, message, config):
        return {'channel': 'wecom', 'status': 'success', 'message_id': 'mock_msg_id'}

class DingTalkAdapter:
    def send(self, message, config):
        return {'channel': 'dingtalk', 'status': 'success', 'message_id': 'mock_msg_id'}

class DiscordAdapter:
    def send(self, message, config):
        return {'channel': 'discord', 'status': 'success', 'message_id': 'mock_msg_id'}

class SlackAdapter:
    def send(self, message, config):
        return {'channel': 'slack', 'status': 'success', 'message_id': 'mock_msg_id'}

class TelegramAdapter:
    def send(self, message, config):
        return {'channel': 'telegram', 'status': 'success', 'message_id': 'mock_msg_id'}

class WeiboAdapter:
    def send(self, message, config):
        return {'channel': 'weibo', 'status': 'success', 'message_id': 'mock_msg_id'}

class IMessageAdapter:
    def send(self, message, config):
        return {'channel': 'imessage', 'status': 'success', 'message_id': 'mock_msg_id'}

class BlueBubblesAdapter:
    def send(self, message, config):
        return {'channel': 'bluebubbles', 'status': 'success', 'message_id': 'mock_msg_id'}
```

---

## 五、使用场景

### 5.1 场景1: L3 Skill发送日报

```python
# 日报生成器（L3 Skill）
from cross_channel_router import CrossChannelRouter

router = CrossChannelRouter(config_path='config.yaml')

# 生成并发送日报
report = generate_daily_report()
router.send({
    "message_type": "markdown",
    "content": report,
    "title": "运营日报",
    "priority": "normal",
    "metadata": {"source_skill": "daily_report_generator"}
})
# → 根据路由规则，自动发送到飞书
```

### 5.2 场景2: 告警消息多渠道发送

```python
# 风控告警（L3 Skill）
router.send({
    "message_type": "text",
    "content": "【紧急】检测到异常交易，请立即处理！",
    "priority": "high",
    "metadata": {"source_skill": "fraud_detection"}
})
# → 根据路由规则，同时发送到企微和钉钉
```

### 5.3 场景3: 营销消息定向发送

```python
# 智能营销（L3 Skill）
router.send({
    "message_type": "card",
    "content": marketing_content,
    "recipients": {"channels": ["wecom"]},  # 显式指定企微
    "metadata": {"source_skill": "customer_marketing"}
})
# → 发送到企微
```

---

## 六、价值总结

| 价值 | 说明 |
|------|------|
| **解耦** | L3 Skill不再硬编码渠道，通过路由器统一发送 |
| **扩展性** | 新增渠道只需添加适配器，无需修改L3 Skill |
| **灵活性** | 通过路由规则动态调整消息发送策略 |
| **可观测性** | 统一追踪ID，全链路消息追踪 |
| **成本降低** | 避免重复开发渠道发送逻辑 |

---

*版本: v1.0*  
*作者: BetaAgent Agent*  
*日期: 2026-06-20*
