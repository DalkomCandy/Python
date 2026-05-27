import time
from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt


class ProgressWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_time: Optional[float] = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        row = QHBoxLayout()
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setMaximumHeight(6)

        self.pct_label = QLabel("0%")
        self.pct_label.setProperty("percentLabel", True)
        self.pct_label.setMinimumWidth(40)
        self.pct_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        row.addWidget(self.bar, 1)
        row.addWidget(self.pct_label)
        layout.addLayout(row)

        self.status_label = QLabel("대기 중...")
        self.status_label.setProperty("statusLabel", True)
        layout.addWidget(self.status_label)

        self.detail_label = QLabel("")
        self.detail_label.setProperty("detailLabel", True)
        layout.addWidget(self.detail_label)

    # ── 공개 API ─────────────────────────────────────

    def set_progress(self, current: int, total: int = 100):
        self.bar.setMaximum(total)
        self.bar.setValue(current)
        self.pct_label.setText(f"{int(current / total * 100)}%" if total else "0%")

        if current == 0 or self.start_time is None:
            self.start_time = time.time()

        if current > 0 and total > 0:
            self.status_label.setText(f"처리 중... {current} / {total}")
            elapsed = time.time() - self.start_time
            speed   = current / elapsed if elapsed > 0 else 0
            eta     = (total - current) / speed if speed > 0 else 0
            self.detail_label.setText(
                f"속도: {speed:.1f}개/초 | 경과: {self._fmt(elapsed)} | 남은 시간: {self._fmt(eta)}"
            )

    def set_status(self, status: str):
        """외부에서 상태 메시지 직접 설정 (완료, 오류 등)"""
        self.status_label.setText(status)

    def reset(self):
        self.bar.setValue(0)
        self.pct_label.setText("0%")
        self.status_label.setText("대기 중...")
        self.detail_label.setText("")
        self.start_time = None

    # ── 내부 ─────────────────────────────────────────

    @staticmethod
    def _fmt(sec: float) -> str:
        if sec < 60:   return f"{int(sec)}초"
        if sec < 3600: return f"{int(sec//60)}분 {int(sec%60)}초"
        return f"{int(sec//3600)}시간 {int((sec%3600)//60)}분"
