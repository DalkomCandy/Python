import sys
import re
from pathlib import Path
from typing import Tuple

IS_WINDOWS           = sys.platform.startswith('win')
INVALID_WIN_CHARS_RE = re.compile(r'[<>:"/\\|?*]')
RESERVED_NAMES       = {
    'CON', 'PRN', 'AUX', 'NUL',
    *(f'COM{i}' for i in range(1, 10)),
    *(f'LPT{i}' for i in range(1, 10)),
}


def validate_filename(name: str) -> Tuple[bool, str]:
    """파일명 유효성 검사 (Windows 제약 포함)"""
    if not name or not name.strip():
        return False, "빈 이름"
    if name in (".", ".."):
        return False, "예약 이름(. / ..)"
    if INVALID_WIN_CHARS_RE.search(name):
        return False, "허용되지 않는 문자 (<>:\"/\\|?*)"
    if name.endswith((" ", ".")):
        return False, "공백/마침표로 끝남"
    if IS_WINDOWS:
        if Path(name).stem.upper() in RESERVED_NAMES:
            return False, f"예약된 장치명 ({Path(name).stem.upper()})"
    try:
        if len(name.encode('utf-8')) > 255:
            return False, "이름이 너무 깁니다 (255바이트 초과)"
    except Exception:
        pass
    return True, ""


def validate_path(path: Path, must_exist: bool = False, must_be_dir: bool = False) -> Tuple[bool, str]:
    """경로 유효성 검사"""
    if not path:
        return False, "경로가 지정되지 않았습니다"
    if must_exist and not path.exists():
        return False, f"경로가 존재하지 않습니다: {path}"
    if must_be_dir and not path.is_dir():
        return False, f"디렉토리가 아닙니다: {path}"
    return True, ""


def is_file_locked(path: Path) -> bool:
    """파일이 다른 프로세스에 의해 잠겨 있는지 확인

    UNC 경로(네트워크 드라이브)에서는 rename이 실패할 수 있으므로
    open() 방식으로 대체.
    """
    if not path.exists():
        return False

    # 네트워크 드라이브 (UNC 경로) — open으로 락 확인
    path_str = str(path)
    if path_str.startswith(('\\\\', '//')):
        try:
            with open(path, 'r+b'):
                return False
        except (IOError, OSError):
            return True

    # 로컬 드라이브 — rename 트릭
    try:
        path.rename(path)
        return False
    except OSError:
        return True
