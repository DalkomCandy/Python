import shutil
import re
from pathlib import Path
from typing import Dict, List

from common.base import FileWorker
from common.utils import is_file_locked


class BankReportWorker(FileWorker):
    def __init__(self, path: Path, username: str = "박규민"):
        super().__init__(target_path=path, uses_com=False)
        self.username = username
        self.pattern = re.compile(r'\[(.*?)\]')
        
        # 은행별 파일 그룹
        self.bank_groups: Dict[str, List[Path]] = {}
    
    def prepare(self) -> bool:
        """파일 분석하여 은행별로 그룹화"""
        if not super().prepare():
            return False
        
        self.emit_message("파일 분석 중...", "info")
        
        # 은행별로 그룹화
        for file_path in self.files:
            matches = self.pattern.findall(file_path.name)
            if matches:
                bank_name = matches[-1].replace(" ", "").upper()
                
                if bank_name not in self.bank_groups:
                    self.bank_groups[bank_name] = []
                
                self.bank_groups[bank_name].append(file_path)
        
        if not self.bank_groups:
            self.finished_error.emit("분류 가능한 파일이 없습니다.")
            return False
        
        self.emit_message(f"{len(self.bank_groups)}개 은행 발견", "info")
        return True
    
    def execute(self):
        total_banks = len(self.bank_groups)
        current = 0
        
        for bank_name, file_list in self.bank_groups.items():
            if not self.check_running():
                return
            
            current += 1
            
            # 대상 폴더: {경로}/{은행명}/{사용자명(파일수)}
            dest_folder = self.target_path / bank_name / f"{self.username}({len(file_list)})"
            
            try:
                dest_folder.mkdir(parents=True, exist_ok=True)
                
                # 파일 복사
                copied = 0
                skipped = 0
                
                for src_file in file_list:
                    if not self.check_running():
                        break
                    
                    # 잠금 체크
                    if is_file_locked(src_file):
                        self.emit_message(f"⚠️ 스킵(열림): {src_file.name}", "warning")
                        skipped += 1
                        continue
                    
                    # 파일 복사
                    shutil.copy2(src_file, dest_folder / src_file.name)
                    copied += 1
                
                self.emit_message(
                    f"✓ [{bank_name}] {copied}개 복사" + 
                    (f", {skipped}개 스킵" if skipped > 0 else ""), 
                    "success"
                )
                self.stats['success'] += 1
                
            except Exception as e:
                self.emit_message(f"❌ [{bank_name}] 실패: {e}", "error")
                self.stats['fail'] += 1
            
            self.emit_progress(current, total_banks)
        
        # 최종 요약
        self.stats['total'] = total_banks
        self.emit_summary()
    
    def process_item(self, file_path: Path) -> bool:
        pass