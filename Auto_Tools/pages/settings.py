"""
설정 탭

구성:
  - DB 연결 설정 (host/port/user/password/database)
  - 앱 로그 뷰어
  - 프로그램 정보
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QPlainTextEdit, QLineEdit,
    QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QFont

from config            import AppConfig
from utils.icons       import Icons
from utils.db_connection import DBConnection


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._db_conn = DBConnection()
        self._build_ui()
        self._load_db_settings()
        self._load_log()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ── DB 연결 설정 ─────────────────────────────────
        db_group  = QGroupBox("DB 연결 설정 (MySQL)")
        db_layout = QFormLayout()
        db_layout.setSpacing(8)
        db_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.f_host = QLineEdit(); self.f_host.setPlaceholderText("localhost")
        self.f_port = QLineEdit(); self.f_port.setPlaceholderText("3306"); self.f_port.setMaximumWidth(80)
        self.f_user = QLineEdit(); self.f_user.setPlaceholderText("root")
        self.f_pass = QLineEdit(); self.f_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.f_db   = QLineEdit(); self.f_db.setPlaceholderText("database명")

        db_layout.addRow("Host:",     self.f_host)
        db_layout.addRow("Port:",     self.f_port)
        db_layout.addRow("User:",     self.f_user)
        db_layout.addRow("Password:", self.f_pass)
        db_layout.addRow("Database:", self.f_db)

        save_row = QHBoxLayout()
        save_row.addStretch()
        self.btn_db_save = QPushButton("저장")
        self.btn_db_save.setIcon(Icons.check())
        self.btn_db_save.setProperty("primaryButton", True)
        self.btn_db_save.clicked.connect(self._save_db_settings)
        save_row.addWidget(self.btn_db_save)

        db_vbox = QVBoxLayout()
        db_vbox.addLayout(db_layout)
        db_vbox.addLayout(save_row)
        db_group.setLayout(db_vbox)
        layout.addWidget(db_group)

        # ── 앱 로그 뷰어 ─────────────────────────────────
        log_group  = QGroupBox("앱 로그")
        log_layout = QVBoxLayout()

        self.log_viewer = QPlainTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setMinimumHeight(240)
        font = QFont("Consolas")
        if not font.exactMatch():
            font = QFont("Courier New")
        font.setPointSize(9)
        self.log_viewer.setFont(font)
        log_layout.addWidget(self.log_viewer)

        btn_row = QHBoxLayout()
        refresh_btn = QPushButton("새로고침")
        refresh_btn.setIcon(Icons.refresh())
        refresh_btn.clicked.connect(self._load_log)

        clear_btn = QPushButton("로그 지우기")
        clear_btn.setIcon(Icons.trash())
        clear_btn.setProperty("dangerButton", True)
        clear_btn.clicked.connect(self._clear_log)

        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        log_layout.addLayout(btn_row)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group, 1)

        # ── 프로그램 정보 ─────────────────────────────────
        about    = QGroupBox("프로그램 정보")
        a_layout = QVBoxLayout()
        lbl = QLabel(
            f"<b>{AppConfig.WINDOW_TITLE}</b><br>"
            "버전: 1.0.0<br>"
            "업무 자동화 및 보고서 관리 도구"
        )
        lbl.setProperty("aboutLabel", True)
        a_layout.addWidget(lbl)
        about.setLayout(a_layout)
        layout.addWidget(about)

    # ── DB 설정 ──────────────────────────────────────

    def _load_db_settings(self):
        self._db_conn.load()
        self.f_host.setText(self._db_conn.host)
        self.f_port.setText(str(self._db_conn.port))
        self.f_user.setText(self._db_conn.user)
        self.f_pass.setText(self._db_conn.password)
        self.f_db.setText(self._db_conn.database)

    def _save_db_settings(self):
        try:
            port = int(self.f_port.text().strip() or 3306)
        except ValueError:
            port = 3306
        self._db_conn.host     = self.f_host.text().strip()
        self._db_conn.port     = port
        self._db_conn.user     = self.f_user.text().strip()
        self._db_conn.password = self.f_pass.text()
        self._db_conn.database = self.f_db.text().strip()
        self._db_conn.save()
        QMessageBox.information(self, "저장 완료", "DB 연결 설정이 저장되었습니다.")

    # ── 로그 뷰어 ────────────────────────────────────

    def _load_log(self):
        log_path = AppConfig.BASE_DIR / "app.log"
        if not log_path.exists():
            self.log_viewer.setPlainText("로그 파일이 없습니다.")
            return
        try:
            lines  = log_path.read_text(encoding='utf-8', errors='replace').splitlines()
            recent = "\n".join(lines[-500:])
            self.log_viewer.setPlainText(recent)
            sb = self.log_viewer.verticalScrollBar()
            sb.setValue(sb.maximum())
        except Exception as e:
            self.log_viewer.setPlainText(f"로그 읽기 실패: {e}")

    def _clear_log(self):
        log_path = AppConfig.BASE_DIR / "app.log"
        try:
            log_path.write_text("", encoding='utf-8')
            self.log_viewer.clear()
        except Exception as e:
            self.log_viewer.setPlainText(f"로그 초기화 실패: {e}")

