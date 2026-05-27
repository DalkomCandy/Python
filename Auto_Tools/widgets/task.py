"""
TaskWidget — 표준 작업 위젯

구성: 입력 영역 + 진행바 + 실행/취소 버튼 + 콘솔 출력
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox,
    QDialog, QLabel, QDialogButtonBox, QSizePolicy, QFileDialog
)
from PyQt6.QtCore import Qt

from .progress  import ProgressWidget
from .console   import ConsoleWidget
from utils.icons    import Icons
from utils.colors   import AppColors
from utils.messages import Msg


def _show_message(parent: QWidget, title: str, msg: str, is_error: bool = False) -> None:
    """
    리사이즈 가능한 메시지 다이얼로그.

    QMessageBox는 크기 고정이라 내용이 길면 잘리는 문제를 해결.
    텍스트 선택(복사)도 가능.
    """
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setSizeGripEnabled(True)
    dlg.resize(480, 160)

    layout = QVBoxLayout(dlg)
    layout.setSpacing(12)

    lbl = QLabel(msg)
    lbl.setWordWrap(True)
    lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    if is_error:
        lbl.setStyleSheet(f"color: {AppColors.ERROR};")
    layout.addWidget(lbl)

    btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    btns.accepted.connect(dlg.accept)
    layout.addWidget(btns)

    dlg.exec()


class TaskWidget(QWidget):
    """
    표준 작업 위젯 베이스 클래스.

    모든 탭이 공통으로 사용하는 레이아웃:
      - 입력 영역 (add_input_widget으로 추가)
      - 진행바 + 실행 버튼 + 취소 버튼
      - 콘솔 출력창 + 로그 저장 버튼
    """

    def __init__(self, title: str = "작업", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.title          = title
        self._worker        = None   # GC 방지 레퍼런스
        self._success_title = "완료"
        self._build_ui()

    # ── UI 구성 ──────────────────────────────────────

    def _build_ui(self) -> None:
        layout   = QVBoxLayout(self)
        group    = QGroupBox(self.title)
        g_layout = QVBoxLayout(group)

        # 입력 영역
        self.input_area = QVBoxLayout()
        self.input_area.setSpacing(8)
        g_layout.addLayout(self.input_area)

        # 실행 행
        run_row = QHBoxLayout()
        run_row.setSpacing(8)

        self.progress = ProgressWidget()
        run_row.addWidget(self.progress, 1)

        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.setIcon(Icons.close())
        self.cancel_btn.setProperty("dangerButton", True)
        self.cancel_btn.setFixedSize(90, 40)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        run_row.addWidget(self.cancel_btn, 0, Qt.AlignmentFlag.AlignTop)

        self.execute_btn = QPushButton("실행")
        self.execute_btn.setIcon(Icons.play())
        self.execute_btn.setProperty("primaryButton", True)
        self.execute_btn.setFixedSize(90, 40)
        run_row.addWidget(self.execute_btn, 0, Qt.AlignmentFlag.AlignTop)

        g_layout.addLayout(run_row)

        # 콘솔 + 로그 저장 버튼
        self.console = ConsoleWidget()
        self.console.setMinimumHeight(150)
        g_layout.addWidget(self.console)

        save_row = QHBoxLayout()
        save_row.addStretch()
        self.save_log_btn = QPushButton("로그 저장")
        self.save_log_btn.setIcon(Icons.save())
        self.save_log_btn.setProperty("secondaryButton", True)
        self.save_log_btn.clicked.connect(self._save_log)
        save_row.addWidget(self.save_log_btn)
        g_layout.addLayout(save_row)

        layout.addWidget(group)

    def add_input_widget(self, widget: QWidget) -> None:
        """입력 영역 하단에 위젯 추가."""
        self.input_area.addWidget(widget)

    # ── Worker 실행 ──────────────────────────────────

    def start_worker(self, worker, success_title: str = "완료") -> None:
        """
        Worker를 시작하고 시그널을 연결.

        - GC 방지를 위해 self._worker에 레퍼런스 유지
        - 실행 중 실행 버튼 → 숨김, 취소 버튼 → 표시
        """
        self._worker        = worker
        self._success_title = success_title
        self.console.clear_messages()
        self.progress.reset()

        self.execute_btn.setVisible(False)
        self.cancel_btn.setVisible(True)

        worker.progress.connect(self.progress.set_progress)
        worker.message.connect(self.console.append_message)
        worker.finished_success.connect(self._on_worker_success)
        worker.finished_error.connect(self._on_worker_error)
        worker.finished.connect(self._on_worker_finished)
        worker.start()

    def _on_cancel_clicked(self) -> None:
        """취소 버튼 클릭 — worker에 중단 요청."""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self.cancel_btn.setEnabled(False)
            self.cancel_btn.setText("중단 중...")

    def _on_worker_success(self, msg: str) -> None:
        self.console.append_message(msg, "success")
        self.progress.set_status("완료")
        _show_message(self, self._success_title, msg)

    def _on_worker_error(self, msg: str) -> None:
        self.console.append_message(msg, "error")
        self.progress.set_status("오류 발생")
        _show_message(self, "오류", msg, is_error=True)

    def _on_worker_finished(self) -> None:
        """작업 완료(성공/실패 무관) — 버튼 상태 복원 및 Worker 정리."""
        self.execute_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("취소")

        if self._worker:
            self._worker.quit()
            self._worker.wait()
            self._worker.deleteLater()
            self._worker = None

    # ── 로그 저장 ────────────────────────────────────

    def _save_log(self) -> None:
        """콘솔 내용을 텍스트 파일로 저장."""
        text = self.console.toPlainText()
        if not text.strip():
            _show_message(self, "알림", "저장할 로그가 없습니다.")
            return

        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        default  = str(Path.home() / f"kisp_log_{ts}.txt")
        save_path, _ = QFileDialog.getSaveFileName(
            self, "로그 저장", default, "텍스트 파일 (*.txt)"
        )
        if save_path:
            Path(save_path).write_text(text, encoding='utf-8')

    # ── 경로 검증 ────────────────────────────────────

    def validate_folder(self, path_str: str) -> Optional[Path]:
        """
        경로 문자열 검증 후 Path 반환.

        검증 순서: 빈 문자열 → 폴더 존재 여부
        실패 시 메시지 표시 후 None 반환.
        """
        if not path_str:
            _show_message(self, "경고", Msg.NO_FOLDER)
            return None
        p = Path(path_str)
        if not p.is_dir():
            self.console.append_message(Msg.NOT_A_DIR, "error")
            return None
        return p
