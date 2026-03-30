"""
ClipboardTable - Excel처럼 복사/붙여넣기가 가능한 테이블

수정 사항:
- _show_context_menu 메서드 추가 (누락되어 있었음)
"""

import qtawesome as qta
from typing import Optional, Iterable, Set
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QApplication, QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QKeySequence, QKeyEvent, QAction


class ClipboardTable(QTableWidget):    
    def __init__(self, 
                 allowed_paste_cols: Optional[Iterable[int]] = None,
                 allowed_edit_cols: Optional[Iterable[int]] = None, 
                 parent=None):
        
        super().__init__(parent)
        
        # 권한 설정
        self.paste_cols: Optional[Set[int]] = set(allowed_paste_cols) if allowed_paste_cols else None
        self.edit_cols: Optional[Set[int]] = set(allowed_edit_cols) if allowed_edit_cols else None
        
        # 테이블 설정
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # 시그널 연결
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    # ========== 키보드 이벤트 ==========
    
    def keyPressEvent(self, event: QKeyEvent):
        """키 입력 처리"""
        if event.matches(QKeySequence.StandardKey.Paste):
            self.paste_from_clipboard()
        elif event.matches(QKeySequence.StandardKey.Copy):
            self.copy_to_clipboard()
        elif event.key() == Qt.Key.Key_Delete:
            self.delete_selected()
        else:
            super().keyPressEvent(event)
    
    # ========== 클립보드 작업 ==========
    
    def copy_to_clipboard(self):
        """선택 영역을 클립보드로 복사"""
        selection = self.selectedRanges()
        if not selection:
            return
        
        rows_data = []
        for r_range in selection:
            for r in range(r_range.topRow(), r_range.bottomRow() + 1):
                row_text = []
                for c in range(r_range.leftColumn(), r_range.rightColumn() + 1):
                    item = self.item(r, c)
                    row_text.append(item.text() if item else "")
                rows_data.append("\t".join(row_text))
        
        QApplication.clipboard().setText("\n".join(rows_data))
    
    def paste_from_clipboard(self):
        """클립보드에서 붙여넣기"""
        text = QApplication.clipboard().text()
        if not text:
            return
        
        start_row = max(0, self.currentRow())
        start_col = max(0, self.currentColumn())
        
        # 탭/줄바꿈으로 분리
        rows = [line.split('\t') for line in text.splitlines()]
        
        for i, row_data in enumerate(rows):
            r = start_row + i
            
            # 필요하면 행 추가
            if r >= self.rowCount():
                self.insertRow(self.rowCount())
            
            for j, val in enumerate(row_data):
                c = start_col + j
                
                # 컬럼 범위 체크
                if c >= self.columnCount():
                    break
                
                # 붙여넣기 권한 체크
                if self.paste_cols is not None and c not in self.paste_cols:
                    continue
                
                # 아이템 생성 또는 가져오기
                item = self.item(r, c)
                if not item:
                    item = QTableWidgetItem()
                    self.setItem(r, c, item)
                
                item.setText(val.strip())
    
    def delete_selected(self):
        """선택된 셀 삭제"""
        for item in self.selectedItems():
            # 편집 권한 체크
            if self.edit_cols is not None and self.column(item) not in self.edit_cols:
                continue
            
            item.setText("")
    
    # ========== 컨텍스트 메뉴 ==========
    
    def _show_context_menu(self, position: QPoint):
        """
        우클릭 컨텍스트 메뉴 표시
        
        Args:
            position: 마우스 클릭 위치
        """
        # 선택된 항목이 없으면 메뉴 표시 안 함
        if not self.selectedItems():
            return
        
        # 메뉴 생성
        menu = QMenu(self)
        
        # 복사 액션
        copy_action = QAction(qta.icon('fa5s.copy', color='#333'), "복사 (Ctrl+C)", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        menu.addAction(copy_action)
        
        # 붙여넣기 액션
        paste_action = QAction(qta.icon('fa5s.paste', color='#333'), "붙여넣기 (Ctrl+V)", self)
        paste_action.triggered.connect(self.paste_from_clipboard)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        # 삭제 액션
        delete_action = QAction(qta.icon('fa5s.trash', color='#d32f2f'), "삭제 (Del)", self)
        delete_action.triggered.connect(self.delete_selected)
        menu.addAction(delete_action)
        
        # 메뉴 표시
        menu.exec(self.viewport().mapToGlobal(position))