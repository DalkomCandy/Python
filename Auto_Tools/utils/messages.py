"""
앱 전체 사용자 메시지 중앙 관리

변경 시 이 파일만 수정하면 모든 곳에 반영됨.
동적 값이 필요한 경우 Msg.fmt(Msg.TEMPLATE, key=value) 사용.
"""


class Msg:

    # ── 공통 UI ──────────────────────────────────────────────
    NO_FOLDER    = "폴더를 선택해주세요."
    NOT_A_DIR    = "유효한 폴더가 아닙니다."
    INVALID_PATH = "유효하지 않은 경로: {path}"
    NETWORK_BLOCKED = "네트워크 드라이브는 지원하지 않습니다.\n로컬 폴더를 선택해주세요."

    # ── Worker 공통 ──────────────────────────────────────────
    COM_MISSING    = "pythoncom 모듈이 없습니다."
    USER_STOPPED   = "사용자에 의해 작업이 중단되었습니다."
    NO_FILES       = "처리할 파일이 없습니다."
    NO_FOLDERS     = "처리할 폴더가 없습니다."
    SCAN_FAIL      = "파일 스캔 실패: {error}"
    FOLDER_SCAN_FAIL = "폴더 스캔 실패: {error}"
    FILE_LOCKED    = "⚠️ 스킵(열림): {name}"

    # ── 전기/당기 이전 ───────────────────────────────────────
    NEXT_FOLDER_FAIL = "당기 폴더 생성 실패: {error}"
    COPY_FAIL        = "⚠️ 복사 실패 ({name}): {error}"
    RENAME_FAIL      = "⚠️ 이름 변경 실패 ({name}): {error}"
    SHORTCUT_NO_SHELL   = "⚠️ 바로가기 생성 불가 (Shell 초기화 실패)"
    SHORTCUT_INVALID    = "⚠️ 바로가기 이름이 유효하지 않습니다"
    SHORTCUT_FAIL       = "⚠️ 바로가기 생성 실패: {error}"
    SHELL_INIT_FAIL     = "⚠️ WScript.Shell 초기화 실패: {error}"

    # ── 업무번호 삭제 ─────────────────────────────────────────
    JOB_DUPLICATE = "⚠️ 중복: {name}"

    # ── Word → PDF ───────────────────────────────────────────
    WORD_LAUNCH_FAIL = "Word 실행 실패: {error}"

    # ── 은행별 보고서 정리 ────────────────────────────────────
    NO_BANK_FILES    = "분류 가능한 파일이 없습니다."
    NO_DOCX          = "선택 폴더에 검사할 .docx 파일이 없습니다."
    EXCEL_SAVE_FAIL  = "엑셀 저장 실패: {error}"

    # ── 평가파일 점검 ─────────────────────────────────────────
    NO_SUBFOLDERS    = "하위 폴더가 없습니다."
    PREFIX_EMPTY     = "점검 Prefix가 선택되지 않았습니다."
    PREFIX_NOT_FOUND = "prefix를 감지할 수 없습니다. 파일명이 'YY.NQ_' 형식인지 확인해주세요."

    @staticmethod
    def fmt(template: str, **kwargs) -> str:
        """동적 값이 있는 메시지 포맷팅"""
        return template.format(**kwargs)
