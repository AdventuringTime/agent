from PySide6.QtCore import QThread, Signal
import queue
import os
import traceback


try:
    from agent import Agent, Session
except ImportError:
    from .agent import Agent, Session


_global_agent_thread = None


def _load_system_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_agent_thread():
    global _global_agent_thread
    if _global_agent_thread is None:
        _global_agent_thread = AgentThread()
        try:
            from core.base_objects import ThreadManager
            ThreadManager().register_thread(_global_agent_thread)
        except ImportError:
            pass
        _global_agent_thread.start()
    return _global_agent_thread


def stop_agent_thread():
    global _global_agent_thread
    if _global_agent_thread is not None:
        _global_agent_thread.stop()
        _global_agent_thread.wait()
        _global_agent_thread = None


class AgentThread(QThread):
    response_received = Signal(object)
    session_created = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.message_queue = queue.Queue()
        self.agent = None
        self.session = None

    def run(self):
        self.agent = Agent(system_prompt=_load_system_prompt())
        self._running = True

        while self._running:
            try:
                message_data = self.message_queue.get(timeout=1)
                if message_data is None:
                    break

                message_type = message_data[0]

                if message_type == 'create_session':
                    self.session = self.agent.create_session()
                    self.session_created.emit()

                elif message_type == 'destroy_session':
                    self.session = None

                elif message_type == 'chat':
                    _, message, pro_enabled, thinking_enabled = message_data
                    if self.session is not None:
                            response = self.session.chat(message, pro=pro_enabled, thinking=thinking_enabled)
                            self.response_received.emit(response)

            except queue.Empty:
                continue
            except Exception:
                self.error_occurred.emit(traceback.format_exc())

        self.agent = None
        self.session = None

    def create_session(self):
        self.message_queue.put(('create_session',))

    def destroy_session(self):
        self.message_queue.put(('destroy_session',))

    def send_message(self, message, pro_enabled, thinking_enabled):
        self.message_queue.put(('chat', message, pro_enabled, thinking_enabled))

    def stop(self):
        self._running = False
        self.message_queue.put(None)

    def quit(self):
        self.stop()
        super().quit()
