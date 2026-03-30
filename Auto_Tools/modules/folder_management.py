import openpyxl
import docx
import qtawesome as qta
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QComboBox,
    QPushButton, QLabel, QMessageBox, QTableWidgetItem, QHeaderView, 
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush

from common.components import PathInputWidget, ClipboardTable
from common.utils import validate_filename, IS_WINDOWS
from config import AppConfig

# 스타일 분리
class StatusColor:
    SUCCESS     = "#2e7d32"
    WARNING     = "#f57c00"
    ERROR       = "#d32f2f"
    INFO        = "#1976d2"
    DEFAULT     = "#000000"

class FolderManagementTab(QTabWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.creator_tab = FolderCreatorTab()
        self.renamer_tab = FolderRenamerTab()
        self.addTab(self.creator_tab, "폴더 생성")
        self.addTab(self.renamer_tab, "폴더명 변경")

    def get_current_status(self) -> str:
        if self.currentWidget() == self.creator_tab: 
            return "일괄 생성 대기"
        return "일괄 이름 변경 대기"

# ------------------------------------------------------------
# 탭 1: 통합 생성기 (계층 구조 지원)
# ------------------------------------------------------------
class FolderCreatorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.hierarchy_mode = False  # 계층 모드 활성화 여부
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.path_input = PathInputWidget(
            "생성 위치:", 
            "항목들이 생성될 상위 경로", 
            setting_key="folder_create_path"
        )
        layout.addWidget(self.path_input)

        # 도구 모음
        toolbar = QHBoxLayout()
        
        # 생성 유형
        self.type_combo = QComboBox()
        self.type_combo.addItem(qta.icon('fa5s.folder',     color='#FBC02D'), "폴더")
        self.type_combo.addItem(qta.icon('fa5s.file-excel', color='#217346'), "Excel")
        self.type_combo.addItem(qta.icon('fa5s.file-word',  color='#2B579A'), "Word")
        self.type_combo.setMinimumWidth(150)
        self.type_combo.setFixedHeight(30)
        
        toolbar.addWidget(QLabel("생성 유형:"))
        toolbar.addWidget(self.type_combo)

        # ✨ 상위 폴더 생성 버튼
        self.btn_hierarchy = QPushButton("상위 폴더 생성")
        self.btn_hierarchy.setIcon(qta.icon('fa5s.layer-group', color='#555555'))
        self.btn_hierarchy.setCheckable(True)  # 토글 버튼
        self.btn_hierarchy.setMinimumWidth(100)
        self.btn_hierarchy.clicked.connect(self.toggle_hierarchy_mode)
        toolbar.addWidget(self.btn_hierarchy)
        
        toolbar.addStretch()

        self.btn_create = QPushButton("생성")
        self.btn_create.setIcon(qta.icon('fa5s.play', color='white'))
        self.btn_create.setProperty("primaryButton", True)
        self.btn_create.setMinimumWidth(130)
        self.btn_create.clicked.connect(self.run_create)
        toolbar.addWidget(self.btn_create)
        
        layout.addLayout(toolbar)

        # 테이블 생성
        self.table = ClipboardTable(
            allowed_paste_cols={0, 1},  # 두 컬럼 모두 붙여넣기 가능
            allowed_edit_cols={0, 1}
        )
        self.setup_table_columns()
        layout.addWidget(self.table)

    def setup_table_columns(self):
        """테이블 컬럼 설정"""
        if self.hierarchy_mode:
            # 계층 모드: 상위 폴더 | 하위 폴더 | 상태
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["상위 폴더", "하위 폴더 (생성할 이름)", "상태"])
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.table.setColumnWidth(0, 200)
        else:
            # 일반 모드: 생성할 이름 | 상태
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["생성할 이름", "상태"])
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.table.setRowCount(15)

    def toggle_hierarchy_mode(self, checked):
        """계층 모드 토글"""
        self.hierarchy_mode = checked
        
        if checked:
            self.btn_hierarchy.setText("일반 모드로")
            self.btn_hierarchy.setIcon(qta.icon('fa5s.list', color='#555'))
        else:
            self.btn_hierarchy.setText("계층 추가")
            self.btn_hierarchy.setIcon(qta.icon('fa5s.layer-group', color='#555'))
        
        # 기존 데이터 백업
        old_data = self._get_table_data()
        
        # 테이블 재구성
        self.setup_table_columns()
        
        # 데이터 복원 (가능한 범위에서)
        self._restore_table_data(old_data)

    def _get_table_data(self) -> List[Tuple]:
        """현재 테이블 데이터 가져오기"""
        data = []
        for r in range(self.table.rowCount()):
            row_data = []
            for c in range(self.table.columnCount() - 1):  # 상태 컬럼 제외
                item = self.table.item(r, c)
                row_data.append(item.text() if item else "")
            if any(row_data):  # 빈 행 제외
                data.append(tuple(row_data))
        return data

    def _restore_table_data(self, old_data: List[Tuple]):
        """데이터 복원"""
        for r, row_data in enumerate(old_data):
            if r >= self.table.rowCount():
                break
            
            if self.hierarchy_mode:
                # 일반 모드 → 계층 모드: 첫 번째 컬럼만 하위 폴더로
                if len(row_data) >= 1:
                    self.table.setItem(r, 1, QTableWidgetItem(row_data[0]))
            else:
                # 계층 모드 → 일반 모드: 상위+하위 합치기
                if len(row_data) >= 2:
                    parent = row_data[0].strip()
                    child = row_data[1].strip()
                    name = f"{parent}/{child}" if parent else child
                    self.table.setItem(r, 0, QTableWidgetItem(name))
                elif len(row_data) >= 1:
                    self.table.setItem(r, 0, QTableWidgetItem(row_data[0]))

    def _get_creation_items(self) -> List[Dict]:
        """생성할 항목 목록 가져오기"""
        items = []
        
        for r in range(self.table.rowCount()):
            if self.hierarchy_mode:
                # 계층 모드
                parent_item = self.table.item(r, 0)
                child_item = self.table.item(r, 1)
                
                parent = parent_item.text().strip() if parent_item else ""
                child = child_item.text().strip() if child_item else ""
                
                if child:  # 하위 폴더가 있어야 함
                    items.append({
                        'row': r,
                        'parent': parent if parent else None,
                        'name': child
                    })
            else:
                # 일반 모드
                name_item = self.table.item(r, 0)
                
                if name_item and name_item.text().strip():
                    items.append({
                        'row': r,
                        'parent': None,
                        'name': name_item.text().strip()
                    })
        
        return items

    def run_create(self):
        """생성 실행"""
        path_str = self.path_input.get_path()
        if not path_str:
            QMessageBox.warning(self, "경고", "생성 위치를 선택하세요.")
            return
        
        base_path = Path(path_str)
        if not base_path.is_dir():
            QMessageBox.warning(self, "오류", "유효한 경로가 아닙니다.")
            return

        items = self._get_creation_items()
        if not items:
            QMessageBox.warning(self, "알림", "입력된 항목이 없습니다.")
            return

        create_type = self.type_combo.currentIndex()
        
        # 계층 구조로 그룹화
        hierarchy = self._build_hierarchy(items)
        
        success_count = 0
        total_count = len(items)
        
        # 상위 폴더별로 처리
        for parent_name, children in hierarchy.items():
            if parent_name:
                # 상위 폴더 생성
                parent_path = base_path / parent_name
                
                # 상위 폴더명 검증
                ok, reason = validate_filename(parent_name)
                if not ok:
                    for child_info in children:
                        self._set_status(
                            child_info['row'], 
                            f"❌ 상위 폴더명 오류: {reason}", 
                            StatusColor.ERROR
                        )
                    continue
                
                # 상위 폴더 생성
                try:
                    parent_path.mkdir(exist_ok=True)
                except Exception as e:
                    for child_info in children:
                        self._set_status(
                            child_info['row'], 
                            f"❌ 상위 폴더 생성 실패: {e}", 
                            StatusColor.ERROR
                        )
                    continue
            else:
                parent_path = base_path
            
            # 하위 항목 생성
            for child_info in children:
                row = child_info['row']
                name = child_info['name']
                
                # 하위 폴더/파일명 검증
                ok, reason = validate_filename(name)
                if not ok:
                    self._set_status(row, f"❌ 불가: {reason}", StatusColor.ERROR)
                    continue

                try:
                    target_path = parent_path / name
                    
                    if create_type == 0:  # 폴더
                        target_path.mkdir(exist_ok=False)
                        
                    elif create_type == 1:  # Excel
                        if target_path.suffix.lower() != '.xlsx':
                            target_path = target_path.with_suffix('.xlsx')
                        if target_path.exists():
                            raise FileExistsError("이미 존재함")
                        wb = openpyxl.Workbook()
                        wb.save(target_path)
                        
                    elif create_type == 2:  # Word
                        if target_path.suffix.lower() != '.docx':
                            target_path = target_path.with_suffix('.docx')
                        if target_path.exists():
                            raise FileExistsError("이미 존재함")
                        doc = docx.Document()
                        doc.save(target_path)

                    # 성공 메시지
                    if parent_name:
                        msg = f"✨ {parent_name}/{name}"
                    else:
                        msg = "✨ 생성 완료"
                    
                    self._set_status(row, msg, StatusColor.SUCCESS)
                    success_count += 1

                except FileExistsError:
                    self._set_status(row, "⚠️ 이미 존재", StatusColor.WARNING)
                except Exception as e:
                    self._set_status(row, f"❌ 실패: {e}", StatusColor.ERROR)

        QMessageBox.information(
            self, 
            "완료", 
            f"총 {success_count}/{total_count}개 항목 생성 완료"
        )

    def _build_hierarchy(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """
        계층 구조 빌드
        
        Returns:
            {상위폴더명: [하위항목들]} 딕셔너리
        """
        hierarchy = defaultdict(list)
        
        for item in items:
            parent = item.get('parent', None)
            hierarchy[parent].append(item)
        
        return hierarchy

    def _set_status(self, row, text, color=None):
        """상태 컬럼 설정"""
        status_col = 2 if self.hierarchy_mode else 1
        
        item = self.table.item(row, status_col)
        if not item:
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, status_col, item)
        
        item.setText(text)
        
        if color:
            item.setForeground(QBrush(QColor(color)))


# ------------------------------------------------------------
# 탭 2: 폴더명 변경기 (기존 코드 유지)
# ------------------------------------------------------------
class FolderRenamerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.path_input = PathInputWidget(
            "대상 폴더:", 
            "이름을 바꿀 파일/폴더가 있는 곳", 
            setting_key="folder_rename_path"
        )
        self.path_input.path_changed.connect(self.load_items)
        layout.addWidget(self.path_input)

        self.table = ClipboardTable(allowed_paste_cols={1}, allowed_edit_cols={1})
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["현재 이름", "새 이름", "상태"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 250)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        
        btn_refresh = QPushButton("목록 새로고침")
        btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#333'))
        btn_refresh.clicked.connect(self.load_items)
        
        btn_replace = QPushButton("문자열 치환")
        btn_replace.setIcon(qta.icon('fa5s.search', color='#333'))
        btn_replace.clicked.connect(self.open_replace_dialog)
        
        btn_preview = QPushButton("변경 미리보기")
        btn_preview.setIcon(qta.icon('fa5s.eye', color='#333'))
        btn_preview.clicked.connect(self.check_preview)
        
        self.btn_apply = QPushButton("변경 사항 적용")
        self.btn_apply.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_apply.setProperty("dangerButton", True)
        self.btn_apply.clicked.connect(self.apply_rename)

        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_replace)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_preview)
        btn_layout.addWidget(self.btn_apply)
        
        layout.addLayout(btn_layout)

    def load_items(self):
        path_str = self.path_input.get_path()
        if not path_str or not Path(path_str).is_dir():
            return
        
        try:
            items = sorted([p.name for p in Path(path_str).iterdir()])
            self.table.setRowCount(len(items))
            
            for i, name in enumerate(items):
                item_old = QTableWidgetItem(name)
                item_old.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.table.setItem(i, 0, item_old)
                self.table.setItem(i, 1, QTableWidgetItem(name))
                
                item_st = QTableWidgetItem("")
                item_st.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(i, 2, item_st)
        except Exception as e:
            QMessageBox.warning(self, "오류", str(e))

    def open_replace_dialog(self):
        dlg = ReplaceDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            find, rep = dlg.get_values()
            if not find:
                return
            
            for r in range(self.table.rowCount()):
                item = self.table.item(r, 1)
                if item:
                    item.setText(item.text().replace(find, rep))

    def check_preview(self) -> List[Tuple[int, str, str]]:
        path_str = self.path_input.get_path()
        if not path_str:
            return []
        
        changes = []
        seen_new = set()
        base_path = Path(path_str)
        
        try:
            existing = {p.name for p in base_path.iterdir()}
        except:
            existing = set()

        for r in range(self.table.rowCount()):
            old = self.table.item(r, 0).text()
            new = self.table.item(r, 1).text().strip()
            status_item = self.table.item(r, 2)
            status_item.setText("")
            
            if old == new:
                continue

            ok, reason = validate_filename(new)
            if not ok:
                status_item.setText(f"❌ {reason}")
                status_item.setForeground(QBrush(QColor(StatusColor.ERROR)))
                continue

            is_case_only = (old.lower() == new.lower())
            if not is_case_only and new in existing:
                status_item.setText("⚠️ 이미 존재")
                status_item.setForeground(QBrush(QColor(StatusColor.WARNING)))
                continue
            
            if new in seen_new:
                status_item.setText("⚠️ 이름 중복")
                status_item.setForeground(QBrush(QColor(StatusColor.WARNING)))
                continue

            seen_new.add(new)
            changes.append((r, old, new))
            status_item.setText("🔄 대소문자" if is_case_only else "✏️ 변경 예정")
            status_item.setForeground(QBrush(QColor(StatusColor.INFO)))

        return changes

    def apply_rename(self):
        changes = self.check_preview()
        if not changes:
            QMessageBox.information(self, "알림", "변경할 항목이 없습니다.")
            return

        if QMessageBox.question(
            self, 
            "확인", 
            f"{len(changes)}개 항목 변경?"
        ) != QMessageBox.StandardButton.Yes:
            return

        base_path = Path(self.path_input.get_path())
        success = 0
        
        for r, old, new in changes:
            try:
                src = base_path / old
                dst = base_path / new
                
                from common.utils import is_file_locked
                if is_file_locked(src):
                    self.table.item(r, 2).setText("🔒 파일 열림")
                    self.table.item(r, 2).setForeground(QBrush(QColor(StatusColor.ERROR)))
                    continue

                if IS_WINDOWS and old.lower() == new.lower():
                    tmp = base_path / f"{old}_TMP_{id(self)}"
                    src.rename(tmp)
                    tmp.rename(dst)
                else:
                    src.rename(dst)
                
                self.table.item(r, 0).setText(new)
                self.table.item(r, 2).setText("✅ 완료")
                self.table.item(r, 2).setForeground(QBrush(QColor(StatusColor.SUCCESS)))
                success += 1
                
            except Exception as e:
                self.table.item(r, 2).setText(f"❌ {e}")
                self.table.item(r, 2).setForeground(QBrush(QColor(StatusColor.ERROR)))

        QMessageBox.information(self, "완료", f"{success}개 변경 완료")


class ReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("문자열 변경")
        
        layout = QFormLayout(self)
        self.f = QLineEdit()
        self.r = QLineEdit()
        
        layout.addRow("찾을 내용:", self.f)
        layout.addRow("바꿀 내용:", self.r)
        
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    
    def get_values(self):
        return self.f.text(), self.r.text()