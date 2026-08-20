"""메인 윈도우"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
    QFormLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QScrollArea, QSpinBox, QSplitter,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from PyQt6.QtGui import QColor

import excel_macro_bot as bot
from .widgets import (
    STATUS_COLORS, STATUS_LABELS, ConsoleView, FolderRow, ProgressPanel, settings,
)
from .worker import BotWorker, MacroListWorker, ScanWorker

COLUMNS = ["파일명", "폴더", "상태", "입력값", "비고"]


def _relative(path: Path, root: Optional[Path]) -> str:
    """root 기준 상대경로. 관계가 없으면 전체 경로를 그대로 보여준다."""
    if root is None:
        return str(path)
    try:
        return str(path.relative_to(root)) or "."
    except ValueError:
        return str(path)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("엑셀 매크로 봇")
        self.resize(1180, 760)

        self.files: List[Path] = []
        self.scan_root: Optional[Path] = None   # 표의 '폴더' 열을 상대경로로 만들 기준
        self.rows: Dict[str, int] = {}          # 파일 경로 → 표 행 번호
        self.results: List[bot.Result] = []
        self.worker: Optional[BotWorker] = None
        self.helper: Optional[object] = None    # 스캔/매크로 목록 워커 참조 유지

        self._build_ui()
        self._load_settings()
        self._set_running(False)
        self.console.append_message(
            "폴더를 고르고 [파일 찾기] → [값 미리보기] 순으로 먼저 확인해 보세요."
        )

    # ── UI 구성 ──────────────────────────────────────
    def _build_ui(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_left())
        splitter.addWidget(self._build_right())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([430, 750])

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(splitter)
        self.setCentralWidget(container)
        self.statusBar().showMessage("준비됨")

        # 검색 조건이 바뀌면 이전 목록으로 실행하지 않도록 비운다
        self.folder.changed.connect(self._invalidate_files)
        self.prefix.textChanged.connect(self._invalidate_files)
        self.pattern.textChanged.connect(self._invalidate_files)
        self.limit.valueChanged.connect(self._invalidate_files)

    def _invalidate_files(self, *_) -> None:
        if not self.files:
            return
        self.files = []
        self.scan_root = None
        self.table.setRowCount(0)
        self.rows.clear()
        self.progress.reset()
        self.statusBar().showMessage("검색 조건이 바뀌었습니다 — [파일 찾기]를 다시 눌러주세요")

    def _build_left(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("panel")
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(2)

        title = QLabel("설정")
        title.setProperty("headline", True)
        outer.addWidget(title)

        outer.addWidget(self._group_target())
        outer.addWidget(self._group_macro())
        outer.addWidget(self._group_cell())
        outer.addWidget(self._group_advanced())
        outer.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(panel)
        scroll.setMinimumWidth(400)
        return scroll

    def _group_target(self) -> QGroupBox:
        group = QGroupBox("대상 폴더")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setSpacing(8)

        self.folder = FolderRow("root", "예: D:\\all폴더")
        form.addRow("폴더", self.folder)

        self.prefix = QLineEdit("26.3Q")
        self.prefix.setToolTip("파일명이 이 문자열로 시작하는 파일만 처리합니다. 비우면 전체.")
        form.addRow("파일명 시작", self.prefix)

        self.pattern = QLineEdit("*.xlsx")
        form.addRow("확장자", self.pattern)

        hint = QLabel("하위 폴더까지 모두 훑습니다 (all폴더 › 개별 폴더 › 파일)")
        hint.setProperty("hint", True)
        hint.setWordWrap(True)
        form.addRow("", hint)
        return group

    def _group_macro(self) -> QGroupBox:
        group = QGroupBox("매크로")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(6)
        self.macro = QComboBox()
        self.macro.setEditable(True)
        self.macro.lineEdit().setPlaceholderText("예: PERSONAL.XLSB!수익_개요")
        self.macro_btn = QPushButton("목록")
        self.macro_btn.setProperty("secondary", True)
        self.macro_btn.setFixedWidth(56)
        self.macro_btn.setToolTip("Excel 을 잠깐 열어 사용 가능한 매크로 이름을 읽어옵니다.")
        self.macro_btn.clicked.connect(self._load_macro_names)
        row.addWidget(self.macro, 1)
        row.addWidget(self.macro_btn)
        wrapper = QWidget()
        wrapper.setLayout(row)
        row.setContentsMargins(0, 0, 0, 0)
        form.addRow("이름", wrapper)

        hint = QLabel(
            "빠른 실행 버튼에 '수익 개요'로 보여도 VBA 이름에는 공백을 쓸 수 없어\n"
            "실제로는 '수익_개요'일 수 있습니다. [목록]으로 확인하세요."
        )
        hint.setProperty("hint", True)
        hint.setWordWrap(True)
        form.addRow("", hint)

        prow = QHBoxLayout()
        prow.setSpacing(6)
        prow.setContentsMargins(0, 0, 0, 0)
        self.personal = QLineEdit()
        self.personal.setPlaceholderText("자동 (XLSTART\\PERSONAL.XLSB)")
        browse = QPushButton("찾기")
        browse.setProperty("secondary", True)
        browse.setFixedWidth(56)
        browse.clicked.connect(self._browse_personal)
        prow.addWidget(self.personal, 1)
        prow.addWidget(browse)
        pwrap = QWidget()
        pwrap.setLayout(prow)
        form.addRow("매크로 파일", pwrap)
        return group

    def _group_cell(self) -> QGroupBox:
        group = QGroupBox("셀")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setSpacing(8)

        self.cell = QLineEdit("B2")
        self.cell.setToolTip("매크로 실행 전에 선택할 셀")
        form.addRow("선택할 셀", self.cell)

        self.value_cell = QLineEdit()
        self.value_cell.setPlaceholderText("비우면 선택할 셀과 동일")
        self.value_cell.setToolTip("InputBox 에 넣을 값을 읽어올 셀")
        form.addRow("값 읽을 셀", self.value_cell)

        self.value_source = QComboBox()
        self.value_source.addItems(["표시값 (앞자리 0 유지)", "원본값"])
        form.addRow("값 기준", self.value_source)

        self.sheet = QLineEdit()
        self.sheet.setPlaceholderText("비우면 열었을 때의 활성 시트")
        form.addRow("시트", self.sheet)
        return group

    def _group_advanced(self) -> QGroupBox:
        group = QGroupBox("고급")
        outer = QVBoxLayout(group)
        outer.setSpacing(8)

        self.advanced_toggle = QCheckBox("고급 옵션 표시")
        self.advanced_toggle.toggled.connect(lambda on: self.advanced_body.setVisible(on))
        outer.addWidget(self.advanced_toggle)

        self.advanced_body = QWidget()
        form = QFormLayout(self.advanced_body)
        form.setContentsMargins(0, 4, 0, 0)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setSpacing(8)

        self.input_method = QComboBox()
        self.input_method.addItems(["기본 (WM_SETTEXT)", "타이핑 (한 글자씩)"])
        self.input_method.setToolTip("값이 입력되지 않으면 타이핑 방식으로 바꿔보세요.")
        form.addRow("입력 방식", self.input_method)

        self.dialog_title = QLineEdit()
        self.dialog_title.setPlaceholderText("비우면 모든 창을 대상으로")
        self.dialog_title.setToolTip("여러 창이 뜰 때 제목 일부로 대상을 좁힙니다.")
        form.addRow("창 제목 필터", self.dialog_title)

        self.appear = QDoubleSpinBox()
        self.appear.setRange(1.0, 600.0)
        self.appear.setValue(30.0)
        self.appear.setSuffix(" 초")
        form.addRow("InputBox 대기", self.appear)

        self.confirm = QDoubleSpinBox()
        self.confirm.setRange(1.0, 120.0)
        self.confirm.setValue(10.0)
        self.confirm.setSuffix(" 초")
        form.addRow("확인 후 대기", self.confirm)

        self.poll = QDoubleSpinBox()
        self.poll.setRange(0.02, 2.0)
        self.poll.setSingleStep(0.05)
        self.poll.setValue(0.12)
        self.poll.setSuffix(" 초")
        form.addRow("창 감시 주기", self.poll)

        self.limit = QSpinBox()
        self.limit.setRange(0, 100000)
        self.limit.setSpecialValueText("전체")
        form.addRow("처리 개수 제한", self.limit)

        self.dismiss = QCheckBox("매크로가 띄우는 후속 안내창 자동 확인")
        self.dismiss.setChecked(True)
        form.addRow("", self.dismiss)

        self.no_personal = QCheckBox("매크로 파일(PERSONAL.XLSB)을 열지 않음")
        form.addRow("", self.no_personal)

        self.keep_open = QCheckBox("작업 후 Excel 을 닫지 않음 (디버깅용)")
        form.addRow("", self.keep_open)

        outer.addWidget(self.advanced_body)
        self.advanced_body.setVisible(False)
        return group

    def _build_right(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # 실행 버튼 줄
        bar = QHBoxLayout()
        bar.setSpacing(8)
        self.scan_btn = QPushButton("파일 찾기")
        self.scan_btn.setProperty("secondary", True)
        self.scan_btn.clicked.connect(self._scan)

        self.dry_btn = QPushButton("값 미리보기")
        self.dry_btn.setProperty("secondary", True)
        self.dry_btn.setToolTip("매크로를 실행하지 않고 각 파일의 셀 값만 읽어봅니다.")
        self.dry_btn.clicked.connect(lambda: self._start("dry"))

        self.probe_btn = QPushButton("창 구조 확인")
        self.probe_btn.setProperty("secondary", True)
        self.probe_btn.setToolTip("첫 파일에서 매크로를 실행해 대화상자 구조만 봅니다. 저장하지 않습니다.")
        self.probe_btn.clicked.connect(lambda: self._start("probe"))

        self.run_btn = QPushButton("실행")
        self.run_btn.setProperty("primary", True)
        self.run_btn.setMinimumWidth(96)
        self.run_btn.clicked.connect(lambda: self._start("run"))

        self.stop_btn = QPushButton("중지")
        self.stop_btn.setProperty("danger", True)
        self.stop_btn.clicked.connect(self._stop)

        bar.addWidget(self.scan_btn)
        bar.addWidget(self.dry_btn)
        bar.addWidget(self.probe_btn)
        bar.addStretch(1)
        bar.addWidget(self.run_btn)
        bar.addWidget(self.stop_btn)
        layout.addLayout(bar)

        self.progress = ProgressPanel()
        layout.addWidget(self.progress)

        # 표 + 콘솔
        inner = QSplitter(Qt.Orientation.Vertical)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        inner.addWidget(self.table)

        self.console = ConsoleView()
        inner.addWidget(self.console)
        inner.setSizes([420, 240])
        layout.addWidget(inner, 1)

        # 하단
        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        self.export_btn = QPushButton("결과 CSV 저장")
        self.export_btn.setProperty("secondary", True)
        self.export_btn.clicked.connect(self._export)
        clear_btn = QPushButton("로그 지우기")
        clear_btn.setProperty("secondary", True)
        clear_btn.clicked.connect(self.console.clear)
        bottom.addWidget(self.export_btn)
        bottom.addWidget(clear_btn)
        bottom.addStretch(1)
        self.summary = QLabel("")
        self.summary.setProperty("hint", True)
        bottom.addWidget(self.summary)
        layout.addLayout(bottom)
        return panel

    # ── 파일 스캔 ────────────────────────────────────
    def _scan(self) -> None:
        root = self._root()
        if root is None:
            return
        self.folder.remember()
        self.scan_btn.setEnabled(False)
        self.statusBar().showMessage("파일을 찾는 중…")

        self.scan_root = root
        worker = ScanWorker(root, self.prefix.text().strip(),
                            self.pattern.text().strip() or "*.xlsx", self.limit.value())
        worker.found.connect(self._on_scanned)
        worker.failed.connect(self._on_scan_failed)
        worker.finished.connect(lambda: self.scan_btn.setEnabled(True))
        self.helper = worker
        worker.start()

    def _on_scanned(self, files: List[Path]) -> None:
        self.files = files
        self._fill_table(files)
        self.statusBar().showMessage(f"대상 파일 {len(files)}개")
        if files:
            self.console.append_message(f"대상 파일 {len(files)}개를 찾았습니다.", "success")
        else:
            self.console.append_message(
                f"조건에 맞는 파일이 없습니다. '파일명 시작'({self.prefix.text().strip()})과 "
                f"확장자를 확인해 보세요.", "warning"
            )

    def _on_scan_failed(self, message: str) -> None:
        self.console.append_message(f"❌ 파일 검색 실패: {message}", "error")
        self.statusBar().showMessage("파일 검색 실패")

    def _fill_table(self, files: List[Path]) -> None:
        # 표를 그리는 중에는 절대 대화상자를 띄우지 않는다 (_root() 를 쓰지 않는 이유)
        root = self.scan_root
        self.table.setRowCount(len(files))
        self.rows.clear()
        for row, path in enumerate(files):
            self.rows[str(path)] = row
            folder = _relative(path.parent, root)
            self.table.setItem(row, 0, QTableWidgetItem(path.name))
            self.table.setItem(row, 1, QTableWidgetItem(folder))
            self._set_status(row, "pending")
            self.table.setItem(row, 3, QTableWidgetItem(""))
            self.table.setItem(row, 4, QTableWidgetItem(""))

    def _set_status(self, row: int, status: str) -> None:
        item = QTableWidgetItem(STATUS_LABELS.get(status, status))
        item.setForeground(QColor(STATUS_COLORS.get(status, "#1d1d1f")))
        self.table.setItem(row, 2, item)

    # ── 매크로 목록 ──────────────────────────────────
    def _load_macro_names(self) -> None:
        self.macro_btn.setEnabled(False)
        self.statusBar().showMessage("매크로 목록을 읽는 중… (Excel 이 잠깐 실행됩니다)")
        self.console.append_message("매크로 목록을 읽는 중…")

        worker = MacroListWorker(self._personal_path())
        worker.listed.connect(self._on_macros)
        worker.failed.connect(lambda m: self.console.append_message(f"❌ {m}", "error"))
        worker.finished.connect(lambda: self.macro_btn.setEnabled(True))
        self.helper = worker
        worker.start()

    def _on_macros(self, names: List[str], warnings: List[str]) -> None:
        for warning in warnings:
            self.console.append_message(f"⚠ {warning}", "warning")
        if not names:
            self.console.append_message(
                "매크로를 찾지 못했습니다. 매크로 파일 경로를 확인하거나 "
                "Alt+F11 에서 직접 이름을 확인하세요.", "warning"
            )
            self.statusBar().showMessage("매크로를 찾지 못했습니다")
            return

        current = self.macro.currentText().strip()
        self.macro.clear()
        self.macro.addItems(names)
        self.macro.setCurrentText(current or names[0])
        self.console.append_message(f"매크로 {len(names)}개를 찾았습니다.", "success")
        self.statusBar().showMessage(f"매크로 {len(names)}개")

    # ── 실행 ─────────────────────────────────────────
    def _start(self, mode: str) -> None:
        root = self._root()
        if root is None:
            return
        if mode != "dry" and not self.macro.currentText().strip():
            QMessageBox.warning(self, "매크로 이름 필요",
                                "실행할 매크로 이름을 입력하세요.\n[목록] 버튼으로 찾을 수 있습니다.")
            return

        self.folder.remember()
        self.scan_root = root

        # 표와 진행률이 항상 실제 처리 대상과 일치하도록 목록을 먼저 확정한다
        files = self.files
        if not files:
            self.console.append_message("파일 목록이 없어 지금 검색합니다…")
            files = bot.collect_files(root, self.prefix.text().strip(),
                                      self.pattern.text().strip() or "*.xlsx")
            if self.limit.value():
                files = files[: self.limit.value()]
            self.files = files
        if not files:
            QMessageBox.information(
                self, "대상 없음",
                f"조건에 맞는 파일이 없습니다.\n\n폴더: {root}\n"
                f"파일명 시작: {self.prefix.text().strip() or '(전체)'}\n"
                f"확장자: {self.pattern.text().strip() or '*.xlsx'}",
            )
            return

        if mode == "probe":
            files = files[:1]

        if mode == "run":
            answer = QMessageBox.question(
                self, "실행 확인",
                f"파일 {len(files)}개를 처리하고 <b>덮어쓰기 저장</b>합니다.<br><br>"
                "· Excel 을 모두 닫으셨나요?<br>"
                "· 폴더를 백업해 두셨나요?<br><br>"
                "계속할까요?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        cfg = self._build_settings(mode)
        self.results = []
        self.summary.setText("")
        self._fill_table(files)
        self.progress.start(len(files))
        self._set_running(True)

        label = {"run": "실행", "dry": "값 미리보기", "probe": "창 구조 확인"}[mode]
        self.console.append_message(f"── {label} 시작 ──")
        if mode == "run":
            self.console.append_message("실행 중에는 Excel 창을 건드리지 마세요.", "warning")

        self.worker = BotWorker(cfg, self._personal_path(), self.keep_open.isChecked(), files)
        self.worker.message.connect(self.console.append_message)
        self.worker.file_started.connect(self._on_file_started)
        self.worker.file_done.connect(self._on_file_done)
        self.worker.completed.connect(self._on_completed)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(lambda: self._set_running(False))
        self.worker.start()

    def _stop(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.stop_btn.setEnabled(False)
            self.console.append_message(
                "중지 요청 — 지금 처리 중인 파일이 끝나면 멈춥니다.", "warning"
            )
            self.statusBar().showMessage("중지 요청됨…")

    def _on_file_started(self, index: int, total: int, path: Path) -> None:
        row = self.rows.get(str(path))
        if row is not None:
            self._set_status(row, "running")
            self.table.scrollToItem(self.table.item(row, 0))
        self.progress.advance(index - 1, total, path.name)

    def _on_file_done(self, index: int, total: int, result: bot.Result) -> None:
        self.results.append(result)
        row = self.rows.get(str(result.path))
        if row is not None:
            self._set_status(row, result.status)
            self.table.setItem(row, 3, QTableWidgetItem(result.value))
            self.table.setItem(row, 4, QTableWidgetItem(result.detail))
        self.progress.advance(index, total, result.path.name)

    def _on_completed(self, results: List[bot.Result]) -> None:
        counts = {"ok": 0, "skipped": 0, "failed": 0}
        for item in results:
            counts[item.status] += 1
        text = f"완료 {counts['ok']} · 건너뜀 {counts['skipped']} · 실패 {counts['failed']}"
        self.summary.setText(text)
        self.progress.finish(text)
        self.statusBar().showMessage(text)
        self.console.append_message(f"── 작업 종료: {text} ──",
                                    "error" if counts["failed"] else "success")
        if counts["failed"]:
            self.console.append_message(
                "실패한 파일은 저장되지 않았습니다. 원인을 고친 뒤 다시 실행하세요.", "warning"
            )

    def _on_failed(self, message: str) -> None:
        self.console.append_message(f"❌ {message}", "error")
        self.progress.reset()
        self.statusBar().showMessage("실행 실패")
        QMessageBox.critical(self, "실행 실패", message)

    def _set_running(self, running: bool) -> None:
        for button in (self.scan_btn, self.dry_btn, self.probe_btn,
                       self.run_btn, self.macro_btn):
            button.setEnabled(not running)
        self.stop_btn.setEnabled(running)

    # ── 설정 조립 ────────────────────────────────────
    def _root(self) -> Optional[Path]:
        text = self.folder.path()
        if not text:
            QMessageBox.warning(self, "폴더 필요", "대상 폴더를 선택하세요.")
            return None
        path = Path(text).expanduser()
        if not path.is_dir():
            QMessageBox.warning(self, "폴더 없음", f"폴더를 찾을 수 없습니다:\n{path}")
            return None
        return path

    def _personal_path(self) -> Optional[Path]:
        if self.no_personal.isChecked():
            return None
        text = self.personal.text().strip()
        return Path(text) if text else bot.default_personal_path()

    def _build_settings(self, mode: str) -> bot.Settings:
        cell = self.cell.text().strip() or "B2"
        dialog = bot.DialogOptions(
            value="",
            title_contains=self.dialog_title.text().strip(),
            poll_interval=self.poll.value(),
            appear_timeout=self.appear.value(),
            confirm_timeout=self.confirm.value(),
            input_method="settext" if self.input_method.currentIndex() == 0 else "chars",
            dismiss_followup=self.dismiss.isChecked(),
            probe=(mode == "probe"),
        )
        return bot.Settings(
            root=self._root(),
            macro=self.macro.currentText().strip(),
            prefix=self.prefix.text().strip(),
            pattern=self.pattern.text().strip() or "*.xlsx",
            target_cell=cell,
            value_cell=self.value_cell.text().strip() or cell,
            value_source="text" if self.value_source.currentIndex() == 0 else "value",
            sheet=self.sheet.text().strip() or None,
            dry_run=(mode == "dry"),
            probe=(mode == "probe"),
            limit=1 if mode == "probe" else self.limit.value(),
            dialog=dialog,
        )

    def _browse_personal(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "매크로 파일 선택", self.personal.text().strip(),
            "Excel 매크로 파일 (*.xlsb *.xlsm *.xlam);;모든 파일 (*.*)",
        )
        if path:
            self.personal.setText(path)

    # ── 결과 저장 ────────────────────────────────────
    def _export(self) -> None:
        if not self.results:
            QMessageBox.information(self, "결과 없음", "저장할 결과가 없습니다.")
            return
        default = f"macro_bot_log_{datetime.now():%Y%m%d_%H%M%S}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "결과 저장", default, "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["파일", "경로", "상태", "입력값", "비고"])
            for item in self.results:
                writer.writerow([item.path.name, str(item.path), item.status,
                                 item.value, item.detail])
        self.console.append_message(f"결과를 저장했습니다: {path}", "success")

    # ── 설정 저장/복원 ───────────────────────────────
    _TEXT_FIELDS = ("prefix", "pattern", "cell", "value_cell", "sheet",
                    "personal", "dialog_title")
    _CHECK_FIELDS = ("dismiss", "no_personal", "keep_open", "advanced_toggle")
    _NUMBER_FIELDS = ("appear", "confirm", "poll", "limit")

    def _load_settings(self) -> None:
        """저장된 값이 있는 항목만 덮어쓴다.

        QSettings.value(key, None, str) 는 키가 없어도 빈 문자열을 돌려주므로
        기본값이 지워진다. 반드시 contains() 로 존재 여부를 먼저 확인할 것.
        """
        store = settings()
        if store.contains("root/last"):
            self.folder.set_path(store.value("root/last", "", str))
        if store.contains("macro"):
            self.macro.setCurrentText(store.value("macro", "", str))

        for name in self._TEXT_FIELDS:
            key = f"field/{name}"
            if store.contains(key):
                getattr(self, name).setText(store.value(key, "", str))
        for name in self._CHECK_FIELDS:
            key = f"check/{name}"
            if store.contains(key):
                getattr(self, name).setChecked(store.value(key, False, bool))
        for name in self._NUMBER_FIELDS:
            key = f"number/{name}"
            if store.contains(key):
                widget = getattr(self, name)
                widget.setValue(type(widget.value())(store.value(key)))
        for name, combo in (("value_source", self.value_source),
                            ("input_method", self.input_method)):
            key = f"combo/{name}"
            if store.contains(key):
                combo.setCurrentIndex(store.value(key, 0, int))

    def _save_settings(self) -> None:
        store = settings()
        store.setValue("root/last", self.folder.path())
        store.setValue("macro", self.macro.currentText().strip())
        for name in self._TEXT_FIELDS:
            store.setValue(f"field/{name}", getattr(self, name).text())
        for name in self._CHECK_FIELDS:
            store.setValue(f"check/{name}", getattr(self, name).isChecked())
        for name in self._NUMBER_FIELDS:
            store.setValue(f"number/{name}", getattr(self, name).value())
        store.setValue("combo/value_source", self.value_source.currentIndex())
        store.setValue("combo/input_method", self.input_method.currentIndex())

    def closeEvent(self, event) -> None:
        if self.worker is not None and self.worker.isRunning():
            answer = QMessageBox.question(
                self, "작업 진행 중",
                "매크로를 실행하는 중입니다. 정말 종료할까요?\n"
                "Excel 이 열린 채로 남을 수 있습니다.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.worker.stop()
            self.worker.wait(3000)
        self._save_settings()
        event.accept()
