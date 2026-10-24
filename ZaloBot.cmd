@echo off
rem Mo ung dung quan ly Bot Zalo tu ma nguon: luon dung code moi nhat, khong can build exe.
rem Cap nhat code: chuot phai bieu tuong Z o khay -^> Cap nhat (hoac nut tren trang Tong quan).
rem (Chi dung chu ASCII: cmd doc file theo bang ma cu, chu co dau se bi loi.)
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" goto run
echo Lan dau chay: dang tao moi truong Python va cai thu vien, vui long doi vai phut...
python -m venv .venv
if errorlevel 1 goto nopython
".venv\Scripts\python.exe" -m pip install -e ".[desktop,personal]"
if errorlevel 1 goto failed

:run
rem pythonw: khong hien cua so den. Tham so them (vd --tray) duoc chuyen tiep.
start "" ".venv\Scripts\pythonw.exe" -m bot gui %*
exit /b 0

:nopython
echo Khong chay duoc Python. Cai Python 3.11 tro len tu https://www.python.org (tick "Add python.exe to PATH") roi mo lai.
pause
exit /b 1

:failed
echo Cai thu vien that bai. Xem loi o tren.
pause
exit /b 1
