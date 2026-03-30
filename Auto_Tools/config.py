# config.py

from pathlib import Path
import sys

class AppConfig:
    
    # [1] 경로 설정
    BASE_DIR = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(__file__).parent.resolve()
    RESOURCES_DIR = BASE_DIR / "gui"
    LOG_DIR = BASE_DIR / "logs"

    # [2] 앱 ID 및 기본 정보 (QSettings 저장 경로로 사용됨)
    ORG_NAME = "KISP"
    APP_NAME = "KISP_Automation_Tool"
    WINDOW_TITLE = "KISP 업무 자동화 매니저"
    STYLE_PATH = RESOURCES_DIR / "style.qss"

    # [2] 윈도우 기본 크기
    DEFAULT_WIDTH = 1000
    DEFAULT_HEIGHT = 700

    # [3] QSettings 저장용 Key값
    KEY_PATH_CREATE = "folder_create_base_path"   # 폴더 생성 탭 경로
    KEY_PATH_RENAME = "folder_rename_base_path"   # 이름 변경 탭 경로
    KEY_PATH_REPORT = "report_base_path"          # 보고서 관리 탭 경로

    # [4] 기타 상수
    DEFAULT_USER_NAME = "박규민"