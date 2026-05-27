"""
날짜/시간 포맷 문자열 중앙 관리
"""

from datetime import datetime

# 포맷 상수
FMT_DATETIME   = "%Y-%m-%d %H:%M:%S"   # 화면 표시용: 2026-05-21 14:30:00
FMT_DATE       = "%Y-%m-%d"             # 날짜만:       2026-05-21
FMT_FILE_STAMP = "%Y%m%d_%H%M%S"        # 파일명용:     20260521_143000


def fmt_now(fmt: str = FMT_DATETIME) -> str:
    """현재 시각을 지정 포맷으로 반환"""
    return datetime.now().strftime(fmt)


def fmt_datetime_str(dt: datetime) -> str:
    return dt.strftime(FMT_DATETIME)


def fmt_date_str(dt: datetime) -> str:
    return dt.strftime(FMT_DATE)


def fmt_file_stamp() -> str:
    """파일명에 쓸 타임스탬프 반환 (예: 20260521_143000)"""
    return datetime.now().strftime(FMT_FILE_STAMP)
