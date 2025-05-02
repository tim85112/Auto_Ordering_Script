@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 腳本清單
set scripts[0]=ubereats_50lan.py
set scripts[1]=ubereats_bafun.py
set scripts[2]=ubereats_bgrking.py
set scripts[3]=ubereats_chenzi.py
set scripts[4]=ubereats_chinshin.py
set scripts[5]=ubereats_coco.py
set scripts[6]=ubereats_hotpot.py
set scripts[7]=ubereats_kfc.py
set scripts[8]=ubereats_milkshop.py
set scripts[9]=ubereats_steak.py

set TOTAL=10
set MAX_PARALLEL=4
set SCRIPT_PATH=C:\Users\ivan\AppData\pythonCode
set /a i=0

:loop
if !i! geq %TOTAL% goto done

:: 每次跑 MAX_PARALLEL 支
set /a endIdx=!i!+%MAX_PARALLEL%-1
if !endIdx! geq %TOTAL% set /a endIdx=%TOTAL%-1

for /L %%j in (!i!,1,!endIdx!) do (
    call set "scriptFile=%%scripts[%%j]%%"
    echo 啟動腳本: !scriptFile!
    start "" /min cmd /k "python %SCRIPT_PATH%\!scriptFile! 2> %SCRIPT_PATH%\error_!scriptFile!.log"
)

timeout /t 45 /nobreak >nul
set /a i=!i!+%MAX_PARALLEL%
goto loop

:done
echo ✅ 所有 UberEats 腳本已啟動！
pause
