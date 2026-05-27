"""
앱 전체 색상 중앙 관리

console.py / folders.py / task.py 등에서 제각각 정의된 색상을 통일.
"""


class AppColors:
    # ── 상태 색상 (console, table status 공통) ────────────────
    SUCCESS = "#2e7d32"
    WARNING = "#ff8f00"
    ERROR   = "#c62828"
    INFO    = "#1976d2"

    # ── UI 액션 색상 ─────────────────────────────────────────
    PRIMARY = "#2196F3"
    DANGER  = "#d32f2f"

    # ── 텍스트 색상 ──────────────────────────────────────────
    TEXT_DARK   = "#333333"
    TEXT_MEDIUM = "#555555"
    TEXT_MUTED  = "#888888"
    TEXT_SUBTLE = "#666666"

    # ── 아이콘 색상 (qta 전달용) ─────────────────────────────
    ICON_DEFAULT = "#555555"
    ICON_NEUTRAL = "#333333"
    ICON_PRIMARY = "#2196F3"
    ICON_DANGER  = "#d32f2f"
    ICON_EXCEL   = "#217346"
    ICON_WORD    = "#2B579A"
    ICON_FOLDER  = "#FBC02D"

    # ── console.py 호환 dict ─────────────────────────────────
    CONSOLE: dict = {
        "info":    "#000000",
        "success": SUCCESS,
        "warning": WARNING,
        "error":   ERROR,
    }
