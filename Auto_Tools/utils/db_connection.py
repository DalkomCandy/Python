"""
DB 연결 관리 — MySQL

설정 저장:
  - host / port / user / database : QSettings (Windows 레지스트리)
  - password                      : keyring   (Windows 자격 증명 관리자)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing      import Optional, List, Tuple, Any
import logging

from PyQt6.QtCore import QSettings

logger = logging.getLogger(__name__)

_KEYRING_SERVICE  = "KISP_DB"
_KEYRING_USERNAME = "db_password"   # 고정 키 — DB 사용자명과 무관

_DEFAULTS = {
    "host":     "localhost",
    "port":     3306,
    "user":     "",
    "database": "",
}


def _keyring_get() -> str:
    try:
        import keyring
        return keyring.get_password(_KEYRING_SERVICE, _KEYRING_USERNAME) or ""
    except Exception:
        return ""


def _keyring_set(password: str) -> None:
    try:
        import keyring
        keyring.set_password(_KEYRING_SERVICE, _KEYRING_USERNAME, password)
    except Exception:
        logger.warning("keyring 저장 실패 — 비밀번호가 유지되지 않습니다.")


@dataclass
class DBResult:
    """쿼리 실행 결과"""
    columns:  List[str]   = field(default_factory=list)
    rows:     List[Tuple] = field(default_factory=list)
    affected: int         = 0
    error:    str         = ""
    elapsed:  float       = 0.0

    @property
    def ok(self) -> bool:
        return not self.error

    @property
    def is_select(self) -> bool:
        return bool(self.columns)


class DBConnection:
    """MySQL 연결 래퍼 (설정 영속성 포함)"""

    MAX_ROWS = 1000

    def __init__(self):
        self._conn    = None
        self.host     = _DEFAULTS["host"]
        self.port     = _DEFAULTS["port"]
        self.user     = _DEFAULTS["user"]
        self.password = ""
        self.database = _DEFAULTS["database"]

    # ── 설정 영속성 ──────────────────────────────────

    @staticmethod
    def _settings() -> QSettings:
        return QSettings("KISP", "KISP_Automation_Tool")

    def load(self) -> None:
        """QSettings + keyring에서 연결 설정 로드"""
        s = self._settings()
        self.host     = s.value("db/host",     _DEFAULTS["host"])
        self.port     = int(s.value("db/port", _DEFAULTS["port"]))
        self.user     = s.value("db/user",     _DEFAULTS["user"])
        self.database = s.value("db/database", _DEFAULTS["database"])
        self.password = _keyring_get()

    def save(self) -> None:
        """QSettings + keyring에 연결 설정 저장"""
        s = self._settings()
        s.setValue("db/host",     self.host)
        s.setValue("db/port",     self.port)
        s.setValue("db/user",     self.user)
        s.setValue("db/database", self.database)
        _keyring_set(self.password)

    # ── 연결 관리 ────────────────────────────────────

    @property
    def is_connected(self) -> bool:
        try:
            return self._conn is not None and self._conn.is_connected()
        except Exception:
            return False

    def connect(self) -> str:
        """
        연결 시도.

        Returns:
            성공 시 빈 문자열, 실패 시 오류 메시지.
        """
        try:
            import mysql.connector
        except ImportError:
            return "mysql-connector-python 패키지가 없습니다.\npip install mysql-connector-python"

        try:
            self.disconnect()
            self._conn = mysql.connector.connect(
                host               = self.host,
                port               = int(self.port),
                user               = self.user,
                password           = self.password,
                database           = self.database or None,
                connection_timeout = 5,
                autocommit         = False,
            )
            logger.info("DB 연결 성공: %s@%s:%s/%s",
                        self.user, self.host, self.port, self.database)
            return ""
        except Exception as e:
            logger.error("DB 연결 실패: %s", e)
            self._conn = None
            return str(e)

    def disconnect(self):
        """연결 해제."""
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    # ── 쿼리 실행 ────────────────────────────────────

    def execute(self, sql: str,
                params: Optional[Tuple[Any, ...]] = None) -> DBResult:
        """
        SQL 실행.

        Args:
            sql:    실행할 SQL 문자열
            params: 바인딩 파라미터 (SQL Injection 방지용)
                    예) "SELECT * FROM t WHERE id = %s", (1,)

        Returns:
            DBResult — SELECT면 columns/rows, DML이면 affected
        """
        import time

        if not self.is_connected:
            return DBResult(error="연결되어 있지 않습니다.")

        sql = sql.strip()
        if not sql:
            return DBResult(error="쿼리가 비어 있습니다.")

        t0 = time.time()
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql, params)
            elapsed = time.time() - t0

            if cursor.description:
                columns = [d[0] for d in cursor.description]
                rows    = cursor.fetchmany(self.MAX_ROWS)
                cursor.close()
                return DBResult(columns=columns, rows=list(rows),
                                elapsed=elapsed)
            else:
                self._conn.commit()
                affected = cursor.rowcount
                cursor.close()
                return DBResult(affected=affected, elapsed=elapsed)

        except Exception as e:
            try:
                self._conn.rollback()
            except Exception:
                pass
            logger.error("쿼리 실행 오류: %s", e)
            return DBResult(error=str(e), elapsed=time.time() - t0)
