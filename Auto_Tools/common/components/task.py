import qtawesome as qta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, QSize

from .progress import ProgressWidget
from .console import ConsoleWidget

class TaskWidget(QWidget):
    def __init__(self, title: str = "작업", compact: bool = False):
        super().__init__()
        self.title = title
        self.compact = compact
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.group_box = QGroupBox(self.title)
        group_layout = QVBoxLayout(self.group_box)
        
        # 1. 입력 영역 (PathInput 등이 들어감)
        self.input_area = QVBoxLayout()
        group_layout.addLayout(self.input_area)
        
        # 2. 실행 및 진행 영역 (한 줄로 배치)
        execution_row = QHBoxLayout()
        execution_row.setSpacing(12)
        
        self.progress = ProgressWidget()
        execution_row.addWidget(self.progress, 1) # 진행바가 왼쪽 공간 차지
        
        self.execute_btn = QPushButton("실행")
        self.execute_btn.setIcon(qta.icon('fa5s.play', color='white'))
        self.execute_btn.setProperty("primaryButton", True)
        self.execute_btn.setFixedSize(110, 40) # 버튼을 좀 더 크고 확실하게
        execution_row.addWidget(self.execute_btn, 0, Qt.AlignmentFlag.AlignTop)
        
        group_layout.addLayout(execution_row)
        
        # 3. 콘솔 영역
        self.console = ConsoleWidget()
        self.console.setMinimumHeight(150) # 최소 높이 지정
        group_layout.addWidget(self.console)
        
        layout.addWidget(self.group_box)
        if not self.compact: layout.addStretch()
    
    def add_input_widget(self, widget: QWidget):
        self.input_area.addWidget(widget)