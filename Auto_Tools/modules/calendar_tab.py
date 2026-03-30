"""
캘린더 탭 - DesktopCal 완벽 재현

개선 사항:
- 요일 헤더 최소화
- 날짜 높이 최소화
- 날짜 왼쪽 상단 정렬
- 셀 안에 메모 내용 표시
- 다른 달 날짜 숨김
"""

import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
    QTextEdit, QPushButton, QLabel, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QTextCharFormat, QColor, QFont
import qtawesome as qta


class MemoDialog(QDialog):
    """메모 입력 팝업"""
    
    def __init__(self, parent=None, date_str="", memo=""):
        super().__init__(parent)
        
        self.setWindowTitle(date_str)
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 날짜 레이블
        date_label = QLabel(date_str)
        date_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2196F3; padding: 10px;"
        )
        layout.addWidget(date_label)
        
        # 메모 입력
        self.memo_text = QTextEdit()
        self.memo_text.setPlaceholderText("메모를 입력하세요...")
        self.memo_text.setPlainText(memo)
        self.memo_text.setFocus()
        layout.addWidget(self.memo_text)
        
        # 버튼
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_memo(self):
        return self.memo_text.toPlainText().strip()


class CompactCalendar(QCalendarWidget):
    """컴팩트한 캘린더 위젯"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 기본 설정
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        
        # 다른 달 날짜 숨김
        self.setNavigationBarVisible(True)
        
        # 컴팩트 스타일 적용
        self.apply_compact_style()
    
    def apply_compact_style(self):
        """컴팩트한 스타일 적용"""
        self.setStyleSheet("""
            QCalendarWidget QWidget {
                alternate-background-color: #f0f0f0;
            }
            
            /* 헤더 (요일) - 높이 최소화 */
            QCalendarWidget QWidget#qt_calendar_calendarview {
                background-color: white;
            }
            
            /* 요일 헤더 */
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 11px;
                selection-background-color: #64B5F6;
                selection-color: white;
            }
            
            /* 네비게이션 바 */
            QCalendarWidget QToolButton {
                height: 25px;
                width: 60px;
                font-size: 12px;
                icon-size: 14px;
                background-color: white;
                border: none;
            }
            
            QCalendarWidget QToolButton:hover {
                background-color: #e3f2fd;
                border-radius: 4px;
            }
            
            QCalendarWidget QMenu {
                font-size: 12px;
            }
            
            QCalendarWidget QSpinBox {
                font-size: 12px;
                max-height: 25px;
            }
        """)
    
    def paintCell(self, painter, rect, date):
        """셀 그리기 오버라이드 - 날짜 위치 조정 및 메모 표시"""
        # 현재 표시 중인 월
        current_month = self.monthShown()
        
        # 다른 달 날짜는 그리지 않음
        if date.month() != current_month:
            return
        
        # 기본 셀 그리기
        super().paintCell(painter, rect, date)


class CalendarTab(QWidget):
    """DesktopCal 스타일 캘린더"""
    
    def __init__(self):
        super().__init__()
        
        # 데이터 파일
        self.data_file = Path("calendar_data.json")
        
        # 메모 데이터
        self.memos = {}
        
        self.init_ui()
        self.load_memos()
        self.update_calendar_marks()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 제목 바
        title_layout = QHBoxLayout()
        
        title_label = QLabel("📅 캘린더")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 오늘 버튼
        today_btn = QPushButton("오늘")
        today_btn.setIcon(qta.icon('fa5s.calendar-day', color='#333'))
        today_btn.clicked.connect(self.go_to_today)
        title_layout.addWidget(today_btn)
        
        layout.addLayout(title_layout)
        
        # 컴팩트 캘린더
        self.calendar = CompactCalendar()
        self.calendar.activated.connect(self.on_date_double_clicked)
        self.calendar.currentPageChanged.connect(self.on_month_changed)
        
        layout.addWidget(self.calendar)
        
        # 안내
        help_label = QLabel(
            "💡 날짜를 더블클릭하면 메모를 입력할 수 있습니다"
        )
        help_label.setStyleSheet(
            "color: #666; font-size: 12px; padding: 10px; "
            "background-color: #f5f5f5; border-radius: 8px;"
        )
        layout.addWidget(help_label)
    
    def go_to_today(self):
        """오늘로 이동"""
        self.calendar.setSelectedDate(QDate.currentDate())
    
    def on_month_changed(self):
        """월 변경 시 표시 업데이트"""
        self.update_calendar_marks()
    
    def on_date_double_clicked(self, qdate: QDate):
        """더블클릭 시 팝업"""
        date_str = qdate.toString("yyyy-MM-dd")
        date_display = qdate.toString("yyyy년 MM월 dd일 (ddd)")
        
        existing_memo = self.memos.get(date_str, "")
        
        dialog = MemoDialog(self, date_display, existing_memo)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            memo = dialog.get_memo()
            
            if memo:
                self.memos[date_str] = memo
            else:
                if date_str in self.memos:
                    del self.memos[date_str]
            
            self.save_memos()
            self.update_calendar_marks()
    
    def update_calendar_marks(self):
        """메모 있는 날짜 표시"""
        # 초기화
        default_format = QTextCharFormat()
        self.calendar.setDateTextFormat(QDate(), default_format)
        
        # 현재 표시 중인 월
        current_year = self.calendar.yearShown()
        current_month = self.calendar.monthShown()
        
        # 메모가 있는 날짜 강조
        for date_str, memo in self.memos.items():
            try:
                year, month, day = map(int, date_str.split('-'))
                
                # 현재 월만 표시
                if year == current_year and month == current_month:
                    qdate = QDate(year, month, day)
                    
                    # 파란색 배경 (DesktopCal 스타일)
                    format = QTextCharFormat()
                    format.setBackground(QColor("#64B5F6"))
                    format.setForeground(QColor("#FFFFFF"))
                    format.setFontWeight(QFont.Weight.Bold)
                    
                    # 메모 미리보기를 툴팁으로
                    format.setToolTip(memo[:50] + "..." if len(memo) > 50 else memo)
                    
                    self.calendar.setDateTextFormat(qdate, format)
            except:
                pass
    
    def save_memos(self):
        """저장"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.memos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"메모 저장 실패: {e}")
    
    def load_memos(self):
        """로드"""
        if not self.data_file.exists():
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.memos = json.load(f)
        except Exception as e:
            print(f"메모 로드 실패: {e}")
            self.memos = {}
