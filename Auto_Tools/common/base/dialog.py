"""
BaseDialog - 다이얼로그 베이스 클래스

수정 사항:
- QWidget → QDialog 상속 (중요!)
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox  # ✅ QDialog


class BaseDialog(QDialog):  # ✅ QDialog 상속
    """
    모든 다이얼로그의 베이스 클래스
    
    자동 제공:
    - 제목 설정
    - 모달 설정
    - OK/Cancel 버튼
    - 입력 검증
    
    사용법:
        class MyDialog(BaseDialog):
            def __init__(self, parent=None):
                super().__init__(parent, title="설정")
            
            def setup_content(self):
                # 내용 구성
                self.content_layout.addWidget(...)
            
            def validate(self) -> bool:
                # 검증 (선택)
                return True
    """
    
    def __init__(self, parent=None, title: str = "다이얼로그"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)  # ✅ QDialog에는 setModal 있음
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 내용 영역 (서브클래스에서 채움)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
        
        # 서브클래스에서 구현
        self.setup_content()
        
        # 확인/취소 버튼
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    
    def setup_content(self):
        """
        내용 영역 구성 (필수 구현)
        
        서브클래스에서 self.content_layout에 위젯을 추가합니다.
        
        Example:
            def setup_content(self):
                self.input = QLineEdit()
                self.content_layout.addWidget(QLabel("이름:"))
                self.content_layout.addWidget(self.input)
        """
        raise NotImplementedError("setup_content() 메서드를 구현해야 합니다.")
    
    def validate(self) -> bool:
        """
        입력 검증 (선택적 구현)
        
        확인 버튼 클릭 시 자동 호출됩니다.
        
        Returns:
            유효하면 True, 아니면 False
        
        Example:
            def validate(self) -> bool:
                if not self.input.text():
                    QMessageBox.warning(self, "오류", "값을 입력하세요")
                    return False
                return True
        """
        return True
    
    def accept(self):
        """
        확인 버튼 클릭 시 호출
        
        validate()가 True를 반환하면 다이얼로그가 닫힙니다.
        """
        if self.validate():
            super().accept()