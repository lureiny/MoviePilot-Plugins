# MoviePilot 事件参数结构文档

本文档详细说明了 MoviePilot 系统中所有广播事件类型的参数结构，供事件执行器插件使用。

## 事件数据格式

事件执行器插件将事件数据打包为 JSON 格式，通过环境变量 `MP_EVENT_DATA` 传递：

```json
{
  "type": "event.type",    // 事件类型
  "data": {                // 事件数据
    // 具体事件的数据字段
  }
}
```

**环境变量**：
- `MP_EVENT_TYPE`: 事件类型（如 `transfer.complete`）
- `MP_EVENT_DATA`: 完整的事件信息（JSON 格式，包含 type 和 data）
- `MP_EVENT_TIME`: 事件触发时间（ISO 格式）

---

## 广播事件 (EventType)

广播事件异步并行执行，适合用于通知、日志记录等不影响主流程的操作。

### 1. PluginReload - 插件重载
**事件类型**: `plugin.reload`
**触发时机**: 插件被重新加载时

**数据结构**:
```json
{
  "type": "plugin.reload",
  "data": {
    "plugin_id": "AutoSignIn"
  }
}
```

---

### 2. PluginAction - 触发插件动作
**事件类型**: `plugin.action`
**触发时机**: 远程命令或手动触发插件动作

**数据结构**:
```json
{
  "type": "plugin.action",
  "data": {
    "action": "site_signin",
    "username": "admin"
  }
}
```

---

### 3. PluginTriggered - 触发插件事件
**事件类型**: `plugin.triggered`
**触发时机**: 插件自定义触发事件

**数据结构**:
```json
{
  "type": "plugin.triggered",
  "data": {
    "plugin_id": "MyPlugin",
    "trigger_type": "custom",
    "trigger_data": {}
  }
}
```

---

### 4. CommandExcute - 执行命令
**事件类型**: `command.excute`
**触发时机**: 执行远程命令时

**数据结构**:
```json
{
  "type": "command.excute",
  "data": {
    "command": "/signin",
    "args": [],
    "channel": "telegram",
    "username": "admin"
  }
}
```

---

### 5. SiteDeleted - 站点已删除
**事件类型**: `site.deleted`
**触发时机**: 删除站点时

**数据结构**:
```json
{
  "type": "site.deleted",
  "data": {
    "site_id": 123,
    "site_name": "PT站点",
    "site_url": "https://pt.example.com"
  }
}
```

---

### 6. SiteUpdated - 站点已更新
**事件类型**: `site.updated`
**触发时机**: 更新站点配置时

**数据结构**:
```json
{
  "type": "site.updated",
  "data": {
    "site_id": 123,
    "site_name": "PT站点",
    "changes": {
      "cookie": "updated"
    }
  }
}
```

---

### 7. SiteRefreshed - 站点已刷新
**事件类型**: `site.refreshed`
**触发时机**: 刷新站点数据时

**数据结构**:
```json
{
  "type": "site.refreshed",
  "data": {
    "site_id": 123,
    "site_name": "PT站点"
  }
}
```

---

### 8. TransferComplete - 整理完成 ⭐
**事件类型**: `transfer.complete`
**触发时机**: 文件整理完成后

**数据结构**:
```json
{
  "type": "transfer.complete",
  "data": {
    "fileitem": {
      "path": "/downloads/Movie.2024.mkv",
      "name": "Movie.2024.mkv",
      "size": 10737418240,
      "extension": ".mkv"
    },
    "meta": {
      "title": "电影名称",
      "year": "2024",
      "season": null,
      "episode": null
    },
    "mediainfo": {
      "tmdb_id": 12345,
      "title": "电影名称",
      "original_title": "Original Title",
      "year": "2024",
      "type": "电影",
      "overview": "电影简介",
      "poster_path": "/path/to/poster.jpg",
      "vote_average": 8.5
    },
    "transferinfo": {
      "source_path": "/downloads/Movie.2024.mkv",
      "source_filename": "Movie.2024.mkv",
      "target_path": "/media/Movies/Movie (2024)/Movie.2024.mkv",
      "target_diritem": {
        "path": "/media/Movies/Movie (2024)",
        "name": "Movie (2024)"
      },
      "file_count": 1,
      "total_size": 10737418240,
      "file_list": ["/downloads/Movie.2024.mkv"],
      "file_list_new": ["/media/Movies/Movie (2024)/Movie.2024.mkv"]
    },
    "downloader": "qbittorrent"
  }
}
```

**字段说明**:
- `mediainfo`: TMDB 媒体信息
- `transferinfo`: 文件转移详细信息
- `fileitem`: 原始文件信息
- `meta`: 文件名识别的元数据

---

### 9. DownloadAdded - 添加下载 ⭐
**事件类型**: `download.added`
**触发时机**: 添加下载任务时

**数据结构**:
```json
{
  "type": "download.added",
  "data": {
    "hash": "torrent_hash_string",
    "context": {
      "meta_info": {
        "title": "电影名称",
        "year": "2024"
      },
      "media_info": {
        "tmdb_id": 12345,
        "title": "电影名称"
      },
      "torrent_info": {
        "title": "Movie.2024.1080p.BluRay.x264",
        "size": 10737418240,
        "seeders": 100,
        "site_name": "PT站点"
      }
    },
    "username": "admin",
    "downloader": "qbittorrent"
  }
}
```

---

### 10. HistoryDeleted - 删除历史记录
**事件类型**: `history.deleted`
**触发时机**: 删除历史记录时

**数据结构**:
```json
{
  "type": "history.deleted",
  "data": {
    "history_id": 123,
    "history_type": "transfer",
    "title": "电影名称"
  }
}
```

---

### 11. DownloadFileDeleted - 删除下载源文件
**事件类型**: `downloadfile.deleted`
**触发时机**: 删除下载源文件时

**数据结构**:
```json
{
  "type": "downloadfile.deleted",
  "data": {
    "path": "/downloads/Movie.2024.mkv",
    "hash": "torrent_hash",
    "downloader": "qbittorrent"
  }
}
```

---

### 12. DownloadDeleted - 删除下载任务
**事件类型**: `download.deleted`
**触发时机**: 删除下载任务时

**数据结构**:
```json
{
  "type": "download.deleted",
  "data": {
    "hash": "torrent_hash",
    "title": "Movie.2024.1080p",
    "downloader": "qbittorrent"
  }
}
```

---

### 13. UserMessage - 收到用户消息
**事件类型**: `user.message`
**触发时机**: 收到用户发送的消息时

**数据结构**:
```json
{
  "type": "user.message",
  "data": {
    "channel": "telegram",
    "username": "user123",
    "userid": "telegram_user_id",
    "text": "消息内容",
    "image": "https://example.com/image.jpg"
  }
}
```

---

### 14. WebhookMessage - 收到Webhook消息
**事件类型**: `webhook.message`
**触发时机**: 收到 Webhook 请求时

**数据结构**:
```json
{
  "type": "webhook.message",
  "data": {
    "source": "webhook_source",
    "event": "event_name",
    "data": {},
    "headers": {}
  }
}
```

---

### 15. NoticeMessage - 发送消息通知
**事件类型**: `notice.message`
**触发时机**: 系统发送通知消息时

**数据结构**:
```json
{
  "type": "notice.message",
  "data": {
    "type": "资源下载",
    "title": "通知标题",
    "text": "通知内容",
    "image": "https://example.com/poster.jpg",
    "link": "https://example.com/detail"
  }
}
```

**通知类型**: 资源下载、整理入库、订阅、站点、媒体服务器、手动处理、插件、其它

---

### 16. SubscribeAdded - 添加订阅 ⭐
**事件类型**: `subscribe.added`
**触发时机**: 添加新订阅时

**数据结构**:
```json
{
  "type": "subscribe.added",
  "data": {
    "subscribe_id": 123,
    "username": "admin",
    "mediainfo": {
      "tmdb_id": 12345,
      "title": "电视剧名称",
      "type": "电视剧",
      "year": "2024",
      "season": 1
    }
  }
}
```

---

### 17. SubscribeModified - 订阅已调整
**事件类型**: `subscribe.modified`
**触发时机**: 修改订阅配置时

**数据结构**:
```json
{
  "type": "subscribe.modified",
  "data": {
    "subscribe_id": 123,
    "username": "admin",
    "changes": {
      "quality": "1080p"
    }
  }
}
```

---

### 18. SubscribeDeleted - 订阅已删除
**事件类型**: `subscribe.deleted`
**触发时机**: 删除订阅时

**数据结构**:
```json
{
  "type": "subscribe.deleted",
  "data": {
    "subscribe_id": 123,
    "username": "admin"
  }
}
```

---

### 19. SubscribeComplete - 订阅已完成 ⭐
**事件类型**: `subscribe.complete`
**触发时机**: 订阅完成（所有剧集下载完成）

**数据结构**:
```json
{
  "type": "subscribe.complete",
  "data": {
    "subscribe_id": 123,
    "subscribe_info": {
      "id": 123,
      "name": "电视剧名称",
      "year": "2024",
      "type": "电视剧",
      "tmdbid": 12345,
      "season": 1,
      "total_episode": 12,
      "completed_episode": 12
    },
    "mediainfo": {
      "tmdb_id": 12345,
      "title": "电视剧名称",
      "type": "电视剧"
    }
  }
}
```

---

### 20. SystemError - 系统错误
**事件类型**: `system.error`
**触发时机**: 系统发生错误时

**数据结构**:
```json
{
  "type": "system.error",
  "data": {
    "type": "event",
    "event_type": "transfer.complete",
    "event_handle": "ClassName.method_name",
    "error": "错误信息",
    "traceback": "完整堆栈跟踪"
  }
}
```

---

### 21. MetadataScrape - 刮削元数据
**事件类型**: `metadata.scrape`
**触发时机**: 需要刮削媒体元数据时

**数据结构**:
```json
{
  "type": "metadata.scrape",
  "data": {
    "meta": {
      "title": "电影名称",
      "year": "2024"
    },
    "mediainfo": {
      "tmdb_id": 12345,
      "title": "电影名称"
    },
    "fileitem": {
      "path": "/media/Movies/Movie (2024)",
      "name": "Movie (2024)"
    },
    "file_list": [
      "/media/Movies/Movie (2024)/Movie.2024.mkv"
    ],
    "overwrite": false
  }
}
```

---

### 22. ModuleReload - 模块重载
**事件类型**: `module.reload`
**触发时机**: 系统模块重新加载时

**数据结构**:
```json
{
  "type": "module.reload",
  "data": {
    "module_id": "Qbittorrent",
    "module_type": "downloader"
  }
}
```

---

### 23. ConfigChanged - 配置项更新
**事件类型**: `config.updated`
**触发时机**: 系统配置更改时

**数据结构**:
```json
{
  "type": "config.updated",
  "data": {
    "config_key": "Downloaders",
    "config_value": {},
    "username": "admin"
  }
}
```

---

### 24. MessageAction - 消息交互动作
**事件类型**: `message.action`
**触发时机**: 用户与交互式消息互动时

**数据结构**:
```json
{
  "type": "message.action",
  "data": {
    "action": "approve",
    "action_id": "action_uuid",
    "message_id": "msg_id",
    "data": {},
    "username": "admin"
  }
}
```

---

### 25. WorkflowExecute - 执行工作流
**事件类型**: `workflow.execute`
**触发时机**: 触发工作流执行时

**数据结构**:
```json
{
  "type": "workflow.execute",
  "data": {
    "workflow_id": "workflow_123"
  }
}
```

---

## 使用示例

### 示例 1: 解析事件数据

```bash
#!/bin/bash

# 从环境变量获取事件数据
EVENT_DATA="$MP_EVENT_DATA"

# 使用 jq 解析 JSON
EVENT_TYPE=$(echo "$EVENT_DATA" | jq -r '.type')
MEDIA_TITLE=$(echo "$EVENT_DATA" | jq -r '.data.mediainfo.title // empty')

echo "事件类型: $EVENT_TYPE"
echo "媒体标题: $MEDIA_TITLE"
```

### 示例 2: 整理完成后发送通知

```bash
#!/bin/bash

EVENT_DATA="$MP_EVENT_DATA"
EVENT_TYPE=$(echo "$EVENT_DATA" | jq -r '.type')

if [ "$EVENT_TYPE" = "transfer.complete" ]; then
  TITLE=$(echo "$EVENT_DATA" | jq -r '.data.mediainfo.title')
  YEAR=$(echo "$EVENT_DATA" | jq -r '.data.mediainfo.year')
  TARGET=$(echo "$EVENT_DATA" | jq -r '.data.transferinfo.target_path')

  curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
    -d "chat_id=<CHAT_ID>" \
    -d "text=✅ 整理完成: $TITLE ($YEAR)%0A路径: $TARGET"
fi
```

### 示例 3: 订阅完成后清理

```bash
#!/bin/bash

EVENT_DATA="$MP_EVENT_DATA"
EVENT_TYPE=$(echo "$EVENT_DATA" | jq -r '.type')

if [ "$EVENT_TYPE" = "subscribe.complete" ]; then
  SUBSCRIBE_ID=$(echo "$EVENT_DATA" | jq -r '.data.subscribe_id')
  TMDB_ID=$(echo "$EVENT_DATA" | jq -r '.data.mediainfo.tmdb_id')

  echo "订阅完成: ID=$SUBSCRIBE_ID, TMDB=$TMDB_ID"
  # 执行清理逻辑
  /usr/local/bin/cleanup.sh "$SUBSCRIBE_ID" "$TMDB_ID"
fi
```

### 示例 4: Python 脚本处理

```python
#!/usr/bin/env python3
import os
import json

# 获取环境变量
event_data_str = os.environ.get('MP_EVENT_DATA', '{}')
event_data = json.loads(event_data_str)

event_type = event_data.get('type')
data = event_data.get('data', {})

if event_type == 'transfer.complete':
    mediainfo = data.get('mediainfo', {})
    title = mediainfo.get('title')
    tmdb_id = mediainfo.get('tmdb_id')

    print(f"整理完成: {title} (TMDB: {tmdb_id})")
    # 执行自定义逻辑...
```

---

## 注意事项

1. **数据格式**: `MP_EVENT_DATA` 包含完整的事件信息（type + data）
2. **JSON 解析**: 推荐使用 `jq` 工具解析 JSON
3. **字段可选性**: 某些字段可能为 `null`，使用 `jq -r '.field // "default"'` 提供默认值
4. **对象序列化**: 复杂对象会被递归转换为字典格式
5. **超时限制**: 命令执行超时 60 秒

---

**文档版本**: 2.0.0
**最后更新**: 2025-12-21
**适用于**: MoviePilot V2
**参考**: 官方 Webhook 插件实现
