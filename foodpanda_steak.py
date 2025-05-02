# Selenium 是自動化瀏覽器操作的工具，這行是打開瀏覽器用的
from selenium import webdriver

# By 是定位元素用的方式（像是找按鈕、輸入框、文字...）
from selenium.webdriver.common.by import By

# Service 是幫你啟動 ChromeDriver 的工具
from selenium.webdriver.chrome.service import Service

# WebDriverWait 是等某個元素出現（例如網頁慢慢載入時用）
from selenium.webdriver.support.ui import WebDriverWait

# EC 是 expected_conditions，用來配合 WebDriverWait 判斷「某個元素出現、可點擊」等條件
from selenium.webdriver.support import expected_conditions as EC

# 這個是自動安裝對應版本的 ChromeDriver，不用自己下載
from webdriver_manager.chrome import ChromeDriverManager

# json 是 Python 內建處理 JSON 檔案（如訂單、優惠券）的工具
import json

# time 是讓程式 sleep 用（例如 time.sleep(3) 暫停 3 秒）
import time

# pickle 是 Python 的物件儲存工具，這裡用來保存 Cookie（讓下次不用再登入）
import pickle

# os 是處理檔案、資料夾的工具（像是判斷檔案在不在）
import os

# 這兩個是處理例外錯誤的（例如等不到按鈕時不會當掉）
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# msvcrt 是 Windows 專用的鍵盤偵測工具（例如按 y/n）
import msvcrt

# sys 是用來讀取 command line 參數，例如 python xxx.py login
import sys

# random 是生成隨機數的模塊，用於模擬人工輸入的延遲
import random


# 讀取訂單JSON文件
def read_order_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # 讀取 ubereats_steak.json 的格式，它是一個包含訂單列表的列表，第二個元素是總價
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                orders = data[0]
                print(f"✅ 成功讀取訂單資料: {len(orders)} 個訂單")
                return orders
            else:
                print(f"❌ 訂單文件格式錯誤")
                return None
    except Exception as e:
        print(f"❌ 讀取訂單檔案失敗: {str(e)}")
        return None

# 🚀 設定 WebDriver
options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")  # 註釋掉最大化設置
options.add_argument("--window-size=1024,768")  # 設置較小的視窗大小
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(r'--user-data-dir=C:\Users\ivan\AppData\Local\Google\Chrome2\UserData_foodpanda_steak')

# ✅ 檢查是否需要首次手動登入
print("\n" + "="*60)
print("Foodpanda 自動訂餐程序 - 牛排館")
print("="*60)

# 檢查命令行參數是否有刪除 Cookie 的指示
force_login = False

if len(sys.argv) > 1 and sys.argv[1].lower() == 'login':
    force_login = True
    print("⚠️ 檢測到登入指令，將強制進行手動登入流程")
else:
    print("🔍 正常模式: 將嘗試使用儲存的 Cookie 登入，若失敗將要求手動登入")
    print("   如需強制手動登入，請使用參數執行: python foodpanda_steak.py login")

print("="*60 + "\n")

# 啟動 WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)  # 增加等待時間到30秒

# 讀取訂單資料
order_file_path = "ubereats_steak.json"
orders = read_order_json(order_file_path)

if not orders:
    print("❌ 無法繼續，訂單資料讀取失敗")
    driver.quit()
    exit()

# 從第一個訂單的備註中獲取地址信息
target_address = ""
if orders and len(orders) > 0:
    # 获取第一个订单的备注，在ubereats_steak.json中是第三个元素中的第一个项目
    notes = orders[0][2] if len(orders[0]) > 2 and isinstance(orders[0][2], list) and len(orders[0][2]) > 0 else []
    for note in notes:
        if note.startswith("備註:"):
            target_address = note.replace("備註:", "").strip()
            print(f"✅ 從訂單中獲取到地址信息: {target_address}")
            break

# 📌 Foodpanda 牛排館 URL - 這裡需要改成牛排館的URL
foodpanda_url = "https://www.foodpanda.com.tw/restaurant/agq8/le-qiang-niu-pai-guan"

# ✅ **嘗試載入已儲存的 Cookie**
try:
    driver.get("https://www.foodpanda.com.tw")
    
    # 如果強制登入，拋出異常以跳到手動登入流程
    if force_login:
        raise Exception("已選擇強制手動登入")
    
    # 檢查 Cookie 文件是否存在
    if not os.path.exists("foodpanda_steak_cookies.pkl"):
        print("⚠️ Cookie文件不存在，需要手動登入")
        raise FileNotFoundError("Cookie文件不存在")
        
        with open("foodpanda_steak_cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
            if not cookies or len(cookies) == 0:
                print("⚠️ Cookie文件内容為空，需要手動登入")
                raise ValueError("Cookie內容為空")
            
            print(f"✅ 已讀取 {len(cookies)} 個Cookie")
            
            # 打印部分Cookie信息用於診斷
            for i, cookie in enumerate(cookies[:2]):  # 只顯示前兩個cookie
                cookie_info = {k: v for k, v in cookie.items() if k not in ['value']}
                print(f"Cookie {i+1} 信息: {cookie_info}")
                if 'expiry' in cookie:
                    expiry_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cookie.get('expiry')))
                    print(f"Cookie {i+1} 過期時間: {expiry_time}")
            
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as cookie_err:
                    print(f"⚠️ 添加Cookie時出錯: {str(cookie_err)}")

    driver.get(foodpanda_url)  # 重新打開牛排館頁面
    print("✅ 嘗試使用 Cookie 直接登入")
    
    # 檢查是否成功登入 (檢查頁面上是否有登入後才會出現的元素)
    try:
        # 等待 5 秒檢查是否有登入狀態的元素 (例如購物車或用戶名)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.cart-button"))
        )
        print("✅ 成功使用 Cookie 登入")
    except:
        # 如果沒有找到登入狀態元素，則視為登入失敗，刪除舊 Cookie 並重新登入
        print("⚠️ Cookie 已過期或無效，需要重新登入")
        raise Exception("Cookie 無效")
        
except Exception as e:
    print(f"⚠️ 無法使用 Cookie 登入: {str(e)}")
    
    print("\n" + "="*60)
    print("⚠️ 請手動登入 Foodpanda")
    print("1. 點擊「登入」按鈕")
    print("2. 輸入您的手機號碼/Email和密碼")
    print("3. 若有驗證碼，請完成驗證")
    print("4. 登入成功後，請等待系統自動檢測")
    print("="*60 + "\n")
    
    # 打開登入頁面
    driver.get(foodpanda_url)
    print("⚠️ 請手動登入 Foodpanda，並完成 reCAPTCHA 驗證")
    print("⚠️ 登入後系統將自動檢測，無需手動確認")
    
    # 給用戶足夠的時間登入，自動檢測登入狀態
    login_timeout = 180  # 增加等待時間至180秒，給用戶更多時間登入
    start_time = time.time()
    
    login_detected = False
    while time.time() - start_time < login_timeout:
        # 嘗試多種方式檢測登入狀態
        try:
            # 方法1: 檢查用戶頭像或個人資料元素
            user_profile = driver.find_elements(By.CSS_SELECTOR, 'svg[data-testid="personal-icon"]')
            
            # 方法2: 檢查是否不再顯示登入按鈕
            login_button = driver.find_elements(By.XPATH, "//*[contains(text(), '登入') or contains(text(), 'Login') or contains(text(), 'Sign in')]")
            login_button_not_visible = len(login_button) == 0
            
            # 更嚴格的登入檢測: 確保至少1個條件，避免誤判
            login_conditions_met = 0
          
            if user_profile:
                login_conditions_met += 1
                print("✓ 檢測到用戶個人資料")
            
            # 如果滿足至少兩個條件，才認為已登入
            if login_conditions_met >= 1:
                print("✅ 檢測到已成功登入（滿足 " + str(login_conditions_met) + " 個條件）")
                login_detected = True
                break
            else:
                print(f"⚠️ 未滿足足夠的登入條件（僅滿足 {login_conditions_met}/1 個條件）")
            
            # 打印當前 URL，幫助診斷
            print(f"當前頁面 URL: {driver.current_url}")
            
            # 手動確認選項
            remaining = login_timeout - (time.time() - start_time)
            print(f"⏳ 等待登入中... 剩餘 {int(remaining)} 秒")
            print("如果您已登入但系統未檢測到，請輸入 'y' 確認已登入，或等待倒計時結束")
            
            # 檢查是否有輸入確認
            for i in range(5):  # 分成5次檢查，每次1秒
                if msvcrt.kbhit():  # 檢查是否有按鍵輸入
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key == 'y':
                        print("✅ 已手動確認登入")
                        login_detected = True
                        break
                time.sleep(1)
                
            if login_detected:
                break
                
        except Exception as e:
            # 如果檢測過程出錯，繼續等待
            remaining = login_timeout - (time.time() - start_time)
            print(f"⏳ 等待登入中... 剩餘 {int(remaining)} 秒")
            print(f"檢測登入狀態時出錯: {str(e)}")
            print("如果您已登入但系統未檢測到，請等待倒計時結束，系統將嘗試保存 Cookie")
            time.sleep(5)
    
    # 確保用戶已登入後再保存 Cookie
    if login_detected or msvcrt.kbhit():  # 再次檢查是否有按鍵輸入
        if not login_detected and msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 'y':
                login_detected = True
    
    # 只有在確認登入成功後才保存Cookie
    if login_detected:
        # 嘗試保存 Cookie
        print("\n" + "="*60)
        print("⏳ 登入流程結束，嘗試保存 Cookie...")
        
        # 保存前先訪問主頁，確保獲取完整 Cookie
        current_url = driver.current_url
        driver.get("https://www.foodpanda.com.tw")
        time.sleep(3)  # 等待頁面加載完成
        
        # **存儲登入後的 Cookie**
        cookies = driver.get_cookies()
        if cookies:
            print(f"獲取到 {len(cookies)} 個 Cookie")
            
            try:
                # 在保存前，先檢查每個 cookie 的有效性
                valid_cookies = []
                for cookie in cookies:
                    # 刪除不必要的字段，這些可能導致添加 cookie 時出錯
                    if 'sameSite' in cookie and cookie['sameSite'] == 'None':
                        cookie['sameSite'] = 'Strict'
                    if 'expiry' in cookie and not isinstance(cookie['expiry'], (int, float)):
                        del cookie['expiry']
                    valid_cookies.append(cookie)
                
                # 保存有效的 cookies
                with open("foodpanda_steak_cookies.pkl", "wb") as file:
                    pickle.dump(valid_cookies, file)
                print("✅ Cookie 已保存，下次將嘗試使用此 Cookie 自動登入")
                
                # 打印部分Cookie信息確認
                for i, cookie in enumerate(valid_cookies[:2]):  # 只顯示前兩個cookie
                    cookie_info = {k: v for k, v in cookie.items() if k not in ['value']}
                    print(f"已保存的 Cookie {i+1} 信息: {cookie_info}")
                    if 'expiry' in cookie:
                        expiry_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cookie.get('expiry')))
                        print(f"已保存的 Cookie {i+1} 過期時間: {expiry_time}")
                        
                # 返回原來的 URL
                driver.get(current_url)
                print("="*60 + "\n")
                
            except Exception as save_err:
                print(f"❌ 保存 Cookie 時出錯: {str(save_err)}")
            
            # 如果沒有檢測到登入但用戶確認已登入，重新載入頁面測試 Cookie
            if not login_detected:
                print("⚠️ 系統未檢測到登入狀態，但仍已保存 Cookie")
                print("⚠️ 正在測試保存的 Cookie 是否有效...")
                
                # 重新載入頁面測試 Cookie
                current_url = driver.current_url
                driver.get("https://www.foodpanda.com.tw")
                driver.delete_all_cookies()
                
                # 載入剛保存的 Cookie
                with open("foodpanda_steak_cookies.pkl", "rb") as file:
                    saved_cookies = pickle.load(file)
                    for cookie in saved_cookies:
                        try:
                            driver.add_cookie(cookie)
                        except Exception as add_err:
                            print(f"⚠️ 測試時添加Cookie失敗: {str(add_err)}")
                
                # 重新打開原頁面
                driver.get(current_url)
                print("✅ Cookie 測試完成，繼續執行程序")
        else:
            print("❌ 無法獲取 Cookie，請確保您已成功登入 Foodpanda")
            
            # 查詢 Cookie 為空的原因
            print("\n🔍 診斷 Cookie 為空的可能原因:")
            print("1. 檢查當前是否真的已登入")
            try:
                login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '登入') or contains(text(), 'Login')]")
                if login_elements:
                    print("⚠️ 頁面上仍然顯示登入選項，可能未成功登入")
                else:
                    print("✅ 未檢測到登入選項，可能已登入但無法獲取 Cookie")
                    
                # 截圖幫助診斷
                screenshot_path = "login_state.png"
                driver.save_screenshot(screenshot_path)
                print(f"✅ 已保存當前頁面截圖至 {screenshot_path} 以幫助診斷")
            except Exception as diag_err:
                print(f"❌ 診斷過程出錯: {str(diag_err)}")
    else:
        print("\n" + "="*60)
        print("⚠️ 未檢測到成功登入，不保存 Cookie")
        print("⚠️ 請在下次執行時使用 'login' 參數手動登入")
        print("="*60 + "\n")
        
        # 詢問是否要繼續執行
        print("是否要繼續執行程序？(y/n)")
        continue_execution = False
        
        # 等待用戶輸入
        for i in range(10):  # 等待10秒
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                if key == 'y':
                    continue_execution = True
                    print("✅ 繼續執行程序")
                    break
                elif key == 'n':
                    print("❌ 停止執行程序")
                    driver.quit()
                    exit()
            time.sleep(1)
        
        if not continue_execution:
            print("❌ 未收到確認，停止執行程序")
            driver.quit()
            exit()

# 等待頁面加載完成
try:
    print("⏳ 等待頁面加載完成...")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
    )
    print("✅ 頁面加載完成")
except:
    print("⚠️ 頁面加載超時，嘗試繼續執行")

# 選擇地址
try:
    print("⏳ 嘗試選擇送餐地址...")
    
    # 點擊地址按鈕
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.location-search-button"))
    ).click()
    print("✅ 已點擊地址按鈕")
    
    # 等待地址列表加載
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.saved-address-list-item"))
    )
    print("✅ 地址列表已加載")
    
    # 選擇特定地址 (根據訂單備註)
    address_elements = driver.find_elements(By.CSS_SELECTOR, "div.saved-address-list-item")
    target_address_found = False
    
    if target_address:
        print(f"🔍 正在尋找地址: {target_address}")
        for address in address_elements:
            if target_address in address.text:
                print(f"✅ 找到目標地址: {address.text}")
                address.click()
                target_address_found = True
                print(f"✅ 已選擇地址: {target_address}")
                break
    
    if not target_address_found:
        print(f"⚠️ 未找到目標地址 {target_address}，嘗試選擇第一個可用地址")
        if address_elements:
            address_elements[0].click()
            print(f"✅ 已選擇第一個可用地址: {address_elements[0].text}")
        else:
            print("❌ 沒有可用的地址")
            
    # 等待地址選擇完成，頁面刷新
    time.sleep(3)
    print("✅ 地址選擇完成")
    
except Exception as e:
    print(f"⚠️ 選擇地址時出錯: {str(e)}")
    print("⚠️ 嘗試繼續執行...")

# ✅ **滾動頁面確保所有元素都加載**
print("⏳ 滾動頁面以加載所有元素...")
driver.execute_script("window.scrollTo(0, 300);")
time.sleep(2)
driver.execute_script("window.scrollTo(0, 600);")
time.sleep(2)
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(2)

# 定義展開食物選項的函數
def expand_food_options():
    """
    展開食物選項頁面中的所有選項，點擊所有"View"開頭的按鈕
    """
    return False  # 不再展開食物選項，直接返回False

# 嘗試多種方式定位搜索按鈕
search_button = None

# 使用最精確的XPath直接定位搜索按鈕
print("🔍 嘗試直接定位店內搜索按鈕...")
try:
    # 使用最精確的XPath
    direct_xpath = "//button[@aria-label='店內搜尋' and @data-testid='search-icon']"
    direct_buttons = driver.find_elements(By.XPATH, direct_xpath)
    print(f"使用精確XPath找到 {len(direct_buttons)} 個按鈕")
    
    if direct_buttons:
        for i, btn in enumerate(direct_buttons):
            try:
                if btn.is_displayed() and btn.is_enabled():
                    print(f"按鈕 {i+1} 可見且可用，位置: {btn.location}")
                    search_button = btn
                    print("✅ 成功直接定位到搜索按鈕")
                    break
            except:
                print(f"按鈕 {i+1} 狀態檢查失敗")
except Exception as e:
    print(f"直接定位搜索按鈕失敗: {str(e)}")

# 如果直接定位失敗，嘗試使用CSS選擇器
if not search_button:
    print("⚠️ 直接定位失敗，嘗試使用CSS選擇器...")
    try:
        css_buttons = driver.find_elements(By.CSS_SELECTOR, "button.search-icon-refreshed")
        print(f"使用CSS選擇器找到 {len(css_buttons)} 個按鈕")
        
        if css_buttons:
            for i, btn in enumerate(css_buttons):
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        print(f"按鈕 {i+1} 可見且可用，位置: {btn.location}")
                        search_button = btn
                        print("✅ 成功使用CSS選擇器定位到搜索按鈕")
                        break
                except:
                    print(f"按鈕 {i+1} 狀態檢查失敗")
    except Exception as e:
        print(f"使用CSS選擇器定位搜索按鈕失敗: {str(e)}")

# 如果找到搜索按鈕，嘗試點擊
if search_button:
    try:
        print("⏳ 嘗試滾動到搜索按鈕位置...")
        # 先滾動到頁面頂部
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # 然後滾動到搜索按鈕位置
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
        time.sleep(3)
        
        # 確保按鈕在視圖中並可點擊
        print(f"搜索按鈕當前位置: {search_button.location}")
        print(f"搜索按鈕是否可見: {search_button.is_displayed()}")
        
        print("⏳ 嘗試點擊搜索按鈕...")
        # 使用JavaScript點擊，更可靠
        driver.execute_script("arguments[0].click();", search_button)
        print("✅ JavaScript點擊成功")
        
        time.sleep(5)  # 等待搜索框出現
        
        # 檢查搜索輸入框是否出現
        try:
            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='店內搜尋']")))
            print("✅ 搜索輸入框已出現，可以繼續")
        except:
            print("⚠️ 搜索輸入框未出現，嘗試其他方式")
            # 嘗試直接定位搜索輸入框
            try:
                search_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, '搜尋') or contains(@placeholder, '查詢')]")
                print("✅ 通過其他方式找到搜索輸入框")
            except:
                print("❌ 無法找到搜索輸入框，可能需要手動操作")
                # 保存截圖以便分析
                driver.save_screenshot("search_error.png")
                print("📸 已保存當前頁面截圖到 search_error.png")
    except Exception as e:
        print(f"❌ 點擊搜索按鈕時出錯: {str(e)}")
        driver.save_screenshot("search_error.png")
        print("📸 已保存當前頁面截圖到 search_error.png")
else:
    print("❌ 無法找到搜索按鈕，嘗試直接定位搜索輸入框")
    try:
        # 嘗試直接定位搜索輸入框，有時候頁面已經顯示了搜索框
        search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='店內搜尋']")
        print("✅ 直接找到搜索輸入框，跳過點擊搜索按鈕步驟")
    except:
        print("❌ 無法找到搜索輸入框，保存頁面源碼和截圖以便分析")
        # 保存頁面源碼
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 已保存頁面源碼到 page_source.html")
        
        # 保存截圖
        driver.save_screenshot("search_error.png")
        print("📸 已保存當前頁面截圖到 search_error.png")
        
        # 詢問是否繼續
        continue_script = input("是否要繼續執行腳本？(y/n): ")
        if continue_script.lower() != 'y':
            print("❌ 腳本終止")
            driver.quit()
            exit()

# 循環處理每個訂單
for order in orders:
    try:
        # 根據ubereats_steak.json格式獲取當前訂單信息
        customer = order[0] if len(order) > 0 else "未知顧客"
        menu_item = order[1] if len(order) > 1 else ""
        options = order[2] if len(order) > 2 else []
        quantity_str = order[3] if len(order) > 3 else "1"
        
        # 過濾掉備註選項
        filtered_options = []
        for option in options:
            if not option.startswith("備註:"):
                filtered_options.append(option)
        options = filtered_options
        
        # 處理數量
        try:
            quantity = int(quantity_str)
        except ValueError:
            quantity = 1
            print(f"⚠️ 無法將數量 '{quantity_str}' 轉換為整數，使用默認值 1")
        
        print(f"\n📋 開始處理 {customer} 的訂單: {menu_item} x {quantity}")
        
        # 1. 搜尋餐點
        try:
            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='店內搜尋']")))
            search_input.clear()
            search_input.send_keys(menu_item)
            time.sleep(2)
            print(f"✅ 已搜尋餐點: {menu_item}")
        except Exception as e:
            print(f"❌ 無法找到或使用搜索輸入框: {str(e)}")
            # 嘗試其他方式
            try:
                search_inputs = driver.find_elements(By.XPATH, "//input")
                if search_inputs:
                    print(f"找到 {len(search_inputs)} 個輸入框，嘗試第一個")
                    search_inputs[0].clear()
                    search_inputs[0].send_keys(menu_item)
                    time.sleep(2)
                    print(f"✅ 已使用替代方法搜尋餐點: {menu_item}")
                else:
                    print("❌ 找不到任何輸入框")
                    continue
            except Exception as e2:
                print(f"❌ 替代搜索方法也失敗: {str(e2)}")
                continue
        
        # 等待搜索結果
        time.sleep(5)
        
        # 2. 點擊搜尋結果中的第一個餐點
        try:
            menu_button = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-testid='menu-product-button-overlay-id']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", menu_button)
            print(f"✅ 成功點擊餐點: {menu_item}")
            time.sleep(3)  # 等待彈窗加載
        except Exception as e:
            print(f"❌ 無法點擊餐點 {menu_item}: {str(e)}")
            # 嘗試其他方式
            try:
                # 嘗試通過餐點名稱定位
                menu_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{menu_item}')]")
                if menu_elements:
                    for element in menu_elements:
                        try:
                            # 嘗試找到可點擊的父元素
                            parent = element
                            for _ in range(5):  # 最多向上查找5層
                                parent = parent.find_element(By.XPATH, "..")
                                if parent.tag_name == 'button' or parent.tag_name == 'a':
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent)
                                    time.sleep(1)
                                    driver.execute_script("arguments[0].click();", parent)
                                    print(f"✅ 通過替代方法點擊餐點: {menu_item}")
                                    time.sleep(3)
                                    break
                        except:
                            continue
                else:
                    print(f"❌ 找不到包含 '{menu_item}' 的元素")
                    continue
            except Exception as e2:
                print(f"❌ 替代點擊方法也失敗: {str(e2)}")
                continue
        
        # 3. 選擇食物細項（根據ubereats_steak.json的格式）
        for option in options:
            # 解析選項類型和值
            option_value = option
            
            # 檢查是否有冒號分隔的選項類型和值
            if ":" in option:
                option_parts = option.split(":", 1)
                option_type = option_parts[0].strip()
                option_value = option_parts[1].strip()
                
                # 跳過備註選項
                if option_type.lower() == "備註":
                    continue
                
                print(f"⏳ 處理選項: {option_type} - {option_value}")
            else:
                print(f"⏳ 處理選項: {option_value}")
            
            try:
                # 尋找選項文本
                option_label = wait.until(EC.presence_of_element_located(
                    (By.XPATH, f"//span[contains(@class, 'item-modifier-option-name') and contains(text(), '{option_value}')]")))
                
                # 嘗試找到並點擊包含該選項的父元素（通常是label或div）
                parent_label = option_label.find_element(By.XPATH, "./ancestor::label")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent_label)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", parent_label)
                print(f"✅ 已選擇選項: {option_value}")
                time.sleep(1)
            except Exception as e:
                # 如果使用標準方法無法找到，嘗試更通用的方法
                try:
                    # 通過更廣泛的選擇器查找
                    xpath_option = f"//*[contains(text(), '{option_value}')]"
                    option_elements = driver.find_elements(By.XPATH, xpath_option)
                    
                    if option_elements:
                        # 找到第一個可見的元素
                        for elem in option_elements:
                            try:
                                if elem.is_displayed():
                                    # 嘗試找到可點擊的父元素
                                    clickable_parent = elem
                                    for _ in range(4):  # 最多向上查找4層
                                        try:
                                            clickable_parent = clickable_parent.find_element(By.XPATH, "..")
                                            if clickable_parent.tag_name in ['button', 'label', 'div'] and clickable_parent.is_displayed():
                                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_parent)
                                                time.sleep(1)
                                                driver.execute_script("arguments[0].click();", clickable_parent)
                                                print(f"✅ 已通過父元素選擇選項: {option_value}")
                                                break
                                        except:
                                            continue
                                    break
                            except:
                                continue
                    else:
                        print(f"⚠️ 無法找到選項: {option_value}")
                except Exception as e2:
                    print(f"⚠️ 選擇選項時出錯: {str(e2)}")
        
        # 4. 選擇數量
        if quantity > 1:
            try:
                for i in range(quantity - 1):  # 默認已有1個，所以減1
                    add_btn = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'counter__button--increase')]")))
                    driver.execute_script("arguments[0].click();", add_btn)
                    time.sleep(0.5)
                print(f"✅ 已設置數量: {quantity}")
            except Exception as e:
                print(f"⚠️ 無法設置數量: {str(e)}")
        
        # 5. 點擊放入購物車
        try:
            print("⏳ 嘗試點擊「放入購物車」按鈕...")
            
            # 使用JavaScript直接查找並點擊"放入購物車"按鈕
            add_to_cart_clicked = driver.execute_script("""
                // 按鈕可能在彈出窗口中，先處理這種情況
                function clickButtonInModal() {
                    // 查找模態框中的放入購物車按鈕
                    var modalButtons = document.querySelectorAll('.modal button, [role="dialog"] button');
                    for (var i = 0; i < modalButtons.length; i++) {
                        if (modalButtons[i].textContent.includes('放入購物車')) {
                            console.log('找到模態框中的放入購物車按鈕');
                            modalButtons[i].scrollIntoView({block: 'center'});
                            modalButtons[i].click();
                            return true;
                        }
                    }
                    return false;
                }
                
                // 直接搜索包含"放入購物車"文字的按鈕
                function searchByText() {
                    // 特別處理從截圖看到的格式
                    var addToCartBtns = document.querySelectorAll('button.cl-button');
                    console.log('找到 ' + addToCartBtns.length + ' 個可能的加入購物車按鈕');
                    
                    for (var i = 0; i < addToCartBtns.length; i++) {
                        if (addToCartBtns[i].textContent.includes('放入購物車')) {
                            console.log('找到放入購物車按鈕: ' + addToCartBtns[i].textContent);
                            addToCartBtns[i].scrollIntoView({block: 'center'});
                            setTimeout(function() {
                                addToCartBtns[i].click();
                            }, 500);
                            return true;
                        }
                    }
                    
                    // 如果上面的方法失敗，嘗試更通用的方法
                    var allButtons = document.querySelectorAll('button');
                    for (var j = 0; j < allButtons.length; j++) {
                        if (allButtons[j].textContent.includes('放入購物車')) {
                            console.log('找到放入購物車按鈕: ' + allButtons[j].textContent);
                            allButtons[j].scrollIntoView({block: 'center'});
                            setTimeout(function() {
                                allButtons[j].click();
                            }, 500);
                            return true;
                        }
                    }
                    
                    return false;
                }
                
                // 嘗試使用精確XPath
                function tryXPath() {
                    var xpathResult = document.evaluate(
                        "//button[.//span[contains(text(), '放入購物車')]]",
                        document,
                        null,
                        XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                        null
                    );
                    
                    if (xpathResult.snapshotLength > 0) {
                        var button = xpathResult.snapshotItem(0);
                        console.log('通過XPath找到放入購物車按鈕');
                        button.scrollIntoView({block: 'center'});
                        setTimeout(function() {
                            button.click();
                        }, 500);
                        return true;
                    }
                    
                    return false;
                }
                
                // 嘗試所有方法
                return clickButtonInModal() || searchByText() || tryXPath();
            """)
            
            if add_to_cart_clicked:
                print(f"✅ 已加入購物車: {menu_item} x {quantity}")
                time.sleep(3)
            else:
                print(f"❌ 無法使用JavaScript點擊'放入購物車'按鈕")
                
                # 嘗試原始方法作為備份
                print("⏳ 嘗試使用原始方法點擊'放入購物車'按鈕...")
                
                # 保存截圖以檢查彈窗內容
                driver.save_screenshot("before_click_cart.png")
                print("📸 已保存點擊前的截圖到 before_click_cart.png")
                
                # 嘗試多種定位方式
                try:
                    # 方法1: 通過按鈕文本
                    add_to_cart = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., '放入購物車')]")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", add_to_cart)
                    print(f"✅ 已使用XPath文本方法加入購物車: {menu_item} x {quantity}")
                except Exception as e1:
                    print(f"❌ XPath文本方法失敗: {str(e1)}")
                    try:
                        # 方法2: 通過按鈕類和span文本
                        add_to_cart = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(@class, 'bds-c-btn') and .//span[contains(text(), '放入購物車')]]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", add_to_cart)
                        print(f"✅ 已使用類+span方法加入購物車: {menu_item} x {quantity}")
                    except Exception as e2:
                        print(f"❌ 類+span方法失敗: {str(e2)}")
                        try:
                            # 方法3: 通過CSS選擇器
                            add_to_cart = wait.until(EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, "button.cl-button")))
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_to_cart)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", add_to_cart)
                            print(f"✅ 已使用CSS選擇器方法加入購物車: {menu_item} x {quantity}")
                        except Exception as e3:
                            print(f"❌ 所有方法均失敗，無法加入購物車: {str(e3)}")
                            driver.save_screenshot(f"add_to_cart_error_{menu_item}.png")
                            print(f"📸 已保存當前頁面截圖到 add_to_cart_error_{menu_item}.png")
        except Exception as e:
            print(f"❌ 無法加入購物車: {str(e)}")
            # 保存截圖以便分析
            driver.save_screenshot(f"add_to_cart_error_{menu_item}.png")
            print(f"📸 已保存當前頁面截圖到 add_to_cart_error_{menu_item}.png")
    
    except Exception as order_error:
        print(f"❌ 處理訂單時發生錯誤: {str(order_error)}")

print("\n✅ 所有訂單處理完成！請檢查購物車並手動結帳")

# 1. 點擊餐具選項 (使用ID選擇器，更可靠)
try:
    print("\n⏳ 嘗試點擊餐具選項...")
    # 等待購物車頁面加載完成
    time.sleep(5)
    
    # 使用JavaScript通過ID直接定位並點擊餐具開關
    cutlery_clicked = driver.execute_script("""
        var cutlerySwitch = document.getElementById('cutlery-switch');
        if (cutlerySwitch) {
            console.log('找到餐具開關元素');
            cutlerySwitch.click();
            return true;
        } else {
            console.log('未找到餐具開關元素');
            return false;
        }
    """)
    
    if cutlery_clicked:
        print("✅ 成功點擊餐具選項")
    else:
        print("⚠️ 未找到餐具開關元素，嘗試其他方法...")
        
        # 嘗試使用XPath定位
        try:
            cutlery_switch = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@id='cutlery-switch' or @data-testid='cart-cutlery-component']")))
            driver.execute_script("arguments[0].click();", cutlery_switch)
            print("✅ 使用XPath成功點擊餐具選項")
        except Exception as e:
            print(f"⚠️ 使用XPath定位餐具開關失敗: {str(e)}")
            
            # 最後嘗試使用更通用的選擇器
            try:
                cutlery_elements = driver.find_elements(By.XPATH, 
                    "//input[@type='checkbox' and (@role='switch' or contains(@class, 'switch'))]")
                if cutlery_elements:
                    driver.execute_script("arguments[0].click();", cutlery_elements[0])
                    print("✅ 使用通用選擇器成功點擊餐具選項")
                else:
                    print("❌ 無法找到餐具開關元素")
                    driver.save_screenshot("cutlery_switch_error.png")
            except Exception as e2:
                print(f"❌ 所有方法都無法點擊餐具開關: {str(e2)}")
                driver.save_screenshot("cutlery_switch_error.png")
    
    time.sleep(2)  # 等待切換狀態更新
except Exception as e:
    print(f"❌ 點擊餐具選項時出錯: {str(e)}")
    driver.save_screenshot("cutlery_switch_error.png")

# 2. 點擊"查看付款方式及地址"按鈕
try:
    print("\n⏳ 嘗試點擊「查看付款方式及地址」按鈕...")
    
    # 使用JavaScript通過文本內容定位並點擊按鈕
    checkout_clicked = driver.execute_script("""
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.includes('查看付款方式及地址')) {
                console.log('找到查看付款方式及地址按鈕');
                buttons[i].scrollIntoView({block: 'center'});
                buttons[i].click();
                return true;
            }
        }
        console.log('未找到查看付款方式及地址按鈕');
        return false;
    """)
    
    if checkout_clicked:
        print("✅ 成功點擊「查看付款方式及地址」按鈕")
        
        # 等待預約訂單確認彈窗出現
        time.sleep(1)
        
        # 處理預約訂單確認彈窗
        print("⏳ 檢查是否有預約訂單確認彈窗...")
        confirm_reservation_clicked = driver.execute_script("""
            // 查找預約訂單確認彈窗中的"繼續"按鈕
            var confirmButton = document.querySelector('button[data-testid="dialogue-confirm-cta"]');
            if (confirmButton) {
                console.log('找到預約訂單確認彈窗中的繼續按鈕');
                confirmButton.scrollIntoView({block: 'center'});
                setTimeout(function() {
                    confirmButton.click();
                }, 300);
                return {success: true, message: '已點擊預約訂單確認彈窗中的繼續按鈕'};
            }
            
            // 備用方法：查找包含"繼續"文字的按鈕
            var allButtons = document.querySelectorAll('button');
            for (var i = 0; i < allButtons.length; i++) {
                if (allButtons[i].textContent.includes('繼續')) {
                    console.log('找到包含繼續文字的按鈕');
                    allButtons[i].scrollIntoView({block: 'center'});
                    setTimeout(function() {
                        allButtons[i].click();
                    }, 300);
                    return {success: true, message: '已點擊包含繼續文字的按鈕'};
                }
            }
            
            // 如果沒有確認彈窗，返回false
            return {success: false, message: '未找到預約訂單確認彈窗'};
        """)
        
        if confirm_reservation_clicked and confirm_reservation_clicked.get('success', False):
            print(f"✅ {confirm_reservation_clicked.get('message', '已處理預約訂單確認')}")
        else:
            print(f"ℹ️ {confirm_reservation_clicked.get('message', '沒有預約訂單確認彈窗需要處理')}")
    else:
        print("⚠️ 未找到「查看付款方式及地址」按鈕，嘗試其他方法...")
        
        # 嘗試使用data-testid定位
        try:
            checkout_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='cart-summary-checkout-button']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkout_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", checkout_button)
            print("✅ 使用data-testid成功點擊「查看付款方式及地址」按鈕")
            
            # 等待預約訂單確認彈窗出現
            time.sleep(1)
            
            # 處理預約訂單確認彈窗
            print("⏳ 檢查是否有預約訂單確認彈窗...")
            confirm_reservation_clicked = driver.execute_script("""
                // 查找預約訂單確認彈窗中的"繼續"按鈕
                var confirmButton = document.querySelector('button[data-testid="dialogue-confirm-cta"]');
                if (confirmButton) {
                    console.log('找到預約訂單確認彈窗中的繼續按鈕');
                    confirmButton.scrollIntoView({block: 'center'});
                    setTimeout(function() {
                        confirmButton.click();
                    }, 300);
                    return {success: true, message: '已點擊預約訂單確認彈窗中的繼續按鈕'};
                }
                
                // 備用方法：查找包含"繼續"文字的按鈕
                var allButtons = document.querySelectorAll('button');
                for (var i = 0; i < allButtons.length; i++) {
                    if (allButtons[i].textContent.includes('繼續')) {
                        console.log('找到包含繼續文字的按鈕');
                        allButtons[i].scrollIntoView({block: 'center'});
                        setTimeout(function() {
                            allButtons[i].click();
                        }, 300);
                        return {success: true, message: '已點擊包含繼續文字的按鈕'};
                    }
                }
                
                // 如果沒有確認彈窗，返回false
                return {success: false, message: '未找到預約訂單確認彈窗'};
            """)
            
            if confirm_reservation_clicked and confirm_reservation_clicked.get('success', False):
                print(f"✅ {confirm_reservation_clicked.get('message', '已處理預約訂單確認')}")
            else:
                print(f"ℹ️ {confirm_reservation_clicked.get('message', '沒有預約訂單確認彈窗需要處理')}")
        except Exception as e:
            print(f"⚠️ 使用data-testid定位按鈕失敗: {str(e)}")
            
            # 最後嘗試使用XPath通過文本內容定位
            try:
                checkout_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., '查看付款方式及地址') or contains(., '結帳') or contains(., '付款')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkout_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", checkout_button)
                print("✅ 使用XPath成功點擊「查看付款方式及地址」按鈕")
                
                # 等待預約訂單確認彈窗出現
                time.sleep(1)
                
                # 處理預約訂單確認彈窗
                print("⏳ 檢查是否有預約訂單確認彈窗...")
                confirm_reservation_clicked = driver.execute_script("""
                    // 查找預約訂單確認彈窗中的"繼續"按鈕
                    var confirmButton = document.querySelector('button[data-testid="dialogue-confirm-cta"]');
                    if (confirmButton) {
                        console.log('找到預約訂單確認彈窗中的繼續按鈕');
                        confirmButton.scrollIntoView({block: 'center'});
                        setTimeout(function() {
                            confirmButton.click();
                        }, 300);
                        return {success: true, message: '已點擊預約訂單確認彈窗中的繼續按鈕'};
                    }
                    
                    // 備用方法：查找包含"繼續"文字的按鈕
                    var allButtons = document.querySelectorAll('button');
                    for (var i = 0; i < allButtons.length; i++) {
                        if (allButtons[i].textContent.includes('繼續')) {
                            console.log('找到包含繼續文字的按鈕');
                            allButtons[i].scrollIntoView({block: 'center'});
                            setTimeout(function() {
                                allButtons[i].click();
                            }, 300);
                            return {success: true, message: '已點擊包含繼續文字的按鈕'};
                        }
                    }
                    
                    // 如果沒有確認彈窗，返回false
                    return {success: false, message: '未找到預約訂單確認彈窗'};
                """)
            except Exception as e3:
                print(f"❌ 使用XPath定位按鈕失敗: {str(e3)}")
                driver.save_screenshot("checkout_button_error.png")
    time.sleep(5)  # 等待頁面跳轉
except Exception as e:
    print(f"❌ 點擊「查看付款方式及地址」按鈕時出錯: {str(e)}")
    driver.save_screenshot("checkout_button_error.png")

print("\n✅ 已完成餐具選項設置並進入付款頁面")

# 等待付款頁面加載完成
time.sleep(5)

# 選擇預約送餐時間
try:
    print("\n⏳ 嘗試設定預約送餐時間...")
    
    # 1. 選擇預約訂單選項
    scheduled_delivery_clicked = driver.execute_script("""
        // 查找並點擊預約訂單選項
        var scheduledDeliveryOption = document.querySelector('input#scheduled-delivery');
        if (scheduledDeliveryOption) {
            console.log('找到預約訂單選項');
            scheduledDeliveryOption.click();
            return true;
        } else {
            // 備用方法：通過文字內容查找
            var labels = document.querySelectorAll('label');
            for (var i = 0; i < labels.length; i++) {
                if (labels[i].textContent.includes('預約訂單')) {
                    console.log('通過文字內容找到預約訂單選項');
                    labels[i].click();
                    return true;
                }
            }
            return false;
        }
    """)
    
    if scheduled_delivery_clicked:
        print("✅ 已選擇預約訂單選項")
        time.sleep(2)
        
        # 等待時間選擇彈窗顯示
        print("⏳ 等待時間選擇彈窗顯示...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".timepicker-time-selector")))
        print("✅ 時間選擇彈窗已顯示")
        
        # 2. 滾動時間列表找到 15:00-15:15 並選擇
        time_selected = driver.execute_script("""
            // 滾動時間列表並尋找 15:00-15:15 時間段
            var timeList = document.querySelector('.timepicker-time-selector');
            if (!timeList) return {success: false, message: '找不到時間列表'};
            
            // 先滾動到列表底部以確保所有時間選項都加載
            timeList.scrollTop = timeList.scrollHeight;
            
            // 等待滾動完成
            setTimeout(function() {
                // 查找包含 15:00 – 15:15 的時間選項
                var allTimeSlots = document.querySelectorAll('.timepicker-time-selector__item');
                var targetSlot = null;
                
                for (var i = 0; i < allTimeSlots.length; i++) {
                    if (allTimeSlots[i].textContent.includes('15:00 – 15:15')) {
                        targetSlot = allTimeSlots[i];
                        break;
                    }
                }
                
                if (targetSlot) {
                    // 確保目標時間槽可見
                    targetSlot.scrollIntoView({block: 'center', behavior: 'smooth'});
                    
                    // 點擊時間選項
                    setTimeout(function() {
                        targetSlot.click();
                    }, 500);
                }
            }, 1000);
            
            return {success: true, message: '已嘗試選擇 15:00-15:15 時間段'};
        """)
        
        if time_selected and time_selected.get('success', False):
            print(f"✅ {time_selected.get('message', '已選擇時間')}")
            time.sleep(2)
            
            # 3. 點擊確認按鈕
            confirm_clicked = driver.execute_script(""" 
                // 查找並點擊確認按鈕
                var confirmButton = document.querySelector('.bds-c-modal__footer button');
                if (confirmButton) {
                    console.log('找到確認按鈕');
                    confirmButton.click();
                    return true;
                }
                return false;
            """)
            
            if confirm_clicked:
                print("✅ 已點擊確認按鈕，成功設定預約送餐時間為 15:00-15:15")
                time.sleep(2)
            else:
                print("❌ 找不到確認按鈕")
                driver.save_screenshot("time_confirmation_error.png")
        else:
            print(f"❌ {time_selected.get('message', '選擇時間失敗')}")
            driver.save_screenshot("time_selection_error.png")
    else:
        print("❌ 找不到預約訂單選項")
        driver.save_screenshot("scheduled_delivery_error.png")
        
except Exception as e:
    print(f"❌ 設定預約送餐時間時出錯: {str(e)}")
    driver.save_screenshot("delivery_time_error.png")

# 等待用戶確認
input("按 Enter 鍵結束...")

# 結束 WebDriver
driver.quit()
