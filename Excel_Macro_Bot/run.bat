@echo off
chcp 65001 > nul
cd /d "%~dp0"

REM ─────────────────────────────────────────────
REM  아래 두 줄만 본인 환경에 맞게 수정하세요.
REM  매크로 이름은 먼저 `python excel_macro_bot.py --list-macros` 로 확인하세요.
REM ─────────────────────────────────────────────
set ROOT=D:\all폴더
set MACRO=PERSONAL.XLSB!수익_개요

echo.
echo   대상 폴더 : %ROOT%
echo   매크로    : %MACRO%
echo.
echo   실행 전에 Excel 을 모두 닫아주세요.
echo.
pause

REM 처음에는 --dry-run 으로 대상 파일과 입력값을 먼저 확인하세요.
REM python excel_macro_bot.py --root "%ROOT%" --dry-run

REM 그 다음 --limit 1 로 파일 하나만 테스트하세요.
REM python excel_macro_bot.py --root "%ROOT%" --macro "%MACRO%" --limit 1

python excel_macro_bot.py --root "%ROOT%" --macro "%MACRO%"

echo.
pause
