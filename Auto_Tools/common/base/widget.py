"""
기본 위젯 모듈

BaseWidget: 모든 커스텀 위젯의 베이스 클래스
"""

from PyQt6.QtWidgets import QWidget


class BaseWidget(QWidget):
    """
    모든 위젯의 베이스 클래스
    
    기본적인 초기화 패턴을 제공합니다.
    서브클래스는 init_ui() 메서드를 구현해야 합니다.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        pass