from pathlib import Path
from .base import FileWorker
from utils import is_file_locked
from utils.messages import Msg


class JobNumberWorker(FileWorker):
    """'J12345_파일명.docx' → '파일명.docx' 일괄 정리"""

    def __init__(self, path: Path):
        super().__init__(target_path=path)
        self._skipped = 0

    def prepare(self) -> bool:
        self._skipped = 0
        return super().prepare()

    def process_item(self, file_path: Path) -> bool:
        if not (file_path.name.startswith("J") and "_" in file_path.name):
            self._skipped += 1
            return True

        if is_file_locked(file_path):
            self.emit_message(Msg.fmt(Msg.FILE_LOCKED, name=file_path.name), "warning")
            return False

        new_name = file_path.name.split("_", 1)[1]
        new_path = file_path.with_name(new_name)

        if new_path.exists():
            self.emit_message(Msg.fmt(Msg.JOB_DUPLICATE, name=new_name), "warning")
            return False

        try:
            file_path.rename(new_path)
            self.emit_message(f"✓ {file_path.name} → {new_name}")
            return True
        except Exception as e:
            self.emit_message(f"❌ 오류 ({file_path.name}): {e}", "error")
            return False

    def finalize(self):
        self.stats['total'] -= self._skipped
        self.emit_summary()
