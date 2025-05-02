# 🔹 0️⃣ **版本資訊**
VERSION = "1.0.2"
LAST_UPDATED = "2024-07-16"
print("\n" + "=" * 50)
print(f"UberEats 訂單抓取程式 (樂強牛排館) v{VERSION} (更新日期: {LAST_UPDATED})")
print("=" * 50)

# 🔹 1️⃣ **導入必要的 Python 套件**
import time  # 設定延遲，讓頁面有時間載入
import json  # 儲存結果為 JSON
import pickle  # 用於保存 cookie
import os  # 處理檔案和目錄
import sys  # 獲取命令列參數
import msvcrt  # 用於偵測鍵盤輸入
import psutil  # 用於處理進程
import subprocess  # 用於執行系統命令
import re  # 正規表達式（Regular Expression），用於提取文字資訊

# 導入 Selenium 相關套件
from selenium import webdriver  # Selenium：自動化網頁操作
from selenium.webdriver.common.by import By  # By：用於指定 HTML 元素
from selenium.webdriver.chrome.service import Service  # 控制 ChromeDriver 服務
from selenium.webdriver.support.ui import WebDriverWait  # 等待元素加載
from selenium.webdriver.support import expected_conditions as EC  # 設定元素等待條件
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 🔹 0️⃣ **版本檢查和進程清理**
def kill_chrome_processes():
    """結束所有 Chrome 相關進程"""
    # 檢查命令列參數是否有不強制關閉Chrome的指示
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'nokill':
        print("🔄 跳過清理 Chrome 進程...")
        return
        
    print("🔄 檢查並清理 Chrome 進程...")
    for proc in psutil.process_iter(['name']):
        try:
            if 'chrome' in proc.info['name'].lower():
                proc.kill()
                print(f"✅ 已終止進程: {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def check_chrome_version():
    """檢查 Chrome 版本"""
    try:
        # Windows 系統檢查 Chrome 版本
        cmd = 'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version'
        result = subprocess.check_output(cmd, shell=True).decode()
        version = result.strip().split()[-1]
        print(f"✅ Chrome 版本: {version}")
        return version
    except:
        print("⚠️ 無法獲取 Chrome 版本")
        return None

def download_matching_chromedriver(chrome_version=None):
    """下載匹配的 ChromeDriver"""
    import requests
    import zipfile
    import io
    import re
    import platform
    
    print("🔄 正在檢查並下載匹配的 ChromeDriver...")
    
    # 如果未提供 Chrome 版本，嘗試獲取
    if not chrome_version:
        chrome_version = check_chrome_version()
    
    if not chrome_version:
        print("❌ 無法確定 Chrome 版本，使用 ChromeDriverManager 自動下載")
        from webdriver_manager.chrome import ChromeDriverManager
        return ChromeDriverManager().install()
    
    # 獲取主要版本號
    major_version = chrome_version.split('.')[0]
    
    # 確定系統類型和 ChromeDriver 下載 URL
    if platform.system() == 'Windows':
        os_type = 'win32'
        driver_filename = 'chromedriver.exe'
    elif platform.system() == 'Darwin':
        os_type = 'mac-x64' if platform.machine() != 'arm64' else 'mac-arm64'
        driver_filename = 'chromedriver'
    else:
        os_type = 'linux64'
        driver_filename = 'chromedriver'
    
    # 設置下載目錄
    download_dir = os.path.join(os.getcwd(), 'chromedriver-downloads')
    os.makedirs(download_dir, exist_ok=True)
    
    # 檢查是否已有匹配版本
    driver_folder = os.path.join(download_dir, f'chromedriver-{major_version}')
    driver_path = os.path.join(driver_folder, driver_filename)
    if os.path.exists(driver_path):
        print(f"✅ 已有匹配的 ChromeDriver {major_version} 版本")
        return driver_path
    
    try:
        # 從 Chrome for Testing 獲取可用版本
        versions_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(versions_url)
        versions_data = response.json()
        
        # 查找匹配的主要版本
        matching_versions = []
        for version_info in versions_data['versions']:
            version = version_info['version']
            if version.startswith(f"{major_version}."):
                # 檢查是否有 chromedriver 下載
                has_driver = False
                for download in version_info.get('downloads', {}).get('chromedriver', []):
                    if download.get('platform') == os_type:
                        has_driver = True
                        break
                if has_driver:
                    matching_versions.append(version)
        
        if not matching_versions:
            print(f"⚠️ 找不到匹配 Chrome {major_version} 的 ChromeDriver，使用自動下載")
            from webdriver_manager.chrome import ChromeDriverManager
            return ChromeDriverManager().install()
        
        # 使用最新的匹配版本
        target_version = matching_versions[-1]
        print(f"✅ 找到匹配的 ChromeDriver 版本: {target_version}")
        
        # 獲取下載 URL
        download_url = None
        for version_info in versions_data['versions']:
            if version_info['version'] == target_version:
                for download in version_info.get('downloads', {}).get('chromedriver', []):
                    if download.get('platform') == os_type:
                        download_url = download.get('url')
                        break
                break
        
        if not download_url:
            print("❌ 無法獲取下載 URL，使用自動下載")
            from webdriver_manager.chrome import ChromeDriverManager
            return ChromeDriverManager().install()
        
        print(f"📥 正在從 {download_url} 下載 ChromeDriver...")
        
        # 下載並解壓 ChromeDriver
        response = requests.get(download_url)
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            # 創建目標目錄
            os.makedirs(driver_folder, exist_ok=True)
            
            # 獲取 zip 內容列表
            file_list = zip_file.namelist()
            print(f"ZIP 文件內容: {file_list[:5]}...")
            
            # 查找 chromedriver 文件
            chromedriver_file = None
            for file in file_list:
                if file.endswith(driver_filename):
                    chromedriver_file = file
                    break
            
            if not chromedriver_file:
                print(f"❌ 在ZIP文件中找不到 {driver_filename}，使用備用方法")
                # 嘗試備用方法：使用 webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                return ChromeDriverManager().install()
            
            print(f"✅ 在ZIP文件中找到 {chromedriver_file}")
            
            # 解壓 chromedriver 文件
            with open(driver_path, 'wb') as f:
                f.write(zip_file.read(chromedriver_file))
            
            # 設置執行權限
            os.chmod(driver_path, 0o755)
            
            print(f"✅ 成功解壓 ChromeDriver 到: {driver_path}")
            return driver_path
    
    except Exception as e:
        print(f"❌ 下載 ChromeDriver 時出錯: {e}")
        print("使用自動下載作為後備")
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            return ChromeDriverManager().install()
        except Exception as e2:
            print(f"❌ 自動下載也失敗: {e2}")
            print("嘗試使用備用方法...")
            try:
                import subprocess
                result = subprocess.run(
                    ["pip", "install", "webdriver-manager"],
                    capture_output=True,
                    text=True
                )
                print(f"安裝 webdriver-manager: {result.stdout}")
                from webdriver_manager.chrome import ChromeDriverManager
                return ChromeDriverManager().install()
            except Exception as e3:
                print(f"❌ 所有嘗試都失敗: {e3}")
                sys.exit(1)

# 檢查並終止現有Chrome進程
kill_chrome_processes()

# 檢查 Chrome 版本
chrome_version = check_chrome_version()

# 下載匹配的 ChromeDriver
chromedriver_path = download_matching_chromedriver(chrome_version)
print(f"🔧 使用 ChromeDriver 路徑: {chromedriver_path}")

# 檢查命令列參數是否有強制登入的指示
force_login = False
if len(sys.argv) > 1 and sys.argv[1].lower() == 'login':
    force_login = True
    print("⚠️ 檢測到登入指令，將強制進行手動登入流程")
    if os.path.exists("ubereats_steak_cookies.pkl"):
        try:
            # os.remove("ubereats_steak_cookies.pkl")
            # print("✅ 已刪除現有的 Cookie 文件")
            print("⚠️ Cookie 無效，但已保留 Cookie 文件")
        except Exception as del_err:
            print(f"⚠️ 刪除 Cookie 文件失敗: {str(del_err)}")
else:
    print("🔍 正常模式: 將嘗試使用儲存的 Cookie 登入，若失敗將要求手動登入")
    print("   如需強制手動登入，請使用參數執行: python ubereats_steak.py login")

print("=" * 60 + "\n")

# 🔹 2️⃣ **設定 Selenium 的 Chrome WebDriver**
options = webdriver.ChromeOptions()  # 設定 Chrome 瀏覽器的選項
# 注释掉最大化
# options.add_argument("--start-maximized")
# 使用固定窗口大小
options.add_argument("--window-size=1024,768")
options.add_argument("--disable-blink-features=AutomationControlled")  # 避免被偵測為自動化
options.add_argument("--no-sandbox")  # 讓 WebDriver 可以在沒有 GUI（無頭模式）下執行
options.add_argument("--disable-dev-shm-usage")  # 避免資源不足的問題
options.add_argument("--no-first-run")  # 避免首次運行提示
options.add_argument("--no-default-browser-check")  # 避免預設瀏覽器檢查
options.add_argument("--disable-gpu")  # 禁用 GPU 加速
options.add_argument("--disable-extensions")  # 禁用擴展
options.add_argument("--disable-infobars")  # 禁用通知欄
options.add_argument("--disable-notifications")  # 禁用通知
options.add_argument("--disable-popup-blocking")  # 禁用彈窗阻擋

# ✅ **不使用使用者資料目錄，改用 Cookie**
options.add_argument(r'--user-data-dir=C:\Users\ivan\AppData\Local\Google\Chrome\UserData_ubereats_steak')
# options.add_argument(r'--profile-directory=Default')

try:
    # 使用下載的 ChromeDriver
    service = Service(executable_path=chromedriver_path)
    # 創建 WebDriver 實例
    
    print("🔄 正在啟動 Chrome...")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    print("✅ Chrome 啟動成功！")
    print(f"🌐 Chrome 版本: {driver.capabilities.get('browserVersion', '未知')}")
    print(f"🔧 ChromeDriver 版本: {driver.capabilities.get('chrome').get('chromedriverVersion', '未知').split(' ')[0]}")
except Exception as e:
    print(f"❌ Chrome 啟動失敗: {e}")
    print("\n詳細錯誤信息:")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)

# 🔹 3️⃣ **嘗試使用 Cookie 登入 Uber Eats**
try:
    # 先訪問 UberEats 主頁
    ubereats_home_url = "https://www.ubereats.com/tw"
    print(f"\n🌍 正在訪問 Uber Eats 首頁: {ubereats_home_url}")
    driver.get(ubereats_home_url)
    print("✅ 成功進入 Uber Eats 首頁！")
    
    # 如果強制登入，拋出例外以跳到手動登入流程
    if force_login:
        raise Exception("已選擇強制手動登入")
    
    # 檢查 Cookie 文件是否存在
    if not os.path.exists("ubereats_steak_cookies.pkl"):
        print("⚠️ Cookie 文件不存在，需要手動登入")
        raise FileNotFoundError("Cookie 文件不存在")
    
    try:
        # 載入保存的 Cookie
        with open("ubereats_steak_cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
            
        if not cookies or len(cookies) == 0:
            print("⚠️ Cookie 文件內容為空，需要手動登入")
            raise ValueError("Cookie 內容為空")
        
        print(f"✅ 已讀取 {len(cookies)} 個 Cookie")
        
        # 顯示部分 Cookie 資訊用於診斷
        for i, cookie in enumerate(cookies[:2]):  # 只顯示前兩個 cookie
            cookie_info = {k: v for k, v in cookie.items() if k not in ['value']}
            print(f"Cookie {i+1} 信息: {cookie_info}")
            if 'expiry' in cookie:
                expiry_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cookie.get('expiry')))
                print(f"Cookie {i+1} 過期時間: {expiry_time}")
        
        # 添加所有 Cookie 到當前 session
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as cookie_err:
                print(f"⚠️ 添加 Cookie 時出錯: {str(cookie_err)}")
        
        # 重新整理頁面以套用 Cookie
        print("🔄 重新整理頁面以套用 Cookie...")
        driver.refresh()
        time.sleep(3)
        
        # 檢查是否成功登入
        try:
            # 等待 5 秒檢查是否有登入狀態的元素 (例如購物車或用戶名)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='購物車']"))
            )
            print("✅ 成功使用 Cookie 登入")
        except:
            print("⚠️ Cookie 已過期或無效，需要重新登入")
            raise Exception("Cookie 無效")
            
    except Exception as cookie_err:
        print(f"⚠️ Cookie 載入失敗: {str(cookie_err)}")
        raise Exception("需要手動登入")
        
except Exception as e:
    print(f"⚠️ 無法使用 Cookie 登入: {str(e)}")
    
    # 刪除舊的 Cookie 文件(如果存在且不是強制登入)
    if os.path.exists("ubereats_steak_cookies.pkl") and not force_login:
        try:
            # os.remove("ubereats_steak_cookies.pkl")
            # print("✅ 已刪除失效的 Cookie 文件")
            print("⚠️ Cookie 無效，但已保留 Cookie 文件")
        except Exception as del_err:
            print(f"⚠️ 刪除 Cookie 文件失敗: {str(del_err)}")
    
    print("\n" + "="*60)
    print("⚠️ 請手動登入 Uber Eats")
    print("1. 點擊右上角的「登入」按鈕")
    print("2. 輸入您的手機號碼/Email和密碼")
    print("3. 若有驗證碼，請完成驗證")
    print("4. 登入成功後，請等待系統自動檢測")
    print("="*60 + "\n")
    
    # 打開登入頁面
    driver.get("https://www.ubereats.com/tw")
    print("⚠️ 請手動登入 Uber Eats，完成所有驗證")
    print("⚠️ 登入後系統將自動檢測，無需手動確認")
    
    # 給用戶足夠的時間登入，自動檢測登入狀態
    login_timeout = 180  # 設置 3 分鐘時間讓用戶登入
    start_time = time.time()
    
    login_detected = False
    while time.time() - start_time < login_timeout:
        try:
            # 檢查是否有購物車按鈕 (登入狀態的標誌)
            cart_button = driver.find_elements(By.CSS_SELECTOR, "button[data-test-id='view-carts-btn'], button[aria-label*='購物車']")
            if cart_button:
                print("✅ 檢測到已成功登入")
                login_detected = True
                break
            
            # 顯示等待信息
            remaining = login_timeout - (time.time() - start_time)
            print(f"⏳ 等待登入中... 剩餘 {int(remaining)} 秒")
            print("如果您已登入但系統未檢測到，請輸入 'y' 確認已登入，或等待倒計時結束")
            
            # 檢查是否有鍵盤輸入
            for i in range(5):  # 每 5 秒檢查一次
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    if key == 'y':
                        print("✅ 已手動確認登入")
                        login_detected = True
                        break
                time.sleep(1)
                
            if login_detected:
                break
                
        except Exception as e:
            remaining = login_timeout - (time.time() - start_time)
            print(f"⏳ 等待登入中... 剩餘 {int(remaining)} 秒")
            print(f"檢測登入狀態時出錯: {str(e)}")
            time.sleep(5)
    
    # 檢查是否登入成功
    if login_detected or (msvcrt.kbhit() and msvcrt.getch().decode('utf-8').lower() == 'y'):
        # 保存 Cookie 供下次使用
        print("\n" + "="*60)
        print("⏳ 登入流程結束，嘗試保存 Cookie...")
        
        # 保存前先訪問主頁，確保獲取完整 Cookie
        current_url = driver.current_url
        driver.get("https://www.ubereats.com/tw")
        time.sleep(3)
        
        # 獲取並儲存登入後的 Cookie
        cookies = driver.get_cookies()
        if cookies:
            print(f"獲取到 {len(cookies)} 個 Cookie")
            
            try:
                # 檢查每個 cookie 的有效性
                valid_cookies = []
                for cookie in cookies:
                    # 處理可能導致問題的字段
                    if 'sameSite' in cookie and cookie['sameSite'] == 'None':
                        cookie['sameSite'] = 'Strict'
                    if 'expiry' in cookie and not isinstance(cookie['expiry'], (int, float)):
                        del cookie['expiry']
                    valid_cookies.append(cookie)
                
                # 保存有效的 cookies
                with open("ubereats_steak_cookies.pkl", "wb") as file:
                    pickle.dump(valid_cookies, file)
                print("✅ Cookie 已保存，下次將嘗試使用此 Cookie 自動登入")
                
                # 顯示部分 Cookie 資訊確認
                for i, cookie in enumerate(valid_cookies[:2]):
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
        else:
            print("❌ 無法獲取 Cookie，請確保您已成功登入 Uber Eats")
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

# 🔹 4️⃣ **進入訂單頁面**
try:
    print("\n🔄 正在訪問 Uber Eats 訂單頁面...")
    driver.get("https://www.ubereats.com/tw/orders")
    print("✅ 成功進入訂單頁面")
    time.sleep(5)  # 等待頁面加載
except Exception as e:
    print(f"❌ 無法訪問 Uber Eats 訂單頁面，錯誤：{e}")
    driver.quit()
    sys.exit(1)

# 🔹 5️⃣ **點擊購物車按鈕**
try:
    # 使用 aria-label 屬性定位購物車按鈕
    cart_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-id='view-carts-btn']")))
    cart_button.click()
    print("✅ 成功點擊購物車按鈕！")

except Exception as e:
    print(f"❌ 找不到購物車按鈕，錯誤：{e}")
    # 嘗試使用 JavaScript 點擊
    try:
        driver.execute_script("document.querySelector(\"button[aria-label='購物車']\").click();")
        print("✅ 使用 JavaScript 成功點擊購物車按鈕！")
    except Exception as js_error:
        print(f"❌ JavaScript 點擊失敗，錯誤：{js_error}")
        driver.quit()
        exit()

# 等待購物車選單載入
time.sleep(3)

# 🔹 6️⃣ **點擊樂強牛排館**
try:
    # 使用 data-testid 屬性定位樂強牛排館餐廳選項
    steak_restaurant = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li[data-testid='menu-item-樂強牛排館']")))
    steak_restaurant.click()
    print("✅ 成功點擊『樂強牛排館』！")
except Exception as e:
    print(f"❌ 找不到『樂強牛排館』，錯誤：{e}")
    # 嘗試使用 XPath 替代方法
    try:
        steak_xpath = "//div[contains(text(), '樂強牛排館')]"
        steak_element = wait.until(EC.element_to_be_clickable((By.XPATH, steak_xpath)))
        steak_element.click()
        print("✅ 使用 XPath 成功點擊『樂強牛排館』！")
    except Exception as xpath_error:
        print(f"❌ XPath 點擊失敗，錯誤：{xpath_error}")
        # 最後嘗試 JavaScript 點擊
        try:
            js_script = """
            var elements = document.querySelectorAll('li[role="menuitem"]');
            for (var i = 0; i < elements.length; i++) {
                if (elements[i].textContent.includes('樂強牛排館')) {
                    elements[i].click();
                    return true;
                }
            }
            return false;
            """
            result = driver.execute_script(js_script)
            if result:
                print("✅ 使用 JavaScript 成功點擊『樂強牛排館』！")
            else:
                print("❌ 無法找到『樂強牛排館』。")
                driver.quit()
                exit()
        except Exception as js_error:
            print(f"❌ JavaScript 點擊失敗，錯誤：{js_error}")
            driver.quit()
            exit()

# 等待餐廳頁面載入
print("⏳ 等待餐廳頁面載入...")
time.sleep(5)

# 🔹 7️⃣ **展開所有訂單內容**
try:
    print("🔄 嘗試展開所有訂單內容...")
    
    # 先獲取所有病友名稱及對應的訂單按鈕
    print("🔍 嘗試獲取病友名稱...")
    # 通過JavaScript獲取有餐點的病友名稱和對應的按鈕
    patients_data = driver.execute_script("""
        // 儲存病友及對應的按鈕
        const patientsData = [];
        
        // 直接找到所有data-baseweb="typo-labelmedium"元素(病友名稱)
        const patientElements = document.querySelectorAll('[data-baseweb="typo-labelmedium"]');
        console.log(`找到 ${patientElements.length} 個病友名稱元素`);
        
        for (let i = 0; i < patientElements.length; i++) {
            try {
                const patientElement = patientElements[i];
                const patientName = patientElement.textContent.trim();
                
                // 排除非病友名稱：包含"本人"字樣、包含"$"符號(價格)、長度小於2的文本
                if (patientName.includes('本人') || 
                    patientName.includes('$') || 
                    patientName.length < 2 ||
                    /^\\d+$/.test(patientName)) { // 純數字
                    console.log(`跳過非病友元素: "${patientName}"`);
                    continue;
                }
                
                // 進一步檢查是否是真正的病友名稱（通常是數字+姓名的格式）
                // 如 "21-20 陳強生" 或者名字包含數字和中文/英文
                const isLikelyPatient = /\d+-\d+\s+[\u4e00-\u9fa5a-zA-Z]+/.test(patientName) || 
                                        /[\u4e00-\u9fa5a-zA-Z]{2,}/.test(patientName);
                
                if (!isLikelyPatient) {
                    console.log(`跳過不符合病友名稱格式的元素: "${patientName}"`);
                    continue;
                }
                
                // 關鍵改進: 檢查父元素是否包含"份餐點"文字
                let hasMealText = false;
                let currentParent = patientElement.parentElement;
                // 向上查找最多5層父元素
                for (let j = 0; j < 5; j++) {
                    if (!currentParent) break;
                    
                    // 檢查此元素及其所有子元素的文本內容
                    if (currentParent.textContent && 
                        (currentParent.textContent.includes('份餐點') || 
                         currentParent.textContent.includes('個餐點'))) {
                        hasMealText = true;
                        break;
                    }
                    
                    currentParent = currentParent.parentElement;
                }
                
                // 如果未找到"份餐點"文字，則跳過此元素
                if (!hasMealText) {
                    console.log(`跳過不包含"份餐點"信息的元素: "${patientName}"`);
                    continue;
                }
                
                // 向上查找至少3-4層，檢查是否包含餐點信息
                let hasMeal = false;
                let button = null;
                
                // 向上查找最多8層父元素，尋找餐點信息和按鈕
                for (let j = 0; j < 8; j++) {
                    if (!currentParent) break;
                    
                    // 查找是否有包含"餐點"文字的元素
                    if (currentParent.textContent && currentParent.textContent.includes('餐點')) {
                        hasMeal = true;
                    }
                    
                    // 查找按鈕元素
                    if (!button) {
                        const foundButton = currentParent.querySelector('button');
                        if (foundButton) button = foundButton;
                    }
                    
                    // 如果找到了按鈕和餐點信息，可以提前結束循環
                    if (hasMeal && button) break;
                    
                    // 向上移動到父元素
                    currentParent = currentParent.parentElement;
                }
                
                // 如果沒有餐點或沒有按鈕，則跳過
                if (!hasMeal || !button) continue;
                
                // 添加到陣列中
                patientsData.push({
                    name: patientName,
                    button: button,
                    // 創建一個唯一標識符
                    id: `patient-${i}-${patientName}`
                });
                console.log(`找到病友: ${patientName}`);
            } catch(e) {
                console.error(`處理第 ${i} 個病友元素時出錯:`, e);
            }
        }
        
        return patientsData;
    """)
    
    # 列出找到的病友
    if patients_data:
        print(f"✅ 成功找到 {len(patients_data)} 個病友:")
        patient_names = [p['name'] for p in patients_data]
        for i, name in enumerate(patient_names):
            print(f"  👤 病友 {i+1}: {name}")
            
        # 優先使用病友數據點擊按鈕
        print("🔄 嘗試點擊病友對應的訂單按鈕...")
        for i, patient in enumerate(patients_data):
            try:
                print(f"🔄 嘗試點擊 {patient['name']} 的訂單按鈕...")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", patient['button'])
                time.sleep(1)  # 等待滾動完成
                driver.execute_script("arguments[0].click();", patient['button'])
                time.sleep(2)  # 等待展開動畫
                print(f"✅ 成功點擊 {patient['name']} 的訂單按鈕")
            except Exception as e:
                print(f"❌ 點擊 {patient['name']} 的訂單按鈕失敗，錯誤：{e}")
        
        print("✅ 訂單展開操作完成！")
    else:
        print("⚠️ 未找到有效的病友資料，將使用一般方法展開訂單")
        # 備用方法：尋找展開按鈕並點擊
        try:
            # 方法1：尋找所有包含展開/收合功能的按鈕
            expand_buttons = driver.find_elements(By.CSS_SELECTOR, "button.aj.cm.cn")
            if expand_buttons:
                print(f"找到 {len(expand_buttons)} 個可能的展開按鈕")
                for i, button in enumerate(expand_buttons):
                    try:
                        print(f"嘗試點擊第 {i+1} 個按鈕...")
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1.5)
                        print(f"✅ 成功點擊第 {i+1} 個按鈕")
                    except Exception as btn_err:
                        print(f"點擊第 {i+1} 個按鈕失敗: {btn_err}")
                print("✅ 完成備用按鈕點擊")
            else:
                # 方法2：使用 XPath 查找按鈕
                print("嘗試使用 XPath 查找展開按鈕...")
                xpath_buttons = driver.find_elements(By.XPATH, "//button[.//svg[contains(@viewBox, '0 0 24 24')]]")
                if xpath_buttons:
                    print(f"通過 XPath 找到 {len(xpath_buttons)} 個按鈕")
                    for i, button in enumerate(xpath_buttons):
                        try:
                            print(f"嘗試點擊 XPath 按鈕 {i+1}...")
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(1.5)
                            print(f"✅ 成功點擊 XPath 按鈕 {i+1}")
                        except Exception as xpath_err:
                            print(f"點擊 XPath 按鈕 {i+1} 失敗: {xpath_err}")
                    print("✅ 完成 XPath 按鈕點擊")
                else:
                    print("❌ 未能找到任何展開按鈕")
        except Exception as backup_err:
            print(f"❌ 備用展開方法失敗: {backup_err}")
        
except Exception as e:
    print(f"❌ 展開訂單內容時發生錯誤：{e}")

# 🔹 8️⃣ **抓取訂單信息**
try:
    print("🔍 開始抓取訂單信息...")
    
    # 使用JavaScript提取訂單信息 - 基於固定標籤和文本內容
    order_items = driver.execute_script("""
        // 訂單項目數組
        const orderItems = [];
        
        // 取得患者名稱映射，以便關聯餐點
        const patientMap = {};
        
        // 查找所有病友名稱，確保排除價格元素
        document.querySelectorAll('[data-baseweb="typo-labelmedium"]').forEach(el => {
            const patientName = el.textContent.trim();
            // 跳過本人和非病友元素（如包含$的價格元素）
            if (patientName.includes('本人') || 
                patientName.includes('$') || 
                patientName.length < 2 || 
                /^\\\\d+$/.test(patientName)) {
                return;
            }
            
            // 向上尋找最外層的容器，通常包含病友+餐點資訊
            let currentElem = el;
            let parentContainer = null;
            
            // 向上尋找可能包含多個餐點的容器
            for (let i = 0; i < 8; i++) {
                if (!currentElem) break;
                currentElem = currentElem.parentElement;
                
                // 檢查是否是包含餐點信息的容器
                if (currentElem && currentElem.textContent.includes('餐點')) {
                    parentContainer = currentElem;
                    break;
                }
            }
            
            if (parentContainer) {
                // 查找此容器中所有價格元素，這些可能是餐點項目的標識
                const priceElems = parentContainer.querySelectorAll('div:not([data-baseweb="typo-labelmedium"])');
                
                priceElems.forEach(elem => {
                    // 如果包含$符號，可能是價格元素
                    if (elem.textContent.includes('$')) {
                        // 尋找餐點名稱元素
                        const nameElems = elem.parentElement.querySelectorAll('div');
                        nameElems.forEach(nameElem => {
                            if (nameElem.textContent && nameElem.textContent.trim() && 
                                !nameElem.textContent.includes('$') &&
                                !nameElem.textContent.includes('數量')) {
                                // 保存餐點名與病友的關聯
                                patientMap[nameElem.textContent.trim()] = patientName;
                            }
                        });
                    }
                });
            }
        });
        
        console.log('找到病友對應餐點映射:', patientMap);
        
        // 1. 首先尋找所有餐點名稱元素 (使用屬性選擇器而非class選擇器)
        const itemNameElements = [];
        
        // 方法1：尋找包含食物名稱的A標籤
        const mealLinks = document.querySelectorAll('a[href*="editItem"]');
        console.log(`找到 ${mealLinks.length} 個餐點鏈接`);
        
        mealLinks.forEach(link => {
            // 從a標籤中尋找餐點名稱
            const nameEls = link.querySelectorAll('div.bo.bp.dr.ds.b1, div[class*="dr"][class*="ds"][class*="b1"]');
            nameEls.forEach(nameEl => {
                if (nameEl.textContent && 
                    nameEl.textContent.trim().length > 1 && 
                    !nameEl.textContent.includes('$') &&
                    !nameEl.textContent.includes('份餐點') &&
                    !nameEl.textContent.includes('數量')) {
                    itemNameElements.push({
                        element: nameEl,
                        name: nameEl.textContent.trim(),
                        container: link  // 使用a標籤作為容器
                    });
                }
            });
        });
        
        // 如果沒有找到餐點，嘗試更多的選擇器
        if (itemNameElements.length === 0) {
            // 方法2：使用屬性選擇器
            document.querySelectorAll('[data-baseweb="box"]').forEach(el => {
                // 檢查元素是否包含價格資訊
                const hasPriceInfo = el.textContent.includes('$');
                
                if (hasPriceInfo) {
                    // 尋找所有可能的餐點名稱
                    const nameEls = el.querySelectorAll('div');
                    nameEls.forEach(nameEl => {
                        if (nameEl.childElementCount === 0 && // 無子元素的文本節點
                            nameEl.textContent && 
                            nameEl.textContent.trim().length > 2 && 
                            nameEl.textContent.trim().length < 50 && // 合理的餐點名稱長度
                            !nameEl.textContent.includes('$') && 
                            !nameEl.textContent.includes('數量') &&
                            !nameEl.textContent.includes('餐點') &&
                            !nameEl.textContent.includes('份餐點') &&
                            !nameEl.textContent.includes('加購')) {
                            
                            itemNameElements.push({
                                element: nameEl,
                                name: nameEl.textContent.trim(),
                                container: el  // 使用找到的容器
                            });
                        }
                    });
                }
            });
        }
        
        console.log(`找到 ${itemNameElements.length} 個可能的餐點名稱元素`);
        
        // 對每個餐點名稱元素，獲取相關信息
        const processedItems = itemNameElements.map((item, index) => {
            try {
                const itemName = item.name;
                console.log(`處理餐點 ${index+1}: ${itemName}`);
                
                // 使用容器元素來提取相關信息
                const container = item.container;
                
                // 餐點容器應該包含價格
                const priceText = container.textContent.match(/\$(\d+(\.\d+)?)/);
                const price = priceText ? priceText[0] : "價格未知";
                
                // 查找數量
                const quantitySelector = container.querySelector('select');
                let quantity = "1"; // 默認數量
                if (quantitySelector) {
                    const selectedOption = Array.from(quantitySelector.options)
                        .find(opt => opt.selected);
                    if (selectedOption) {
                        quantity = selectedOption.textContent.trim();
                    }
                }
                
                // 查找食物細項
                const foodDetails = {};
                
                // 查找口味選擇
                const flavorTitleEls = Array.from(container.querySelectorAll('div')).filter(
                    el => el.textContent.includes('口味選擇')
                );
                
                if (flavorTitleEls.length > 0) {
                    // 尋找口味選擇後的列表項
                    const ulElement = flavorTitleEls[0].nextElementSibling;
                    if (ulElement && ulElement.tagName === 'UL') {
                        const flavorItems = Array.from(ulElement.querySelectorAll('li')).map(
                            li => li.textContent.trim()
                        );
                        if (flavorItems.length > 0) {
                            foodDetails['口味選擇'] = flavorItems;
                        }
                    }
                }
                
                // 嘗試根據文本內容尋找口味選擇
                if (!foodDetails['口味選擇']) {
                    // 使用通用方法尋找任何可能包含"口味"或特定選項的元素
                    const allElements = container.querySelectorAll('div, span, li');
                    const flavorOptions = [];
                    
                    for (const el of allElements) {
                        const text = el.textContent.trim();
                        // 只檢查實際存在的三種口味：蘑菇、黑胡椒、綜合
                        if (text && 
                            text.length > 1 && 
                            text.length < 25 && // 避免抓取太長的文本
                            !text.includes('$') && // 排除含有價格的文本
                            !text.includes('份餐點') && // 排除含有"份餐點"的文本
                            !text.includes('加購') && // 排除含有"加購"的文本
                            (text === '黑胡椒' || 
                             text === '蘑菇' || 
                             text === '綜合')) {
                            // 只添加確定的口味選項文本
                            flavorOptions.push(text);
                        }
                    }
                    
                    if (flavorOptions.length > 0) {
                        foodDetails['口味選擇'] = flavorOptions;
                    }
                }
                
                // 查找加購項目
                const addOnTitleEls = Array.from(container.querySelectorAll('div')).filter(
                    el => el.textContent.includes('加購')
                );
                
                if (addOnTitleEls.length > 0) {
                    // 尋找加購後的列表項
                    const ulElement = addOnTitleEls[0].nextElementSibling;
                    if (ulElement && ulElement.tagName === 'UL') {
                        const addOnItems = Array.from(ulElement.querySelectorAll('li')).map(
                            li => li.textContent.trim()
                        );
                        if (addOnItems.length > 0) {
                            foodDetails['加購'] = addOnItems;
                        }
                    }
                }
                
                // 嘗試根據文本內容尋找加購項目
                if (!foodDetails['加購']) {
                    // 使用通用方法尋找任何可能包含"加"的元素
                    const allElements = container.querySelectorAll('div, span, li');
                    const addOnOptions = [];
                    
                    for (const el of allElements) {
                        const text = el.textContent.trim();
                        // 檢查是否是可能的加購項目
                        if (text && 
                            text.length > 1 && 
                            !text.includes('加購') && // 排除標題
                            (text.includes('加蛋') || 
                             text.includes('加') || 
                             text.includes('升級'))) {
                            addOnOptions.push(text);
                        }
                    }
                    
                    if (addOnOptions.length > 0) {
                        foodDetails['加購'] = addOnOptions;
                    }
                }
                
                // 查找備註
                const noteText = container.textContent.match(/備註：([^$]+)/);
                if (noteText && noteText[1].trim()) {
                    foodDetails['備註'] = [noteText[1].trim()];
                }
                
                // 嘗試查找關聯的病友
                let patientName = "未知病友";
                
                // 方法1：從父容器查找病友名稱
                let parentElem = container;
                for (let i = 0; i < 8; i++) {
                    if (!parentElem) break;
                    
                    const patientEls = parentElem.querySelectorAll('[data-baseweb="typo-labelmedium"]');
                    for (const el of patientEls) {
                        const name = el.textContent.trim();
                        // 確認是病友名稱（通常包含數字-數字 的格式）
                        if (name && 
                            !name.includes('本人') && 
                            !name.includes('$') && 
                            name.length >= 2 && 
                            /\d+-\d+/.test(name)) {
                            patientName = name;
                            console.log(`從容器中找到餐點 "${itemName}" 對應的病友: ${patientName}`);
                            break;
                        }
                    }
                    
                    if (patientName !== "未知病友") break;
                    parentElem = parentElem.parentElement;
                }
                
                // 方法2：從映射中查找
                if (patientName === "未知病友" && patientMap[itemName]) {
                    patientName = patientMap[itemName];
                    console.log(`從映射中找到餐點 "${itemName}" 對應的病友: ${patientName}`);
                }
                
                // 構建最終的餐點對象
                return {
                    病友: patientName,
                    餐點: itemName,
                    食物細項: foodDetails,
                    數量: quantity,
                    單價: `NT${price}`
                };
            } catch (err) {
                console.error(`處理餐點 ${index+1} 出錯:`, err);
                return null;
            }
        }).filter(item => item !== null);
        
        // 去重
        const uniqueItems = [];
        const seenKeys = new Set();
        
        for (const item of processedItems) {
            const key = `${item.病友}-${item.餐點}-${item.單價}`;
            if (!seenKeys.has(key)) {
                seenKeys.add(key);
                uniqueItems.push(item);
            }
        }
        
        console.log(`最終處理得到 ${uniqueItems.length} 個有效餐點`);
        
        // 獲取總價
        let totalPrice = "總價未知";
        const subtotalElement = document.querySelector('[data-testid="subtotal-breakdown"]');
        if (subtotalElement) {
            const richTextElems = subtotalElement.querySelectorAll('[data-testid="rich-text"]');
            if (richTextElems.length > 0) {
                // 最後一個rich-text元素通常是總價
                totalPrice = richTextElems[richTextElems.length - 1].textContent.trim();
            }
        }
        
        // 返回完整訂單信息
        return {
            items: uniqueItems.length > 0 ? uniqueItems : processedItems,
            總價: totalPrice.includes('$') ? totalPrice : `NT${totalPrice}`
        };
    """)
    
    # 輸出訂單信息
    if order_items and 'items' in order_items and len(order_items['items']) > 0:
        print(f"\n📋 成功抓取到 {len(order_items['items'])} 個餐點信息")
        print(f"💰 訂單總價：{order_items['總價']}")
        
        # 按病友分組顯示餐點信息
        patient_items = {}
        for item in order_items['items']:
            patient_name = item['病友']
            if patient_name not in patient_items:
                patient_items[patient_name] = []
            patient_items[patient_name].append(item)
        
        # 為每個病友顯示餐點
        for patient_name, items in patient_items.items():
            print(f"\n👤 病友: {patient_name} (共 {len(items)} 個餐點)")
            for i, item in enumerate(items):
                print(f"  🍲 餐點 {i+1}: {item['餐點']}")
                
                if '食物細項' in item and item['食物細項']:
                    print(f"     🔍 食物細項:")
                    for category, values in item['食物細項'].items():
                        if isinstance(values, list):
                            for value in values:
                                print(f"        • {category}: {value}")
                        else:
                            print(f"        • {category}: {values}")
                
                print(f"     🔢 數量: {item['數量']}")
                print(f"     💵 單價: {item['單價']}")
        
        # 保存訂單信息到JSON文件
        # 修改輸出格式為列表形式 (不使用字典)
        output_items = []
        
        # 遍歷所有訂單項，轉換為列表格式
        for item in order_items['items']:
            # 處理食物細項，將其轉換為列表格式，每個選項單獨一個項目
            food_details_list = []
            if '食物細項' in item and item['食物細項']:
                for category, values in item['食物細項'].items():
                    if category and values:
                        # 如果是陣列，則每個值單獨加入
                        if isinstance(values, list):
                            for value in values:
                                food_details_list.append(f"{category}: {value}")
                        else:
                            # 兼容處理字串情況
                            food_details_list.append(f"{category}: {values}")
            
            # 創建一個訂單項列表
            order_item_list = [
                item["病友"],
                item["餐點"],
                food_details_list,  # 食物細項作為子列表
                item["數量"],
                item["單價"]
            ]
            output_items.append(order_item_list)
        
        # 創建最終輸出列表
        output_json = [
            output_items,  # 第一個元素是訂單項列表
            order_items['總價']  # 第二個元素是總價
        ]
        
        # 處理Windows環境下的編碼問題
        try:
            with open("ubereats_steak.json", "w", encoding="utf-8") as f:
                json.dump(output_json, f, ensure_ascii=False, indent=4)
            print("\n✅ 訂單信息已保存到 'ubereats_steak.json'")
        except UnicodeEncodeError:
            print("\n⚠️ 檢測到編碼問題，嘗試使用UTF-8-SIG編碼保存...")
            with open("ubereats_steak.json", "w", encoding="utf-8-sig") as f:
                json.dump(output_json, f, ensure_ascii=False, indent=4)
            print("\n✅ 訂單信息已使用UTF-8-SIG編碼保存到 'ubereats_steak.json'")
        except Exception as save_err:
            print(f"\n❌ 保存訂單信息時出錯: {save_err}")
            # 嘗試使用ASCII兼容模式
            try:
                with open("ubereats_steak.json", "w", encoding="utf-8") as f:
                    json.dump(output_json, f, ensure_ascii=True, indent=4)
                print("\n✅ 訂單信息已使用ASCII兼容模式保存到 'ubereats_steak.json'")
            except Exception as ascii_err:
                print(f"\n❌ 所有保存方式都失敗: {ascii_err}")
        
       
    else:
        print("❌ 未能抓取到訂單信息")
    
except Exception as e:
    print(f"❌ 抓取訂單信息時發生錯誤：{e}")

# 等待以便查看結果
time.sleep(5)

print("✅ 自動點擊流程執行完成！")

# 在最後加入總結資訊
print("\n" + "=" * 50)
print("📊 執行總結:")
print(f"   - 程式版本: v{VERSION}")
print(f"   - Python 版本: {sys.version.split()[0]}")
print(f"   - Chrome 版本: {driver.capabilities.get('browserVersion', '未知')}")
print(f"   - ChromeDriver 版本: {driver.capabilities.get('chrome').get('chromedriverVersion', '未知').split(' ')[0]}")
print(f"   - 執行時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

# 關閉瀏覽器
try:
    driver.quit()
    print("\n✅ 瀏覽器已安全關閉")
except Exception as e:
    print(f"\n⚠️ 關閉瀏覽器時發生錯誤：{e}")
    print("詳細錯誤資訊：")
    import traceback
    print(traceback.format_exc())
