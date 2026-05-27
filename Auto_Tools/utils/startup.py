import winreg
import sys
from pathlib import Path


class StartupManager:
    """Windows 시작 프로그램 레지스트리 관리"""

    APP_NAME = "KISP_Automation_Tool"
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @staticmethod
    def get_executable_path() -> str:
        if getattr(sys, 'frozen', False):
            return sys.executable
        script = Path(__file__).parent.parent / "main.py"
        return f'"{sys.executable}" "{script}"'

    @classmethod
    def is_enabled(cls) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, cls.APP_NAME)
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)
        except Exception:
            return False

    @classmethod
    def enable(cls) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_SET_VALUE)
            try:
                winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, cls.get_executable_path())
            finally:
                winreg.CloseKey(key)
            return True
        except Exception:
            return False

    @classmethod
    def disable(cls) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, cls.APP_NAME)
            except FileNotFoundError:
                pass
            finally:
                winreg.CloseKey(key)
            return True
        except Exception:
            return False
