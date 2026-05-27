"""
KISP 업무 자동화 매니저 — 진입점

멀티 인스턴스 방지:
  락 파일 방식으로 중복 실행 차단.
  비정상 종료 후에도 락이 남지 않음.
"""

import sys
import logging
from logging.handlers import RotatingFileHandler
from PyQt6.QtWidgets import QApplication, QMessageBox

from config import AppConfig
from gui.main_window import MainWindow

# ── 로깅 설정 ─────────────────────────────────────────────
_log_path = AppConfig.BASE_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            _log_path,
            maxBytes    = 1 * 1024 * 1024,  # 1 MB
            backupCount = 3,
            encoding    = 'utf-8'
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

# 락 파일 경로
_LOCK_FILE = AppConfig.BASE_DIR / ".kisp.lock"
_lock_handle = None


def _acquire_lock() -> bool:
    """
    락 파일로 중복 실행 방지.

    Returns:
        최초 실행이면 True, 이미 실행 중이면 False.
    """
    global _lock_handle
    import os

    try:
        # O_CREAT | O_EXCL → 파일이 이미 있으면 실패
        fd = os.open(str(_LOCK_FILE),
                     os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        _lock_handle = os.fdopen(fd, 'w')
        _lock_handle.write(str(os.getpid()))
        _lock_handle.flush()
        return True
    except FileExistsError:
        # 이미 실행 중
        return False
    except Exception:
        # 락 파일 생성 실패 시 일단 실행 허용
        return True


def _release_lock():
    """락 파일 해제"""
    global _lock_handle
    try:
        if _lock_handle:
            _lock_handle.close()
        _LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def exception_hook(exc_type, exc_value, exc_traceback):
    logging.critical("Uncaught exception:",
                     exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    app.setApplicationName(AppConfig.APP_NAME)
    app.setOrganizationName(AppConfig.ORG_NAME)

    # ── 멀티 인스턴스 방지 ──────────────────────────────
    if not _acquire_lock():
        QMessageBox.information(
            None, AppConfig.WINDOW_TITLE, "이미 실행 중입니다.")
        sys.exit(0)

    # 종료 시 락 해제
    app.aboutToQuit.connect(_release_lock)

    # ── 앱 아이콘 ────────────────────────────────────────
    icon_path = AppConfig.RESOURCES_DIR / "icon.ico"
    if icon_path.exists():
        from PyQt6.QtGui import QIcon
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        import qtawesome as qta
        app.setWindowIcon(qta.icon('fa5s.cog', color='#0071e3'))

    # ── 스타일시트 ────────────────────────────────────────
    if AppConfig.STYLE_PATH.exists():
        app.setStyleSheet(
            AppConfig.STYLE_PATH.read_text(encoding="utf-8"))
    else:
        logging.warning("스타일시트 없음: %s", AppConfig.STYLE_PATH)

    window = MainWindow()
    window.show()
    logging.info("%s 시작", AppConfig.APP_NAME)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
