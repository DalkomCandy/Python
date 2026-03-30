import win32com.client
from pathlib import Path
from typing import List

from common.base import FileWorker
from common.utils import is_file_locked


class WordToPdfWorker(FileWorker):
    """Word → PDF 변환 워커"""
    
    def __init__(self, path: Path):
        super().__init__(target_path=path, uses_com=True)
        self.word_app = None
    
    def scan_files(self) -> List[Path]:
        """Word 파일만 스캔 (임시 파일 제외)"""
        return [
            f for f in self.target_path.iterdir() 
            if f.is_file() 
            and f.suffix.lower() in ('.doc', '.docx') 
            and not f.name.startswith('~$')
        ]
    
    def prepare(self) -> bool:
        """Word 애플리케이션 초기화"""
        if not super().prepare():
            return False
        
        try:
            self.word_app = win32com.client.Dispatch('Word.Application')
            self.word_app.Visible = False
            self.word_app.DisplayAlerts = False
            return True
        except Exception as e:
            self.finished_error.emit(f"Word 실행 실패: {e}")
            return False
    
    def process_item(self, file_path: Path) -> bool:
        """개별 파일 변환"""
        # 파일 잠금 체크
        if is_file_locked(file_path):
            self.emit_message(f"⚠️ 스킵(열림): {file_path.name}", "warning")
            return False
        
        pdf_path = file_path.with_suffix('.pdf')
        
        try:
            doc = self.word_app.Documents.Open(
                str(file_path), 
                ReadOnly=True, 
                Visible=False
            )
            doc.SaveAs(str(pdf_path), FileFormat=17)
            doc.Close(SaveChanges=False)
            
            self.emit_message(f"✓ {file_path.name}", "success")
            return True
            
        except Exception as e:
            self.emit_message(f"❌ {file_path.name}: {e}", "error")
            return False
    
    def finalize(self):
        """Word 애플리케이션 종료"""
        if self.word_app:
            try:
                self.word_app.Quit(SaveChanges=False)
            except:
                pass
        
        super().finalize()