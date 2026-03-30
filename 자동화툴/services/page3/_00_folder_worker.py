from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
import openpyxl
import docx


class FolderManagementWorker(QThread):
    """
    폴더/파일 생성 및 이름 변경 Worker
    
    Signals:
        status_updated(int, str, str): (row, message, color)
        finished(int): 성공 개수
    """
    
    status_updated = pyqtSignal(int, str, str)
    finished = pyqtSignal(int)

    def __init__(self, task_type: str, base_path: Path, names: list, tasks: list):
        """
        Args:
            task_type: 'create' 또는 'rename'
            base_path: 작업 기준 경로
            names: 이름 목록 (사용 안 함, 호환성 유지)
            tasks: 작업 목록
        """
        super().__init__()
        self.task_type = task_type
        self.base_path = base_path
        self.tasks = tasks

    def run(self):
        """작업 실행"""
        success_count = 0
        
        for task in self.tasks:
            try:
                if self.task_type == 'create':
                    row, name, c_type = task
                    self._create_logic(row, name, c_type)
                elif self.task_type == 'rename':
                    row, old, new = task
                    self._rename_logic(row, old, new)
                
                success_count += 1
                
            except Exception as e:
                # 실패 시 빨간색 메시지 전송
                self.status_updated.emit(task[0], f"❌ 실패: {str(e)}", "#d32f2f")
        
        self.finished.emit(success_count)

    def _create_logic(self, row: int, name: str, c_type: int):
        """
        항목 생성
        
        Args:
            row: 행 번호
            name: 생성할 이름
            c_type: 0=폴더, 1=엑셀, 2=워드
        """
        target = self.base_path / name
        
        if c_type == 0:  # 폴더
            target.mkdir(parents=True, exist_ok=False)
            
        elif c_type == 1:  # 엑셀
            target = target.with_suffix('.xlsx')
            if target.exists():
                raise FileExistsError("이미 존재함")
            openpyxl.Workbook().save(target)
            
        elif c_type == 2:  # 워드
            target = target.with_suffix('.docx')
            if target.exists():
                raise FileExistsError("이미 존재함")
            docx.Document().save(target)
        
        self.status_updated.emit(row, "✨ 완료", "#2e7d32")

    def _rename_logic(self, row: int, old: str, new: str):
        """
        이름 변경
        
        Args:
            row: 행 번호
            old: 기존 이름
            new: 새 이름
        """
        src = self.base_path / old
        dst = self.base_path / new
        
        # 대소문자만 다른 경우는 허용
        if dst.exists() and old.lower() != new.lower():
            raise FileExistsError("이름 중복")
        
        src.rename(dst)
        self.status_updated.emit(row, "✅ 완료", "#2e7d32")