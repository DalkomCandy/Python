import qtawesome as qta
from typing import Optional, Iterable, Set
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QApplication, QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QKeySequence, QKeyEvent, QAction
from utils.icons import Icons


class ClipboardTable(QTableWidget):
    """Excel처럼 복사/붙여넣기/삭제가 가능한 테이블"""

    def __init__(self,
                 allowed_paste_cols: Optional[Iterable[int]] = None,
                 allowed_edit_cols:  Optional[Iterable[int]] = None,
                 parent=None):
        super().__init__(parent)
        self.paste_cols: Optional[Set[int]] = set(allowed_paste_cols) if allowed_paste_cols else None
        self.edit_cols:  Optional[Set[int]] = set(allowed_edit_cols)  if allowed_edit_cols  else None

        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    # ── 키보드 ───────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent):
        if   event.matches(QKeySequence.StandardKey.Paste):  self.paste_from_clipboard()
        elif event.matches(QKeySequence.StandardKey.Copy):   self.copy_to_clipboard()
        elif event.key() == Qt.Key.Key_Delete:               self.delete_selected()
        else: super().keyPressEvent(event)

    # ── 클립보드 ─────────────────────────────────────

    def copy_to_clipboard(self):
        rows_data = []
        for r_range in self.selectedRanges():
            for r in range(r_range.topRow(), r_range.bottomRow() + 1):
                row_text = []
                for c in range(r_range.leftColumn(), r_range.rightColumn() + 1):
                    item = self.item(r, c)
                    row_text.append(item.text() if item else "")
                rows_data.append("\t".join(row_text))
        QApplication.clipboard().setText("\n".join(rows_data))

    def paste_from_clipboard(self):
        text = QApplication.clipboard().text()
        if not text: return

        sr, sc = max(0, self.currentRow()), max(0, self.currentColumn())
        for i, row_data in enumerate([l.split('\t') for l in text.splitlines()]):
            r = sr + i
            if r >= self.rowCount(): self.insertRow(self.rowCount())
            for j, val in enumerate(row_data):
                c = sc + j
                if c >= self.columnCount(): break
                if self.paste_cols is not None and c not in self.paste_cols: continue
                item = self.item(r, c) or QTableWidgetItem()
                item.setText(val.strip())
                self.setItem(r, c, item)

    def delete_selected(self):
        for item in self.selectedItems():
            if self.edit_cols is None or self.column(item) in self.edit_cols:
                item.setText("")

    # ── 컨텍스트 메뉴 ────────────────────────────────

    def _show_context_menu(self, position: QPoint):
        if not self.selectedItems(): return
        menu = QMenu(self)
        menu.addAction(Icons.copy(),  "복사 (Ctrl+C)",      self.copy_to_clipboard)
        menu.addAction(Icons.paste(), "붙여넣기 (Ctrl+V)", self.paste_from_clipboard)
        menu.addSeparator()
        menu.addAction(Icons.trash(), "삭제 (Del)",          self.delete_selected)
        menu.exec(self.viewport().mapToGlobal(position))
