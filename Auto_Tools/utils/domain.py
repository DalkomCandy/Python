"""
KISP 업무 도메인 상수 중앙 관리

eval_validator.py / report_validator.py 에 흩어져 있던
업무 규칙 관련 정규식 / 키워드 / 오프셋 값을 한 곳에서 관리.
업무 규칙이 바뀌면 이 파일만 수정하면 됨.
"""

import re


# ── 파일 확장자 ──────────────────────────────────────────────────────
EXCEL_EXTENSIONS = {".xlsx", ".xlsm", ".xlsb"}
WORD_EXTENSIONS  = {".doc", ".docx"}


# ── 변동 시트 ────────────────────────────────────────────────────────
CHANGE_SHEETS      = {"변동X", "변동O", "변동O(반영O)", "변동 TBU"}
CHANGE_SHEETS_NORM = {re.sub(r'\s+', '', s) for s in CHANGE_SHEETS}  # 공백 무시 비교용


# ── 정규식 ───────────────────────────────────────────────────────────

# 대장 시트명: 대장MMDD (예: 대장0331)
DAEJANG_RE = re.compile(r"^대장(\d{2})(\d{2})$")

# 펀드코드: F로 시작하는 숫자 (예: F12345)
FUND_CODE_RE = re.compile(r"^F\d+$")

# 평가 분기 prefix: YY.NQ 형식 (예: 26.1Q)
PREFIX_RE = re.compile(r"(\d{2}\.\d[Qq])")

# 파일명 내 날짜: YYYY-MM-DD, YYYYMMDD 등 (예: 2026-03-31, 20260331)
DATE_IN_NAME_RE = re.compile(r'(\d{4})[.\-_]?(\d{2})[.\-_]?(\d{2})')

# 보고서 파일명의 괄호 날짜: (YYYY-MM-DD) 형식
DATE_PAREN_RE = re.compile(r'\((\d{4}-\d{2}-\d{2})\)')

# 외화 통화 코드
FX_RE = re.compile(r"USD|EUR|JPY|GBP|CNY", re.IGNORECASE)

# 은행명 추출: [은행명] 패턴 (예: [신한은행])
BANK_NAME_RE = re.compile(r'\[(.*?)\]')

# 숫자만 추출 (콤마, 단위 등 제거용)
NUM_RE = re.compile(r"[^\d]")


# ── 키워드 ───────────────────────────────────────────────────────────
F1_NAME       = "F_1"           # Named Range 이름
KEYWORD_MISUI = "미지급분배금"  # 대장 시트 확인 키워드
COOP_KW       = ("투자조합", "합자회사", "투자합자")  # 투자조합 판별 키워드


# ── 셀 오프셋 (평가 엑셀 템플릿 기준) ───────────────────────────────
F1_OFFSET_ROW  = 3   # F_1 Named Range → 아래 3행 = 펀드코드
F1_OFFSET_COL  = 1   # F_1 Named Range → 오른쪽 1열 = 펀드코드
NAV_OFFSET_ROW = 4   # _nav Named Range → 아래 4행 = 장부기준일
NAV_OFFSET_COL = 1   # _nav Named Range → 오른쪽 1열 = 장부기준일
