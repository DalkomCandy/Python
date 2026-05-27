"""쿼리 관리 탭"""

from pathlib import Path
from typing  import Optional

import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QPlainTextEdit,
    QPushButton, QLabel, QFileDialog, QInputDialog,
    QMessageBox, QApplication, QFrame, QMenu, QLineEdit,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QDragEnterEvent, QDropEvent, QFont, QColor

from utils        import Icons, AppColors, QueryStore, DBConnection
from config       import AppConfig
from widgets.task import _show_message

QUERY_EXTENSIONS = {'.txt', '.sql'}
TYPE_FOLDER = 'folder'
TYPE_QUERY  = 'query'


# ── 커스텀 트리 아이템 ────────────────────────────────────────────────
# ItemDataRole 대신 Python 속성으로 직접 저장 → PyQt6 enum 문제 없음

class TreeNode(QTreeWidgetItem):
    """id / type 을 Python 속성으로 보관하는 트리 아이템"""
    def __init__(self, parent, node_id: str, node_type: str, name: str):
        super().__init__(parent)
        self.node_id   = node_id
        self.node_type = node_type
        self.setText(0, name)


# ── 메인 탭 ──────────────────────────────────────────────────────────

class QuerySettingsTab(QWidget):

    def __init__(self):
        super().__init__()
        self.store       = QueryStore(AppConfig.QUERIES_FILE)
        self._current_id: Optional[str] = None
        self._dirty      = False
        self._db         = DBConnection()
        self.setAcceptDrops(True)
        self._build_ui()
        self._load_tree()

    # ── UI ───────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # 툴바
        tb = QHBoxLayout()
        bf = QPushButton("파일 추가")
        bf.setIcon(Icons.folder_open())
        bf.clicked.connect(lambda: self.browse_files())

        bfold = QPushButton("폴더 추가")
        bfold.setIcon(qta.icon('fa5s.folder-plus', color=AppColors.ICON_DEFAULT))
        bfold.clicked.connect(lambda: self._add_folder(None))

        hint = QLabel("또는 .txt / .sql 파일을 드래그하세요")
        hint.setStyleSheet(f"color:{AppColors.TEXT_MUTED}; font-size:11px;")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  쿼리 이름 검색...")
        self.search.setMaximumWidth(220)
        self.search.textChanged.connect(self._filter)

        tb.addWidget(bf); tb.addWidget(bfold)
        tb.addWidget(hint); tb.addStretch(); tb.addWidget(self.search)
        root.addLayout(tb)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 왼쪽: 트리
        left = QWidget()
        ll   = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 4, 0); ll.setSpacing(4)
        ll.addWidget(self._hdr("쿼리 목록"))

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(False)   # 루트 아이템 branch 화살표 제거
        self.tree.setIndentation(16)           # 자식 들여쓰기 16px
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._ctx_menu)
        self.tree.currentItemChanged.connect(self._on_select)
        ll.addWidget(self.tree)

        self.btn_rename = QPushButton("이름 수정")
        self.btn_rename.setIcon(Icons.search())
        self.btn_rename.setEnabled(False)
        self.btn_rename.clicked.connect(self._rename_cur)

        self.btn_del = QPushButton("삭제")
        self.btn_del.setIcon(Icons.trash())
        self.btn_del.setProperty("dangerButton", True)
        self.btn_del.setEnabled(False)
        self.btn_del.clicked.connect(self._delete_cur)

        br = QHBoxLayout()
        br.addWidget(self.btn_rename); br.addWidget(self.btn_del)
        ll.addLayout(br)

        # 오른쪽: 편집기 + DB
        right = QWidget()
        rl    = QVBoxLayout(right)
        rl.setContentsMargins(4, 0, 0, 0); rl.setSpacing(6)

        self.lbl_content = self._hdr("내용")
        rl.addWidget(self.lbl_content)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("왼쪽에서 쿼리를 선택하세요.")
        self.editor.setEnabled(False)
        self.editor.textChanged.connect(lambda: setattr(self, '_dirty', True))
        self.editor.setFont(self._mono())
        self.editor.setMinimumHeight(160)
        rl.addWidget(self.editor)

        er = QHBoxLayout(); er.addStretch()
        self.btn_fmt  = self._btn("SQL 포맷", qta.icon('fa5s.magic', color=AppColors.ICON_DEFAULT), self._fmt_sql,  enabled=False)
        self.btn_copy = self._btn("복사",     Icons.copy(),                                          self.copy,      enabled=False)
        self.btn_save = self._btn("저장",     Icons.check(),                                         self.save,      enabled=False, primary=True)
        self.btn_run  = self._btn("실행",     Icons.play(),                                          self._run,      enabled=False)
        for b in (self.btn_fmt, self.btn_copy, self.btn_save, self.btn_run):
            er.addWidget(b)
        rl.addLayout(er)

        # DB 연결 — 상태 + 연결/해제 버튼만 (설정은 설정 탭에서)
        dbg = QGroupBox("DB 연결 (MySQL)")
        dbl = QHBoxLayout(dbg); dbl.setSpacing(10)
        self.lbl_conn = QLabel("● 미연결")
        self.lbl_conn.setStyleSheet(f"color:{AppColors.ERROR}; font-weight:600;")
        hint = QLabel("연결 정보는 설정 탭에서 입력하세요.")
        hint.setStyleSheet(f"color:{AppColors.TEXT_MUTED}; font-size:11px;")
        self.btn_conn = QPushButton("연결")
        self.btn_conn.setFixedWidth(72)
        self.btn_conn.setProperty("primaryButton", True)
        self.btn_conn.clicked.connect(self._toggle_conn)
        dbl.addWidget(self.lbl_conn)
        dbl.addWidget(hint)
        dbl.addStretch()
        dbl.addWidget(self.btn_conn)
        rl.addWidget(dbg)

        self.lbl_result = self._hdr("결과")
        rl.addWidget(self.lbl_result)

        self.tbl = QTableWidget()
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.horizontalHeader().setStretchLastSection(True)
        self.tbl.setMinimumHeight(160)
        rl.addWidget(self.tbl)

        splitter.addWidget(left); splitter.addWidget(right)
        splitter.setStretchFactor(0, 1); splitter.setStretchFactor(1, 3)
        splitter.setSizes([220, 660])
        root.addWidget(splitter, 1)

    @staticmethod
    def _hdr(text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"font-weight:600; color:{AppColors.TEXT_DARK};")
        return l

    @staticmethod
    def _mono() -> QFont:
        f = QFont("Consolas")
        if not f.exactMatch(): f = QFont("Courier New")
        f.setPointSize(10)
        return f

    @staticmethod
    def _btn(text, icon, slot, enabled=True, primary=False) -> QPushButton:
        b = QPushButton(text)
        b.setIcon(icon)
        b.setEnabled(enabled)
        b.clicked.connect(slot)
        if primary:
            b.setProperty("primaryButton", True)
        return b

    # ── DB 연결 ──────────────────────────────────────

    def _toggle_conn(self):
        if self._db.is_connected:
            self._db.disconnect()
            self._update_conn(False)
        else:
            self._db.load()

            if not self._db.user:
                _show_message(self, "설정 필요",
                              "설정 탭에서 DB 연결 정보를 먼저 입력해주세요.")
                return

            err = self._db.connect()
            if err:
                _show_message(self, "연결 실패", err, is_error=True)
                self._update_conn(False)
            else:
                self._update_conn(True)

    def _update_conn(self, ok: bool):
        if ok:
            name = self._db.database or self._db.host
            self.lbl_conn.setText(f"● {name}")
            self.lbl_conn.setStyleSheet(f"color:{AppColors.SUCCESS}; font-weight:600;")
            self.btn_conn.setText("해제")
            self.btn_conn.setProperty("primaryButton", False)
            self.btn_conn.setProperty("dangerButton", True)
        else:
            self.lbl_conn.setText("● 미연결")
            self.lbl_conn.setStyleSheet(f"color:{AppColors.ERROR}; font-weight:600;")
            self.btn_conn.setText("연결")
            self.btn_conn.setProperty("dangerButton", False)
            self.btn_conn.setProperty("primaryButton", True)
        self.btn_conn.style().unpolish(self.btn_conn)
        self.btn_conn.style().polish(self.btn_conn)
        if self._current_id:
            self.btn_run.setEnabled(ok)

    # ── 쿼리 실행 ────────────────────────────────────

    def _run(self):
        cur = self.editor.textCursor()
        sql = cur.selectedText().strip() if cur.hasSelection() else self.editor.toPlainText().strip()
        if not sql: return
        if not self._db.is_connected:
            _show_message(self, "알림", "DB에 연결되어 있지 않습니다."); return
        self.lbl_result.setText("결과  실행 중...")
        QApplication.processEvents()
        self._show_result(self._db.execute(sql))

    def _show_result(self, res):
        t = self.tbl; elapsed = f"{res.elapsed*1000:.1f}ms"
        t.clear(); t.setRowCount(0); t.setColumnCount(0)
        if not res.ok:
            self.lbl_result.setText(f"결과  ❌ 오류 ({elapsed})")
            t.setColumnCount(1); t.setHorizontalHeaderLabels(["오류 메시지"])
            t.setRowCount(1)
            it = QTableWidgetItem(res.error); it.setForeground(QColor(AppColors.ERROR))
            t.setItem(0, 0, it); return
        if res.is_select:
            lim = len(res.rows) == DBConnection.MAX_ROWS
            self.lbl_result.setText(f"결과  ✅ {len(res.rows)}행{' (최대'+str(DBConnection.MAX_ROWS)+'행)' if lim else ''} ({elapsed})")
            t.setColumnCount(len(res.columns)); t.setHorizontalHeaderLabels(res.columns)
            t.setRowCount(len(res.rows))
            for r, row in enumerate(res.rows):
                for c, val in enumerate(row):
                    t.setItem(r, c, QTableWidgetItem("" if val is None else str(val)))
            t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            t.horizontalHeader().setStretchLastSection(True)
        else:
            self.lbl_result.setText(f"결과  ✅ {res.affected}행 영향 ({elapsed})")

    # ── 검색 ─────────────────────────────────────────

    def _filter(self, kw: str):
        kw = kw.strip().lower()
        def _ap(node) -> bool:
            m  = kw in node.text(0).lower()
            cm = any(_ap(node.child(i)) for i in range(node.childCount()))
            node.setHidden(not (m or cm or not kw))
            if cm: node.setExpanded(True)
            return m or cm
        for i in range(self.tree.topLevelItemCount()):
            _ap(self.tree.topLevelItem(i))

    # ── 트리 ─────────────────────────────────────────

    def _load_tree(self):
        self.tree.clear()
        # 루트는 tree 위젯 직접, 자식은 TreeNode 사용
        for item in self.store.all():
            node = TreeNode(self.tree, item['id'], item['type'], item['name'])
            self._set_icon(node, item)
            if item['type'] == TYPE_FOLDER:
                self._add_children(node, item.get('children', []))
        self.tree.expandAll()

    def _add_children(self, parent: 'TreeNode', items: list):
        """자식 아이템 재귀 추가 — parent는 반드시 TreeNode"""
        for item in items:
            node = TreeNode(parent, item['id'], item['type'], item['name'])
            self._set_icon(node, item)
            if item['type'] == TYPE_FOLDER:
                self._add_children(node, item.get('children', []))

    @staticmethod
    def _set_icon(node: 'TreeNode', item: dict):
        if item['type'] == TYPE_FOLDER:
            node.setIcon(0, qta.icon('fa5s.folder', color='#FBC02D'))
        else:
            ext = Path(item['name']).suffix.lower()
            node.setIcon(0, qta.icon(
                'fa5s.database' if ext == '.sql' else 'fa5s.file-alt',
                color=AppColors.ICON_DEFAULT))

    def _find(self, qid: str) -> Optional[TreeNode]:
        def _s_node(node) -> Optional[TreeNode]:
            """TreeNode 안에서 재귀 탐색"""
            if isinstance(node, TreeNode) and node.node_id == qid:
                return node
            for i in range(node.childCount()):
                found = _s_node(node.child(i))
                if found:
                    return found
            return None

        for i in range(self.tree.topLevelItemCount()):
            found = _s_node(self.tree.topLevelItem(i))
            if found:
                return found
        return None

    # ── 컨텍스트 메뉴 ────────────────────────────────

    def _ctx_menu(self, pos):
        node = self.tree.itemAt(pos)
        menu = QMenu(self)
        if node is None:
            menu.addAction(qta.icon('fa5s.folder-plus', color='#FBC02D'), "새 폴더",   lambda: self._add_folder(None))
            menu.addAction(Icons.folder_open(),                            "파일 추가", lambda: self.browse_files())
        else:
            nid, ntype = node.node_id, node.node_type
            if ntype == TYPE_FOLDER:
                menu.addAction(qta.icon('fa5s.folder-plus', color='#FBC02D'), "새 하위 폴더", lambda _id=nid: self._add_folder(_id))
                menu.addAction(Icons.folder_open(), "파일 추가", lambda _id=nid: self.browse_files(_id))
                menu.addSeparator()
            menu.addAction(Icons.search(), "이름 변경", lambda n=node: self._rename(n))
            menu.addAction(qta.icon('fa5s.arrows-alt', color=AppColors.ICON_DEFAULT), "이동", lambda _id=nid: self._move(_id))
            menu.addSeparator()
            menu.addAction(Icons.trash(), "삭제", lambda n=node: self._delete(n))
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    # ── 파일 / 폴더 추가 ─────────────────────────────

    def browse_files(self, parent_id: Optional[str] = None):
        paths, _ = QFileDialog.getOpenFileNames(self, "쿼리 파일 선택", "", "쿼리 파일 (*.sql *.txt);;모든 파일 (*)")
        for p in paths: self._add_file(p, parent_id)

    def _add_file(self, path_str: str, parent_id: Optional[str] = None):
        p = Path(path_str)
        if p.suffix.lower() not in QUERY_EXTENSIONS: return
        try:    content = p.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            _show_message(self, "오류", f"파일 읽기 실패: {e}", is_error=True); return

        if parent_id is None:
            cur = self.tree.currentItem()
            if isinstance(cur, TreeNode) and cur.node_type == TYPE_FOLDER:
                parent_id = cur.node_id

        q    = self.store.add_query(p.name, content, parent_id)
        pn   = self._find(parent_id) if parent_id else None
        if pn:
            node = TreeNode(pn, q['id'], TYPE_QUERY, q['name'])
            pn.setExpanded(True)
        else:
            node = TreeNode(self.tree, q['id'], TYPE_QUERY, q['name'])
        ext = p.suffix.lower()
        node.setIcon(0, qta.icon('fa5s.database' if ext == '.sql' else 'fa5s.file-alt', color=AppColors.ICON_DEFAULT))
        self.tree.setCurrentItem(node)

    def _add_folder(self, parent_id: Optional[str]):
        name, ok = QInputDialog.getText(self, "새 폴더", "폴더 이름:")
        if not ok or not name.strip(): return
        folder = self.store.add_folder(name.strip(), parent_id)
        pn     = self._find(parent_id) if parent_id else None
        if pn:
            node = TreeNode(pn, folder['id'], TYPE_FOLDER, folder['name'])
            pn.setExpanded(True)
        else:
            node = TreeNode(self.tree, folder['id'], TYPE_FOLDER, folder['name'])
        node.setIcon(0, qta.icon('fa5s.folder', color='#FBC02D'))
        self.tree.setCurrentItem(node)

    # ── 드래그앤드롭 ─────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            if any(Path(u.toLocalFile()).suffix.lower() in QUERY_EXTENSIONS for u in event.mimeData().urls()):
                event.acceptProposedAction(); return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls(): self._add_file(url.toLocalFile())

    # ── 선택 변경 ────────────────────────────────────

    def _on_select(self, current, previous):
        if (self._dirty and isinstance(previous, TreeNode)
                and previous.node_type == TYPE_QUERY):
            self.store.update(previous.node_id, content=self.editor.toPlainText())
            self._dirty = False

        is_q = isinstance(current, TreeNode) and current.node_type == TYPE_QUERY
        self.btn_rename.setEnabled(isinstance(current, TreeNode))
        self.btn_del.setEnabled(isinstance(current, TreeNode))

        if not is_q:
            self._clear(); return

        q = self.store.get(current.node_id)
        if not q: return
        self._current_id = current.node_id
        self.editor.blockSignals(True)
        self.editor.setPlainText(q.get('content', ''))
        self.editor.blockSignals(False)
        self._dirty = False
        self._set_edit(True)
        self.btn_fmt.setEnabled(Path(q['name']).suffix.lower() == '.sql')
        self.btn_run.setEnabled(self._db.is_connected)
        self.lbl_content.setText(f"내용 — {q['name']}")

    def _clear(self):
        self.editor.blockSignals(True); self.editor.setPlainText(""); self.editor.blockSignals(False)
        self._current_id = None; self._dirty = False
        self._set_edit(False); self.lbl_content.setText("내용")

    def _set_edit(self, on: bool):
        self.editor.setEnabled(on); self.btn_copy.setEnabled(on); self.btn_save.setEnabled(on)
        if not on: self.btn_fmt.setEnabled(False); self.btn_run.setEnabled(False)

    # ── 편집기 액션 ──────────────────────────────────

    def save(self):
        if self._current_id:
            self.store.update(self._current_id, content=self.editor.toPlainText())
            self._dirty = False

    def copy(self):
        t = self.editor.toPlainText()
        if t: QApplication.clipboard().setText(t)

    def _fmt_sql(self):
        try: import sqlparse
        except ImportError:
            _show_message(self, "알림", "pip install sqlparse 후 사용 가능합니다."); return
        raw = self.editor.toPlainText().strip()
        if raw: self.editor.setPlainText(sqlparse.format(raw, reindent=True, keyword_case='upper', indent_width=4))

    # ── 트리 액션 ────────────────────────────────────

    def _rename_cur(self):
        n = self.tree.currentItem()
        if isinstance(n, TreeNode): self._rename(n)

    def _delete_cur(self):
        n = self.tree.currentItem()
        if isinstance(n, TreeNode): self._delete(n)

    def _rename(self, node: TreeNode):
        new, ok = QInputDialog.getText(self, "이름 변경", "새 이름:", text=node.text(0))
        if not ok or not new.strip() or new.strip() == node.text(0): return
        new = new.strip()
        self.store.update(node.node_id, name=new); node.setText(0, new)
        if self._current_id == node.node_id: self.lbl_content.setText(f"내용 — {new}")

    def _move(self, qid: str):
        folders = self.store.folders()
        choices = ["(루트)"] + [f['name'] for f in folders if f['id'] != qid]
        choice, ok = QInputDialog.getItem(self, "이동", "이동할 폴더:", choices, 0, False)
        if not ok: return
        new_parent = None if choice == "(루트)" else next((f['id'] for f in folders if f['name'] == choice), None)
        self.store.move(qid, new_parent); self._load_tree()

    def _delete(self, node: TreeNode):
        suffix = "\n(하위 쿼리 전체 포함)" if node.node_type == TYPE_FOLDER else ""
        if QMessageBox.question(
                self, "삭제 확인",
                f"'{node.text(0)}' 을(를) 삭제하시겠습니까?{suffix}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self.store.delete(node.node_id)
        parent = node.parent()
        if parent is not None:
            parent.removeChild(node)   # 자식 노드 → 부모에서 제거
        else:
            idx = self.tree.indexOfTopLevelItem(node)
            self.tree.takeTopLevelItem(idx)   # 루트 노드 → tree에서 직접 제거
        if self._current_id == node.node_id:
            self._clear()
