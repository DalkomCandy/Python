import win32com.client
from pathlib import Path
from typing import List

from .base import FileWorker
from utils import is_file_locked
from utils.domain import WORD_EXTENSIONS
from utils.messages import Msg


class WordToPdfWorker(FileWorker):
    """폴더 안 Word 파일을 PDF로 일괄 변환"""

    def __init__(self, path: Path):
        super().__init__(target_path=path, uses_com=True)
        self.word_app = None

    def scan_files(self) -> List[Path]:
        return [
            f for f in self.target_path.iterdir()
            if f.is_file()
            and f.suffix.lower() in WORD_EXTENSIONS
            and not f.name.startswith('~$')
        ]

    def prepare(self) -> bool:
        if not super().prepare(): return False
        try:
            self.word_app = win32com.client.Dispatch('Word.Application')
            self.word_app.Visible      = False
            self.word_app.DisplayAlerts = False
            return True
        except Exception as e:
            self.finished_error.emit(Msg.fmt(Msg.WORD_LAUNCH_FAIL, error=e)); return False

    def process_item(self, file_path: Path) -> bool:
        if is_file_locked(file_path):
            self.emit_message(Msg.fmt(Msg.FILE_LOCKED, name=file_path.name), "warning")
            return False
        try:
            doc = self.word_app.Documents.Open(str(file_path), ReadOnly=True, Visible=False)
            doc.SaveAs(str(file_path.with_suffix('.pdf')), FileFormat=17)
            doc.Close(SaveChanges=False)
            self.emit_message(f"✓ {file_path.name}", "success")
            return True
        except Exception as e:
            self.emit_message(f"❌ {file_path.name}: {e}", "error"); return False

    def finalize(self):
        if self.word_app:
            try: self.word_app.Quit(SaveChanges=False)
            except: pass
        super().finalize()
