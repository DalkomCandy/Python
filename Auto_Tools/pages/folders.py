import openpyxl
import docx
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QComboBox,
    QPushButton, QLabel, QMessageBox, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush

from widgets import PathInputWidget, ClipboardTable
from utils   import validate_filename, IS_WINDOWS, is_file_locked
from utils.colors import AppColors
from utils.icons  import Icons
from utils.messages import Msg
from config  import AppConfig


class FolderManagementTab(QTabWidget):
    def __init__(self):
        super().__init__()
        self.addTab(FolderCreatorTab(), "폴더 생성")
        self.addTab(FolderRenamerTab(), "폴더명 변경")


# ── 탭 1: 폴더/파일 생성 ──────────────────────────────────────

class FolderCreatorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.hierarchy_mode = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.path_input = PathInputWidget(
            "생성 위치:", "항목들이 생성될 상위 경로",
            setting_key=AppConfig.KEY_PATH_CREATE
        )
        layout.addWidget(self.path_input)

        # 툴바
        toolbar = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItem(Icons.folder_color(), "폴더")
        self.type_combo.addItem(Icons.excel(), "Excel")
        self.type_combo.addItem(Icons.word(), "Word")
        self.type_combo.setMinimumWidth(150)
        self.type_combo.setFixedHeight(30)
        toolbar.addWidget(QLabel("생성 유형:"))
        toolbar.addWidget(self.type_combo)

        self.btn_hierarchy = QPushButton("상위 폴더 생성")
        self.btn_hierarchy.setIcon(Icons.layer())
        self.btn_hierarchy.setCheckable(True)
        self.btn_hierarchy.clicked.connect(self.toggle_hierarchy_mode)
        toolbar.addWidget(self.btn_hierarchy)

        toolbar.addStretch()

        btn_create = QPushButton("생성")
        btn_create.setIcon(Icons.play())
        btn_create.setProperty("primaryButton", True)
        btn_create.setMinimumWidth(130)
        btn_create.clicked.connect(self.run_create)
        toolbar.addWidget(btn_create)
        layout.addLayout(toolbar)

        self.table = ClipboardTable(allowed_paste_cols={0, 1}, allowed_edit_cols={0, 1})
        self.setup_table_columns()
        layout.addWidget(self.table)

        # 행 추가/삭제 버튼
        row_btn_layout = QHBoxLayout()
        btn_add_row = QPushButton("행 추가")
        btn_add_row.setIcon(Icons.plus())
        btn_add_row.setProperty("secondaryButton", True)
        btn_add_row.clicked.connect(self._add_row)

        btn_del_row = QPushButton("행 삭제")
        btn_del_row.setIcon(Icons.minus())
        btn_del_row.setProperty("secondaryButton", True)
        btn_del_row.clicked.connect(self._delete_row)

        row_btn_layout.addWidget(btn_add_row)
        row_btn_layout.addWidget(btn_del_row)
        row_btn_layout.addStretch()
        layout.addLayout(row_btn_layout)

    def _add_row(self) -> None:
        """테이블 맨 아래에 빈 행 추가."""
        self.table.insertRow(self.table.rowCount())

    def _delete_row(self) -> None:
        """선택된 행 삭제. 선택 없으면 마지막 행 삭제."""
        selected = self.table.currentRow()
        row = selected if selected >= 0 else self.table.rowCount() - 1
        if row >= 0:
            self.table.removeRow(row)

    def setup_table_columns(self):
        if self.hierarchy_mode:
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["상위 폴더", "하위 폴더 (생성할 이름)", "상태"])
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.table.setColumnWidth(0, 200)
        else:
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["생성할 이름", "상태"])
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(15)

    def toggle_hierarchy_mode(self, checked: bool):
        self.hierarchy_mode = checked
        self.btn_hierarchy.setText("일반 모드로" if checked else "상위 폴더 생성")
        old_data = self._get_table_data()
        self.setup_table_columns()
        self._restore_table_data(old_data)

    def _get_table_data(self) -> List[Tuple]:
        data = []
        for r in range(self.table.rowCount()):
            row = [
                (self.table.item(r, c).text() if self.table.item(r, c) else "")
                for c in range(self.table.columnCount() - 1)
            ]
            if any(row): data.append(tuple(row))
        return data

    def _restore_table_data(self, old_data: List[Tuple]):
        for r, row in enumerate(old_data):
            if r >= self.table.rowCount(): break
            if self.hierarchy_mode:
                if len(row) >= 1:
                    self.table.setItem(r, 1, QTableWidgetItem(row[0]))
            else:
                if len(row) >= 2:
                    p, c = row[0].strip(), row[1].strip()
                    self.table.setItem(r, 0, QTableWidgetItem(f"{p}/{c}" if p else c))
                elif len(row) >= 1:
                    self.table.setItem(r, 0, QTableWidgetItem(row[0]))

    def _get_creation_items(self) -> List[Dict]:
        items = []
        for r in range(self.table.rowCount()):
            if self.hierarchy_mode:
                parent = (self.table.item(r, 0).text().strip() if self.table.item(r, 0) else "")
                child  = (self.table.item(r, 1).text().strip() if self.table.item(r, 1) else "")
                if child: items.append({'row': r, 'parent': parent or None, 'name': child})
            else:
                it = self.table.item(r, 0)
                if it and it.text().strip():
                    items.append({'row': r, 'parent': None, 'name': it.text().strip()})
        return items

    def run_create(self):
        path_str = self.path_input.get_path()
        if not path_str:
            QMessageBox.warning(self, "경고", "생성 위치를 선택하세요."); return
        base_path = Path(path_str)
        if not base_path.is_dir():
            QMessageBox.warning(self, "오류", "유효한 경로가 아닙니다."); return

        items = self._get_creation_items()
        if not items:
            QMessageBox.warning(self, "알림", "입력된 항목이 없습니다."); return

        create_type = self.type_combo.currentIndex()
        hierarchy   = defaultdict(list)
        for item in items:
            hierarchy[item.get('parent')].append(item)

        success, total = 0, len(items)

        for parent_name, children in hierarchy.items():
            if parent_name:
                ok, reason = validate_filename(parent_name)
                if not ok:
                    for c in children: self._set_status(c['row'], f"❌ 상위 폴더명 오류: {reason}", AppColors.ERROR)
                    continue
                try:
                    parent_path = base_path / parent_name
                    parent_path.mkdir(exist_ok=True)
                except Exception as e:
                    for c in children: self._set_status(c['row'], f"❌ 상위 폴더 생성 실패: {e}", AppColors.ERROR)
                    continue
            else:
                parent_path = base_path

            for child in children:
                row, name = child['row'], child['name']
                ok, reason = validate_filename(name)
                if not ok:
                    self._set_status(row, f"❌ 불가: {reason}", AppColors.ERROR); continue
                try:
                    target = parent_path / name
                    if create_type == 0:
                        target.mkdir(exist_ok=False)
                    elif create_type == 1:
                        target = target.with_suffix('.xlsx')
                        if target.exists(): raise FileExistsError
                        openpyxl.Workbook().save(target)
                    elif create_type == 2:
                        target = target.with_suffix('.docx')
                        if target.exists(): raise FileExistsError
                        docx.Document().save(target)
                    self._set_status(row, f"✨ {parent_name}/{name}" if parent_name else "✨ 생성 완료", AppColors.SUCCESS)
                    success += 1
                except FileExistsError:
                    self._set_status(row, "⚠️ 이미 존재", AppColors.WARNING)
                except Exception as e:
                    self._set_status(row, f"❌ 실패: {e}", AppColors.ERROR)
                QApplication.processEvents()  # UI 응답성 유지

        QMessageBox.information(self, "완료", f"총 {success}/{total}개 항목 생성 완료")

    def _set_status(self, row: int, text: str, color: str = None):
        col  = 2 if self.hierarchy_mode else 1
        item = self.table.item(row, col) or QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        item.setText(text)
        if color: item.setForeground(QBrush(QColor(color)))
        self.table.setItem(row, col, item)


# ── 탭 2: 폴더명 변경 ────────────────────────────────────────

class FolderRenamerTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.path_input = PathInputWidget(
            "대상 폴더:", "이름을 바꿀 파일/폴더가 있는 곳",
            setting_key=AppConfig.KEY_PATH_RENAME
        )
        self.path_input.path_changed.connect(self.load_items)
        layout.addWidget(self.path_input)

        self.table = ClipboardTable(allowed_paste_cols={1}, allowed_edit_cols={1})
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["현재 이름", "새 이름", "상태"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 250)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self._btn("목록 새로고침", 'fa5s.sync-alt', self.load_items))
        btn_row.addWidget(self._btn("문자열 치환",   'fa5s.search',   self.open_replace_dialog))
        btn_row.addWidget(self._btn("행 추가",       'fa5s.plus',     self._add_row))
        btn_row.addWidget(self._btn("행 삭제",       'fa5s.minus',    self._delete_row))
        btn_row.addStretch()
        btn_row.addWidget(self._btn("변경 미리보기", 'fa5s.eye',      self.check_preview))
        apply_btn = self._btn("변경 사항 적용", 'fa5s.check', self.apply_rename, danger=True)
        btn_row.addWidget(apply_btn)
        layout.addLayout(btn_row)

    def _add_row(self) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        empty = QTableWidgetItem("")
        empty.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 0, empty)
        self.table.setItem(row, 1, QTableWidgetItem(""))
        st = QTableWidgetItem("")
        st.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 2, st)

    def _delete_row(self) -> None:
        selected = self.table.currentRow()
        row = selected if selected >= 0 else self.table.rowCount() - 1
        if row >= 0:
            self.table.removeRow(row)

    def _btn(self, text, icon, slot, danger=False):
        import qtawesome as qta
        btn = QPushButton(text)
        btn.setIcon(qta.icon(icon, color='white' if danger else AppColors.ICON_NEUTRAL))
        if danger: btn.setProperty("dangerButton", True)
        btn.clicked.connect(slot)
        return btn

    def load_items(self):
        path_str = self.path_input.get_path()
        if not path_str or not Path(path_str).is_dir(): return
        try:
            items = sorted(p.name for p in Path(path_str).iterdir())
            self.table.setRowCount(len(items))
            for i, name in enumerate(items):
                old = QTableWidgetItem(name)
                old.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.table.setItem(i, 0, old)
                self.table.setItem(i, 1, QTableWidgetItem(name))
                st = QTableWidgetItem("")
                st.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(i, 2, st)
        except Exception as e:
            QMessageBox.warning(self, "오류", str(e))

    def open_replace_dialog(self):
        dlg = ReplaceDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            find, rep = dlg.get_values()
            if not find: return
            for r in range(self.table.rowCount()):
                if item := self.table.item(r, 1):
                    item.setText(item.text().replace(find, rep))

    def check_preview(self) -> List[Tuple[int, str, str]]:
        path_str = self.path_input.get_path()
        if not path_str: return []

        base_path = Path(path_str)
        try:    existing = {p.name for p in base_path.iterdir()}
        except: existing = set()

        changes, seen = [], set()
        for r in range(self.table.rowCount()):
            old_item = self.table.item(r, 0)
            new_item = self.table.item(r, 1)
            st_item  = self.table.item(r, 2)

            # 셀이 None이면 스킵
            if not old_item or not new_item or not st_item:
                continue

            old = old_item.text()
            new = new_item.text().strip()
            st_item.setText("")

            if old == new: continue

            ok, reason = validate_filename(new)
            if not ok:
                st_item.setText(f"❌ {reason}")
                st_item.setForeground(QBrush(QColor(AppColors.ERROR))); continue

            case_only = old.lower() == new.lower()
            if not case_only and new in existing:
                st_item.setText("⚠️ 이미 존재")
                st_item.setForeground(QBrush(QColor(AppColors.WARNING))); continue

            if new in seen:
                st_item.setText("⚠️ 이름 중복")
                st_item.setForeground(QBrush(QColor(AppColors.WARNING))); continue

            seen.add(new)
            changes.append((r, old, new))
            st_item.setText("🔄 대소문자" if case_only else "✏️ 변경 예정")
            st_item.setForeground(QBrush(QColor(AppColors.INFO)))
        return changes

    def apply_rename(self):
        changes = self.check_preview()
        if not changes:
            QMessageBox.information(self, "알림", "변경할 항목이 없습니다."); return
        if QMessageBox.question(self, "확인", f"{len(changes)}개 항목 변경?") != QMessageBox.StandardButton.Yes:
            return

        base_path = Path(self.path_input.get_path())
        success   = 0

        for r, old, new in changes:
            st = self.table.item(r, 2)
            if not st:
                continue
            try:
                src, dst = base_path / old, base_path / new
                if is_file_locked(src):
                    st.setText("🔒 파일 열림")
                    st.setForeground(QBrush(QColor(AppColors.ERROR))); continue
                if IS_WINDOWS and old.lower() == new.lower():
                    tmp = base_path / f"{old}_TMP_{id(self)}"
                    src.rename(tmp); tmp.rename(dst)
                else:
                    src.rename(dst)
                self.table.item(r, 0).setText(new)
                st.setText("✅ 완료")
                st.setForeground(QBrush(QColor(AppColors.SUCCESS)))
                success += 1
            except Exception as e:
                st.setText(f"❌ {e}")
                st.setForeground(QBrush(QColor(AppColors.ERROR)))

        QMessageBox.information(self, "완료", f"{success}개 변경 완료")


class ReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("문자열 변경")
        layout = QFormLayout(self)
        self.f = QLineEdit(); self.r = QLineEdit()
        layout.addRow("찾을 내용:", self.f)
        layout.addRow("바꿀 내용:", self.r)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_values(self): return self.f.text(), self.r.text()
