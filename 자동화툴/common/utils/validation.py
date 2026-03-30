import sys
import re
from pathlib import Path
from typing import Tuple

# Windows 예약어 및 금지 문자
IS_WINDOWS = sys.platform.startswith('win')
INVALID_WIN_CHARS_RE = re.compile(r'[<>:"/\|?*]')
RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    *(f'COM{i}' for i in range(1, 10)),
    *(f'LPT{i}' for i in range(1, 10)),
}


def validate_filename(name: str) -> Tuple[bool, str]:
    """
    파일명 유효성 검사
    
    Windows 제약 사항 포함:
        - 예약어 (CON, PRN, etc.)
        - 금지 문자 (<>:"/\|?*)
        - 공백/마침표로 끝남
    
    Args:
        name: 검증할 파일명
    
    Returns:
        (유효 여부, 오류 메시지)
    """
    # 빈 문자열 체크
    if not name or not name.strip():
        return False, "빈 이름"
    
    # 예약 이름 체크
    if name in (".", ".."):
        return False, "예약 이름(. / ..)"
    
    # 금지 문자 체크
    if INVALID_WIN_CHARS_RE.search(name):
        return False, "허용되지 않는 문자 (<>:\"/\\|?*)"
    
    # 끝 문자 체크
    if name.endswith((" ", ".")):
        return False, "공백/마침표로 끝남"
    
    # Windows 예약 장치명 체크
    if IS_WINDOWS:
        stem = Path(name).stem.upper()
        if stem in RESERVED_NAMES:
            return False, f"예약된 장치명 ({stem})"
    
    # 길이 체크
    try:
        if len(name.encode('utf-8')) > 255:
            return False, "이름이 너무 깁니다 (255바이트 초과)"
    except:
        pass
    
    return True, ""


def validate_path(path: Path, must_exist: bool = False, must_be_dir: bool = False) -> Tuple[bool, str]:
    if not path:
        return False, "경로가 지정되지 않았습니다"
    
    if must_exist and not path.exists():
        return False, f"경로가 존재하지 않습니다: {path}"
    
    if must_be_dir and not path.is_dir():
        return False, f"디렉토리가 아닙니다: {path}"
    
    return True, ""