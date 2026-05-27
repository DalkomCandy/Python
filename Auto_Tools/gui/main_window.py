"""
메인 윈도우 — 사이드바 + 콘텐츠 영역

지연 로딩(Lazy Loading):
  탭은 사용자가 처음 클릭할 때 생성됩니다.
  무거운 라이브러리(openpyxl, win32com 등)가 필요한 탭은
  클릭 전까지 import되지 않아 앱 시작 속도가 크게 향상됩니다.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QListWidget, QStackedWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import QCloseEvent

from config      import AppConfig
from utils.icons import Icons


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.settings   = QSettings(AppConfig.ORG_NAME, AppConfig.APP_NAME)
        self._factories = []   # 탭 생성 factory 함수 목록
        self._loaded    = []   # 탭 로드 여부

        self._build_ui()
        self._load_settings()

    # ── UI ──────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle(AppConfig.WINDOW_TITLE)
        self.resize(AppConfig.DEFAULT_WIDTH, AppConfig.DEFAULT_HEIGHT)

        container = QWidget()
        self.setCentralWidget(container)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setIconSize(QSize(20, 20))
        self.sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: #ffffff;
                border-left: 1px solid #e5e5e5;
            }
        """)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_area)

        # 탭 등록 — factory lambda로 지연 로딩
        # pages 모듈 import는 factory 내부에서 발생 → 시작 시 불필요한 import 없음
        self._add_page("평가 설정",  "fa5s.chart-line",  self._make_evaluation)
        self._add_page("보고서 관리", "fa5s.file-alt",    self._make_reports)
        self._add_page("폴더 관리",  "fa5s.folder",       self._make_folders)
        self._add_page("쿼리 관리",  "fa5s.sticky-note",  self._make_queries)
        self._add_page("설정",       "fa5s.cog",          self._make_settings)

        self.sidebar.currentRowChanged.connect(self._on_tab_changed)
        self.sidebar.setCurrentRow(0)

    # ── 탭 Factory ──────────────────────────────────
    # 각 함수 내에서 import → 해당 탭 클릭 시에만 모듈 로드

    @staticmethod
    def _make_evaluation():
        from pages.evaluation import EvaluationManagementTab
        return EvaluationManagementTab()

    @staticmethod
    def _make_reports():
        from pages.reports import ReportManagementTab
        return ReportManagementTab()

    @staticmethod
    def _make_folders():
        from pages.folders import FolderManagementTab
        return FolderManagementTab()

    @staticmethod
    def _make_queries():
        from pages.queries import QuerySettingsTab
        return QuerySettingsTab()

    @staticmethod
    def _make_settings():
        from pages.settings import SettingsTab
        return SettingsTab()

    # ── 탭 등록 / 지연 로딩 ─────────────────────────

    def _add_page(self, name: str, icon_name: str, factory):
        """사이드바 아이템 + placeholder 추가, factory 저장"""
        item = QListWidgetItem(name)
        item.setIcon(Icons.sidebar(icon_name))
        self.sidebar.addItem(item)

        placeholder = QWidget()
        self.content_area.addWidget(placeholder)

        self._factories.append(factory)
        self._loaded.append(False)

    def _on_tab_changed(self, index: int):
        """사이드바 선택 변경 — 미로드 탭이면 생성"""
        if index < 0 or index >= len(self._factories):
            return

        if not self._loaded[index]:
            widget = self._factories[index]()
            old    = self.content_area.widget(index)

            # placeholder(index) → new widget(index), old shifts to index+1
            self.content_area.insertWidget(index, widget)
            self.content_area.removeWidget(old)
            old.deleteLater()

            self._loaded[index] = True

        self.content_area.setCurrentIndex(index)

    # ── 이벤트 ──────────────────────────────────────

    def closeEvent(self, event: QCloseEvent):
        self._save_settings()
        event.accept()

    # ── 설정 ────────────────────────────────────────

    def _save_settings(self):
        self.settings.setValue("geometry",    self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    def _load_settings(self):
        if geo := self.settings.value("geometry"):
            self.restoreGeometry(geo)
        if state := self.settings.value("windowState"):
            self.restoreState(state)
