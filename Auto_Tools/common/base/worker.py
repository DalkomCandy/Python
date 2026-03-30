"""
Worker 베이스 클래스 모듈

모든 백그라운드 작업 Worker의 베이스 클래스를 정의합니다.
"""

import logging
from typing import Optional, List, Any
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal


class AbstractWorker(QThread):
    # 시그널 정의
    progress = pyqtSignal(int, int)
    message = pyqtSignal(str, str)
    finished_success = pyqtSignal(str)
    finished_error = pyqtSignal(str)
    
    def __init__(self, uses_com: bool = False):
        """
        Args:
            uses_com: COM 사용 여부 (Windows)
        """
        super().__init__()
        self.uses_com = uses_com
        self._is_running = True
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 통계
        self.stats = {
            'total': 0,
            'success': 0,
            'partial': 0,
            'fail': 0
        }
    
    # ========== 제어 메서드 ==========
    
    def stop(self):
        """작업 중지 요청"""
        self._is_running = False
        self.logger.info("⛔ 작업 중지 요청")
    
    def check_running(self) -> bool:
        """
        중단 요청 확인
        
        Returns:
            계속 실행 가능하면 True, 중단되었으면 False
        """
        if not self._is_running:
            self.emit_message("사용자에 의해 작업이 중단되었습니다.", "warning")
            return False
        return True
    
    # ========== 메시지/진행률 전송 ==========
    
    def emit_progress(self, current: int, total: int):
        """진행률 전송"""
        if self._is_running:
            self.progress.emit(current, total)
    
    def emit_message(self, msg: str, msg_type: str = "info"):
        """
        메시지 전송
        
        Args:
            msg: 메시지 내용
            msg_type: 'info', 'success', 'warning', 'error'
        """
        if not self._is_running:
            return
        
        # 로깅
        if msg_type == "error":
            self.logger.error(msg)
        elif msg_type == "warning":
            self.logger.warning(msg)
        else:
            self.logger.info(msg)
        
        # UI에 전송
        self.message.emit(msg, msg_type)
    
    # ========== 라이프사이클 메서드 ==========
    
    def run(self):
        """
        QThread 실행 진입점
        전체 실행 흐름을 제어합니다.
        """
        # COM 초기화
        if self.uses_com:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                self.finished_error.emit("pythoncom 모듈이 없습니다.")
                return
        
        try:
            # 1. 검증
            if not self.validate_inputs():
                return
            
            # 2. 준비
            if not self.prepare():
                return
            
            # 3. 실행
            self.execute()
            
            # 4. 마무리
            self.finalize()
            
        except Exception as e:
            self.logger.error(f"작업 중 예외: {e}", exc_info=True)
            self.finished_error.emit(f"오류 발생: {str(e)}")
            
        finally:
            # COM 정리
            if self.uses_com:
                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                except:
                    pass
    
    def validate_inputs(self) -> bool:
        """
        입력 검증 (선택적 구현)
        
        Returns:
            검증 성공 시 True, 실패 시 False
        """
        return True
    
    def prepare(self) -> bool:
        """
        준비 작업 (선택적 구현)
        
        Returns:
            준비 성공 시 True, 실패 시 False
        """
        return True
    
    def execute(self):
        """
        실제 작업 수행 (필수 구현)
        
        서브클래스에서 반드시 구현해야 합니다.
        """
        raise NotImplementedError("execute() 메서드를 구현해야 합니다.")
    
    def finalize(self):
        """
        마무리 작업 (선택적 구현)
        
        통계 전송 등
        """
        pass
    
    # ========== 유틸리티 메서드 ==========
    
    def emit_summary(self):
        """통계 기반 요약 메시지 전송"""
        total = self.stats['total']
        success = self.stats['success']
        partial = self.stats['partial']
        fail = self.stats['fail']
        
        if fail > 0:
            msg = f"⚠️ 완료 (성공: {success}, 부분성공: {partial}, 실패: {fail})"
            self.finished_error.emit(msg)
        elif partial > 0:
            msg = f"✓ 완료 (성공: {success}, 경고: {partial})"
            self.finished_success.emit(msg)
        else:
            msg = f"✓ {total}개 항목 처리 완료"
            self.finished_success.emit(msg)


class FileWorker(AbstractWorker):
    """
    파일 작업 전용 Worker
    
    파일 목록을 스캔하고 각 파일에 대해 process_item()을 호출합니다.
    """
    
    def __init__(self, target_path: Path, uses_com: bool = False):
        """
        Args:
            target_path: 작업 대상 경로
            uses_com: COM 사용 여부
        """
        super().__init__(uses_com)
        self.target_path = target_path
        self.files: List[Path] = []
    
    def validate_inputs(self) -> bool:
        """경로 검증"""
        if not self.target_path:
            self.finished_error.emit("경로가 지정되지 않았습니다.")
            return False
        
        if not self.target_path.exists():
            self.finished_error.emit(f"경로가 존재하지 않습니다: {self.target_path}")
            return False
        
        if not self.target_path.is_dir():
            self.finished_error.emit(f"폴더가 아닙니다: {self.target_path}")
            return False
        
        return True
    
    def prepare(self) -> bool:
        """파일 스캔"""
        try:
            self.files = self.scan_files()
            self.stats['total'] = len(self.files)
            
            if not self.files:
                self.finished_success.emit("처리할 파일이 없습니다.")
                return False
            
            self.emit_message(f"📁 {len(self.files)}개 파일 발견", "info")
            return True
            
        except Exception as e:
            self.finished_error.emit(f"파일 스캔 실패: {e}")
            return False
    
    def scan_files(self) -> List[Path]:
        """
        파일 스캔 (서브클래스에서 커스터마이징 가능)
        
        Returns:
            파일 경로 리스트
        """
        return [f for f in self.target_path.iterdir() if f.is_file()]
    
    def execute(self):
        """파일 목록을 순회하며 처리"""
        for i, file_path in enumerate(self.files, 1):
            if not self.check_running():
                return
            
            try:
                success = self.process_item(file_path)
                
                if success:
                    self.stats['success'] += 1
                else:
                    self.stats['fail'] += 1
                    
            except Exception as e:
                self.stats['fail'] += 1
                self.emit_message(f"❌ 오류 ({file_path.name}): {e}", "error")
                self.logger.error(f"파일 처리 오류: {file_path}", exc_info=True)
            
            self.emit_progress(i, self.stats['total'])
    
    def process_item(self, file_path: Path) -> bool:
        """
        개별 파일 처리 (필수 구현)
        
        Args:
            file_path: 처리할 파일 경로
        
        Returns:
            성공 시 True, 실패 시 False
        """
        raise NotImplementedError("process_item() 메서드를 구현해야 합니다.")
    
    def finalize(self):
        """통계 전송"""
        self.emit_summary()


class FolderWorker(AbstractWorker):
    """
    폴더 계층 작업 전용 Worker
    
    폴더 목록을 스캔하고 각 폴더에 대해 process_folder()를 호출합니다.
    """
    
    def __init__(self, source_path: Path, target_path: Optional[Path] = None, 
                 uses_com: bool = False):
        """
        Args:
            source_path: 원본 경로
            target_path: 대상 경로 (선택)
            uses_com: COM 사용 여부
        """
        super().__init__(uses_com)
        self.source_path = source_path
        self.target_path = target_path
        self.folders: List[Path] = []
    
    def validate_inputs(self) -> bool:
        """경로 검증"""
        if not self.source_path or not self.source_path.exists():
            self.finished_error.emit("원본 경로가 유효하지 않습니다.")
            return False
        
        if self.target_path and not self.target_path.parent.exists():
            self.finished_error.emit("대상 경로의 상위 폴더가 존재하지 않습니다.")
            return False
        
        return True
    
    def prepare(self) -> bool:
        """폴더 스캔"""
        try:
            self.folders = [d for d in self.source_path.iterdir() if d.is_dir()]
            self.stats['total'] = len(self.folders)
            
            if not self.folders:
                self.finished_success.emit("처리할 폴더가 없습니다.")
                return False
            
            self.emit_message(f"📁 {len(self.folders)}개 폴더 발견", "info")
            return True
            
        except Exception as e:
            self.finished_error.emit(f"폴더 스캔 실패: {e}")
            return False
    
    def execute(self):
        """폴더 목록을 순회하며 처리"""
        for i, folder_path in enumerate(self.folders, 1):
            if not self.check_running():
                return
            
            try:
                had_errors = self.process_folder(folder_path)
                
                if had_errors:
                    self.stats['partial'] += 1
                else:
                    self.stats['success'] += 1
                    
            except Exception as e:
                self.stats['fail'] += 1
                self.emit_message(f"❌ 오류 ({folder_path.name}): {e}", "error")
                self.logger.error(f"폴더 처리 오류: {folder_path}", exc_info=True)
            
            self.emit_progress(i, self.stats['total'])
    
    def process_folder(self, folder_path: Path) -> bool:
        """
        개별 폴더 처리 (필수 구현)
        
        Args:
            folder_path: 처리할 폴더 경로
        
        Returns:
            오류가 있었으면 True, 없으면 False
        """
        raise NotImplementedError("process_folder() 메서드를 구현해야 합니다.")
    
    def finalize(self):
        """통계 전송"""
        self.emit_summary()
