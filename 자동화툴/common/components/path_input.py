import qtawesome as qta
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from config import AppConfig


class PathInputWidget(QWidget):
    path_changed = pyqtSignal(str)
    
    def __init__(self, label: str, placeholder: str, setting_key: str = None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setting_key = setting_key
        self.init_ui(label, placeholder)
        
        if self.setting_key:
            self.load_path()
    
    # path_input.py 일부 수정
    def init_ui(self, label: str, placeholder: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # 상하 여백 추가
        layout.setSpacing(6) # 컴포넌트 간격 확대
        
        self.label = QLabel(label)
        self.label.setStyleSheet("font-weight: 500;") # 라벨 강조
        
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        
        self.browse_btn = QPushButton("") # 아이콘 옆에 텍스트 추가 가능
        self.browse_btn.setIcon(qta.icon('fa5s.folder-open', color='#555'))
        self.browse_btn.setProperty("browseButton", True)
        self.browse_btn.setFixedWidth(80) # 버튼 크기 고정
        
        layout.addWidget(self.label)
        layout.addWidget(self.input, 1)
        layout.addWidget(self.browse_btn)

    def browse_folder(self):
        """폴더 선택 다이얼로그"""
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if folder:
            path = str(Path(folder).resolve())
            self.input.setText(path)

    def get_path(self) -> str:
        return self.input.text().strip()
    
    def set_path(self, path: str):
        self.input.setText(path)

    def _on_text_changed(self, text: str):
        """텍스트 변경 이벤트"""
        self.path_changed.emit(text)
        if self.setting_key:
            self.save_path(text)

    def save_path(self, path: str):
        """설정에 경로 저장"""
        if not self.setting_key:
            return
        
        settings = QSettings(AppConfig.ORG_NAME, AppConfig.APP_NAME)
        settings.setValue(self.setting_key, path)

    def load_path(self):
        """설정에서 경로 불러오기"""
        if not self.setting_key:
            return
        
        settings = QSettings(AppConfig.ORG_NAME, AppConfig.APP_NAME)
        saved_path = settings.value(self.setting_key, "")
        if saved_path:
            self.input.setText(saved_path)