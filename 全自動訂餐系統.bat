@echo off
chcp 65001 > nul
cd /d C:\Users\ivan\AppData\pythonCode
echo 檢查是否已安裝必要的庫...
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo 正在安裝Pillow庫...
    pip install pillow
) else (
    echo Pillow庫已安裝，無需重新安裝
)
echo 啟動訂餐系統...
python food_delivery_tool.py
pause 