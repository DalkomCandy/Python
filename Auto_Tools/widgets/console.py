import time
from PyQt6.QtWidgets import QTextEdit, QSizePolicy
from utils.colors import AppColors


class ConsoleWidget(QTextEdit):
    COLORS = AppColors.CONSOLE

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def append_message(self, message: str, msg_type: str = "info"):
        color = self.COLORS.get(msg_type, self.COLORS["info"])
        ts    = time.strftime("[%H:%M:%S]")
        self.append(
            f'<span style="color:#888;font-size:11px">{ts}</span> '
            f'<span style="color:{color}">{message}</span>'
        )
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear_messages(self):
        self.clear()
