from pathlib import Path
from PyQt6.QtWidgets import QTabWidget, QLineEdit, QWidget, QHBoxLayout, QComboBox, QLabel
from PyQt6.QtCore import Qt

from workers.transfer        import TransferWorker
from workers.eval_validator  import EvalValidatorWorker
from widgets import PathInputWidget, TaskWidget
from widgets.task import _show_message
from utils.messages import Msg


# 라벨 열 너비 — PathInputWidget의 라벨 너비와 동일하게 맞춰 정렬 통일
_LABEL_WIDTH = 80


def _labeled_row(label_text: str, field: QWidget) -> QWidget:
    """[고정폭 라벨][입력 필드] 한 행을 만들어 반환. PathInputWidget과 정렬 일치."""
    row    = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)

    lbl = QLabel(label_text)
    lbl.setProperty("pathLabel", True)
    lbl.setFixedWidth(_LABEL_WIDTH)

    layout.addWidget(lbl)
    layout.addWidget(field, 1)
    return row


class EvaluationManagementTab(QTabWidget):
    def __init__(self):
        super().__init__()
        self.addTab(TransferWorkTab(),    "전기 종목 이전 작업")
        self.addTab(EvalValidatorTab(),   "평가파일 종합 점검")


class TransferWorkTab(TaskWidget):
    """전기 → 당기 종목 이전 UI"""

    def __init__(self):
        super().__init__("")
        self._build_inputs()
        self.execute_btn.clicked.connect(self.start_transfer)

    def _build_inputs(self):
        self.prev_path = PathInputWidget("전기 폴더:", "전기 데이터가 있는 폴더")
        self.next_path = PathInputWidget("당기 폴더:", "당기 데이터를 저장할 폴더")

        self.link_name = QLineEdit()
        self.link_name.setPlaceholderText("바로가기 이름 (선택)")

        self.prev_word = QLineEdit()
        self.prev_word.setPlaceholderText("변경할 문구 (예: 2025)")

        self.next_word = QLineEdit()
        self.next_word.setPlaceholderText("새로운 문구 (예: 2026)")

        self.add_input_widget(self.prev_path)
        self.add_input_widget(self.next_path)
        self.add_input_widget(_labeled_row("바로 가기:", self.link_name))
        self.add_input_widget(_labeled_row("전기 문구:", self.prev_word))
        self.add_input_widget(_labeled_row("당기 문구:", self.next_word))

    def start_transfer(self):
        prev_str = self.prev_path.get_path()
        if not prev_str:
            _show_message(self, "경고", Msg.NO_FOLDER)
            return

        self.start_worker(TransferWorker(
            Path(prev_str),
            Path(self.next_path.get_path()),
            self.link_name.text(),
            self.prev_word.text(),
            self.next_word.text()
        ))


class EvalValidatorTab(TaskWidget):
    """평가파일 종합 점검 UI"""

    def __init__(self):
        super().__init__("")
        self._build_inputs()
        self.execute_btn.clicked.connect(self.run_validation)

    def _build_inputs(self):
        self.base_path = PathInputWidget("상위 폴더:", "종목 폴더들이 있는 상위 경로")
        self.base_path.path_changed.connect(self._refresh_prefixes)

        # 분기 + 가평가 한 행에 배치
        option_widget = QWidget()
        option_layout = QHBoxLayout(option_widget)
        option_layout.setContentsMargins(0, 0, 0, 0)
        option_layout.setSpacing(8)

        lbl1 = QLabel("점검 분기:")
        lbl1.setProperty("pathLabel", True)
        lbl1.setFixedWidth(_LABEL_WIDTH)

        self.prefix_combo = QComboBox()
        self.prefix_combo.setEditable(True)
        self.prefix_combo.setMinimumWidth(120)
        self.prefix_combo.lineEdit().setPlaceholderText("폴더 선택 시 자동 감지")

        lbl2 = QLabel("가평가:")
        lbl2.setProperty("pathLabel", True)

        self.ga_combo = QComboBox()
        self.ga_combo.addItems(["가평가 제외", "가평가 포함"])
        self.ga_combo.setMinimumWidth(120)

        option_layout.addWidget(lbl1)
        option_layout.addWidget(self.prefix_combo)
        option_layout.addSpacing(16)
        option_layout.addWidget(lbl2)
        option_layout.addWidget(self.ga_combo)
        option_layout.addStretch()

        self.add_input_widget(self.base_path)
        self.add_input_widget(option_widget)

    def _refresh_prefixes(self, path_str: str):
        self.prefix_combo.clear()
        p = Path(path_str)
        if not p.is_dir():
            return
        prefixes = EvalValidatorWorker.detect_prefixes(p)
        if prefixes:
            self.prefix_combo.addItems(prefixes)
        else:
            self.prefix_combo.lineEdit().setPlaceholderText("감지된 분기 없음")

    def run_validation(self):
        target = self.validate_folder(self.base_path.get_path())
        if not target:
            return
        prefix = self.prefix_combo.currentText().strip()
        if not prefix:
            _show_message(self, "경고", Msg.PREFIX_EMPTY)
            return
        include_ga = self.ga_combo.currentIndex() == 1
        self.start_worker(
            EvalValidatorWorker(target, prefix, include_ga),
            success_title="점검 완료"
        )


