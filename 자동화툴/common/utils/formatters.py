from datetime import datetime

def format_time(seconds: float) -> str:

    if seconds < 60:
        return f"{int(seconds)}초"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}분 {secs}초"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}시간 {minutes}분"


def format_file_size(bytes_size: int) -> str:

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.1f} PB"


def format_timestamp(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:

    if dt is None:
        dt = datetime.now()
    
    return dt.strftime(format_str)

# [1] 파일명용 타임스탬프 생성
def format_date_filename(prefix: str = "", suffix: str = "", 
                        format_str: str = "%Y%m%d_%H%M%S") -> str:

    timestamp = datetime.now().strftime(format_str)
    
    parts = []
    if prefix:
        parts.append(prefix)
    parts.append(timestamp)
    if suffix:
        parts.append(suffix)
    
    return "_".join(parts)

def format_progress_message(current: int, total: int, item_name: str = "") -> str:

    msg = f"[{current}/{total}]"
    if item_name:
        msg += f" {item_name}"
    
    return msg