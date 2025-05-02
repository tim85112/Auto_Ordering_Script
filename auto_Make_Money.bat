@echo off
setlocal enabledelayedexpansion

:: Step 1: 執行 UberEats 訂單擷取
echo ✅ 執行 UberEats 資料擷取中...
call runAll_uber.bat

:: Step 2: 定義所有腳本與 JSON 對應名稱
set scriptList=hotpot steak bafun bgrking chinshin coco 50lan kfc milkshop
set count=0

:: Step 3: 逐一檢查對應的 JSON 是否存在
for %%i in (%scriptList%) do (
    set jsonFile=ubereats_%%i.json
    if exist "!jsonFile!" (
        echo 🔍 偵測到 JSON 檔: !jsonFile!
        echo 🚀 執行對應的程式: foodpanda_%%i.py
        start "" python foodpanda_%%i.py
        set /a count+=1
    ) else (
        echo ⛔ 找不到 JSON 檔: !jsonFile!，跳過 foodpanda_%%i.py
    )

    :: 每執行1個就暫停 60 秒，避免一次開太多瀏覽器
    if !count! EQU 1 (
        echo ⏸️ 執行1個程式，暫停 60 秒...
        timeout /t 60
        set count=0
    )
)

echo ✅ 所有處理程序已結束。
pause
