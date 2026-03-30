"""
설정 탭

기능:
- Windows 시작 프로그램 등록/해제
- 트레이로 시작 옵션
- 기타 프로그램 설정
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox, 
    QMessageBox, QLabel, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import QSettings, Qt
import qtawesome as qta

from common.utils.startup import StartupManager


class SettingsTab(QWidget):
    """설정 탭"""
    
    def __init__(self):
        super().__init__()
        
        # 설정 관리
        self.settings = QSettings("박규민", "KISP Settings Manager")
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ========================================
        # 일반 설정
        # ========================================
        general_group = QGroupBox("일반 설정")
        general_layout = QVBoxLayout()
        general_layout.setSpacing(10)
        
        # Windows 시작 프로그램
        startup_layout = QHBoxLayout()
        startup_layout.addWidget(
            qta.IconWidget('fa5s.power-off', color='#2196F3')
        )
        
        self.startup_checkbox = QCheckBox(
            "Windows 시작 시 자동 실행"
        )
        self.startup_checkbox.stateChanged.connect(self.on_startup_changed)
        startup_layout.addWidget(self.startup_checkbox)
        startup_layout.addStretch()
        
        general_layout.addLayout(startup_layout)
        
        # 도움말 텍스트
        help_label = QLabel(
            "  컴퓨터를 켤 때 자동으로 프로그램이 시작됩니다."
        )
        help_label.setStyleSheet("color: #666; font-size: 11px;")
        general_layout.addWidget(help_label)
        
        general_layout.addSpacing(10)
        
        # 트레이로 시작
        tray_layout = QHBoxLayout()
        tray_layout.addWidget(
            qta.IconWidget('fa5s.window-minimize', color='#2196F3')
        )
        
        self.start_minimized_checkbox = QCheckBox(
            "시스템 트레이로 시작"
        )
        self.start_minimized_checkbox.stateChanged.connect(
            self.on_start_minimized_changed
        )
        tray_layout.addWidget(self.start_minimized_checkbox)
        tray_layout.addStretch()
        
        general_layout.addLayout(tray_layout)
        
        # 도움말 텍스트
        help_label2 = QLabel(
            "  프로그램 시작 시 창을 표시하지 않고 트레이에만 아이콘을 표시합니다."
        )
        help_label2.setStyleSheet("color: #666; font-size: 11px;")
        general_layout.addWidget(help_label2)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # ========================================
        # 시스템 트레이 안내
        # ========================================
        info_group = QGroupBox("시스템 트레이 사용 방법")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        info_texts = [
            "• 창 닫기(X) 버튼을 누르면 트레이로 최소화됩니다",
            "• 트레이 아이콘을 더블클릭하면 창이 다시 열립니다",
            "• 트레이 아이콘을 우클릭하면 메뉴가 표시됩니다",
            "• 프로그램을 완전히 종료하려면 트레이 메뉴에서 '종료'를 선택하세요",
        ]
        
        for text in info_texts:
            label = QLabel(text)
            label.setStyleSheet("color: #555; font-size: 12px;")
            info_layout.addWidget(label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # ========================================
        # 정보
        # ========================================
        about_group = QGroupBox("프로그램 정보")
        about_layout = QVBoxLayout()
        
        about_label = QLabel(
            "<b>KISP Settings Manager</b><br>"
            "버전: 1.0.0<br>"
            "제작: 박규민<br>"
            "<br>"
            "업무 자동화 및 보고서 관리 도구"
        )
        about_label.setStyleSheet("color: #333; font-size: 12px;")
        about_layout.addWidget(about_label)
        
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        # 여백
        layout.addStretch()
    
    def load_settings(self):
        """설정 로드"""
        # 시작 프로그램 상태
        self.startup_checkbox.setChecked(StartupManager.is_enabled())
        
        # 트레이로 시작
        start_minimized = self.settings.value(
            "start_minimized", 
            False, 
            type=bool
        )
        self.start_minimized_checkbox.setChecked(start_minimized)
    
    def on_startup_changed(self, state):
        """시작 프로그램 설정 변경"""
        if state == Qt.CheckState.Checked.value:
            # 등록
            if StartupManager.enable():
                QMessageBox.information(
                    self,
                    "완료",
                    "시작 프로그램에 등록되었습니다.\n"
                    "다음 부팅부터 자동으로 시작됩니다."
                )
            else:
                QMessageBox.warning(
                    self,
                    "오류",
                    "시작 프로그램 등록에 실패했습니다."
                )
                # 실패 시 체크박스 원래대로
                self.startup_checkbox.setChecked(False)
        else:
            # 제거
            if StartupManager.disable():
                QMessageBox.information(
                    self,
                    "완료",
                    "시작 프로그램에서 제거되었습니다."
                )
            else:
                QMessageBox.warning(
                    self,
                    "오류",
                    "시작 프로그램 제거에 실패했습니다."
                )
                # 실패 시 체크박스 원래대로
                self.startup_checkbox.setChecked(True)
    
    def on_start_minimized_changed(self, state):
        """트레이로 시작 설정 변경"""
        start_minimized = (state == Qt.CheckState.Checked.value)
        self.settings.setValue("start_minimized", start_minimized)
        
        if start_minimized:
            QMessageBox.information(
                self,
                "설정 완료",
                "다음 시작부터 트레이에만 아이콘이 표시됩니다."
            )
        else:
            QMessageBox.information(
                self,
                "설정 완료",
                "다음 시작부터 창이 표시됩니다."
            )
