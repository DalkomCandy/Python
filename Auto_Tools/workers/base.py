"""
Worker 베이스 클래스

계층 구조:
  AbstractWorker  — QThread 기반 공통 뼈대 (시그널, 생명주기, 통계)
  ├── FileWorker  — 파일 목록 스캔 후 process_item() 순차 호출
  └── FolderWorker— 폴더 목록 스캔 후 process_folder() 순차 호출

사용 방법:
  class MyWorker(FileWorker):
      def process_item(self, file_path: Path) -> bool:
          # 처리 로직
          return True  # 성공 시 True
"""

import logging
from pathlib import Path
from typing import Optional, List

from PyQt6.QtCore import QThread, pyqtSignal

from utils.messages import Msg


class AbstractWorker(QThread):
    """
    모든 Worker의 베이스 클래스.

    시그널:
      progress(current, total)  — 진행률 (UI 진행바 연결용)
      message(text, type)       — 로그 메시지 ('info'|'success'|'warning'|'error')
      finished_success(msg)     — 성공 완료 메시지
      finished_error(msg)       — 오류 완료 메시지

    생명주기 (run() 내 실행 순서):
      validate_inputs() → prepare() → execute() → finalize()

    NOTE:
      ABC의 @abstractmethod는 PyQt6 QThread의 메타클래스와 충돌하여
      사용 불가. 대신 __init_subclass__로 클래스 정의 시점에 경고.
    """

    progress         = pyqtSignal(int, int)
    message          = pyqtSignal(str, str)
    finished_success = pyqtSignal(str)
    finished_error   = pyqtSignal(str)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        has_execute = any(
            'execute' in base.__dict__
            for base in cls.__mro__
            if base not in (AbstractWorker, object)
        )
        if not has_execute:
            import warnings
            warnings.warn(
                f"{cls.__name__}은(는) execute()를 반드시 구현해야 합니다.",
                UserWarning, stacklevel=2
            )

    def __init__(self, uses_com: bool = False) -> None:
        """
        Args:
            uses_com: Windows COM 사용 여부.
                      True면 run() 시작/종료 시 CoInitialize/CoUninitialize 호출.
        """
        super().__init__()
        self.uses_com       = uses_com
        self._is_running    = True
        self._stop_notified = False
        self.logger         = logging.getLogger(self.__class__.__name__)
        self.stats          = {'total': 0, 'success': 0, 'partial': 0, 'fail': 0}

    # ── 제어 ────────────────────────────────────────

    def stop(self) -> None:
        """작업 중단 요청. 현재 항목 처리 완료 후 중단."""
        self._is_running = False

    def check_running(self) -> bool:
        """
        중단 요청 여부 확인.

        Returns:
            계속 실행 가능하면 True, 중단 요청됐으면 False.
        """
        if not self._is_running:
            if not self._stop_notified:
                self.logger.warning(Msg.USER_STOPPED)
                self.message.emit(Msg.USER_STOPPED, "warning")
                self._stop_notified = True
            return False
        return True

    # ── 시그널 발행 ──────────────────────────────────

    def emit_progress(self, current: int, total: int) -> None:
        """진행률 시그널 발행."""
        if self._is_running:
            self.progress.emit(current, total)

    def emit_message(self, msg: str, msg_type: str = "info") -> None:
        """
        메시지 시그널 발행 + 로그 기록.

        Args:
            msg:      메시지 내용
            msg_type: 'info' | 'success' | 'warning' | 'error'
        """
        if not self._is_running:
            return
        log = {'error': self.logger.error, 'warning': self.logger.warning}
        log.get(msg_type, self.logger.info)(msg)
        self.message.emit(msg, msg_type)

    def emit_summary(self) -> None:
        """stats 기반 완료 요약 시그널 발행."""
        s, p, f = self.stats['success'], self.stats['partial'], self.stats['fail']
        total   = self.stats['total']
        if f > 0:
            parts = [f"성공: {s}"]
            if p: parts.append(f"부분성공: {p}")
            parts.append(f"실패: {f}")
            self.finished_error.emit(f"⚠️ 완료 ({', '.join(parts)})")
        elif p > 0:
            self.finished_success.emit(f"✓ 완료 (성공: {s}, 경고: {p})")
        else:
            self.finished_success.emit(f"✓ {total}개 항목 처리 완료")

    # ── 생명주기 ─────────────────────────────────────

    def run(self) -> None:
        """QThread 진입점. validate → prepare → execute → finalize 순서 보장."""
        if self.uses_com:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                self.finished_error.emit(Msg.COM_MISSING)
                return
        try:
            if not self.validate_inputs(): return
            if not self.prepare():         return
            self.execute()
            self.finalize()
        except Exception as e:
            self.logger.error(f"작업 중 예외: {e}", exc_info=True)
            self.finished_error.emit(f"오류 발생: {e}")
        finally:
            if self.uses_com:
                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

    def validate_inputs(self) -> bool:
        """입력 검증. 실패 시 False 반환 → run() 중단."""
        return True

    def prepare(self) -> bool:
        """실행 준비 (파일 스캔 등). 실패 시 False 반환 → run() 중단."""
        return True

    def execute(self) -> None:
        """실제 작업 수행. 서브클래스에서 반드시 구현."""
        raise NotImplementedError(f"{self.__class__.__name__}.execute()를 구현해야 합니다.")

    def finalize(self) -> None:
        """마무리 (통계 전송 등). 선택적 구현."""
        pass


class FileWorker(AbstractWorker):
    """
    파일 단위 작업 Worker.

    파일 목록을 스캔한 뒤 각 파일에 대해 process_item()을 순차 호출.

    서브클래스 구현:
      - process_item(file_path) → bool  (필수)
      - scan_files() → List[Path]       (선택, 기본: 직접 하위 파일 전체)
    """

    def __init__(self, target_path: Path, uses_com: bool = False) -> None:
        super().__init__(uses_com)
        self.target_path = target_path
        self.files: List[Path] = []

    def validate_inputs(self) -> bool:
        if not self.target_path or not self.target_path.is_dir():
            self.finished_error.emit(Msg.fmt(Msg.INVALID_PATH, path=self.target_path))
            return False
        return True

    def prepare(self) -> bool:
        try:
            self.files = self.scan_files()
            self.stats['total'] = len(self.files)
            if not self.files:
                self.finished_success.emit(Msg.NO_FILES)
                return False
            self.emit_message(f"📁 {len(self.files)}개 파일 발견")
            return True
        except Exception as e:
            self.finished_error.emit(Msg.fmt(Msg.SCAN_FAIL, error=e))
            return False

    def scan_files(self) -> List[Path]:
        """스캔할 파일 목록 반환. 오버라이드로 필터링 가능."""
        return [f for f in self.target_path.iterdir() if f.is_file()]

    def execute(self) -> None:
        for i, path in enumerate(self.files, 1):
            if not self.check_running():
                return
            try:
                if self.process_item(path):
                    self.stats['success'] += 1
                else:
                    self.stats['fail'] += 1
            except Exception as e:
                self.stats['fail'] += 1
                self.emit_message(f"❌ 오류 ({path.name}): {e}", "error")
            self.emit_progress(i, self.stats['total'])

    def process_item(self, file_path: Path) -> bool:
        """
        개별 파일 처리. 서브클래스에서 반드시 구현.

        Returns:
            성공 시 True, 실패 시 False.
        """
        raise NotImplementedError

    def finalize(self) -> None:
        self.emit_summary()


class FolderWorker(AbstractWorker):
    """
    폴더 단위 작업 Worker.

    폴더 목록을 스캔한 뒤 각 폴더에 대해 process_folder()를 순차 호출.

    서브클래스 구현:
      - process_folder(folder_path) → bool  (필수, 오류 있으면 True)
    """

    def __init__(
        self,
        source_path: Path,
        target_path: Optional[Path] = None,
        uses_com: bool = False,
    ) -> None:
        super().__init__(uses_com)
        self.source_path = source_path
        self.target_path = target_path
        self.folders: List[Path] = []

    def validate_inputs(self) -> bool:
        if not self.source_path or not self.source_path.exists():
            self.finished_error.emit(Msg.fmt(Msg.INVALID_PATH, path=self.source_path))
            return False
        return True

    def prepare(self) -> bool:
        try:
            self.folders = [d for d in self.source_path.iterdir() if d.is_dir()]
            self.stats['total'] = len(self.folders)
            if not self.folders:
                self.finished_success.emit(Msg.NO_FOLDERS)
                return False
            self.emit_message(f"📁 {len(self.folders)}개 폴더 발견")
            return True
        except Exception as e:
            self.finished_error.emit(Msg.fmt(Msg.FOLDER_SCAN_FAIL, error=e))
            return False

    def execute(self) -> None:
        for i, path in enumerate(self.folders, 1):
            if not self.check_running():
                return
            try:
                had_errors = self.process_folder(path)
                if had_errors:
                    self.stats['partial'] += 1
                else:
                    self.stats['success'] += 1
            except Exception as e:
                self.stats['fail'] += 1
                self.emit_message(f"❌ 오류 ({path.name}): {e}", "error")
            self.emit_progress(i, self.stats['total'])

    def process_folder(self, folder_path: Path) -> bool:
        """
        개별 폴더 처리. 서브클래스에서 반드시 구현.

        Returns:
            오류가 있었으면 True, 없으면 False.
        """
        raise NotImplementedError

    def finalize(self) -> None:
        self.emit_summary()
