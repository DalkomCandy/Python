from pathlib import Path

from common.base import FileWorker
from common.utils import is_file_locked

class JobNumberWorker(FileWorker):
    def __init__(self, path: Path):
        super().__init__(target_path=path, uses_com=False)
    
    def process_item(self, file_path: Path) -> bool:
        # 대상 파일이 아니면 성공으로 처리 (스킵)
        if not (file_path.name.startswith("J") and "_" in file_path.name):
            return True
        
        # 파일 잠금 체크
        if is_file_locked(file_path):
            self.emit_message(f"⚠️ 스킵(열림): {file_path.name}", "warning")
            return False
        
        # 이름 변경 시도
        try:
            new_name = file_path.name.split("_", 1)[1]
            new_path = file_path.with_name(new_name)
            
            # 중복 체크
            if new_path.exists():
                self.emit_message(f"⚠️ 중복: {new_name}", "warning")
                return False
            
            # 변경 실행
            file_path.rename(new_path)
            self.emit_message(f"✓ {file_path.name} → {new_name}", "info")
            return True
            
        except Exception as e:
            self.emit_message(f"❌ 오류 ({file_path.name}): {e}", "error")
            return False