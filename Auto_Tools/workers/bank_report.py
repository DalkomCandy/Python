import shutil
from pathlib import Path
from typing import Dict, List

from .base import AbstractWorker
from utils import is_file_locked
from utils.messages import Msg
from utils.domain import BANK_NAME_RE
class BankReportWorker(AbstractWorker):
    """[은행명] 패턴 파일을 은행별 폴더로 분류"""

    def __init__(self, path: Path):
        super().__init__()
        self.target_path = path
        self.bank_groups: Dict[str, List[Path]] = {}

    def validate_inputs(self) -> bool:
        if not self.target_path or not self.target_path.is_dir():
            self.finished_error.emit(Msg.fmt(Msg.INVALID_PATH, path=self.target_path))
            return False
        return True

    def prepare(self) -> bool:
        files = [f for f in self.target_path.iterdir() if f.is_file()]
        if not files:
            self.finished_success.emit(Msg.NO_FILES)
            return False

        for f in files:
            matches = BANK_NAME_RE.findall(f.name)
            if matches:
                bank = matches[-1].replace(" ", "").upper()
                self.bank_groups.setdefault(bank, []).append(f)

        if not self.bank_groups:
            self.finished_error.emit(Msg.NO_BANK_FILES)
            return False

        self.stats['total'] = len(self.bank_groups)
        self.emit_message(f"{len(self.bank_groups)}개 은행 발견")
        return True

    def execute(self):
        for i, (bank, files) in enumerate(self.bank_groups.items(), 1):
            if not self.check_running():
                return

            dest = self.target_path / bank / f"이동({len(files)})"
            try:
                dest.mkdir(parents=True, exist_ok=True)
                copied, skipped = 0, 0

                for f in files:
                    if not self.check_running():
                        break
                    if is_file_locked(f):
                        self.emit_message(Msg.fmt(Msg.FILE_LOCKED, name=f.name), "warning")
                        skipped += 1
                        continue
                    shutil.copy2(f, dest / f.name)
                    copied += 1

                msg = f"✓ [{bank}] {copied}개 복사"
                if skipped:
                    msg += f", {skipped}개 스킵"
                self.emit_message(msg, "success")
                self.stats['success'] += 1

            except Exception as e:
                self.emit_message(f"❌ [{bank}] 실패: {e}", "error")
                self.stats['fail'] += 1

            self.emit_progress(i, self.stats['total'])

    def finalize(self):
        self.emit_summary()
