"""
qtawesome 아이콘 중앙 관리

각 파일에 하드코딩된 icon 이름/색상을 한 곳에서 관리.
변경 시 이 파일만 수정하면 됨.
"""

import qtawesome as qta
from .colors import AppColors


class Icons:
    # ── 사이드바 ─────────────────────────────────────────────
    @staticmethod
    def sidebar(icon_name: str):
        """main_window 사이드바용 — 아이콘 이름을 동적으로 받음"""
        return qta.icon(icon_name, color=AppColors.ICON_DEFAULT)

    @staticmethod
    def evaluation(): return qta.icon('fa5s.chart-line',  color=AppColors.ICON_DEFAULT)
    @staticmethod
    def reports():    return qta.icon('fa5s.file-alt',    color=AppColors.ICON_DEFAULT)
    @staticmethod
    def folder_nav(): return qta.icon('fa5s.folder',      color=AppColors.ICON_DEFAULT)
    @staticmethod
    def query():      return qta.icon('fa5s.sticky-note', color=AppColors.ICON_DEFAULT)
    @staticmethod
    def settings():   return qta.icon('fa5s.cog',         color=AppColors.ICON_DEFAULT)

    # ── 액션 버튼 ────────────────────────────────────────────
    @staticmethod
    def play():    return qta.icon('fa5s.play',        color='white')
    @staticmethod
    def check():   return qta.icon('fa5s.check',       color='white')
    @staticmethod
    def close():   return qta.icon('fa5s.times',       color='white')
    @staticmethod
    def save():    return qta.icon('fa5s.save',        color=AppColors.ICON_NEUTRAL)
    @staticmethod
    def plus():    return qta.icon('fa5s.plus',        color=AppColors.ICON_NEUTRAL)
    @staticmethod
    def minus():   return qta.icon('fa5s.minus',       color=AppColors.ICON_NEUTRAL)
    @staticmethod
    def refresh(): return qta.icon('fa5s.sync-alt',    color=AppColors.ICON_NEUTRAL)
    @staticmethod
    def search():  return qta.icon('fa5s.search',      color=AppColors.ICON_NEUTRAL)
    @staticmethod
    def preview(): return qta.icon('fa5s.eye',         color=AppColors.ICON_NEUTRAL)
    @staticmethod
    def trash():   return qta.icon('fa5s.trash',       color=AppColors.ICON_DANGER)
    @staticmethod
    def layer():   return qta.icon('fa5s.layer-group', color=AppColors.ICON_DEFAULT)
    @staticmethod
    def list_icon(): return qta.icon('fa5s.list',      color=AppColors.ICON_DEFAULT)

    # ── 파일/폴더 ─────────────────────────────────────────────
    @staticmethod
    def folder_open():  return qta.icon('fa5s.folder-open', color=AppColors.ICON_DEFAULT)
    @staticmethod
    def folder_color(): return qta.icon('fa5s.folder',      color=AppColors.ICON_FOLDER)
    @staticmethod
    def excel():        return qta.icon('fa5s.file-excel',  color=AppColors.ICON_EXCEL)
    @staticmethod
    def word():         return qta.icon('fa5s.file-word',   color=AppColors.ICON_WORD)

    # ── 클립보드 ─────────────────────────────────────────────
    @staticmethod
    def copy():  return qta.icon('fa5s.copy',  color=AppColors.ICON_NEUTRAL)
    @staticmethod
    def paste(): return qta.icon('fa5s.paste', color=AppColors.ICON_NEUTRAL)

    # ── 시스템 ───────────────────────────────────────────────
    @staticmethod
    def power():  return qta.icon('fa5s.power-off', color=AppColors.ICON_PRIMARY)
    @staticmethod
    def minimize(): return qta.icon('fa5s.window-minimize', color=AppColors.ICON_PRIMARY)

    # ── IconWidget 전용 (settings 등에서 인라인 위젯으로 사용) ─
    @staticmethod
    def power_widget():   return qta.IconWidget('fa5s.power-off',       color=AppColors.ICON_PRIMARY)
    @staticmethod
    def minimize_widget(): return qta.IconWidget('fa5s.window-minimize', color=AppColors.ICON_PRIMARY)
