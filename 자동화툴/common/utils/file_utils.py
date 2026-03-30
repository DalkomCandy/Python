import sys
import re
from pathlib import Path
from typing import Tuple

# Windows 예약어 및 금지 문자 설정
IS_WINDOWS = sys.platform.startswith('win')
INVALID_WIN_CHARS_RE = re.compile(r'[<>:"/\|?*]')
RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    *(f'COM{i}' for i in range(1, 10)),
    *(f'LPT{i}' for i in range(1, 10)),
}

def validate_filename(name: str) -> Tuple[bool, str]:
    """
    파일명 유효성 검사 (Windows 제약 포함)
    Return: (유효여부 Bool, 이유 String)
    """
    if not name or not name.strip():
        return False, "빈 이름"
    
    if name in (".", ".."):
        return False, "예약 이름(. / ..)"
    
    if INVALID_WIN_CHARS_RE.search(name):
        return False, "허용되지 않는 문자 (<>:\"/\|?*)"
    
    if name.endswith((" ", ".")):
        return False, "공백/마침표로 끝남"
    
    if IS_WINDOWS:
        stem = Path(name).stem.upper()
        if stem in RESERVED_NAMES:
            return False, f"예약된 장치명 ({stem})"
            
    try:
        if len(name.encode('utf-8')) > 255:
            return False, "이름이 너무 깁니다"
    except:
        pass
        
    return True, ""

def is_file_locked(path: Path) -> bool:
    """
    파일이 다른 프로세스(Excel, Word 등)에 의해 잠겨있는지 확인
    True: 잠김 (사용 중), False: 안전함
    """
    if not path.exists():
        return False
        
    try:
        # 파일 이름을 자기 자신으로 변경 시도 (잠금 확인용 트릭)
        path.rename(path)
        return False
    except OSError:
        return True