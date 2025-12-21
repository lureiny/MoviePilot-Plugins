# 事件执行器插件

## 插件简介

事件执行器插件允许你监听 MoviePilot 系统中的所有事件（广播事件和链式事件），并在事件触发时执行自定义的 Bash 命令。事件数据会以 JSON 格式通过环境变量传递给你的命令，让你可以实现各种自动化操作。

## 主要功能

- ✅ 监听所有系统事件（27个广播事件 + 13个链式事件）
- ✅ 选择性监听特定事件类型
- ✅ 将事件数据序列化为 JSON 并通过环境变量传递
- ✅ 支持任意 Bash 命令或脚本
- ✅ 完整的事件日志记录功能
- ✅ 60秒超时保护
- ✅ 详细的错误日志

## 安装方法

1. 将 `eventexecutor` 目录复制到 MoviePilot 插件目录：
   ```bash
   cp -r /data/mp/CustomPlugins/plugins/eventexecutor /path/to/moviepilot/app/plugins/
   ```

2. 在 MoviePilot 管理界面重载插件

3. 在插件设置中启用并配置事件执行器

## 配置说明

### 配置项

1. **启用插件**: 开关插件功能
2. **记录事件日志**: 在日志中记录所有捕获的事件（调试用）
3. **Bash 命令**: 要执行的命令或脚本路径
4. **监听的事件类型**: 选择要监听的事件（留空则监听所有事件）

### 环境变量

执行命令时，以下环境变量会被设置：

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `MP_EVENT_TYPE` | 事件类型 | `transfer.complete` |
| `MP_EVENT_ID` | 事件唯一ID | `uuid-string` |
| `MP_EVENT_DATA` | 事件数据（JSON格式） | `{"mediainfo": {...}}` |
| `MP_EVENT_PRIORITY` | 事件优先级 | `10` |
| `MP_EVENT_TIME` | 事件触发时间 | `2025-01-01T12:00:00` |

## 使用示例

### 示例 1: 记录所有事件到文件

**Bash 命令**:
```bash
echo "[$(date)] $MP_EVENT_TYPE" >> /tmp/mp-events.log && echo "$MP_EVENT_DATA" >> /tmp/mp-events.log && echo "---" >> /tmp/mp-events.log
```

### 示例 2: 整理完成后发送 Telegram 通知

**Bash 命令**:
```bash
if [ "$MP_EVENT_TYPE" = "transfer.complete" ]; then
  TITLE=$(echo "$MP_EVENT_DATA" | jq -r '.mediainfo.title // "未知"')
  YEAR=$(echo "$MP_EVENT_DATA" | jq -r '.mediainfo.year // ""')
  curl -s -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
    -d "chat_id=<YOUR_CHAT_ID>" \
    -d "text=✅ 整理完成: $TITLE ($YEAR)"
fi
```

### 示例 3: 使用外部脚本处理事件

**Bash 命令**:
```bash
/usr/local/bin/handle-moviepilot-event.sh
```

**脚本内容** (`/usr/local/bin/handle-moviepilot-event.sh`):
```bash
#!/bin/bash

EVENT_TYPE="$MP_EVENT_TYPE"
EVENT_DATA="$MP_EVENT_DATA"

case "$EVENT_TYPE" in
  "transfer.complete")
    # 整理完成后的处理
    TITLE=$(echo "$EVENT_DATA" | jq -r '.mediainfo.title')
    echo "整理完成: $TITLE"
    # 执行自定义逻辑...
    ;;

  "download.added")
    # 下载添加后的处理
    HASH=$(echo "$EVENT_DATA" | jq -r '.hash')
    echo "新增下载: $HASH"
    # 执行自定义逻辑...
    ;;

  "subscribe.complete")
    # 订阅完成后的处理
    SUBSCRIBE_ID=$(echo "$EVENT_DATA" | jq -r '.subscribe_id')
    echo "订阅完成: $SUBSCRIBE_ID"
    # 执行自定义逻辑...
    ;;

  *)
    echo "未处理的事件类型: $EVENT_TYPE"
    ;;
esac
```

### 示例 4: 使用 Python 脚本处理事件

**Bash 命令**:
```bash
/usr/bin/python3 /usr/local/bin/mp-event-handler.py
```

**Python 脚本** (`/usr/local/bin/mp-event-handler.py`):
```python
#!/usr/bin/env python3
import os
import json
import requests

def main():
    event_type = os.environ.get('MP_EVENT_TYPE')
    event_data_str = os.environ.get('MP_EVENT_DATA')

    if not event_type or not event_data_str:
        return

    event_data = json.loads(event_data_str)

    # 处理整理完成事件
    if event_type == 'transfer.complete':
        mediainfo = event_data.get('mediainfo', {})
        title = mediainfo.get('title', '未知')
        tmdb_id = mediainfo.get('tmdb_id')

        # 发送通知到自定义API
        requests.post('https://your-api.com/notify', json={
            'type': 'media_organized',
            'title': title,
            'tmdb_id': tmdb_id
        })

    # 处理下载添加事件
    elif event_type == 'download.added':
        context = event_data.get('context', {})
        torrent_info = context.get('torrent_info', {})
        torrent_title = torrent_info.get('title', '未知')

        print(f"新增下载: {torrent_title}")
        # 执行自定义逻辑...

if __name__ == '__main__':
    main()
```

### 示例 5: 订阅完成后清理

**Bash 命令**:
```bash
if [ "$MP_EVENT_TYPE" = "subscribe.complete" ]; then
  SUBSCRIBE_ID=$(echo "$MP_EVENT_DATA" | jq -r '.subscribe_id')
  TMDB_ID=$(echo "$MP_EVENT_DATA" | jq -r '.mediainfo.tmdb_id')
  # 调用清理脚本
  /usr/local/bin/cleanup-subscription.sh "$SUBSCRIBE_ID" "$TMDB_ID"
fi
```

## 事件类型说明

### 常用广播事件

| 事件类型 | 事件值 | 说明 |
|---------|--------|------|
| 整理完成 | `transfer.complete` | 文件整理完成后触发 |
| 添加下载 | `download.added` | 添加下载任务时触发 |
| 添加订阅 | `subscribe.added` | 添加新订阅时触发 |
| 订阅完成 | `subscribe.complete` | 订阅完成（所有剧集下载完成）时触发 |
| 站点已删除 | `site.deleted` | 删除站点时触发 |
| 收到用户消息 | `user.message` | 收到用户消息时触发 |
| 系统错误 | `system.error` | 系统发生错误时触发 |

详细的事件参数结构请参考 [EVENT_STRUCTURE.md](./EVENT_STRUCTURE.md)

## 注意事项

1. **权限问题**: 确保 Bash 命令或脚本有执行权限
   ```bash
   chmod +x /usr/local/bin/your-script.sh
   ```

2. **超时限制**: 命令执行超时为 60 秒，超时会被强制终止

3. **JSON 解析**: 建议使用 `jq` 工具解析 JSON 数据
   ```bash
   # 安装 jq
   apt-get install jq  # Debian/Ubuntu
   yum install jq      # CentOS/RHEL
   ```

4. **错误处理**: 命令执行失败会记录到日志，不影响系统其他功能

5. **性能考虑**: 如果监听所有事件，确保命令执行效率，避免阻塞

6. **安全性**: 不要在命令中包含敏感信息，使用环境变量或配置文件

7. **日志调试**: 启用"记录事件日志"选项可以查看详细的事件信息

## 常见问题

### Q: 为什么命令没有执行？
A: 检查以下几点：
- 插件是否已启用
- Bash 命令是否正确
- 是否选择了正确的事件类型
- 查看 MoviePilot 日志是否有错误信息

### Q: 如何调试命令？
A:
1. 启用"记录事件日志"选项
2. 在命令中添加日志输出
   ```bash
   echo "Debug: $MP_EVENT_TYPE" >> /tmp/debug.log
   ```
3. 查看 MoviePilot 日志

### Q: 可以执行多个命令吗？
A: 可以，使用 `&&` 或 `;` 连接多个命令，或者调用一个脚本文件

### Q: 事件数据中的对象是什么格式？
A: 对象会被序列化为包含 `_type` 字段的 JSON 字典，详见 EVENT_STRUCTURE.md

## 高级用法

### 过滤特定事件

只监听整理完成和下载添加事件：
```bash
if [[ "$MP_EVENT_TYPE" =~ ^(transfer.complete|download.added)$ ]]; then
  /usr/local/bin/handle-event.sh
fi
```

### 异步执行长时间任务

```bash
# 后台执行，避免阻塞
/usr/local/bin/long-running-task.sh &
```

### 集成到消息队列

```bash
# 将事件推送到 RabbitMQ
echo "$MP_EVENT_DATA" | \
  curl -X POST "http://localhost:15672/api/queues/%2F/moviepilot/messages" \
    -u guest:guest \
    -H "Content-Type: application/json" \
    -d "{\"payload\":\"$(cat)\",\"encoding\":\"string\"}"
```

## 更新日志

### v1.0.0 (2025-12-21)
- 首次发布
- 支持监听所有广播事件和链式事件
- 支持自定义 Bash 命令执行
- 支持事件类型过滤
- 支持事件日志记录

## 许可证

MIT License

## 作者

Custom

## 相关链接

- [MoviePilot 项目](https://github.com/jxxghp/MoviePilot)
- [事件参数结构文档](./EVENT_STRUCTURE.md)
