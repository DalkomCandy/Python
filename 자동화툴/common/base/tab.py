from abc import abstractmethod
from typing import Optional

from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import QSettings

from config import AppConfig


class BaseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
    
        self.settings = QSettings(AppConfig.ORG_NAME, AppConfig.APP_NAME)
        
        self.setup_ui()
        self.connect_signals()
        self.load_settings()
    
    # ========== 라이프사이클 메서드 ==========
    
    def setup_ui(self):
        """
        UI 구성 (필수 구현)
        
        위젯 생성 및 레이아웃 배치
        """
        raise NotImplementedError("setup_ui() 메서드를 구현해야 합니다.")
    
    def connect_signals(self):
        """
        시그널 연결 (선택적 구현)
        
        버튼 클릭, 입력 변경 등의 이벤트 연결
        """
        pass
    
    #TODO
    def load_settings(self):
        pass
    
    #TODO
    def save_settings(self):
        pass
    
    # ========== 유틸리티 메서드 ==========
    
    def get_tab_title(self) -> str:
        """
        탭 제목 반환 (필수 구현)
        
        Returns:
            탭 제목 문자열
        """
        raise NotImplementedError("get_tab_title() 메서드를 구현해야 합니다.")
    
    def get_tab_status(self) -> str:
        """
        탭 상태 반환 (선택적 구현)
        
        상태바 표시용
        
        Returns:
            상태 문자열
        """
        return self.get_tab_title()
    
    def validate_form(self) -> bool:
        """
        폼 검증 (선택적 구현)
        
        실행 전 입력값 검증
        
        Returns:
            유효하면 True, 아니면 False
        """
        return True
    
    def show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, title: str, message: str):
        QMessageBox.warning(self, title, message)
    
    def show_info(self, title: str, message: str):
        QMessageBox.information(self, title, message)
    
    def ask_confirmation(self, title: str, message: str) -> bool:
        """
        확인 다이얼로그 표시
        
        Returns:
            Yes 선택 시 True, No 선택 시 False
        """
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    # ========== 설정 관련 헬퍼 ==========
    
    def get_setting(self, key: str, default=None):
        """설정 값 가져오기"""
        return self.settings.value(key, default)
    
    def set_setting(self, key: str, value):
        """설정 값 저장"""
        self.settings.setValue(key, value)


class WorkerTab(BaseTab):
    """
    Worker를 사용하는 Tab의 베이스 클래스
    
    Worker 연결 및 진행률 표시 패턴 제공
    """
    
    def __init__(self, parent=None):
        self.worker: Optional[any] = None
        super().__init__(parent)
    
    # ========== Worker 관리 ==========
    
    @abstractmethod
    def create_worker(self):
        """
        Worker 인스턴스 생성 (필수 구현)
        
        Returns:
            Worker 인스턴스
        """
        raise NotImplementedError("create_worker() 메서드를 구현해야 합니다.")
    
    def start_worker(self):
        """Worker 실행"""
        # 폼 검증
        if not self.validate_form():
            return
        
        # 이미 실행 중이면 무시
        if self.worker and self.worker.isRunning():
            self.show_warning("경고", "작업이 이미 실행 중입니다.")
            return
        
        # Worker 생성
        try:
            self.worker = self.create_worker()
        except Exception as e:
            self.show_error("오류", f"작업 생성 실패: {e}")
            return
        
        # Worker 연결
        self.connect_worker()
        
        # 실행 전 처리
        self.before_worker_start()
        
        # 시작
        self.worker.start()
    
    def connect_worker(self):
        """Worker 시그널 연결"""
        if not self.worker:
            return
        
        # 진행률
        if hasattr(self, 'progress'):
            self.worker.progress.connect(self.on_worker_progress)
        
        # 메시지
        if hasattr(self, 'console'):
            self.worker.message.connect(self.on_worker_message)
        
        # 완료
        self.worker.finished_success.connect(self.on_worker_success)
        self.worker.finished_error.connect(self.on_worker_error)
        self.worker.finished.connect(self.on_worker_finished)
    
    def stop_worker(self):
        """Worker 중지"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
    
    # ========== Worker 이벤트 핸들러 ==========
    
    def before_worker_start(self):
        """
        Worker 시작 전 처리 (선택적 구현)
        
        예: 버튼 비활성화, 진행률 초기화
        """
        # 진행률 초기화
        if hasattr(self, 'progress') and hasattr(self.progress, 'reset'):
            self.progress.reset()
        
        # 콘솔 초기화
        if hasattr(self, 'console') and hasattr(self.console, 'clear_messages'):
            self.console.clear_messages()
        
        # 실행 버튼 비활성화
        if hasattr(self, 'execute_btn'):
            self.execute_btn.setEnabled(False)
    
    def on_worker_progress(self, current: int, total: int):
        """진행률 업데이트"""
        if hasattr(self, 'progress') and hasattr(self.progress, 'set_progress'):
            self.progress.set_progress(current, total)
    
    def on_worker_message(self, message: str, msg_type: str):
        """메시지 표시"""
        if hasattr(self, 'console') and hasattr(self.console, 'append_message'):
            self.console.append_message(message, msg_type)
    
    def on_worker_success(self, message: str):
        """성공 완료"""
        if hasattr(self, 'console') and hasattr(self.console, 'append_message'):
            self.console.append_message(message, "success")
        self.show_info("완료", message)
    
    def on_worker_error(self, message: str):
        """오류 완료"""
        if hasattr(self, 'console') and hasattr(self.console, 'append_message'):
            self.console.append_message(message, "error")
        self.show_error("오류", message)
    
    def on_worker_finished(self):
        """
        Worker 완료 (선택적 구현)
        
        성공/실패 관계없이 항상 호출됨
        """
        # 실행 버튼 다시 활성화
        if hasattr(self, 'execute_btn'):
            self.execute_btn.setEnabled(True)
        
        # Worker 정리
        if self.worker:
            self.worker.quit()
            self.worker.wait(5000)
            self.worker.deleteLater()
            self.worker = None