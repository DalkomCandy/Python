"""
PathInputWidget — 경로 입력 위젯

기능:
  - 폴더 찾아보기 버튼
  - 드래그앤드롭 지원
  - editingFinished 시 QSettings 저장 (미완성 경로 저장 방지)
  - 최근 사용 경로 히스토리 드롭다운 (최대 8개)
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog
)
from PyQt6.QtCore import pyqtSignal, QSettings
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from config      import AppConfig
from utils.icons import Icons

_HISTORY_MAX = 8  # 히스토리 최대 저장 개수


class PathInputWidget(QWidget):
    """
    경로 입력 위젯.

    - 직접 입력 또는 찾아보기 버튼으로 경로 선택
    - 드래그앤드롭으로 폴더 경로 설정 가능
    - 최근 사용한 경로를 드롭다운으로 재선택 가능
    """

    path_changed = pyqtSignal(str)

    def __init__(
        self,
        label: str,
        placeholder: str,
        setting_key: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setting_key = setting_key
        self.setAcceptDrops(True)
        self._build_ui(label, placeholder)

        self.browse_btn.clicked.connect(self.browse_folder)
        self.combo.currentTextChanged.connect(self._on_text_changed)
        self.combo.lineEdit().editingFinished.connect(self._save_on_finish)

        if self.setting_key:
            self._load_history()

    # ── UI ───────────────────────────────────────────

    def _build_ui(self, label: str, placeholder: str) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.label = QLabel(label)
        self.label.setProperty("pathLabel", True)
        self.label.setFixedWidth(80)   # 라벨 열 너비 고정 → 입력 시작점 정렬

        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo.lineEdit().setPlaceholderText(placeholder)
        self.combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )

        self.browse_btn = QPushButton()
        self.browse_btn.setIcon(Icons.folder_open())
        self.browse_btn.setProperty("browseButton", True)
        self.browse_btn.setFixedWidth(44)

        layout.addWidget(self.label)
        layout.addWidget(self.combo, 1)
        layout.addWidget(self.browse_btn)

    # ── 공개 API ─────────────────────────────────────

    def get_path(self) -> str:
        """현재 입력된 경로 반환."""
        return self.combo.currentText().strip()

    def set_path(self, path: str) -> None:
        """경로를 프로그래밍으로 설정."""
        self.combo.setCurrentText(path)

    # ── 폴더 선택 ────────────────────────────────────

    def browse_folder(self) -> None:
        """파일 탐색기 다이얼로그로 폴더 선택."""
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if folder:
            path = str(Path(folder).resolve())
            self.combo.setCurrentText(path)
            self._save_on_finish()

    # ── 이벤트 ───────────────────────────────────────

    def _on_text_changed(self, text: str) -> None:
        self.path_changed.emit(text)

    def _save_on_finish(self) -> None:
        """포커스를 잃거나 Enter 시 히스토리에 저장."""
        path = self.combo.currentText().strip()
        if not path or not self.setting_key:
            return
        self._push_history(path)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls and (p := Path(urls[0].toLocalFile())).is_dir():
            self.combo.setCurrentText(str(p))
            self._save_on_finish()

    # ── 히스토리 ─────────────────────────────────────

    def _history_key(self) -> str:
        return f"{self.setting_key}_history"

    def _load_history(self) -> None:
        """저장된 히스토리를 콤보박스에 로드."""
        s       = QSettings(AppConfig.ORG_NAME, AppConfig.APP_NAME)
        history = s.value(self._history_key(), [])
        if isinstance(history, str):
            history = [history]

        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItems(history)
        if history:
            self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)

    def _push_history(self, path: str) -> None:
        """히스토리 맨 앞에 경로 추가 후 저장 (중복 제거, 최대 8개)."""
        s       = QSettings(AppConfig.ORG_NAME, AppConfig.APP_NAME)
        history = s.value(self._history_key(), [])
        if isinstance(history, str):
            history = [history]

        history = [p for p in history if p != path]
        history.insert(0, path)
        history = history[:_HISTORY_MAX]

        s.setValue(self._history_key(), history)

        # 콤보박스도 갱신
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItems(history)
        self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)
