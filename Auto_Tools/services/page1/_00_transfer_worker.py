"""
전기 종목 이전 워커 - FolderWorker 기반 리팩토링
"""

import shutil
from pathlib import Path
from win32com.client import Dispatch

from common.base import FolderWorker


class TransferWorker(FolderWorker):
    """
    전기 종목 이전 작업
    
    폴더 단위로:
    1. 폴더 복사
    2. 바로가기 생성  
    3. 파일명 일괄 변경
    """
    
    def __init__(self, prev_path: Path, next_path: Path, 
                 link_name: str, prev_word: str, next_word: str):

        # FolderWorker 초기화
        super().__init__(
            source_path=prev_path,
            target_path=next_path,
            uses_com=True  # 바로가기 생성용
        )
        
        self.link_name = link_name.strip()
        self.prev_word = prev_word
        self.next_word = next_word
    
    def prepare(self) -> bool:
        """당기 폴더 생성 + 폴더 스캔"""
        # 1. 당기 폴더 생성
        try:
            self.target_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.finished_error.emit(f"당기 폴더 생성 실패: {e}")
            return False
        
        # 2. 전기 폴더 스캔 (자동)
        return super().prepare()
    
    def process_folder(self, folder_path: Path) -> bool:
        """
        개별 폴더 처리 (핵심 로직만!)
        
        Args:
            folder_path: 처리할 폴더 (전기 폴더 내의 각 종목 폴더)
        
        Returns:
            오류가 있었으면 True, 없으면 False
        """
        had_errors = False
        target_name = folder_path.name
        dst_path = self.target_path / target_name
        
        self.emit_message(f"📁 처리 중: {target_name}", "info")
        
        # 1. 폴더 복사
        try:
            self._copy_folder_recursive(folder_path, dst_path)
        except Exception as e:
            self.emit_message(f"⚠️ 복사 실패 ({target_name}): {e}", "warning")
            had_errors = True
        
        # 2. 바로가기 생성
        if self.link_name:
            if not self._create_shortcut(folder_path, dst_path):
                had_errors = True
        
        # 3. 파일명 변경
        if self.prev_word and self.next_word:
            if not self._rename_files_recursive(dst_path):
                had_errors = True
        
        if not had_errors:
            self.emit_message(f"✓ {target_name} 완료", "success")
        
        return had_errors
    
    # ========== 내부 헬퍼 메서드 ==========
    
    def _copy_folder_recursive(self, src: Path, dst: Path):
        """재귀적 폴더 복사"""
        dst.mkdir(exist_ok=True)
        
        for item in src.iterdir():
            if not self.check_running():
                return
            
            dst_item = dst / item.name
            
            if item.is_dir():
                self._copy_folder_recursive(item, dst_item)
            else:
                # 최신 파일만 복사
                if not dst_item.exists() or item.stat().st_mtime > dst_item.stat().st_mtime:
                    shutil.copy2(item, dst_item)
    
    def _create_shortcut(self, target: Path, folder: Path) -> bool:
        try:
            shell = Dispatch('WScript.Shell')
            
            # 파일명에 사용 불가능한 문자 제거
            safe_name = "".join(
                c for c in self.link_name 
                if c not in r'<>:"/\|?*'
            )
            
            if not safe_name:
                self.emit_message("⚠️ 바로가기 이름이 유효하지 않습니다", "warning")
                return False
            
            lnk_path = folder / f"{safe_name}.lnk"
            shortcut = shell.CreateShortCut(str(lnk_path))
            shortcut.TargetPath = str(target)
            shortcut.WorkingDirectory = str(folder)
            shortcut.Save()
            
            return True
            
        except Exception as e:
            self.emit_message(f"⚠️ 바로가기 생성 실패: {e}", "warning")
            return False
    
    def _rename_files_recursive(self, folder: Path) -> bool:
        had_errors = False
        
        for file_path in list(folder.rglob('*')):
            if not self.check_running():
                break
            
            if file_path.is_file() and self.prev_word in file_path.name:
                new_name = file_path.name.replace(self.prev_word, self.next_word)
                new_path = file_path.with_name(new_name)
                
                if not new_path.exists():
                    try:
                        file_path.rename(new_path)
                    except Exception as e:
                        self.emit_message(
                            f"⚠️ 이름 변경 실패 ({file_path.name}): {e}",
                            "warning"
                        )
                        had_errors = True
        
        return not had_errors