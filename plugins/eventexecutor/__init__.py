import json
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.core.event import Event, eventmanager
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType


class EventExecutor(_PluginBase):
    # 插件名称
    plugin_name = "事件执行器"
    # 插件描述
    plugin_desc = "监听系统事件，将事件数据作为环境变量传递给自定义 Bash 命令执行。"
    # 插件图标
    plugin_icon = "executor.png"
    # 插件版本
    plugin_version = "1.1.0"
    # 插件作者
    plugin_author = "Custom"
    # 作者主页
    author_url = "https://github.com/lureiny"
    # 插件配置项ID前缀
    plugin_config_prefix = "eventexecutor_"
    # 加载顺序
    plugin_order = 99
    # 可使用的用户级别
    auth_level = 1
    # V2 插件
    plugin_v2 = True

    # 私有属性
    _enabled: bool = False
    _bash_command: str = ""
    _event_type: str = ""  # 单个事件类型（单选）
    _timeout: int = 60  # 命令执行超时时间（秒）
    _log_events: bool = False

    def init_plugin(self, config: dict = None):
        """初始化插件"""
        if config:
            self._enabled = config.get("enabled", False)
            self._bash_command = config.get("bash_command", "")
            self._event_type = config.get("event_type", "")
            self._timeout = config.get("timeout", 60)
            self._log_events = config.get("log_events", False)

        if self._enabled:
            logger.info("事件执行器插件已启用")
            if self._bash_command:
                logger.info(f"执行命令：{self._bash_command}")
            if self._event_type:
                logger.info(f"监听事件：{self._event_type}")
            else:
                logger.info("监听所有广播事件")
            logger.info(f"命令超时时间：{self._timeout}秒")

    def get_state(self) -> bool:
        """获取插件状态"""
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """注册远程命令"""
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        """注册 API"""
        pass

    def get_service(self) -> List[Dict[str, Any]]:
        """注册服务"""
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """配置表单"""
        # 所有广播事件类型选项（单选下拉列表）
        event_options = [
            {"title": "🌐 全部事件", "value": ""},  # 空字符串表示全部事件
            {"title": "插件重载 (plugin.reload)", "value": "plugin.reload"},
            {"title": "触发插件动作 (plugin.action)", "value": "plugin.action"},
            {"title": "触发插件事件 (plugin.triggered)", "value": "plugin.triggered"},
            {"title": "执行命令 (command.excute)", "value": "command.excute"},
            {"title": "站点已删除 (site.deleted)", "value": "site.deleted"},
            {"title": "站点已更新 (site.updated)", "value": "site.updated"},
            {"title": "站点已刷新 (site.refreshed)", "value": "site.refreshed"},
            {"title": "⭐ 整理完成 (transfer.complete)", "value": "transfer.complete"},
            {"title": "⭐ 添加下载 (download.added)", "value": "download.added"},
            {"title": "删除历史记录 (history.deleted)", "value": "history.deleted"},
            {"title": "删除下载源文件 (downloadfile.deleted)", "value": "downloadfile.deleted"},
            {"title": "删除下载任务 (download.deleted)", "value": "download.deleted"},
            {"title": "收到用户消息 (user.message)", "value": "user.message"},
            {"title": "收到Webhook消息 (webhook.message)", "value": "webhook.message"},
            {"title": "发送消息通知 (notice.message)", "value": "notice.message"},
            {"title": "⭐ 添加订阅 (subscribe.added)", "value": "subscribe.added"},
            {"title": "订阅已调整 (subscribe.modified)", "value": "subscribe.modified"},
            {"title": "订阅已删除 (subscribe.deleted)", "value": "subscribe.deleted"},
            {"title": "⭐ 订阅已完成 (subscribe.complete)", "value": "subscribe.complete"},
            {"title": "系统错误 (system.error)", "value": "system.error"},
            {"title": "刮削元数据 (metadata.scrape)", "value": "metadata.scrape"},
            {"title": "模块重载 (module.reload)", "value": "module.reload"},
            {"title": "配置项更新 (config.updated)", "value": "config.updated"},
            {"title": "消息交互动作 (message.action)", "value": "message.action"},
            {"title": "执行工作流 (workflow.execute)", "value": "workflow.execute"},
        ]

        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'log_events',
                                            'label': '记录事件日志',
                                            'hint': '在日志中记录捕获的事件',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'timeout',
                                            'label': '命令超时（秒）',
                                            'type': 'number',
                                            'hint': '命令执行超时时间',
                                            'persistent-hint': True
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'event_type',
                                            'label': '监听的事件类型',
                                            'hint': '选择要监听的单个事件类型，或选择"全部事件"',
                                            'persistent-hint': True,
                                            'clearable': True,
                                            'items': event_options
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VTextarea',
                                        'props': {
                                            'model': 'bash_command',
                                            'label': 'Bash 命令',
                                            'placeholder': 'echo "Event: $MP_EVENT_TYPE" >> /var/log/mp-events.log',
                                            'hint': '事件数据通过环境变量传递：MP_EVENT_TYPE, MP_EVENT_DATA, MP_EVENT_TIME',
                                            'persistent-hint': True,
                                            'rows': 3
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12},
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'style': 'white-space: pre-line;',
                                            'text': '💡 环境变量说明：\n'
                                                    '• MP_EVENT_TYPE：事件类型（如 transfer.complete）\n'
                                                    '• MP_EVENT_DATA：事件数据（JSON 格式）\n'
                                                    '• MP_EVENT_TIME：事件触发时间（ISO 格式）\n\n'
                                                    '⚠️ 注意事项：\n'
                                                    '• 建议使用 jq 工具解析 JSON 数据\n'
                                                    '• 查看插件目录下的 README.md 获取详细示例\n'
                                                    '• ⭐ 标记的事件是最常用的事件类型'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "bash_command": "",
            "event_type": "",  # 默认为空（全部事件）
            "timeout": 60,
            "log_events": False
        }

    def get_page(self) -> List[dict]:
        """插件页面"""
        pass

    def stop_service(self):
        """停止服务"""
        pass

    @staticmethod
    def __to_dict(obj: Any) -> Any:
        """
        递归将对象转换为字典（参考官方 webhook 插件实现）
        """
        if isinstance(obj, dict):
            return {k: EventExecutor.__to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [EventExecutor.__to_dict(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(EventExecutor.__to_dict(list(obj)))
        elif isinstance(obj, set):
            return list(EventExecutor.__to_dict(list(obj)))
        elif hasattr(obj, 'to_dict'):
            return EventExecutor.__to_dict(obj.to_dict())
        elif hasattr(obj, '__dict__'):
            return EventExecutor.__to_dict(obj.__dict__)
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)

    def _should_handle_event(self, event_type: str) -> bool:
        """
        判断是否应该处理该事件
        空字符串表示监听所有事件
        """
        if not self._event_type:
            # 未配置或配置为空字符串，处理所有事件
            return True
        # 精确匹配配置的事件类型
        return event_type == self._event_type

    def _execute_bash_command(self, event: Event):
        """
        执行 Bash 命令
        将事件信息作为环境变量传递
        """
        if not self._bash_command:
            return

        # 转换事件数据为字典
        event_data_dict = self.__to_dict(event.event_data)

        # 构建事件信息（参考 webhook 插件的格式）
        event_info = {
            "type": event.event_type.value,
            "data": event_data_dict
        }

        # 序列化为 JSON
        try:
            event_data_json = json.dumps(event_info, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[事件执行器] 事件数据序列化失败：{str(e)}")
            return

        # 准备环境变量
        env = os.environ.copy()
        env['MP_EVENT_TYPE'] = event.event_type.value
        env['MP_EVENT_DATA'] = event_data_json
        env['MP_EVENT_TIME'] = datetime.now().isoformat()

        if self._log_events:
            logger.info(f"[事件执行器] 事件类型：{event.event_type.value}")
            logger.debug(f"[事件执行器] 事件数据：\n{event_data_json}")

        try:
            # 执行命令，使用配置的超时时间
            result = subprocess.run(
                self._bash_command,
                shell=True,
                env=env,
                capture_output=True,
                text=True,
                timeout=self._timeout
            )

            if result.returncode != 0:
                logger.error(
                    f"[事件执行器] 命令执行失败 (退出码 {result.returncode})：\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )
            elif self._log_events and result.stdout:
                logger.info(f"[事件执行器] 命令输出：\n{result.stdout}")

        except subprocess.TimeoutExpired:
            logger.error(f"[事件执行器] 命令执行超时（>{self._timeout}秒）")
        except Exception as e:
            logger.error(f"[事件执行器] 命令执行异常：{str(e)}")

    @eventmanager.register(EventType)
    def on_event(self, event: Event = None):
        """
        监听所有广播事件（参考官方 webhook 插件）
        """
        if not self._enabled or not event or not event.event_type:
            return

        # 检查是否应该处理此事件
        if not self._should_handle_event(event.event_type.value):
            return

        # 执行 bash 命令
        self._execute_bash_command(event)
