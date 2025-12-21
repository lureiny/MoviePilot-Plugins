#!/usr/bin/env python3
"""
事件执行器插件 - 单元测试套件

测试覆盖：
1. 插件初始化和配置
2. 所有事件类型的处理
3. 事件过滤逻辑
4. 数据序列化
5. 超时机制
6. 错误处理

运行方法:
    python3 test_unit.py
    或
    python3 -m unittest test_unit.py
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock, call
import json
import subprocess

# Mock MoviePilot dependencies before importing
sys.modules['app'] = MagicMock()
sys.modules['app.core'] = MagicMock()
sys.modules['app.core.event'] = MagicMock()
sys.modules['app.schemas'] = MagicMock()
sys.modules['app.schemas.types'] = MagicMock()
sys.modules['app.plugins'] = MagicMock()
sys.modules['app.log'] = MagicMock()

# Mock EventType enum
from enum import Enum
class MockEventType(str, Enum):
    """Mock EventType for testing"""
    # 转移完成事件
    TransferComplete = "transfer.complete"
    # 下载事件
    DownloadAdded = "download.added"
    DownloadRemoved = "download.removed"
    DownloadFileCompleted = "download.file.completed"
    DownloadHashCompleted = "download.hash.completed"
    # 订阅事件
    SubscribeAdded = "subscribe.added"
    SubscribeComplete = "subscribe.complete"
    SubscribeDeleted = "subscribe.deleted"
    # 插件事件
    PluginReload = "plugin.reload"
    PluginAction = "plugin.action"
    # 系统事件
    SystemError = "system.error"
    SystemWarning = "system.warning"
    # 用户事件
    UserMessage = "user.message"
    # 站点事件
    SiteDeleted = "site.deleted"
    SiteUpdated = "site.updated"
    SiteAdded = "site.added"
    # 命令事件
    CommandExec = "command.exec"
    # Webhook事件
    WebhookMessage = "webhook.message"
    # 名称识别事件
    NameRecognize = "name.recognize"
    # 名称识别请求事件
    NameRecognizeRequest = "name.recognize.request"
    # 刷新媒体库事件
    WebhookRefresh = "webhook.refresh"
    # 订阅搜索事件
    SubscribeSearch = "subscribe.search"
    # 名称识别请求事件
    NameTestRecognize = "name.test.recognize"
    # 种子删除事件
    TorrentRemoved = "torrent.removed"
    # 媒体添加事件
    MediaAdded = "media.added"

sys.modules['app.schemas.types'].EventType = MockEventType

# Mock Event class
class MockEvent:
    def __init__(self, event_type: str, event_data: dict = None):
        self.event_type = event_type
        self.event_data = event_data or {}

sys.modules['app.core.event'].Event = MockEvent

# Mock eventmanager
class MockEventManager:
    @staticmethod
    def register(event_type):
        def decorator(func):
            return func
        return decorator

sys.modules['app.core.event'].eventmanager = MockEventManager()

# Mock _PluginBase
class MockPluginBase:
    def __init__(self):
        pass

    def get_form(self):
        return None

    def get_page(self):
        return None

    def stop_service(self):
        pass

sys.modules['app.plugins']._PluginBase = MockPluginBase

# Mock logger
mock_logger = MagicMock()
sys.modules['app.log'].logger = mock_logger

# Add MoviePilot path for plugin import
moviepilot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, moviepilot_path)


class TestEventExecutorPlugin(unittest.TestCase):
    """事件执行器插件测试类"""

    def setUp(self):
        """测试前准备"""
        # 动态导入插件类
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "eventexecutor",
            os.path.join(os.path.dirname(__file__), "__init__.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.EventExecutor = module.EventExecutor

        # 创建插件实例
        self.plugin = self.EventExecutor()

    def tearDown(self):
        """测试后清理"""
        if hasattr(self.plugin, 'stop_service'):
            self.plugin.stop_service()

    # ==================== 基础功能测试 ====================

    def test_plugin_metadata(self):
        """测试插件元数据"""
        self.assertEqual(self.plugin.plugin_name, "事件执行器")
        self.assertEqual(self.plugin.plugin_version, "1.1.0")
        self.assertEqual(self.plugin.plugin_author, "Custom")
        self.assertTrue(self.plugin.plugin_v2)
        self.assertEqual(self.plugin.auth_level, 1)

    def test_plugin_init_default(self):
        """测试插件默认初始化"""
        self.plugin.init_plugin(None)
        self.assertFalse(self.plugin.get_state())
        self.assertEqual(self.plugin._bash_command, "")
        self.assertEqual(self.plugin._event_type, "")
        self.assertEqual(self.plugin._timeout, 60)
        self.assertFalse(self.plugin._log_events)

    def test_plugin_init_with_config(self):
        """测试插件配置初始化"""
        config = {
            "enabled": True,
            "bash_command": "echo test",
            "event_type": "transfer.complete",
            "timeout": 120,
            "log_events": True
        }
        self.plugin.init_plugin(config)

        self.assertTrue(self.plugin.get_state())
        self.assertEqual(self.plugin._bash_command, "echo test")
        self.assertEqual(self.plugin._event_type, "transfer.complete")
        self.assertEqual(self.plugin._timeout, 120)
        self.assertTrue(self.plugin._log_events)

    def test_plugin_get_form(self):
        """测试配置表单生成"""
        form, defaults = self.plugin.get_form()

        # 检查返回值类型
        self.assertIsInstance(form, list)
        self.assertIsInstance(defaults, dict)

        # 检查默认值
        self.assertEqual(defaults["enabled"], False)
        self.assertEqual(defaults["bash_command"], "")
        self.assertEqual(defaults["event_type"], "")
        self.assertEqual(defaults["timeout"], 60)
        self.assertEqual(defaults["log_events"], False)

    # ==================== 事件过滤测试 ====================

    def test_should_handle_event_all(self):
        """测试监听所有事件"""
        self.plugin._event_type = ""  # 空字符串表示全部事件

        self.assertTrue(self.plugin._should_handle_event("transfer.complete"))
        self.assertTrue(self.plugin._should_handle_event("download.added"))
        self.assertTrue(self.plugin._should_handle_event("subscribe.complete"))
        self.assertTrue(self.plugin._should_handle_event("plugin.action"))

    def test_should_handle_event_specific(self):
        """测试监听特定事件"""
        self.plugin._event_type = "transfer.complete"

        self.assertTrue(self.plugin._should_handle_event("transfer.complete"))
        self.assertFalse(self.plugin._should_handle_event("download.added"))
        self.assertFalse(self.plugin._should_handle_event("subscribe.complete"))

    def test_should_handle_event_none(self):
        """测试未配置事件类型"""
        self.plugin._event_type = None

        # None 会被转换为 False，应该监听所有事件
        self.assertTrue(self.plugin._should_handle_event("transfer.complete"))

    # ==================== 数据序列化测试 ====================

    def test_to_dict_primitives(self):
        """测试基本类型序列化"""
        # 整数
        self.assertEqual(self.EventExecutor._EventExecutor__to_dict(42), 42)
        # 浮点数
        self.assertEqual(self.EventExecutor._EventExecutor__to_dict(3.14), 3.14)
        # 字符串
        self.assertEqual(self.EventExecutor._EventExecutor__to_dict("test"), "test")
        # 布尔值
        self.assertEqual(self.EventExecutor._EventExecutor__to_dict(True), True)
        # None
        self.assertEqual(self.EventExecutor._EventExecutor__to_dict(None), None)

    def test_to_dict_collections(self):
        """测试集合类型序列化"""
        # 字典
        data = {"key": "value", "num": 123}
        result = self.EventExecutor._EventExecutor__to_dict(data)
        self.assertEqual(result, {"key": "value", "num": 123})

        # 列表
        data = [1, 2, 3, "test"]
        result = self.EventExecutor._EventExecutor__to_dict(data)
        self.assertEqual(result, [1, 2, 3, "test"])

        # 元组
        data = (1, 2, 3)
        result = self.EventExecutor._EventExecutor__to_dict(data)
        self.assertEqual(result, (1, 2, 3))

        # 集合
        data = {1, 2, 3}
        result = self.EventExecutor._EventExecutor__to_dict(data)
        self.assertIsInstance(result, list)
        self.assertEqual(set(result), {1, 2, 3})

    def test_to_dict_nested(self):
        """测试嵌套数据结构序列化"""
        data = {
            "mediainfo": {
                "title": "测试",
                "year": 2024,
                "tags": ["动作", "科幻"]
            },
            "files": [
                {"name": "file1.mkv", "size": 1024},
                {"name": "file2.mkv", "size": 2048}
            ]
        }
        result = self.EventExecutor._EventExecutor__to_dict(data)
        self.assertEqual(result["mediainfo"]["title"], "测试")
        self.assertEqual(len(result["files"]), 2)

    def test_to_dict_object_with_to_dict(self):
        """测试具有 to_dict 方法的对象序列化"""
        class MockObject:
            def to_dict(self):
                return {"key": "value"}

        obj = MockObject()
        result = self.EventExecutor._EventExecutor__to_dict(obj)
        self.assertEqual(result, {"key": "value"})

    def test_to_dict_object_with_dict(self):
        """测试具有 __dict__ 属性的对象序列化"""
        class MockObject:
            def __init__(self):
                self.name = "test"
                self.value = 123
                self._private = "hidden"

        obj = MockObject()
        result = self.EventExecutor._EventExecutor__to_dict(obj)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 123)

    def test_to_dict_unknown_type(self):
        """测试未知类型序列化（转为字符串）"""
        # 对象有 __dict__ 时会序列化为字典
        class CustomType:
            def __str__(self):
                return "CustomType instance"

        obj = CustomType()
        result = self.EventExecutor._EventExecutor__to_dict(obj)
        # __dict__ 优先于 __str__，所以返回空字典
        self.assertEqual(result, {})

        # 测试有属性的对象
        obj.value = "test"
        result = self.EventExecutor._EventExecutor__to_dict(obj)
        self.assertEqual(result, {"value": "test"})

    # ==================== 命令执行测试 ====================

    @patch('subprocess.run')
    def test_execute_bash_command_success(self, mock_run):
        """测试 Bash 命令执行成功"""
        # 配置插件
        self.plugin._enabled = True
        self.plugin._bash_command = "echo test"
        self.plugin._timeout = 60

        # Mock subprocess.run 返回成功
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # 创建测试事件
        event = MockEvent(MockEventType.PluginAction, {"action": "test"})

        # 执行命令
        self.plugin._execute_bash_command(event)

        # 验证 subprocess.run 被调用
        mock_run.assert_called_once()
        call_args = mock_run.call_args

        # 验证命令
        self.assertEqual(call_args[0][0], "echo test")

        # 验证参数
        self.assertTrue(call_args[1]['shell'])
        self.assertTrue(call_args[1]['capture_output'])
        self.assertEqual(call_args[1]['timeout'], 60)

        # 验证环境变量
        env = call_args[1]['env']
        self.assertIn('MP_EVENT_TYPE', env)
        self.assertIn('MP_EVENT_DATA', env)
        self.assertIn('MP_EVENT_TIME', env)
        self.assertEqual(env['MP_EVENT_TYPE'], 'plugin.action')

    @patch('subprocess.run')
    def test_execute_bash_command_failure(self, mock_run):
        """测试 Bash 命令执行失败"""
        self.plugin._enabled = True
        self.plugin._bash_command = "exit 1"

        # Mock subprocess.run 返回失败
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error message"
        mock_run.return_value = mock_result

        event = MockEvent(MockEventType.PluginAction, {"action": "test"})

        # 执行命令（不应该抛出异常）
        self.plugin._execute_bash_command(event)

        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_execute_bash_command_timeout(self, mock_run):
        """测试 Bash 命令超时"""
        self.plugin._enabled = True
        self.plugin._bash_command = "sleep 1000"
        self.plugin._timeout = 1

        # Mock subprocess.run 抛出超时异常
        mock_run.side_effect = subprocess.TimeoutExpired("sleep 1000", 1)

        event = MockEvent(MockEventType.PluginAction, {"action": "test"})

        # 执行命令（不应该抛出异常）
        self.plugin._execute_bash_command(event)

        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_execute_bash_command_exception(self, mock_run):
        """测试 Bash 命令执行异常"""
        self.plugin._enabled = True
        self.plugin._bash_command = "invalid command"

        # Mock subprocess.run 抛出异常
        mock_run.side_effect = Exception("Test exception")

        event = MockEvent(MockEventType.PluginAction, {"action": "test"})

        # 执行命令（不应该抛出异常）
        self.plugin._execute_bash_command(event)

        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_execute_bash_command_custom_timeout(self, mock_run):
        """测试自定义超时时间"""
        self.plugin._enabled = True
        self.plugin._bash_command = "echo test"
        self.plugin._timeout = 120  # 自定义 120 秒

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        event = MockEvent(MockEventType.PluginAction, {"action": "test"})
        self.plugin._execute_bash_command(event)

        # 验证使用了自定义超时
        call_args = mock_run.call_args
        self.assertEqual(call_args[1]['timeout'], 120)

    def test_execute_bash_command_no_command(self):
        """测试未配置命令"""
        self.plugin._enabled = True
        self.plugin._bash_command = ""

        event = MockEvent(MockEventType.PluginAction, {"action": "test"})

        # 应该直接返回，不执行任何操作
        with patch('subprocess.run') as mock_run:
            self.plugin._execute_bash_command(event)
            mock_run.assert_not_called()

    # ==================== 事件处理测试 ====================

    def test_on_event_disabled(self):
        """测试插件禁用时不处理事件"""
        self.plugin._enabled = False
        self.plugin._bash_command = "echo test"

        with patch.object(self.plugin, '_execute_bash_command') as mock_exec:
            event = MockEvent(MockEventType.PluginAction, {"action": "test"})
            self.plugin.on_event(event)
            mock_exec.assert_not_called()

    def test_on_event_none(self):
        """测试空事件"""
        self.plugin._enabled = True
        self.plugin._bash_command = "echo test"

        with patch.object(self.plugin, '_execute_bash_command') as mock_exec:
            self.plugin.on_event(None)
            mock_exec.assert_not_called()

    @patch('subprocess.run')
    def test_on_event_filtered(self, mock_run):
        """测试事件过滤"""
        self.plugin._enabled = True
        self.plugin._bash_command = "echo test"
        self.plugin._event_type = "transfer.complete"  # 只监听整理完成

        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # 发送匹配的事件
        event1 = MockEvent(MockEventType.TransferComplete, {})
        self.plugin.on_event(event1)
        self.assertEqual(mock_run.call_count, 1)

        # 发送不匹配的事件
        event2 = MockEvent(MockEventType.DownloadAdded, {})
        self.plugin.on_event(event2)
        self.assertEqual(mock_run.call_count, 1)  # 不应该增加

    # ==================== 各种事件类型测试 ====================

    def create_event_data_samples(self):
        """创建各种事件的示例数据"""
        return {
            MockEventType.TransferComplete: {
                "mediainfo": {"title": "测试电影", "year": "2024", "tmdb_id": 12345},
                "transferinfo": {"target_path": "/media/Movies/Test/test.mkv"},
                "downloader": "qbittorrent"
            },
            MockEventType.DownloadAdded: {
                "hash": "abc123",
                "downloader": "qbittorrent",
                "username": "admin"
            },
            MockEventType.SubscribeAdded: {
                "subscribe_id": 123,
                "username": "admin",
                "mediainfo": {"tmdb_id": 12345, "title": "测试剧集"}
            },
            MockEventType.SubscribeComplete: {
                "subscribe_id": 123,
                "subscribe_info": {"name": "测试剧集", "completed_episode": 12}
            },
            MockEventType.SiteDeleted: {
                "site_id": 1,
                "site_name": "测试站点"
            },
            MockEventType.UserMessage: {
                "channel": "telegram",
                "username": "user",
                "text": "测试消息"
            },
            MockEventType.SystemError: {
                "type": "event",
                "error": "测试错误"
            },
            MockEventType.PluginAction: {
                "action": "test_action"
            }
        }

    @patch('subprocess.run')
    def test_all_event_types(self, mock_run):
        """测试所有事件类型的处理"""
        self.plugin._enabled = True
        self.plugin._bash_command = "echo test"
        self.plugin._event_type = ""  # 监听所有事件

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        event_samples = self.create_event_data_samples()

        for event_type, data in event_samples.items():
            with self.subTest(event_type=event_type):
                event = MockEvent(event_type, data)
                self.plugin.on_event(event)

                # 验证环境变量中的事件数据
                call_args = mock_run.call_args
                env = call_args[1]['env']

                # 验证事件类型
                self.assertEqual(env['MP_EVENT_TYPE'], event_type.value)

                # 验证事件数据是 JSON 格式
                event_data_json = env['MP_EVENT_DATA']
                parsed_data = json.loads(event_data_json)
                self.assertEqual(parsed_data['type'], event_type.value)
                self.assertIn('data', parsed_data)

    @patch('subprocess.run')
    def test_transfer_complete_event_data(self, mock_run):
        """测试整理完成事件的数据结构"""
        self.plugin._enabled = True
        self.plugin._bash_command = "echo test"

        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        event_data = {
            "mediainfo": {
                "title": "测试电影",
                "year": "2024",
                "tmdb_id": 12345,
                "type": "电影"
            },
            "transferinfo": {
                "source_path": "/downloads/test.mkv",
                "target_path": "/media/Movies/Test/test.mkv",
                "file_count": 1
            }
        }

        event = MockEvent(MockEventType.TransferComplete, event_data)
        self.plugin.on_event(event)

        # 获取传递给命令的环境变量
        call_args = mock_run.call_args
        env = call_args[1]['env']
        parsed_data = json.loads(env['MP_EVENT_DATA'])

        # 验证数据结构
        self.assertEqual(parsed_data['type'], 'transfer.complete')
        self.assertEqual(parsed_data['data']['mediainfo']['title'], '测试电影')
        self.assertEqual(parsed_data['data']['transferinfo']['file_count'], 1)

    # ==================== JSON 序列化完整性测试 ====================

    def test_json_serialization_completeness(self):
        """测试 JSON 序列化的完整性"""
        complex_data = {
            "string": "测试字符串",
            "number": 12345,
            "float": 3.14159,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "mixed_list": [1, "two", {"three": 3}]
        }

        event = MockEvent(MockEventType.PluginAction, complex_data)

        # 执行序列化
        event_data_dict = self.EventExecutor._EventExecutor__to_dict(event.event_data)
        event_info = {
            "type": event.event_type.value,
            "data": event_data_dict
        }

        # 验证可以序列化为 JSON
        try:
            json_str = json.dumps(event_info, ensure_ascii=False)
            parsed = json.loads(json_str)

            # 验证数据完整性
            self.assertEqual(parsed['data']['string'], '测试字符串')
            self.assertEqual(parsed['data']['number'], 12345)
            self.assertEqual(parsed['data']['float'], 3.14159)
            self.assertEqual(parsed['data']['bool'], True)
            self.assertIsNone(parsed['data']['none'])
            self.assertEqual(parsed['data']['list'], [1, 2, 3])
            self.assertEqual(parsed['data']['dict']['nested'], 'value')

        except Exception as e:
            self.fail(f"JSON 序列化失败: {e}")


class TestEventExecutorIntegration(unittest.TestCase):
    """集成测试 - 测试插件与事件系统的集成"""

    def setUp(self):
        """测试前准备"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "eventexecutor",
            os.path.join(os.path.dirname(__file__), "__init__.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.EventExecutor = module.EventExecutor
        self.plugin = self.EventExecutor()

    @patch('subprocess.run')
    def test_full_workflow(self, mock_run):
        """测试完整工作流程"""
        # 1. 初始化配置
        config = {
            "enabled": True,
            "bash_command": "echo $MP_EVENT_TYPE >> /tmp/test.log",
            "event_type": "",
            "timeout": 60,
            "log_events": False
        }
        self.plugin.init_plugin(config)

        # 2. 验证配置
        self.assertTrue(self.plugin.get_state())

        # 3. Mock 命令执行
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "transfer.complete\n"
        mock_run.return_value = mock_result

        # 4. 发送事件
        event_data = {
            "mediainfo": {"title": "测试电影"},
            "transferinfo": {"target_path": "/media/test.mkv"}
        }
        event = MockEvent(MockEventType.TransferComplete, event_data)

        # 5. 处理事件
        self.plugin.on_event(event)

        # 6. 验证命令被执行
        mock_run.assert_called_once()

        # 7. 验证环境变量
        call_args = mock_run.call_args
        env = call_args[1]['env']
        self.assertIn('MP_EVENT_TYPE', env)
        self.assertEqual(env['MP_EVENT_TYPE'], 'transfer.complete')

        # 8. 验证数据可以解析
        parsed_data = json.loads(env['MP_EVENT_DATA'])
        self.assertEqual(parsed_data['type'], 'transfer.complete')


def run_tests():
    """运行测试套件"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestEventExecutorPlugin))
    suite.addTests(loader.loadTestsFromTestCase(TestEventExecutorIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("事件执行器插件 - 单元测试套件")
    print("="*70 + "\n")

    success = run_tests()

    print("\n" + "="*70)
    if success:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请检查上述错误信息")
    print("="*70 + "\n")

    sys.exit(0 if success else 1)
