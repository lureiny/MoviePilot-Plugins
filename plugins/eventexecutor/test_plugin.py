#!/usr/bin/env python3
"""
事件执行器插件测试脚本

用法:
    python test_plugin.py

说明:
    这个脚本会模拟发送各种事件来测试插件功能，无需实际的人机交互。
    测试前请确保:
    1. 插件已安装到 MoviePilot
    2. 插件已启用
    3. 配置了正确的 Bash 命令
"""

import sys
import os

# 添加 MoviePilot 路径到 Python 路径
moviepilot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, moviepilot_path)

from app.core.event import eventmanager, Event
from app.schemas.types import EventType


def create_mock_mediainfo():
    """创建模拟的 MediaInfo 对象"""
    class MockMediaInfo:
        def __init__(self):
            self.tmdb_id = 12345
            self.title = "测试电影"
            self.original_title = "Test Movie"
            self.year = "2024"
            self.type = "电影"
            self.overview = "这是一个测试电影的简介"
            self.poster_path = "/test/poster.jpg"
            self.backdrop_path = "/test/backdrop.jpg"
            self.vote_average = 8.5

        def to_dict(self):
            return {
                "tmdb_id": self.tmdb_id,
                "title": self.title,
                "original_title": self.original_title,
                "year": self.year,
                "type": self.type,
                "overview": self.overview,
                "poster_path": self.poster_path,
                "backdrop_path": self.backdrop_path,
                "vote_average": self.vote_average
            }

    return MockMediaInfo()


def create_mock_transferinfo():
    """创建模拟的 TransferInfo 对象"""
    class MockDirItem:
        def __init__(self, path, name):
            self.path = path
            self.name = name

    class MockTransferInfo:
        def __init__(self):
            self.source_path = "/downloads/Test.Movie.2024.1080p.mkv"
            self.source_filename = "Test.Movie.2024.1080p.mkv"
            self.target_path = "/media/Movies/Test Movie (2024)/Test.Movie.2024.1080p.mkv"
            self.target_diritem = MockDirItem("/media/Movies/Test Movie (2024)", "Test Movie (2024)")
            self.file_count = 1
            self.total_size = 5368709120  # 5GB
            self.file_list = ["/downloads/Test.Movie.2024.1080p.mkv"]
            self.file_list_new = ["/media/Movies/Test Movie (2024)/Test.Movie.2024.1080p.mkv"]

    return MockTransferInfo()


def create_mock_fileitem():
    """创建模拟的 FileItem 对象"""
    class MockFileItem:
        def __init__(self):
            self.path = "/downloads/Test.Movie.2024.1080p.mkv"
            self.name = "Test.Movie.2024.1080p.mkv"
            self.size = 5368709120
            self.extension = ".mkv"

    return MockFileItem()


def create_mock_meta():
    """创建模拟的 MetaInfo 对象"""
    class MockMeta:
        def __init__(self):
            self.title = "测试电影"
            self.year = "2024"
            self.season = None
            self.episode = None

    return MockMeta()


def test_transfer_complete_event():
    """测试整理完成事件"""
    print("\n" + "="*60)
    print("测试 1: 整理完成事件 (transfer.complete)")
    print("="*60)

    event_data = {
        "fileitem": create_mock_fileitem(),
        "meta": create_mock_meta(),
        "mediainfo": create_mock_mediainfo(),
        "transferinfo": create_mock_transferinfo(),
        "downloader": "qbittorrent"
    }

    print(f"📤 发送事件: {EventType.TransferComplete.value}")
    print(f"📦 事件数据: 包含 mediainfo, transferinfo, fileitem, meta")

    # 发送事件
    eventmanager.send_event(EventType.TransferComplete, event_data)

    print("✅ 事件已发送")
    print("💡 提示: 检查日志查看插件是否执行了 Bash 命令")


def test_download_added_event():
    """测试下载添加事件"""
    print("\n" + "="*60)
    print("测试 2: 添加下载事件 (download.added)")
    print("="*60)

    class MockContext:
        def __init__(self):
            self.meta_info = {"title": "测试电影", "year": "2024"}
            self.media_info = create_mock_mediainfo()
            self.torrent_info = {
                "title": "Test.Movie.2024.1080p.BluRay.x264-GROUP",
                "size": 5368709120,
                "seeders": 100,
                "site_name": "测试站点"
            }

    event_data = {
        "hash": "abc123def456",
        "context": MockContext(),
        "username": "admin",
        "downloader": "qbittorrent"
    }

    print(f"📤 发送事件: {EventType.DownloadAdded.value}")
    print(f"📦 事件数据: hash={event_data['hash']}, downloader={event_data['downloader']}")

    eventmanager.send_event(EventType.DownloadAdded, event_data)

    print("✅ 事件已发送")


def test_subscribe_complete_event():
    """测试订阅完成事件"""
    print("\n" + "="*60)
    print("测试 3: 订阅完成事件 (subscribe.complete)")
    print("="*60)

    event_data = {
        "subscribe_id": 123,
        "subscribe_info": {
            "id": 123,
            "name": "测试电视剧",
            "year": "2024",
            "type": "电视剧",
            "tmdbid": 67890,
            "season": 1,
            "total_episode": 12,
            "completed_episode": 12
        },
        "mediainfo": {
            "tmdb_id": 67890,
            "title": "测试电视剧",
            "type": "电视剧"
        }
    }

    print(f"📤 发送事件: {EventType.SubscribeComplete.value}")
    print(f"📦 事件数据: subscribe_id={event_data['subscribe_id']}")

    eventmanager.send_event(EventType.SubscribeComplete, event_data)

    print("✅ 事件已发送")


def test_plugin_action_event():
    """测试插件动作事件"""
    print("\n" + "="*60)
    print("测试 4: 触发插件动作事件 (plugin.action)")
    print("="*60)

    event_data = {
        "action": "test_action",
        "username": "admin"
    }

    print(f"📤 发送事件: {EventType.PluginAction.value}")
    print(f"📦 事件数据: action={event_data['action']}")

    eventmanager.send_event(EventType.PluginAction, event_data)

    print("✅ 事件已发送")


def test_system_error_event():
    """测试系统错误事件"""
    print("\n" + "="*60)
    print("测试 5: 系统错误事件 (system.error)")
    print("="*60)

    event_data = {
        "type": "event",
        "event_type": "transfer.complete",
        "event_handle": "TestClass.test_method",
        "error": "这是一个测试错误",
        "traceback": "Traceback (most recent call last):\n  File test.py, line 1, in <module>\n    raise Exception('Test')"
    }

    print(f"📤 发送事件: {EventType.SystemError.value}")
    print(f"📦 事件数据: error={event_data['error']}")

    eventmanager.send_event(EventType.SystemError, event_data)

    print("✅ 事件已发送")


def print_test_header():
    """打印测试头部信息"""
    print("\n" + "🧪"*30)
    print("事件执行器插件 - 模拟测试")
    print("🧪"*30)
    print("\n📋 测试说明:")
    print("1. 确保插件已在 MoviePilot 中安装并启用")
    print("2. 配置 Bash 命令，例如:")
    print("   echo \"$MP_EVENT_DATA\" >> /tmp/mp-test-events.log")
    print("3. 运行此脚本将发送多个模拟事件")
    print("4. 检查日志或输出文件确认插件是否正常工作")
    print("\n⚙️  推荐配置:")
    print("- 启用插件: 是")
    print("- 记录事件日志: 是")
    print("- 监听的事件类型: 🌐 全部事件")
    print("- Bash 命令: echo \"[$MP_EVENT_TYPE] $(date)\" >> /tmp/mp-test.log")
    print("- 命令超时: 60 秒")


def print_test_summary():
    """打印测试总结"""
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print("✅ 已发送 5 个模拟事件:")
    print("   1. transfer.complete (整理完成)")
    print("   2. download.added (添加下载)")
    print("   3. subscribe.complete (订阅完成)")
    print("   4. plugin.action (触发插件动作)")
    print("   5. system.error (系统错误)")
    print("\n🔍 验证方法:")
    print("1. 查看 MoviePilot 日志，搜索 '[事件执行器]'")
    print("2. 检查配置的输出文件（如 /tmp/mp-test.log）")
    print("3. 确认每个事件都触发了 Bash 命令执行")
    print("\n💡 如果没有看到输出:")
    print("- 检查插件是否已启用")
    print("- 检查是否配置了 Bash 命令")
    print("- 检查事件类型过滤设置")
    print("- 查看日志中的错误信息")
    print("\n" + "="*60 + "\n")


def main():
    """主函数"""
    try:
        print_test_header()

        # 运行所有测试
        test_transfer_complete_event()
        test_download_added_event()
        test_subscribe_complete_event()
        test_plugin_action_event()
        test_system_error_event()

        print_test_summary()

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
