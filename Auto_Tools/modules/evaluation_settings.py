# evaluation_settings.py

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QTabWidget, QLineEdit, QMessageBox, QLabel, QWidget, QFormLayout

from services.page1._00_transfer_worker import TransferWorker
from common.components import PathInputWidget
from common.components import TaskWidget

class EvaluationSettingsTab(QTabWidget):
    """평가 설정 탭"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.transfer_tab = TransferWorkTab()
        self.addTab(self.transfer_tab, "전기 종목 이전 작업")

    def get_current_status(self) -> str:
        return "전기 종목 데이터 이전 및 갱신 작업"

class TransferWorkTab(TaskWidget):
    """전기 종목 이전 작업 UI"""
    
    def __init__(self):
        super().__init__("") 
        self.worker: Optional[TransferWorker] = None
        self.init_task_ui()
    
    def init_task_ui(self):

        self.prev_path = PathInputWidget("전기 폴더:", "전기 데이터가 있는 폴더 선택")
        self.next_path = PathInputWidget("당기 폴더:", "당기 데이터를 저장할 폴더 선택")

        self.link_name = QLineEdit()
        self.link_name.setPlaceholderText("바로가기 이름 (선택사항)")

        self.prev_word = QLineEdit()
        self.prev_word.setPlaceholderText("변경할 문구 (예: 2025)")

        self.next_word = QLineEdit()
        self.next_word.setPlaceholderText("새로운 문구 (예: 2026)")

        form_widget = QWidget()
        form = QFormLayout(form_widget)
        form.setContentsMargins(0, 0, 0, 0)
        form.addRow("바로 가기:", self.link_name)
        form.addRow("전기 문구:", self.prev_word)
        form.addRow("당기 문구:", self.next_word)

        self.add_input_widget(self.prev_path)
        self.add_input_widget(self.next_path)
        self.add_input_widget(form_widget)

        self.execute_btn.clicked.connect(self.start_transfer)

    def start_transfer(self):
        """Worker 호출 부분"""
        # Pathlib 객체로 변환
        # (PathInputWidget이 아직 Path 객체 반환을 안 하면 str로 받아서 변환)
        prev_str = self.prev_path.get_path()
        next_str = self.next_path.get_path()

        if not prev_str:
            QMessageBox.warning(self, "오류", "전기 폴더를 선택해주세요.")
            return

        # [핵심] 외부 파일에 있는 Worker 클래스 사용
        self.worker = TransferWorker(
            Path(prev_str), 
            Path(next_str),
            self.link_name.text(),
            self.prev_word.text(),
            self.next_word.text()
        )
        
        self._connect_worker()
        self.worker.start()
    
    def _connect_worker(self):
        self.console.clear_messages()
        self.progress.reset()
        self.execute_btn.setEnabled(False)
        
        self.worker.progress.connect(self.progress.set_progress)
        self.worker.message.connect(self.console.append_message)
        self.worker.finished_success.connect(self.on_success)
        self.worker.finished_error.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)
    
    def on_success(self, message):
        self.console.append_message(message, "success")
        QMessageBox.information(self, "완료", message)
    
    def on_error(self, message):
        self.console.append_message(message, "error")
        QMessageBox.critical(self, "오류", message)
    
    def on_finished(self):
        self.execute_btn.setEnabled(True)
        self.worker = None