from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QTabWidget, QMessageBox

from services.page2._00_JobNum import JobNumberWorker
from services.page2._01_WordToPdf import WordToPdfWorker
from services.page2._02_BankReport import BankReportWorker

from common.components.task import TaskWidget
from common.components.path_input import PathInputWidget
from common.base import AbstractWorker

class ReportManagementTab(QTabWidget):
    """보고서 관리 메인 탭"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # 팩토리 패턴: 똑같은 UI 구조에 '제목', '설명', '사용할 일꾼'만 바꿔서 끼워넣기
        self.addTab(
            ReportTaskTab("", "J로 시작하는 파일명 정리", JobNumberWorker),
            "업무번호 삭제"
        )
        self.addTab(
            ReportTaskTab("", "Word 문서가 있는 폴더", WordToPdfWorker),
            "Word → PDF 변환"
        )
        self.addTab(
            ReportTaskTab("", "[은행명] 형식의 파일 정리", BankReportWorker),
            "은행별 보고서 정리"
        )

    def get_current_status(self) -> str:
        """메인 윈도우 상태바 연동"""
        current_widget = self.currentWidget()
        if isinstance(current_widget, ReportTaskTab):
            return current_widget.title
        return "보고서 관리"


class ReportTaskTab(TaskWidget):
    """
    [만능 탭] 설정된 Worker 클래스를 동적으로 실행하는 UI
    """
    def __init__(self, title: str, path_desc: str, worker_class: type):
        super().__init__(title) # 부모 클래스(TaskWidget) 초기화
        self.worker_class = worker_class # 나중에 실행할 일꾼 클래스 저장
        self.worker: Optional[AbstractWorker] = None  # ✅ 수정: WorkerBase → AbstractWorker
        
        # UI 구성 (TaskWidget이 기본 틀 제공)
        self.path_input = PathInputWidget("대상 폴더:", path_desc)
        self.add_input_widget(self.path_input)
        
        self.execute_btn.clicked.connect(self.execute_task)

    def execute_task(self):
        """저장해둔 Worker 클래스를 생성해서 실행"""
        path_str = self.path_input.get_path()
        if not path_str:
            QMessageBox.warning(self, "경고", "폴더를 선택해주세요.")
            return

        target_path = Path(path_str)
        if not target_path.is_dir():
            self.console.append_message("유효한 폴더가 아닙니다.", "error")
            return
        
        # [핵심] 여기서 일꾼 인스턴스 생성 (동적 할당)
        self.worker = self.worker_class(target_path)
        self._connect_worker()
        self.worker.start()

    def _connect_worker(self):
        self.console.clear_messages()
        self.progress.reset()
        self.execute_btn.setEnabled(False)
        
        self.worker.progress.connect(self.progress.set_progress)
        self.worker.message.connect(self.console.append_message)
        self.worker.finished_success.connect(self._on_success)
        self.worker.finished_error.connect(self._on_error)
        self.worker.finished.connect(lambda: self.execute_btn.setEnabled(True))

    def _on_success(self, msg):
        self.console.append_message(msg, "success")
        QMessageBox.information(self, "완료", msg)

    def _on_error(self, msg):
        self.console.append_message(msg, "error")
        QMessageBox.critical(self, "오류", msg)