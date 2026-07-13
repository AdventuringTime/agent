import sys
from PySide6.QtWidgets import QApplication

from agent_window import AgentWindow, stop_agent_thread

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AgentWindow()
    window.show()
    exit_code = app.exec()
    stop_agent_thread()
    sys.exit(exit_code)
