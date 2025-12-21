# 事件执行器插件 - 测试指南

本指南提供了两种测试插件功能的方法，无需等待实际事件发生。

## 测试方法 1: 模拟事件测试（推荐）

使用 Python 脚本发送模拟事件来测试插件功能。

### 步骤 1: 配置插件

在 MoviePilot 管理界面配置插件：

**基础配置**：
- ✅ 启用插件：是
- ✅ 记录事件日志：是（方便调试）
- 🌐 监听的事件类型：全部事件
- ⏱️ 命令超时：60 秒

**Bash 命令**（选择一个）：

**选项 A - 使用测试脚本**（推荐）：
```bash
/data/mp/CustomPlugins/plugins/eventexecutor/test_handler.sh
```

**选项 B - 简单日志**：
```bash
echo "[$MP_EVENT_TYPE] $(date)" >> /tmp/mp-test.log
```

**选项 C - 完整 JSON 日志**：
```bash
echo "$MP_EVENT_DATA" >> /tmp/mp-events-full.log
```

### 步骤 2: 运行测试脚本

进入 MoviePilot 容器或服务器，运行测试脚本：

```bash
# 方法 1: 直接运行
cd /data/mp/CustomPlugins/plugins/eventexecutor
python3 test_plugin.py

# 方法 2: 指定 Python 路径
python3 /data/mp/CustomPlugins/plugins/eventexecutor/test_plugin.py
```

### 步骤 3: 查看测试结果

**查看 MoviePilot 日志**：
```bash
# 搜索插件日志
grep "事件执行器" /path/to/moviepilot/logs/moviepilot.log

# 实时查看日志
tail -f /path/to/moviepilot/logs/moviepilot.log | grep "事件执行器"
```

**查看测试输出文件**：
```bash
# 如果使用了 test_handler.sh
cat /tmp/moviepilot-events-test.log

# 如果使用了简单日志
cat /tmp/mp-test.log

# 如果使用了完整 JSON 日志
cat /tmp/mp-events-full.log
```

### 预期输出

**测试脚本输出**：
```
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪
事件执行器插件 - 模拟测试
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪

============================================================
测试 1: 整理完成事件 (transfer.complete)
============================================================
📤 发送事件: transfer.complete
📦 事件数据: 包含 mediainfo, transferinfo, fileitem, meta
✅ 事件已发送

============================================================
测试 2: 添加下载事件 (download.added)
============================================================
📤 发送事件: download.added
📦 事件数据: hash=abc123def456, downloader=qbittorrent
✅ 事件已发送

...
```

**日志文件输出**（使用 test_handler.sh）：
```
================================================================
[2025-12-21 10:30:45] 收到事件
================================================================
事件类型: transfer.complete
事件时间: 2025-12-21T10:30:45.123456

事件数据 (格式化):
{
  "type": "transfer.complete",
  "data": {
    "mediainfo": {
      "title": "测试电影",
      "year": "2024",
      ...
    }
  }
}

关键信息提取:
  - 媒体标题: 测试电影
  - 年份: 2024
  - 目标路径: /media/Movies/Test Movie (2024)/Test.Movie.2024.1080p.mkv

================================================================
```

---

## 测试方法 2: 手动触发事件

如果你想测试特定事件，可以手动触发。

### 触发整理完成事件

在 MoviePilot 中手动整理一个文件：

1. 上传或复制一个测试视频文件到下载目录
2. 使用 MoviePilot 的"手动整理"功能
3. 整理完成后会自动触发 `transfer.complete` 事件
4. 检查日志或输出文件

### 触发下载添加事件

1. 在 MoviePilot 中添加一个下载任务
2. 会自动触发 `download.added` 事件

### 触发订阅完成事件

1. 创建一个测试订阅
2. 等待订阅完成
3. 会触发 `subscribe.complete` 事件

---

## 常见问题排查

### 问题 1: 没有看到任何输出

**可能原因**：
- 插件未启用
- Bash 命令未配置
- 事件类型过滤设置不正确

**解决方法**：
```bash
# 1. 检查插件状态
grep "事件执行器插件已启用" /path/to/logs/moviepilot.log

# 2. 检查配置
# 在 MoviePilot 管理界面确认配置

# 3. 手动测试 Bash 命令
MP_EVENT_TYPE="test.event" \
MP_EVENT_DATA='{"type":"test","data":{}}' \
MP_EVENT_TIME="2025-12-21T10:00:00" \
bash -c 'echo "Event: $MP_EVENT_TYPE" >> /tmp/test.log'

# 4. 检查测试日志文件
cat /tmp/test.log
```

### 问题 2: 权限错误

**错误信息**：
```
Permission denied: /tmp/mp-test.log
```

**解决方法**：
```bash
# 给日志文件正确的权限
chmod 666 /tmp/mp-test.log

# 或者更改为有权限的目录
# 修改 test_handler.sh 中的 LOG_FILE 变量
```

### 问题 3: jq 未安装

**错误信息**：
```
jq: command not found
```

**解决方法**：
```bash
# Debian/Ubuntu
apt-get install jq

# CentOS/RHEL
yum install jq

# Alpine (Docker)
apk add jq
```

### 问题 4: 命令执行超时

**错误信息**：
```
[事件执行器] 命令执行超时（>60秒）
```

**解决方法**：
- 增加超时时间配置（在插件设置中）
- 优化 Bash 命令，减少执行时间
- 将长时间任务改为后台执行：`your-command &`

---

## 测试脚本说明

### test_plugin.py

**功能**：
- 发送 5 个模拟事件到 MoviePilot
- 包含完整的事件数据结构
- 模拟真实场景的事件

**发送的事件**：
1. `transfer.complete` - 整理完成
2. `download.added` - 添加下载
3. `subscribe.complete` - 订阅完成
4. `plugin.action` - 触发插件动作
5. `system.error` - 系统错误

**数据结构**：
- 完整的 MediaInfo（媒体信息）
- 完整的 TransferInfo（转移信息）
- 完整的 FileItem（文件信息）
- 符合实际事件的数据格式

### test_handler.sh

**功能**：
- 接收事件数据
- 解析 JSON 并提取关键信息
- 记录到日志文件
- 支持多种事件类型

**特点**：
- 自动检测 jq 是否安装
- 根据事件类型提取不同信息
- 格式化输出便于阅读
- 同时输出到文件和标准输出

---

## 调试技巧

### 1. 启用详细日志

在插件配置中启用"记录事件日志"，可以看到：
- 收到的事件类型
- 事件数据内容
- 命令执行结果
- 错误信息

### 2. 测试单个事件

修改 `test_plugin.py`，只运行需要的测试：

```python
if __name__ == "__main__":
    print_test_header()

    # 只测试整理完成事件
    test_transfer_complete_event()

    print_test_summary()
```

### 3. 使用简单命令验证

先用最简单的命令测试：
```bash
echo "OK" >> /tmp/plugin-test.log
```

确认基础功能正常后，再使用复杂的脚本。

### 4. 查看完整事件数据

使用这个命令保存完整的事件数据：
```bash
echo "$MP_EVENT_DATA" | jq '.' > /tmp/event-$(date +%s).json
```

每次事件都会生成一个独立的 JSON 文件，便于分析。

---

## 高级测试

### 测试特定事件类型

1. 在插件配置中选择特定事件类型（如 `transfer.complete`）
2. 运行测试脚本
3. 只有匹配的事件会触发命令执行

### 测试超时功能

1. 配置一个会超时的命令：
   ```bash
   sleep 120  # 睡眠 120 秒
   ```
2. 设置超时时间为 30 秒
3. 运行测试，应该看到超时错误

### 测试错误处理

1. 配置一个会失败的命令：
   ```bash
   exit 1
   ```
2. 运行测试
3. 检查日志中的错误信息

---

## 测试检查清单

测试完成后，确认以下内容：

- [ ] 插件成功接收到所有测试事件
- [ ] Bash 命令被正确执行
- [ ] 事件数据完整且格式正确
- [ ] 环境变量正确传递
- [ ] 日志输出符合预期
- [ ] 超时机制工作正常
- [ ] 错误处理工作正常
- [ ] 事件类型过滤工作正常

---

**测试完成后记得**：
- 清理测试日志文件
- 恢复正常的插件配置
- 将监听事件类型改为需要的类型

祝测试顺利！🎉
