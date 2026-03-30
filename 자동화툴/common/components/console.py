import time
from PyQt6.QtWidgets import QTextEdit, QSizePolicy

class ConsoleWidget(QTextEdit):
    # 메시지 타입별 색상
    COLORS = {
        "info"      : "#000000",
        "success"   : "#2e7d32",
        "warning"   : "#ff8f00",
        "error"     : "#c62828"
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def append_message(self, message: str, msg_type: str = "info"):
        color = self.COLORS.get(msg_type, self.COLORS["info"])
        timestamp = time.strftime("[%H:%M:%S]")
        
        html = (
            f'<span style="color:#888; font-size:11px">{timestamp}</span> '
            f'<span style="color:{color}">{message}</span>'
        )
        
        self.append(html)
        
        # 자동 스크롤
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
    
    def clear_messages(self):
        self.clear()