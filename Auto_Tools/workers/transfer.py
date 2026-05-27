import shutil
from pathlib import Path
from win32com.client import Dispatch

from .base import FolderWorker
from utils.messages import Msg


class TransferWorker(FolderWorker):
    """전기 → 당기 폴더 복사 + 바로가기 생성 + 파일명 일괄 변경"""

    def __init__(self, prev_path: Path, next_path: Path,
                 link_name: str, prev_word: str, next_word: str):
        super().__init__(source_path=prev_path, target_path=next_path, uses_com=True)
        self.link_name  = link_name.strip()
        self.prev_word  = prev_word
        self.next_word  = next_word
        self._shell     = None   # WScript.Shell 재사용

    def prepare(self) -> bool:
        try:
            self.target_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.finished_error.emit(Msg.fmt(Msg.NEXT_FOLDER_FAIL, error=e)); return False

        if self.link_name:
            try:
                self._shell = Dispatch('WScript.Shell')
            except Exception as e:
                self.emit_message(Msg.fmt(Msg.SHELL_INIT_FAIL, error=e), "warning")

        return super().prepare()

    def process_folder(self, folder_path: Path) -> bool:
        had_errors = False
        dst = self.target_path / folder_path.name
        self.emit_message(f"📁 처리 중: {folder_path.name}")

        try:
            self._copy_recursive(folder_path, dst)
        except Exception as e:
            self.emit_message(Msg.fmt(Msg.COPY_FAIL, name=folder_path.name, error=e), "warning")
            had_errors = True

        if self.link_name and not self._create_shortcut(folder_path, dst):
            had_errors = True

        if self.prev_word and self.next_word and not self._rename_files(dst):
            had_errors = True

        if not had_errors:
            self.emit_message(f"✓ {folder_path.name} 완료", "success")
        return had_errors

    def _copy_recursive(self, src: Path, dst: Path):
        dst.mkdir(exist_ok=True)
        for item in src.iterdir():
            if not self.check_running(): return
            d = dst / item.name
            if item.is_dir():
                self._copy_recursive(item, d)
            elif not d.exists() or item.stat().st_mtime > d.stat().st_mtime:
                shutil.copy2(item, d)

    def _create_shortcut(self, target: Path, folder: Path) -> bool:
        if not self._shell:
            self.emit_message(Msg.SHORTCUT_NO_SHELL, "warning"); return False
        try:
            safe_name = "".join(c for c in self.link_name if c not in r'<>:"/\|?*')
            if not safe_name:
                self.emit_message(Msg.SHORTCUT_INVALID, "warning"); return False
            lnk = folder / f"{safe_name}.lnk"
            sc  = self._shell.CreateShortCut(str(lnk))
            sc.TargetPath       = str(target)
            sc.WorkingDirectory = str(folder)
            sc.Save()
            return True
        except Exception as e:
            self.emit_message(Msg.fmt(Msg.SHORTCUT_FAIL, error=e), "warning"); return False

    def _rename_files(self, folder: Path) -> bool:
        ok = True
        for f in list(folder.rglob('*')):
            if not self.check_running(): break
            if f.is_file() and self.prev_word in f.name:
                new_path = f.with_name(f.name.replace(self.prev_word, self.next_word))
                if not new_path.exists():
                    try:
                        f.rename(new_path)
                    except Exception as e:
                        self.emit_message(Msg.fmt(Msg.RENAME_FAIL, name=f.name, error=e), "warning")
                        ok = False
        return ok
