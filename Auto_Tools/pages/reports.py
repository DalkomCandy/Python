from PyQt6.QtWidgets import QTabWidget

from workers.job_number       import JobNumberWorker
from workers.word_to_pdf      import WordToPdfWorker
from workers.bank_report      import BankReportWorker
from workers.report_validator import ReportValidatorWorker
from widgets import TaskWidget, PathInputWidget
from config import AppConfig


class ReportManagementTab(QTabWidget):
    def __init__(self):
        super().__init__()
        self.addTab(ReportTaskTab("", "J로 시작하는 파일명 정리",   JobNumberWorker,  AppConfig.KEY_PATH_JOB_NUM),  "업무번호 삭제")
        self.addTab(ReportTaskTab("", "Word 문서가 있는 폴더",       WordToPdfWorker,  AppConfig.KEY_PATH_WORD_PDF), "Word → PDF 변환")
        self.addTab(ReportTaskTab("", "[은행명] 형식의 파일 정리",  BankReportWorker, AppConfig.KEY_PATH_BANK),     "은행별 보고서 정리")
        self.addTab(ReportValidatorTab(),                                                                            "보고서 검증")


class ReportTaskTab(TaskWidget):
    """Worker 클래스를 주입받아 실행하는 범용 탭"""

    def __init__(self, title: str, path_desc: str, worker_class: type, setting_key: str = None):
        super().__init__(title)
        self.worker_class = worker_class
        self.path_input = PathInputWidget("대상 폴더:", path_desc, setting_key=setting_key)
        self.add_input_widget(self.path_input)
        self.execute_btn.clicked.connect(self.execute_task)

    def execute_task(self):
        target = self.validate_folder(self.path_input.get_path())
        if target:
            self.start_worker(self.worker_class(target))


class ReportValidatorTab(TaskWidget):
    """보고서 검증 — CF / 누락 / NAV 3종 검사"""

    def __init__(self):
        super().__init__("")
        self.path_input = PathInputWidget("보고서 폴더:", ".docx 파일이 있는 폴더",
                                          setting_key=AppConfig.KEY_PATH_VALIDATOR)
        self.add_input_widget(self.path_input)
        self.execute_btn.clicked.connect(self.run_validation)

    def run_validation(self):
        # 네트워크 드라이브 체크는 validate_folder()에 통합됨
        target = self.validate_folder(self.path_input.get_path())
        if target:
            self.start_worker(ReportValidatorWorker(target), success_title="검사 완료")

