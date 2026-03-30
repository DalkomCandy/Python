"""
메인 윈도우 - 시스템 트레이 기능 추가

새로운 기능:
- 시스템 트레이 아이콘
- 트레이 메뉴 (열기/숨기기/종료)
- X 버튼 눌러도 종료 안 됨 (트레이로 숨김)
- 트레이 아이콘 더블클릭으로 창 표시
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QListWidget, QStackedWidget, QListWidgetItem, QLabel,
    QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import QAction, QCloseEvent
import qtawesome as qta

# 기존 모듈들
from modules.evaluation_settings import EvaluationSettingsTab
from modules.report_management import ReportManagementTab
from modules.folder_management import FolderManagementTab
from modules.calendar_tab import CalendarTab
from modules.settings import SettingsTab


class MainWindow(QMainWindow):
    """
    메인 윈도우 - 시스템 트레이 상주 기능 포함
    """
    
    WINDOW_TITLE = "KISP Manager"
    DEFAULT_WIDTH = 950
    DEFAULT_HEIGHT = 650

    def __init__(self):
        super().__init__()
        
        # 설정 관리
        self.settings = QSettings("박규민", "KISP Settings Manager")
        
        # 트레이 알림 플래그
        self._hide_notified = False
        
        # UI 초기화
        self.init_ui()
        
        # 시스템 트레이 초기화
        self.init_system_tray()

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        # 메인 컨테이너 (가로 배치)
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 왼쪽 사이드바 (메뉴)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setIconSize(QSize(20, 20))
        self.sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # 오른쪽 컨텐츠 영역
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: #ffffff;
                border-left: 1px solid #e5e5e5; 
            }
        """)

        # 레이아웃에 배치
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

        # 메뉴 및 페이지 추가
        self.add_menu("캘린더", "fa5s.calendar-alt", CalendarTab())
        self.add_menu("평가 설정", "fa5s.chart-line", EvaluationSettingsTab())
        self.add_menu("보고서 관리", "fa5s.file-alt", ReportManagementTab())
        self.add_menu("폴더 관리", "fa5s.folder", FolderManagementTab())
        self.add_menu("설정", "fa5s.cog", SettingsTab())

        # 이벤트 연결
        self.sidebar.currentRowChanged.connect(self.content_area.setCurrentIndex)
        
        # 초기 선택
        self.sidebar.setCurrentRow(0)

    def add_menu(self, name: str, icon: str, widget: QWidget):
        """사이드바 메뉴와 페이지를 동시에 추가"""
        # 사이드바 아이템
        item = QListWidgetItem(name)
        item.setIcon(qta.icon(icon, color="#555"))
        self.sidebar.addItem(item)
        
        # 컨텐츠 영역에 위젯 추가
        self.content_area.addWidget(widget)
    
    # ========================================
    # 시스템 트레이 기능
    # ========================================
    
    def init_system_tray(self):
        """시스템 트레이 아이콘 초기화"""
        # 트레이 아이콘 생성
        self.tray_icon = QSystemTrayIcon(self)
        
        # 아이콘 설정
        icon = qta.icon('fa5s.briefcase', color='#2196F3')
        self.tray_icon.setIcon(icon)
        
        # 툴팁
        self.tray_icon.setToolTip("KISP Settings Manager")
        
        # 트레이 메뉴 생성
        self.create_tray_menu()
        
        # 트레이 아이콘 클릭 이벤트
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # 트레이 아이콘 표시
        self.tray_icon.show()
    
    def create_tray_menu(self):
        """트레이 메뉴 생성"""
        tray_menu = QMenu()
        
        # 열기
        show_action = QAction(
            qta.icon('fa5s.window-maximize', color='#333'),
            "열기",
            self
        )
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        # 숨기기
        hide_action = QAction(
            qta.icon('fa5s.window-minimize', color='#333'),
            "숨기기",
            self
        )
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        # 종료
        quit_action = QAction(
            qta.icon('fa5s.power-off', color='#d32f2f'),
            "종료",
            self
        )
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        # 메뉴 설정
        self.tray_icon.setContextMenu(tray_menu)
    
    def on_tray_icon_activated(self, reason):
        """
        트레이 아이콘 클릭 이벤트
        
        더블클릭 시 창 표시
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """창 표시 및 활성화"""
        self.show()
        self.activateWindow()  # 창을 맨 앞으로
        self.raise_()  # 다른 창 위로
        
        # 최소화되어 있었다면 복원
        if self.isMinimized():
            self.showNormal()
    
    def closeEvent(self, event: QCloseEvent):
        """
        창 닫기 이벤트 (X 버튼 클릭)
        
        DesktopCal처럼 닫기 버튼 눌러도 트레이로 최소화
        완전 종료는 트레이 메뉴에서만 가능
        """
        # 창을 완전히 닫지 않고 숨김
        event.ignore()
        self.hide()
        
        # 처음 숨길 때만 알림
        if not self._hide_notified:
            self.tray_icon.showMessage(
                "KISP Settings Manager",
                "프로그램이 백그라운드에서 실행 중입니다.\n"
                "트레이 아이콘을 더블클릭하면 다시 열립니다.",
                QSystemTrayIcon.MessageIcon.Information,
                2000  # 2초
            )
            self._hide_notified = True
    
    def quit_application(self):
        """프로그램 완전 종료"""
        # 확인 대화상자
        reply = QMessageBox.question(
            self,
            "종료 확인",
            "KISP Settings Manager를 종료하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 설정 저장
            self.save_settings()
            
            # 트레이 아이콘 제거
            self.tray_icon.hide()
            
            # 애플리케이션 종료
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
    
    def save_settings(self):
        """설정 저장"""
        # 창 크기/위치 저장
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
    
    def load_settings(self):
        """설정 로드"""
        # 창 크기/위치 복원
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
