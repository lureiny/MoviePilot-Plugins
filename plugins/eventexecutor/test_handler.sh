#!/bin/bash
#
# 事件执行器插件 - 测试用 Bash 脚本
#
# 用法:
#   在插件配置中设置此脚本的完整路径
#   例如: /data/mp/CustomPlugins/plugins/eventexecutor/test_handler.sh
#
# 功能:
#   - 记录所有接收到的事件到日志文件
#   - 解析事件数据并提取关键信息
#   - 输出到标准输出和日志文件

# 日志文件路径（可修改）
LOG_FILE="/tmp/moviepilot-events-test.log"

# 获取当前时间
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 写入分隔线
echo "================================================================" >> "$LOG_FILE"
echo "[$TIMESTAMP] 收到事件" >> "$LOG_FILE"
echo "================================================================" >> "$LOG_FILE"

# 记录事件类型
echo "事件类型: $MP_EVENT_TYPE" >> "$LOG_FILE"
echo "事件时间: $MP_EVENT_TIME" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 检查是否安装了 jq（用于解析 JSON）
if command -v jq &> /dev/null; then
    echo "事件数据 (格式化):" >> "$LOG_FILE"
    echo "$MP_EVENT_DATA" | jq '.' >> "$LOG_FILE" 2>&1

    # 提取一些关键信息
    echo "" >> "$LOG_FILE"
    echo "关键信息提取:" >> "$LOG_FILE"

    # 根据事件类型提取不同的信息
    case "$MP_EVENT_TYPE" in
        "transfer.complete")
            MEDIA_TITLE=$(echo "$MP_EVENT_DATA" | jq -r '.data.mediainfo.title // "N/A"')
            MEDIA_YEAR=$(echo "$MP_EVENT_DATA" | jq -r '.data.mediainfo.year // "N/A"')
            TARGET_PATH=$(echo "$MP_EVENT_DATA" | jq -r '.data.transferinfo.target_path // "N/A"')
            echo "  - 媒体标题: $MEDIA_TITLE" >> "$LOG_FILE"
            echo "  - 年份: $MEDIA_YEAR" >> "$LOG_FILE"
            echo "  - 目标路径: $TARGET_PATH" >> "$LOG_FILE"
            ;;

        "download.added")
            HASH=$(echo "$MP_EVENT_DATA" | jq -r '.data.hash // "N/A"')
            DOWNLOADER=$(echo "$MP_EVENT_DATA" | jq -r '.data.downloader // "N/A"')
            echo "  - 种子哈希: $HASH" >> "$LOG_FILE"
            echo "  - 下载器: $DOWNLOADER" >> "$LOG_FILE"
            ;;

        "subscribe.complete")
            SUBSCRIBE_ID=$(echo "$MP_EVENT_DATA" | jq -r '.data.subscribe_id // "N/A"')
            MEDIA_TITLE=$(echo "$MP_EVENT_DATA" | jq -r '.data.mediainfo.title // "N/A"')
            echo "  - 订阅ID: $SUBSCRIBE_ID" >> "$LOG_FILE"
            echo "  - 媒体标题: $MEDIA_TITLE" >> "$LOG_FILE"
            ;;

        *)
            echo "  - 事件类型: $MP_EVENT_TYPE" >> "$LOG_FILE"
            ;;
    esac
else
    # 如果没有 jq，直接输出原始 JSON
    echo "事件数据 (原始 JSON):" >> "$LOG_FILE"
    echo "$MP_EVENT_DATA" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "提示: 安装 jq 可获得更好的格式化输出" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "================================================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 同时输出到标准输出（会被插件记录到日志）
echo "✅ 事件已记录: $MP_EVENT_TYPE -> $LOG_FILE"

# 返回成功
exit 0
