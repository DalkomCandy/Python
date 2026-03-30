import time
from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt

class ProgressWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_time: Optional[float] = None
        self.init_ui()
    
    def init_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 진행률 바 + 퍼센트
        progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(6)
        
        self.percent_label = QLabel("0%")
        self.percent_label.setProperty("percentLabel", True)
        self.percent_label.setMinimumWidth(40)
        self.percent_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        progress_layout.addWidget(self.progress_bar, 1)
        progress_layout.addWidget(self.percent_label)
        layout.addLayout(progress_layout)
        
        # 상태 메시지
        self.status_label = QLabel("대기 중...")
        self.status_label.setProperty("statusLabel", True)
        layout.addWidget(self.status_label)
        
        # 상세 정보 (속도, ETA)
        self.detail_label = QLabel("")
        self.detail_label.setProperty("detailLabel", True)
        layout.addWidget(self.detail_label)
    
    def set_progress(self, current: int, total: int = 100):
        """
        진행률 설정
        
        Args:
            current: 현재 값
            total: 전체 값
        """
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
        # 퍼센트 계산
        if total > 0:
            percent = int((current / total) * 100)
            self.percent_label.setText(f"{percent}%")
        else:
            self.percent_label.setText("0%")
        
        # 시작 시간 기록
        if current == 0 or self.start_time is None:
            self.start_time = time.time()
        
        # 상세 정보 업데이트
        if current > 0 and total > 0:
            self._update_detail_info(current, total)
    
    def set_status(self, status: str):
        """
        상태 메시지 설정
        
        Args:
            status: 상태 문자열
        """
        self.status_label.setText(status)
    
    def _update_detail_info(self, current: int, total: int):
        """상세 정보 업데이트 (속도, ETA)"""
        if self.start_time is None:
            return
        
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            # 속도 계산
            speed = current / elapsed
            
            # 남은 시간 계산
            remaining = total - current
            eta = remaining / speed if speed > 0 else 0
            
            self.detail_label.setText(
                f"속도: {speed:.1f}개/초 | "
                f"경과: {self._format_time(elapsed)} | "
                f"남은 시간: {self._format_time(eta)}"
            )
    
    def _format_time(self, seconds: float) -> str:
        """시간 포맷팅"""
        if seconds < 60:
            return f"{int(seconds)}초"
        elif seconds < 3600:
            return f"{int(seconds // 60)}분 {int(seconds % 60)}초"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}시간 {minutes}분"
    
    def reset(self):
        """초기화"""
        self.progress_bar.setValue(0)
        self.percent_label.setText("0%")
        self.status_label.setText("대기 중...")
        self.detail_label.setText("")
        self.start_time = None