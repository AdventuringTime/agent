from datetime import datetime

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QPushButton, QScrollArea,
                               QLabel)
from PySide6.QtCore import Qt
try:
    from agent_thread import get_agent_thread, stop_agent_thread
except ImportError:
    from .agent_thread import get_agent_thread, stop_agent_thread

__all__ = ['AgentWindow', 'stop_agent_thread']

try:
    from core.base_objects import BaseWindow
except ImportError:
    from PySide6.QtWidgets import QMainWindow as BaseWindow


class AgentWindow(BaseWindow):
    """
    Agent对话窗口类，提供对话界面和日志查看功能

    特性：
    - 单例模式，确保只有一个窗口实例
    - 支持从主程序或独立运行
    - 对话区域使用布局实现，用户消息带背景框
    - 日志面板可通过按钮打开
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """
        单例模式实现，确保只有一个窗口实例

        Returns:
            AgentWindow: 窗口实例
        """
        if cls._instance is not None:
            if cls._instance.isMinimized():
                cls._instance.showNormal()
            cls._instance.raise_()
            cls._instance.activateWindow()
            return cls._instance
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, parent=None):
        """
        初始化Agent窗口

        Parameters:
            parent (QWidget, optional): 父窗口，默认为None
        """
        if AgentWindow._initialized:
            return
        super().__init__(parent)
        self.setWindowTitle("Agent")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        self.thinking_mode = False
        self.pro_mode = False

        self.agent_thread = get_agent_thread()
        self.agent_thread.response_received.connect(self.handle_response)
        self.agent_thread.error_occurred.connect(self.handle_error)
        self.agent_thread.create_session()

        self.init_ui()

        AgentWindow._instance = self
        AgentWindow._initialized = True

    def init_ui(self):
        """初始化窗口界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.init_conversation_area(self.main_layout)
        self.init_input_area(self.main_layout)
        self.init_log_dock()

    def init_conversation_area(self, parent_layout):
        """
        初始化对话区域，使用滚动区域和垂直布局实现

        Parameters:
            parent_layout (QLayout): 父布局
        """
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
        """)

        self.conversation_container = QWidget()
        self.conversation_layout = QVBoxLayout(self.conversation_container)
        self.conversation_layout.addStretch()

        self.scroll_area.setWidget(self.conversation_container)
        parent_layout.addWidget(self.scroll_area)

    def init_input_area(self, parent_layout):
        """
        初始化输入区域，包含多行文本框和按钮

        Parameters:
            parent_layout (QLayout): 父布局
        """
        input_layout = QVBoxLayout()

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("输入消息...")
        self.input_edit.setMaximumHeight(150)
        self.input_edit.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                color: #FFFFFF;
                font-size: 14px;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        input_layout.addWidget(self.input_edit)

        button_layout = QHBoxLayout()

        self.log_button = QPushButton("日志")
        self.log_button.clicked.connect(self.open_log)
        button_layout.addWidget(self.log_button)

        self.thinking_button = QPushButton("深度思考")
        self.thinking_button.setCheckable(True)
        self.thinking_button.clicked.connect(self.toggle_thinking_mode)
        button_layout.addWidget(self.thinking_button)

        self.pro_button = QPushButton("专家模式")
        self.pro_button.setCheckable(True)
        self.pro_button.clicked.connect(self.toggle_pro_mode)
        button_layout.addWidget(self.pro_button)

        button_layout.addStretch()

        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)

        input_layout.addLayout(button_layout)
        parent_layout.addLayout(input_layout)

    def toggle_thinking_mode(self):
        """切换深度思考模式"""
        self.thinking_mode = self.thinking_button.isChecked()

    def toggle_pro_mode(self):
        """切换专家模式"""
        self.pro_mode = self.pro_button.isChecked()

    def init_log_dock(self):
        """初始化日志面板"""
        from PySide6.QtWidgets import QDockWidget

        self.log_dock = QDockWidget("日志", self)
        self.log_dock.setMinimumWidth(300)

        self.log_scroll_area = QScrollArea()
        self.log_scroll_area.setWidgetResizable(True)
        self.log_container = QWidget()
        self.log_layout = QVBoxLayout(self.log_container)
        self.log_layout.setSpacing(10)
        self.log_layout.addStretch()

        self.log_scroll_area.setWidget(self.log_container)
        self.log_dock.setWidget(self.log_scroll_area)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.log_dock)
        self.log_dock.hide()

    def open_log(self):
        """打开日志面板"""
        self.log_dock.show()

    def send_message(self):
        """
        发送消息，将用户输入添加到对话区域，并通过线程队列异步调用Agent获取回复
        """
        text = self.input_edit.toPlainText().strip()
        if not text:
            return

        self.add_message("user_text", text)
        final_text = "元数据：\n当前时间 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n用户输入：\n" + text
        self.add_log("input", f"thinking:{self.thinking_mode}, pro:{self.pro_mode}\n{final_text}")

        thinking_enabled = self.thinking_mode
        pro_enabled = self.pro_mode

        self.thinking_button.setChecked(False)
        self.thinking_mode = False
        self.pro_button.setChecked(False)
        self.pro_mode = False

        self.input_edit.clear()

        self.agent_thread.send_message(final_text, pro_enabled, thinking_enabled)

    def handle_response(self, response):
        """
        处理Agent响应

        Parameters:
            response: Agent响应对象
        """
        try:
            for block in response.content:
                if block.type == "thinking":
                    self.add_log("thinking", block.thinking)
                elif block.type == "text":
                    assistant_text = block.text
                    self.add_message("assistant_text", assistant_text)
                    self.add_log("output", assistant_text)
                else:
                    self.add_log("error", f"Unexpected block type: {block.type}", "red")

            if response.stop_reason in ['end_turn', 'max_tokens', 'stop_sequence']:
                usage_str = f"usage:" \
                           f"cache_read_input_tokens={response.usage.cache_read_input_tokens}, " \
                           f"input_tokens={response.usage.input_tokens}, " \
                           f"output_tokens={response.usage.output_tokens}"
                self.add_log("usage", usage_str)
            else:
                self.add_log("warning", f"stop_reason: {response.stop_reason}", "yellow")
        except Exception:
            import traceback
            try:
                from core.error_window import show_error_window
                show_error_window(None, traceback.format_exc(), self)
            except ImportError:
                pass
            self.add_log("error", traceback.format_exc(), "red")

    def handle_error(self, error_message):
        """
        处理线程错误

        Parameters:
            error_message (str): 错误信息
        """
        try:
            from core.error_window import show_error_window
            show_error_window(None, error_message, self)
        except ImportError:
            pass
        self.add_log("error", error_message, "red")

    def add_message(self, message_type, text):
        """
        添加消息到对话区域

        Parameters:
            message_type (str): 消息类型，"user_text" 或 "assistant_text"
            text (str): 消息内容

        Raises:
            ValueError: 如果 message_type 不是 "user_text" 或 "assistant_text"
        """
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 5, 0, 5)

        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        if message_type == "user_text":
            text_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-size: 14px;
                    background-color: #2A2A2A;
                    border-radius: 8px;
                    padding: 8px 12px;
                }
            """)
        elif message_type == "assistant_text":
            text_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-size: 14px;
                }
            """)
        else:
            raise ValueError(f"Unknown message_type: {message_type}")
        message_layout.addWidget(text_label)
        # 该框架下尝试使 text_label 只占部分空间对齐会导致异常的自动换行

        self.conversation_layout.insertWidget(self.conversation_layout.count() - 1, message_widget)

    def add_log(self, log_type, text, style=None):
        """
        添加日志到日志面板

        Parameters:
            log_type (str): 日志类型，如 "input", "thinking", "output"
            text (str): 日志内容
            style (str, optional): 日志标签颜色样式，如 "yellow", "red" 默认 None
        """
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(2)

        type_label = QLabel(log_type)
        type_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if style == "yellow":
            type_label.setStyleSheet("""
                QLabel {
                    color: #FFD700;
                    font-size: 12px;
                    font-family: Consolas, Monaco, monospace;
                }
            """)
        elif style == "red":
            type_label.setStyleSheet("""
                QLabel {
                    color: #FF0000;
                    font-size: 12px;
                    font-family: Consolas, Monaco, monospace;
                }
            """)
        else:
            type_label.setStyleSheet("""
                QLabel {
                    color: #007AFF;
                    font-size: 12px;
                    font-family: Consolas, Monaco, monospace;
                }
            """)

        text_label = QLabel(text)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 12px;
                font-family: Consolas, Monaco, monospace;
            }
        """)

        log_layout.addWidget(type_label)
        log_layout.addWidget(text_label)
        self.log_layout.addWidget(log_widget)

    def scroll_to_bottom(self):
        """滚动对话区域到底部"""
        if hasattr(self.scroll_area, 'verticalScrollBar'):
            scroll_bar = self.scroll_area.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

    def closeEvent(self, event):
        """
        窗口关闭事件处理

        Parameters:
            event (QCloseEvent): 关闭事件对象
        """
        if hasattr(self, 'agent_thread'):
            self.agent_thread.destroy_session()

        super().closeEvent(event)
        AgentWindow._instance = None
        AgentWindow._initialized = False
