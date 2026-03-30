"""
메인 진입점 - 시스템 트레이 상주 기능 추가

새로운 기능:
- app.setQuitOnLastWindowClosed(False) - 창 닫아도 종료 안 됨
- 시작 시 트레이로 시작 옵션
"""

import sys
import logging
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from gui.main_window import MainWindow

# --- 애플리케이션 설정 ---
APP_NAME = "KISP Settings Manager"
ORG_NAME = "박규민"
LOG_FILENAME = "app.log"
STYLE_PATH = Path("gui/style.qss")

# --- 경로 처리 헬퍼 함수 ---
def get_resource_path(relative_path: Path) -> Path:
    """리소스 파일 경로 가져오기"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller로 패키징된 경우
        base_path = Path(sys._MEIPASS)
    else:
        # 일반 파이썬 실행 환경
        base_path = Path(__file__).parent.resolve()
    
    return base_path / relative_path

# --- 로깅 설정 ---
log_path = get_resource_path(Path(LOG_FILENAME))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- 전역 예외 처리 핸들러 ---
def exception_hook(exc_type, exc_value, exc_traceback):
    """Uncaught Exception 로깅"""
    logging.critical(
        "Uncaught exception:", 
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def main():
    """애플리케이션 메인 진입점"""
    # 전역 예외 훅 등록
    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    
    # ========================================
    # 시스템 트레이 상주 설정
    # ========================================
    # 중요! 창이 모두 닫혀도 앱이 종료되지 않도록 설정
    app.setQuitOnLastWindowClosed(False)
    
    logging.info("시스템 트레이 모드 활성화")

    # 스타일시트 적용
    qss_file = get_resource_path(STYLE_PATH)
    
    try:
        if qss_file.exists():
            app.setStyleSheet(qss_file.read_text(encoding="utf-8"))
            logging.info(f"스타일시트 적용 완료: {qss_file}")
        else:
            logging.warning(f"스타일시트 파일을 찾을 수 없습니다: {qss_file}")
    except Exception as e:
        logging.error(f"스타일시트 로드 오류: {e}")

    # 메인 윈도우 생성
    try:
        window = MainWindow()
        
        # 설정 로드
        settings = QSettings(ORG_NAME, APP_NAME)
        start_minimized = settings.value("start_minimized", False, type=bool)
        
        # ========================================
        # 시작 시 표시 방식 결정
        # ========================================
        if start_minimized:
            # 트레이로 시작 (창 표시 안 함)
            logging.info("트레이로 시작")
            window.hide()
            window.tray_icon.showMessage(
                "KISP Settings Manager",
                "백그라운드에서 실행 중입니다.\n"
                "트레이 아이콘을 더블클릭하면 열립니다.",
                window.tray_icon.MessageIcon.Information,
                2000
            )
        else:
            # 창 표시
            logging.info("창으로 시작")
            window.show()
        
        logging.info(f"{APP_NAME} 시작됨")
        
        # 이벤트 루프 시작
        sys.exit(app.exec())
        
    except Exception as e:
        logging.critical(
            f"애플리케이션 실행 중 치명적 오류 발생: {e}", 
            exc_info=True
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
