from pathlib import Path
import sys


class AppConfig:

    # 경로
    BASE_DIR      = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(__file__).parent.resolve()
    RESOURCES_DIR = BASE_DIR / "gui"
    STYLE_PATH    = RESOURCES_DIR / "style.qss"

    # 앱 정보 (QSettings 키로도 사용)
    ORG_NAME     = "KISP"
    APP_NAME     = "KISP_Automation_Tool"
    WINDOW_TITLE = "KISP 업무 자동화 매니저"

    # 윈도우 기본 크기
    DEFAULT_WIDTH  = 1000
    DEFAULT_HEIGHT = 700

    # QSettings 키
    KEY_PATH_CREATE    = "folder_create_path"
    KEY_PATH_RENAME    = "folder_rename_path"
    KEY_PATH_JOB_NUM   = "report_job_number_path"
    KEY_PATH_WORD_PDF  = "report_word_pdf_path"
    KEY_PATH_BANK      = "report_bank_path"
    KEY_PATH_VALIDATOR = "report_validator_path"

    # 데이터 파일
    QUERIES_FILE = BASE_DIR / "queries.json"
