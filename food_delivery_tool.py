import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, wait
from PIL import Image, ImageTk

# 店家對應表（編號: [ubereats腳本, foodpanda腳本]）
store_mapping = {
    1: ["ubereats_kfc.py", "foodpanda_kfc.py"],
    2: ["ubereats_coco.py", "foodpanda_coco.py"],
    3: ["ubereats_chinshin.py", "foodpanda_chinshin.py"],
    4: ["ubereats_50lan.py", "foodpanda_50lan.py"],
    5: ["ubereats_bafun.py", "foodpanda_bafun.py"],
    6: ["ubereats_bgrking.py", "foodpanda_bgrking.py"],
    7: ["ubereats_chenzi.py", "foodpanda_chenzi.py"],
    8: ["ubereats_hotpot.py", "foodpanda_hotpot.py"],
    9: ["ubereats_milkshop.py", "foodpanda_milkshop.py"],
    10: ["ubereats_steak.py", "foodpanda_steak.py"],
}

store_names = {
    1: "肯德基",
    2: "CoCo都可",
    3: "清心福全",
    4: "50嵐",
    5: "八方雲集",
    6: "漢堡王",
    7: "陳記麻辣",
    8: "喜喜鍋",
    9: "迷客夏",
    10: "樂強牛排館",
}

class OutputRedirector:
    """重定向輸出到 GUI 文本框"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""
        self.last_update_time = time.time()
        
    def write(self, string):
        self.buffer += string
        # 定期更新 UI，避免過於頻繁的更新
        current_time = time.time()
        if current_time - self.last_update_time > 0.1 or "\n" in string:
            self.flush()
            self.last_update_time = current_time
            
    def flush(self):
        if self.buffer:
            # 在主線程中更新 UI
            self.text_widget.after(0, self._update_text)
    
    def _update_text(self):
        # 添加文本到文本框
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, self.buffer)
        self.text_widget.see(tk.END)  # 自動滾動到底部
        self.text_widget.configure(state=tk.DISABLED)
        self.buffer = ""

class DeliveryToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("全自動化訂餐系統")
        self.root.geometry("900x600")
        # 沙漠主題色彩
        self.bg_color = "#E6D2B5"  # 淺沙色背景
        self.text_color = "#623B1C"  # 深咖啡色文字
        self.accent_color = "#8B5A2B"  # 棕色強調
        self.button_color = "#A07955"  # 按鈕顏色
        self.button_text_color = "#FFF8E7"  # 按鈕文字顏色
        self.warning_color = "#C14A09"  # 警告色

        self.root.configure(bg=self.bg_color)
        self.running_processes = []
        self.pending_fp_scripts = {}  # 待執行的Foodpanda腳本 {店家ID：腳本路徑}
        
        # 嘗試載入沙漠背景圖片
        try:
            # 建立一個臨時文件來保存沙漠背景圖片 (如果不存在)
            desert_bg_path = "desert_bg.jpg"
            if not os.path.exists(desert_bg_path):
                # 從網絡下載沙漠圖片或創建一個簡單的漸變背景
                self.create_desert_background(desert_bg_path)
                
            # 載入並調整背景圖片尺寸
            bg_image = Image.open(desert_bg_path)
            bg_image = bg_image.resize((900, 600), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
            # 創建背景標籤
            bg_label = tk.Label(root, image=self.bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
        except Exception as e:
            print(f"無法載入背景圖片: {e}")
            # 如果載入失敗，使用純色背景
            pass
        
        # 設置主框架 (半透明效果)
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        
        # 標題
        title_label = tk.Label(
            self.main_frame, 
            text="全自動化訂餐系統",
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(pady=(20, 30))
        
        # 說明文字框架
        instruction_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        instruction_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 說明文字
        instruction_label = tk.Label(
            instruction_frame,
            text="請輸入要下單的店家編號（用逗號分隔）：",
            font=("Arial", 14, "bold"),  # 放大字體並加粗
            bg=self.bg_color,
            fg=self.text_color,
            anchor="w"
        )
        instruction_label.pack(fill=tk.X, pady=(5, 5))  # 減少底部間距
        
        # 店家列表框架
        store_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        store_frame.pack(fill=tk.X, pady=(5, 10))  # 減少與說明文字的間距
        
        # 左側店家列表框架
        left_store_frame = tk.Frame(store_frame, bg=self.bg_color)
        left_store_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=(50, 30))
        
        # 右側店家列表框架
        right_store_frame = tk.Frame(store_frame, bg=self.bg_color)
        right_store_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=(30, 50))
        
        # 填充店家列表
        mid_point = len(store_names) // 2 + len(store_names) % 2
        for idx, (store_id, store_name) in enumerate(store_names.items()):
            frame = left_store_frame if idx < mid_point else right_store_frame
            store_label = tk.Label(
                frame,
                text=f"{store_id}. {store_name}",
                font=("Arial", 14, "bold"),  # 放大字體
                bg=self.bg_color,
                fg=self.text_color,
                anchor="center"  # 文字居中
            )
            store_label.pack(fill=tk.X, pady=3)  # 減少每個項目間的間距
        
        # 輸入框和按鈕框架
        input_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=(0, 5))  # 減少與店家列表的間距
        
        # 增加輸入框的寬度
        self.entry = tk.Entry(input_frame, font=("Arial", 12), width=60, bg="#FFF8E7")
        self.entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # 按鈕框架
        button_frame = tk.Frame(input_frame, bg=self.bg_color)
        button_frame.pack(side=tk.RIGHT)
        
        # 執行按鈕
        self.run_button = tk.Button(
            button_frame,
            text="開始執行",
            command=self.run_scripts,
            font=("Arial", 11, "bold"),
            bg=self.button_color,
            fg=self.button_text_color,
            relief=tk.RAISED,
            padx=15,
            pady=5
        )
        self.run_button.pack(side=tk.LEFT)
        
        # 停止按鈕
        self.stop_button = tk.Button(
            button_frame,
            text="停止所有",
            command=self.stop_all_scripts,
            font=("Arial", 11, "bold"),
            bg=self.button_color,  # 使用相同的按鈕顏色
            fg=self.button_text_color,  # 修改回米白色，與其他按鈕一致
            relief=tk.RAISED,
            padx=15,
            pady=5,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 清空按鈕
        self.clear_button = tk.Button(
            button_frame,
            text="清空日誌",
            command=self.clear_log,
            font=("Arial", 11),
            bg=self.button_color,  # 使用相同的按鈕顏色
            fg=self.button_text_color,
            relief=tk.RAISED,
            padx=15,
            pady=5
        )
        self.clear_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 日誌框架
        log_frame = tk.LabelFrame(
            self.main_frame,
            text="執行日誌",
            font=("Arial", 11),
            bg=self.bg_color,
            fg=self.accent_color
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 10))  # 增加日誌框架的上方間距
        
        # 日誌文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            width=80,
            height=20,  # 增加高度
            font=("Consolas", 10),
            bg="#FFF8E7",
            fg=self.text_color
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.configure(state=tk.DISABLED)
        
        # 狀態欄
        self.status_var = tk.StringVar()
        self.status_var.set("就緒")
        self.status_bar = tk.Label(
            self.main_frame,
            textvariable=self.status_var,
            font=("Arial", 30),
            bg=self.bg_color,
            fg=self.accent_color,
            anchor="w"
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # 配置按鍵綁定
        self.entry.bind("<Return>", lambda event: self.run_scripts())
        
        # 設置日誌重定向
        self.stdout_redirector = OutputRedirector(self.log_text)
        
        # 顯示歡迎訊息
        self.log("歡迎使用全自動化訂餐系統！請輸入店家編號並點擊「開始執行」。", "info")

    def create_desert_background(self, save_path):
        """創建一個簡單的沙漠漸變背景"""
        width, height = 900, 600
        image = Image.new('RGB', (width, height), color='#E6D2B5')
        
        # 創建漸變效果
        for y in range(height):
            for x in range(width):
                # 頂部是藍天，底部是沙漠
                if y < height // 3:  # 上部分是天空
                    r = int(135 + (y / (height // 3)) * 40)
                    g = int(206 + (y / (height // 3)) * 10)
                    b = int(250 - (y / (height // 3)) * 50)
                else:  # 下部分是沙漠
                    sand_factor = (y - height // 3) / (height * 2 // 3)
                    r = int(220 + sand_factor * 15)
                    g = int(190 + sand_factor * 20)
                    b = int(150 + sand_factor * 15)
                    
                    # 加入一些隨機變化，模擬沙子
                    if x % 5 == 0 and y % 5 == 0:
                        r = min(255, r + 10)
                        g = min(255, g + 5)
                        b = min(255, b - 5)
                
                image.putpixel((x, y), (r, g, b))
        
        # 儲存圖片
        image.save(save_path)

    def log(self, message, level="info"):
        """添加日誌消息到文本框"""
        timestamp = time.strftime("%H:%M:%S")
        
        prefix = ""
        if level == "info":
            prefix = "ℹ️ "
        elif level == "success":
            prefix = "✅ "
        elif level == "error":
            prefix = "❌ "
        elif level == "warning":
            prefix = "⚠️ "
        
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix}{message}\n")
        self.log_text.see(tk.END)  # 滾動到最新的日誌
        self.log_text.configure(state=tk.DISABLED)

    def clear_log(self):
        """清空日誌文本框"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.log("日誌已清空", "info")

    def run_scripts(self):
        """解析輸入並執行相應腳本"""
        # 禁用按鈕，防止重複點擊
        self.run_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        
        # 獲取輸入內容
        raw_input = self.entry.get().strip()
        if not raw_input:
            messagebox.showwarning("提示", "請輸入店家編號！")
            self.run_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
            return
        
        # 啟動執行線程
        threading.Thread(target=self._execute_scripts, args=(raw_input,), daemon=True).start()

    def _execute_scripts(self, raw_input):
        """在單獨的線程中執行腳本"""
        try:
            # 解析店家編號
            selected_ids = []
            for item in raw_input.split(','):
                item = item.strip()
                if item.isdigit():
                    selected_ids.append(int(item))
            
            # 獲取當前腳本路徑
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 準備UberEats腳本執行
            ue_processes = []
            max_parallel = 3  # 最多同時執行3個UberEats腳本
            
            # 創建進程池
            with ThreadPoolExecutor(max_workers=max_parallel) as executor:
                futures = []
                for store_id in selected_ids:
                    if store_id in store_mapping:
                        ue_script_name, fp_script_name = store_mapping[store_id]
                        # 使用絕對路徑
                        ue_script = os.path.join(current_dir, ue_script_name)
                        fp_script = os.path.join(current_dir, fp_script_name)
                        
                        store_name = store_names.get(store_id, f"未知({store_id})")
                        
                        # 將Foodpanda腳本添加到待執行列表
                        self.pending_fp_scripts[store_id] = fp_script
                        
                        # 檢查UberEats腳本文件是否存在
                        if not os.path.exists(ue_script):
                            self.log(f"腳本 {ue_script} 不存在，跳過 {store_name} 的訂單", "error")
                            # 從待執行列表中移除
                            if store_id in self.pending_fp_scripts:
                                del self.pending_fp_scripts[store_id]
                            continue
                        
                        # 檢查並刪除舊的JSON文件
                        json_file = os.path.splitext(ue_script_name)[0] + ".json"
                        json_path = os.path.join(current_dir, json_file)
                        if os.path.exists(json_path):
                            try:
                                os.remove(json_path)
                                self.log(f"已刪除舊的{json_file}文件", "info")
                            except Exception as e:
                                self.log(f"刪除舊的{json_file}文件失敗: {str(e)}", "warning")
                        
                        # 提交UberEats腳本到線程池
                        future = executor.submit(
                            self._run_ue_script, 
                            ue_script, 
                            store_id, 
                            store_name
                        )
                        futures.append(future)
            
            # 等待所有UberEats腳本完成
            wait(futures)
        
            # 檢查是否有Foodpanda腳本需要執行
            if not self.pending_fp_scripts:
                self.log("沒有需要執行的Foodpanda腳本", "warning")
                self.status_var.set("執行完成")
                self.run_button.configure(state=tk.NORMAL)
                self.stop_button.configure(state=tk.DISABLED)
                return
            
            # 設置_fp_scheduled標誌為False，準備在_handle_ue_process_exit中啟動排程
            self._fp_scheduled = False
            self.log("所有UberEats腳本已完成，將開始執行Foodpanda腳本", "info")
        
        except Exception as e:
            self.log(f"執行腳本時發生錯誤: {str(e)}", "error")
            self.status_var.set("執行錯誤")
            self.root.after(0, lambda: self.run_button.configure(state=tk.NORMAL))
    
    def _run_ue_script(self, script_path, store_id, store_name):
        try:
            self.log(f"正在執行 {store_name} 的 UberEats 訂單腳本...", "info")
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            proc = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",  # 🔥 強制使用 utf-8 解碼輸出
                bufsize=1,
                env=env
            )
            self.running_processes.append(proc)
            
            # 讀取輸出
            for line in iter(proc.stdout.readline, ''):
                if line:
                    self.log_text.configure(state=tk.NORMAL)
                    timestamp = time.strftime("%H:%M:%S")
                    self.log_text.insert(tk.END, f"[{timestamp}] [UberEats - {store_name}] {line}")
                    self.log_text.see(tk.END)
                    self.log_text.configure(state=tk.DISABLED)
            
            # 進程結束
            proc.stdout.close()
            return_code = proc.wait()
            
            # 處理UberEats腳本執行結束事件，並啟動相應的Foodpanda腳本
            self.root.after(0, lambda: self._handle_ue_process_exit(store_id, store_name, return_code))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"執行 {store_name} 的 UberEats 腳本時發生錯誤: {str(e)}", "error"))
            self.root.after(0, lambda: self._remove_pending_fp(store_id))

    def _handle_ue_process_exit(self, store_id, store_name, return_code):
        """處理UberEats腳本執行結束事件，並啟動相應的Foodpanda腳本"""
        prefix = f"UberEats - {store_name}"
        if return_code == 0:
            self.log(f"{prefix} 執行完成", "success")
            
            # 檢查JSON文件是否存在
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ue_script_name = store_mapping[store_id][0]
            json_name = os.path.join(current_dir, os.path.splitext(ue_script_name)[0] + ".json")
            
            # 使用絕對路徑優先，如果找不到再使用相對路徑
            if not os.path.exists(json_name):
                # 嘗試直接使用相對路徑
                alt_json_name = os.path.splitext(ue_script_name)[0] + ".json"
                if os.path.exists(alt_json_name):
                    json_name = alt_json_name
                    self.log(f"找到JSON文件：{alt_json_name}", "info")
                else:
                    self.log(f"無法找到 {json_name} 或 {alt_json_name}，無法執行 Foodpanda 腳本", "error")
                    # 從待執行列表中移除
                    if store_id in self.pending_fp_scripts:
                        del self.pending_fp_scripts[store_id]
                    return
            
            # 啟動對應的Foodpanda腳本
            if store_id in self.pending_fp_scripts:
                fp_script = self.pending_fp_scripts[store_id]
                
                # 檢查腳本是否存在
                if not os.path.exists(fp_script):
                    self.log(f"腳本 {fp_script} 不存在，跳過 {store_name} 的 Foodpanda 訂單", "error")
                else:
                    # 將執行Foodpanda腳本的任務添加到待執行列表
                    self.log(f"UberEats 腳本已完成，已將 {store_name} 的 Foodpanda 訂單腳本加入排程", "info")
                    # 不立即執行，而是通過_schedule_fp_scripts方法排程執行
                    if not hasattr(self, '_fp_scheduled') or not self._fp_scheduled:
                        self._fp_scheduled = True
                        self.root.after(1000, self._schedule_fp_scripts)  # 等待1秒後開始執行第一個腳本
            
            # 不在這裡移除，而是在_schedule_fp_scripts中移除
        else:
            # 執行失敗
            self.log(f"{prefix} 執行失敗，返回代碼: {return_code}", "error")
            # 從待執行列表中移除
            if store_id in self.pending_fp_scripts:
                del self.pending_fp_scripts[store_id]
        
        # 檢查是否所有進程都已結束且沒有待執行的Foodpanda腳本
        self.running_processes = [p for p in self.running_processes if p.poll() is None]
        if not self.running_processes and not self.pending_fp_scripts:
            self.status_var.set("執行完成")
            self.stop_button.configure(state=tk.DISABLED)
            self.run_button.configure(state=tk.NORMAL)
            self._fp_scheduled = False

    def _remove_pending_fp(self, store_id):
        """從待執行列表中移除Foodpanda腳本"""
        if store_id in self.pending_fp_scripts:
            del self.pending_fp_scripts[store_id]

    def _schedule_fp_scripts(self):
        if not self.pending_fp_scripts:
            self.status_var.set("執行完成")
            self.run_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
            return
        
        # 獲取第一個待執行的腳本
        store_id = next(iter(self.pending_fp_scripts.keys()))
        fp_script = self.pending_fp_scripts[store_id]
        store_name = store_names.get(store_id, f"未知({store_id})")
        
        # 執行Foodpanda腳本
        try:
            self.log(f"正在執行 {store_name} 的 Foodpanda 訂單腳本...", "info")
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            proc_fp = subprocess.Popen(
                [sys.executable, fp_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env
            )
            self.running_processes.append(proc_fp)
            
            # 使用線程讀取輸出
            threading.Thread(
                target=self._process_fp_output,
                args=(proc_fp, store_name),
                daemon=True
            ).start()
            
        except Exception as e:
            self.log(f"啟動 {store_name} 的 Foodpanda 腳本時發生錯誤: {str(e)}", "error")
        
        # 從待執行列表中移除
        del self.pending_fp_scripts[store_id]
        
        # 設置計時器，45秒後執行下一個
        if self.pending_fp_scripts:
            self.root.after(45000, self._schedule_fp_scripts)
        else:
            # 沒有更多腳本需要執行
            self.root.after(0, lambda: self.log("所有Foodpanda腳本已排程", "info"))

    def _process_fp_output(self, process, store_name):
        """處理Foodpanda腳本的輸出流"""
        prefix = f"Foodpanda - {store_name}"
        
        for line in iter(process.stdout.readline, ''):
            if line:
                # 將輸出添加到日誌
                self.log_text.configure(state=tk.NORMAL)
                timestamp = time.strftime("%H:%M:%S")
                self.log_text.insert(tk.END, f"[{timestamp}] [{prefix}] {line}")
                self.log_text.see(tk.END)
                self.log_text.configure(state=tk.DISABLED)
        
        # 進程結束
        process.stdout.close()
        return_code = process.wait()
        
        # 在主線程中更新 UI
        self.root.after(0, lambda: self._handle_fp_process_exit(prefix, return_code))
    
    def _handle_fp_process_exit(self, prefix, return_code):
        """處理Foodpanda腳本執行結束事件"""
        if return_code == 0:
            self.log(f"{prefix} 執行完成", "success")
        else:
            self.log(f"{prefix} 執行結束，返回代碼: {return_code}", "warning")
        
        # 檢查是否所有進程都已結束且沒有待執行的Foodpanda腳本
        self.running_processes = [p for p in self.running_processes if p.poll() is None]
        if not self.running_processes and not self.pending_fp_scripts:
            self.status_var.set("執行完成")
            self.stop_button.configure(state=tk.DISABLED)
            self.run_button.configure(state=tk.NORMAL)

    def stop_all_scripts(self):
        """停止所有正在運行的腳本"""
        if not self.running_processes:
            return
        
        self.log("正在停止所有腳本...", "warning")
        
        # 終止所有進程
        for proc in self.running_processes:
            if proc.poll() is None:  # 如果進程還在運行
                try:
                    proc.terminate()
                    # 給進程一些時間自行退出
                    time.sleep(0.5)
                    # 如果還在運行，強制結束
                    if proc.poll() is None:
                        proc.kill()
                except Exception as e:
                    self.log(f"停止腳本時發生錯誤: {str(e)}", "error")
        
        # 清空進程列表和待執行列表
        self.running_processes = []
        self.pending_fp_scripts = {}
        
        # 更新 UI
        self.log("已停止所有腳本", "info")
        self.status_var.set("已停止")
        self.run_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)

    def on_closing(self):
        """窗口關閉時的處理"""
        if self.running_processes:
            if messagebox.askokcancel("確認退出", "仍有腳本在運行中，確定要退出嗎？"):
                self.stop_all_scripts()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    # 創建主窗口
    root = tk.Tk()
    app = DeliveryToolApp(root)
    
    # 設置關閉事件處理
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 啟動主循環
    root.mainloop() 