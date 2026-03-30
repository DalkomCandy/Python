"""
Windows 시작 프로그램 관리

레지스트리를 사용하여 Windows 시작 시 자동 실행 설정
"""

import winreg
import sys
from pathlib import Path


class StartupManager:
    """
    Windows 시작 프로그램 관리
    
    레지스트리 경로:
        HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
    """
    
    APP_NAME = "KISP_Settings_Manager"
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    @staticmethod
    def get_executable_path():
        """
        실행 파일 경로 가져오기
        
        Returns:
            실행 파일의 전체 경로
        """
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 .exe 파일
            return sys.executable
        else:
            # 개발 모드 (python main.py)
            python_exe = sys.executable
            script_path = Path(__file__).parent.parent.parent / "main.py"
            return f'"{python_exe}" "{script_path}"'
    
    @classmethod
    def is_enabled(cls):
        """
        시작 프로그램 등록 여부 확인
        
        Returns:
            등록되어 있으면 True, 아니면 False
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_READ
            )
            
            try:
                # 값이 존재하는지 확인
                winreg.QueryValueEx(key, cls.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                # 값이 없음
                winreg.CloseKey(key)
                return False
                
        except Exception as e:
            print(f"레지스트리 읽기 오류: {e}")
            return False
    
    @classmethod
    def enable(cls):
        """
        시작 프로그램에 등록
        
        Returns:
            성공 시 True, 실패 시 False
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            
            exe_path = cls.get_executable_path()
            winreg.SetValueEx(
                key,
                cls.APP_NAME,
                0,
                winreg.REG_SZ,
                exe_path
            )
            winreg.CloseKey(key)
            
            print(f"시작 프로그램 등록 완료: {exe_path}")
            return True
            
        except Exception as e:
            print(f"시작 프로그램 등록 실패: {e}")
            return False
    
    @classmethod
    def disable(cls):
        """
        시작 프로그램에서 제거
        
        Returns:
            성공 시 True, 실패 시 False
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, cls.APP_NAME)
                winreg.CloseKey(key)
                print("시작 프로그램 제거 완료")
                return True
            except FileNotFoundError:
                # 이미 등록되어 있지 않음
                winreg.CloseKey(key)
                return True
                
        except Exception as e:
            print(f"시작 프로그램 제거 실패: {e}")
            return False


# ========================================
# 테스트 코드
# ========================================
if __name__ == "__main__":
    print("=== Windows 시작 프로그램 관리 ===")
    print()
    
    # 현재 상태 확인
    is_enabled = StartupManager.is_enabled()
    print(f"현재 상태: {'등록됨' if is_enabled else '등록 안 됨'}")
    print(f"실행 경로: {StartupManager.get_executable_path()}")
    print()
    
    # 테스트 메뉴
    print("1. 시작 프로그램 등록")
    print("2. 시작 프로그램 제거")
    print("3. 종료")
    
    choice = input("\n선택: ")
    
    if choice == "1":
        if StartupManager.enable():
            print("✅ 등록 완료!")
        else:
            print("❌ 등록 실패!")
    
    elif choice == "2":
        if StartupManager.disable():
            print("✅ 제거 완료!")
        else:
            print("❌ 제거 실패!")
    
    print()
    print(f"최종 상태: {'등록됨' if StartupManager.is_enabled() else '등록 안 됨'}")
