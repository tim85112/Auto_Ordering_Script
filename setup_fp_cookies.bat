@echo off
rem 設定代碼頁為UTF-8
chcp 65001 > nul

rem 添加延遲以確保代碼頁更改生效
ping -n 2 127.0.0.1 > nul

echo ===================================================
echo Foodpanda Cookie 初始化設置程式
echo ===================================================
echo.
echo 本程式將幫助您登入所有 Foodpanda 服務並獲取必要的 Cookie。
echo 這是使用 Foodpanda 自動抓取程式之前的必要步驟。
echo.
echo 請選擇要進行設置的服務：
echo.
echo  1) 樂強牛排館 (foodpanda_steak)
echo  2) 喜喜鍋精緻蔬食 (foodpanda_hotpot)
echo  3) 清心 (foodpanda_chinshin)
echo  4) 漢堡王 (foodpanda_bgrking) 
echo  5) 50嵐 (foodpanda_50lan)
echo  6) 八方雲集 (foodpanda_bafun)
echo  7) CoCo都可 (foodpanda_coco)
echo  8) 肯德基 (foodpanda_kfc)
echo  9) 迷客夏 (foodpanda_milkshop)
echo  10) 全部設置 (依次登入所有服務)
echo  0) 退出程式
echo.

set /p choice=請輸入選擇 (0-10): 

if "%choice%"=="0" goto end
if "%choice%"=="1" goto setup_steak
if "%choice%"=="2" goto setup_hotpot
if "%choice%"=="3" goto setup_chinshin
if "%choice%"=="4" goto setup_bgrking
if "%choice%"=="5" goto setup_50lan
if "%choice%"=="6" goto setup_bafun
if "%choice%"=="7" goto setup_coco
if "%choice%"=="8" goto setup_kfc
if "%choice%"=="9" goto setup_milkshop
if "%choice%"=="10" goto setup_all

echo 無效的選擇，請重新運行程式。
goto end

:setup_steak
echo.
echo ===================================================
echo 正在設置樂強牛排館 Cookie...
echo ===================================================
echo.
echo 將啟動登入頁面，請使用您的 Foodpanda 帳號登入。
echo 登入成功後，系統將自動保存 Cookie。
echo.
echo 按任意鍵開始...
pause > nul
python foodpanda_steak.py login
goto end_with_success

:setup_hotpot
echo.
echo ===================================================
echo 正在設置喜喜鍋精緻蔬食 Cookie...
echo ===================================================
echo.
echo 將啟動登入頁面，請使用您的 Foodpanda 帳號登入。
echo 登入成功後，系統將自動保存 Cookie。
echo.
echo 按任意鍵開始...
pause > nul
python foodpanda_hotpot.py login
goto end_with_success

:setup_chinshin
echo.
echo ===================================================
echo 正在設置清心 Cookie...
echo ===================================================
echo.
echo 將啟動登入頁面，請使用您的 Foodpanda 帳號登入。
echo 登入成功後，系統將自動保存 Cookie。
echo.
echo 按任意鍵開始...
pause > nul
python foodpanda_chinshin.py login
goto end_with_success

:setup_bgrking
echo.
echo ===================================================
echo 正在設置漢堡王 Cookie...
echo ===================================================
echo.
echo 將啟動登入頁面，請使用您的 Foodpanda 帳號登入。
echo 登入成功後，系統將自動保存 Cookie。
echo.
echo 按任意鍵開始...
pause > nul
python foodpanda_bgrking.py login
goto end_with_success

:setup_50lan
echo.
echo ===================================================
echo 正在設置50嵐 Cookie...
echo ===================================================
echo.
echo 將啟動登入頁面，請使用您的 Foodpanda 帳號登入。
echo 登入成功後，系統將自動保存 Cookie。
echo.
echo 按任意鍵開始...
pause > nul
python foodpanda_50lan.py login
goto end_with_success

:setup_bafun
echo.
echo ===================================================
echo 正在設置八方雲集 Cookie...
echo ===================================================
echo.
echo 將啟動登入頁面，請使用您的 Foodpanda 帳號登入。
echo 登入成功後，系統將自動保存 Cookie。
echo.
echo 按任意鍵開始...
pause > nul
python foodpanda_bafun.py login
goto end_with_success

:setup_coco
echo.
echo ===================================================
echo 正在設置CoCo都可 Cookie...
echo ===================================================
echo.
echo 將啟動登入頁面，請使用您的 Foodpanda 帳號登入。
echo 登入成功後，系統將自動保存 Cookie。
echo.
echo 按任意鍵開始...
pause > nul
python foodpanda_coco.py login
goto end_with_success

:setup_kfc
echo.
echo ===================================================
echo 正在設置肯德基 Cookie...
echo ===================================================
echo.
echo 將啟動登入頁面，請使用您的 Foodpanda 帳號登入。
echo 登入成功後，系統將自動保存 Cookie。
echo.
echo 按任意鍵開始...
pause > nul
python foodpanda_kfc.py login
goto end_with_success

:setup_milkshop
echo.
echo ===================================================
echo 正在設置迷客夏 Cookie...
echo ===================================================
echo.
echo 將啟動登入頁面，請使用您的 Foodpanda 帳號登入。
echo 登入成功後，系統將自動保存 Cookie。
echo.
echo 按任意鍵開始...
pause > nul
python foodpanda_milkshop.py login
goto end_with_success

:setup_all
echo.
echo ===================================================
echo 依次設置所有服務的 Cookie
echo ===================================================
echo.
echo 您將需要依次登入所有服務，每個服務完成後請關閉窗口繼續下一個。
echo.

echo 1/9: 設置樂強牛排館 Cookie...
echo 按任意鍵開始...
pause > nul
python foodpanda_steak.py login

echo.
echo 2/9: 設置喜喜鍋精緻蔬食 Cookie...
echo 按任意鍵開始...
pause > nul
python foodpanda_hotpot.py login

echo.
echo 3/9: 設置清心 Cookie...
echo 按任意鍵開始...
pause > nul
python foodpanda_chinshin.py login

echo.
echo 4/9: 設置漢堡王 Cookie...
echo 按任意鍵開始...
pause > nul
python foodpanda_bgrking.py login

echo.
echo 5/9: 設置50嵐 Cookie...
echo 按任意鍵開始...
pause > nul
python foodpanda_50lan.py login

echo.
echo 6/9: 設置八方雲集 Cookie...
echo 按任意鍵開始...
pause > nul
python foodpanda_bafun.py login

echo.
echo 7/9: 設置CoCo都可 Cookie...
echo 按任意鍵開始...
pause > nul
python foodpanda_coco.py login

echo.
echo 8/9: 設置肯德基 Cookie...
echo 按任意鍵開始...
pause > nul
python foodpanda_kfc.py login

echo.
echo 9/9: 設置迷客夏 Cookie...
echo 按任意鍵開始...
pause > nul
python foodpanda_milkshop.py login

echo.
echo ===================================================
echo 所有服務的 Cookie 設置已完成！
echo ===================================================
goto end_with_success

:end_with_success
echo.
echo ===================================================
echo Cookie 設置已完成
echo ===================================================
echo.
echo 現在您可以使用 runAll_fp.bat 來同時執行所有抓取程式。
echo.

:end
echo 按任意鍵退出...
pause > nul 