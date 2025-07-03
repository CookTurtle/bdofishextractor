import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import re
import shutil
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
import chardet
import sys

def get_exe_dir():
    """取得exe檔案所在的目錄"""
    if getattr(sys, 'frozen', False):
        # 如果是打包後的exe
        return os.path.dirname(sys.executable)
    else:
        # 如果是直接執行的Python腳本
        return os.path.dirname(os.path.abspath(__file__))

# 設定檔案和data目錄的路徑
EXE_DIR = get_exe_dir()
CONFIG_FILE = os.path.join(EXE_DIR, "config.json")
DATA_DIR = os.path.join(EXE_DIR, "data")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"user_folder": ""}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def detect_file_encoding(file_path):
    """檢測檔案編碼"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    except:
        return 'utf-8'

def read_file_with_encoding(file_path):
    """使用適當編碼讀取檔案"""
    encodings_to_try = ['utf-8', 'utf-8-sig', 'gbk', 'big5', 'cp950', 'cp1252', 'iso-8859-1']
    
    detected_encoding = detect_file_encoding(file_path)
    if detected_encoding and detected_encoding.lower() not in encodings_to_try:
        encodings_to_try.insert(0, detected_encoding)

    for encoding in encodings_to_try:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
                if '<WorldmapBookMark>' in content or '<?xml' in content:
                    return content, encoding
        except (UnicodeDecodeError, UnicodeError):
            continue

    # 如果所有都失敗，最後嘗試用 utf-8 並替換錯誤字元
    with open(file_path, "r", encoding="utf-8", errors='replace') as f:
        return f.read(), 'utf-8'

def extract_worldmap_bookmark(content):
    """提取 WorldmapBookMark 區段，使用更精確的正則表達式"""
    # 使用更嚴格的正則表達式來匹配完整的 WorldmapBookMark 標籤
    pattern = r'<WorldmapBookMark[^>]*>.*?</WorldmapBookMark>'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if matches:
        # 如果找到多個匹配，選擇最長的（通常是最完整的）
        return max(matches, key=len)
    
    # 如果沒找到，嘗試更寬鬆的匹配
    pattern_loose = r'<WorldmapBookMark>.*?</WorldmapBookMark>'
    matches_loose = re.findall(pattern_loose, content, re.DOTALL | re.IGNORECASE)
    
    if matches_loose:
        return max(matches_loose, key=len)
    
    return None

def validate_xml_structure(content):
    """驗證XML結構是否有效"""
    try:
        # 嘗試解析XML以確保結構有效
        ET.fromstring(content)
        return True
    except (ET.ParseError, ExpatError):
        return False

def get_sea_names():
    if not os.path.exists(DATA_DIR):
        return []  # 如果data資料夾不存在，返回空列表
    
    valid_files = []
    for f in os.listdir(DATA_DIR):
        if f.endswith(".xml"):
            file_path = os.path.join(DATA_DIR, f)
            try:
                content, _ = read_file_with_encoding(file_path)
                # 檢查檔案是否包含 WorldmapBookMark
                if extract_worldmap_bookmark(content):
                    valid_files.append(os.path.splitext(f)[0])
            except Exception:
                # 如果檔案無法讀取或解析，跳過它
                continue
    
    return sorted(valid_files)

class SeaSelectorApp:
    def __init__(self, master):
        self.master = master
        self.config = load_config()
        self.all_sea_names = get_sea_names()

        master.title("海域選擇器")
        master.geometry("450x250")
        master.resizable(False, False)
        
        # 設定視窗圖示
        self.set_window_icon(master)

        self.path_label = tk.Label(master, text="📂 使用者資料夾：")
        self.path_label.pack(pady=(10, 0))

        self.path_display = tk.Label(master, text=self.config["user_folder"] or "尚未設定", fg="blue", wraplength=400)
        self.path_display.pack()

        self.select_button = tk.Button(master, text="選擇資料夾", command=self.select_user_folder)
        self.select_button.pack(pady=5)

        tk.Label(master, text="🔍 搜尋海域：").pack()
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_dropdown)
        self.entry = tk.Entry(master, textvariable=self.search_var, width=40)
        self.entry.pack(pady=3)

        self.combo_var = tk.StringVar()
        self.combo = ttk.Combobox(master, textvariable=self.combo_var, values=self.all_sea_names, width=40)
        self.combo.pack(pady=3)

        self.apply_button = tk.Button(master, text="套用海域到 gamevariable.xml", command=self.inject_bookmark)
        self.apply_button.pack(pady=8)
        
        # 添加狀態顯示和說明
        if len(self.all_sea_names) > 0:
            status_text = f"找到 {len(self.all_sea_names)} 個有效海域檔案"
            status_color = "green"
        else:
            status_text = "未找到海域檔案，請將資料集放入與程式同目錄的 data 資料夾中"
            status_color = "red"
        
        self.status_label = tk.Label(master, text=status_text, fg=status_color, wraplength=400)
        self.status_label.pack(pady=5)
        
        # 添加data資料夾路徑顯示
        data_path_text = f"資料集位置：{DATA_DIR}"
        self.data_path_label = tk.Label(master, text=data_path_text, fg="gray", font=("Arial", 8), wraplength=400)
        self.data_path_label.pack(pady=(0, 5))
    
    def set_window_icon(self, master):
        """設定視窗圖示"""
        def resource_path(relative_path):
            """獲取資源的實際路徑（支援 PyInstaller 打包）"""
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(EXE_DIR, relative_path)
        # 尋找圖示檔案（支援多種格式）
        icon_files = ['icon.ico', 'app.ico', 'sea.ico', 'icon.png', 'app.png', 'sea.png']
        icon_path = None
            
        for icon_file in icon_files:
            potential_path = resource_path(icon_file)
            if os.path.exists(potential_path):
                icon_path = potential_path
                break
            
        if icon_path:
            if icon_path.lower().endswith('.ico'):
                # 使用 .ico 檔案
                master.iconbitmap(icon_path)
            elif icon_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # 使用其他圖片格式
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                    # 調整圖示大小
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                master.iconphoto(True, photo)
                    # 保存引用以防止垃圾回收
                master.icon_photo = photo
        else:
                # 如果找不到圖示檔案，創建簡單的文字圖示
            self.create_default_icon(master)

    def create_default_icon(self, master):
        """創建預設圖示（如果沒有圖示檔案）"""
        try:
            # 創建一個簡單的文字圖示
            import tkinter as tk
            from tkinter import font
            
            # 創建一個小的Canvas來製作圖示
            temp_canvas = tk.Canvas(master, width=32, height=32)
            temp_canvas.configure(bg='lightblue')
            temp_canvas.create_text(16, 16, text='海', fill='darkblue', 
                                  font=('Arial', '14', 'bold'))
            
            # 將Canvas轉換為PhotoImage
            temp_canvas.update()
            ps = temp_canvas.postscript(colormode='color', width=32, height=32)
            
            # 這個方法比較複雜，我們改用更簡單的方式
            # 直接設定程式的標題列文字
            master.title("🌊 海域選擇器")
            
            # 刪除臨時Canvas
            temp_canvas.destroy()
            
        except Exception as e:
            master.title("海域選擇器")

    def select_user_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.config["user_folder"] = path
            save_config(self.config)
            self.path_display.config(text=path)

    def update_dropdown(self, *args):
        keyword = self.search_var.get().lower()
        filtered = [name for name in self.all_sea_names if keyword in name.lower()]
        self.combo["values"] = filtered
        if filtered:
            self.combo.current(0)
        else:
            self.combo.set("")

    def inject_bookmark(self):
        selected = self.combo_var.get()
        sea_path = os.path.join(DATA_DIR, f"{selected}.xml")
        user_dir = self.config.get("user_folder", "")
        target_path = os.path.join(user_dir, "gamevariable.xml")

        if not selected:
            messagebox.showerror("錯誤", "請選擇海域")
            return
        
        if not os.path.exists(sea_path):
            messagebox.showerror("錯誤", f"海域檔案不存在：{sea_path}")
            return
            
        if not user_dir:
            messagebox.showerror("錯誤", "請先選擇使用者資料夾")
            return
            
        if not os.path.exists(target_path):
            messagebox.showerror("錯誤", "gamevariable.xml 不存在於指定資料夾")
            return

        try:
            # 讀取海域檔案
            self.status_label.config(text="正在讀取海域檔案...", fg="orange")
            self.master.update()
            
            sea_content, sea_encoding = read_file_with_encoding(sea_path)
            bookmark_block = extract_worldmap_bookmark(sea_content)
            
            if not bookmark_block:
                messagebox.showerror("錯誤", f"在海域檔案 {selected}.xml 中找不到有效的 WorldmapBookMark 區段")
                self.status_label.config(text="操作失敗", fg="red")
                return

            # 讀取目標檔案
            self.status_label.config(text="正在讀取目標檔案...", fg="orange")
            self.master.update()
            
            gamevar_content, gamevar_encoding = read_file_with_encoding(target_path)

            if "<WorldmapBookMark" not in gamevar_content:
                messagebox.showerror("錯誤", "gamevariable.xml 中找不到 WorldmapBookMark 區段")
                self.status_label.config(text="操作失敗", fg="red")
                return

            # 替換 WorldmapBookMark 區塊
            self.status_label.config(text="正在替換內容...", fg="orange")
            self.master.update()
            
            # 使用更精確的替換
            pattern = r'<WorldmapBookMark[^>]*>.*?</WorldmapBookMark>'
            if re.search(pattern, gamevar_content, re.DOTALL | re.IGNORECASE):
                new_content = re.sub(pattern, bookmark_block, gamevar_content, flags=re.DOTALL | re.IGNORECASE)
            else:
                # 如果找不到帶屬性的標籤，嘗試簡單版本
                pattern_simple = r'<WorldmapBookMark>.*?</WorldmapBookMark>'
                new_content = re.sub(pattern_simple, bookmark_block, gamevar_content, flags=re.DOTALL | re.IGNORECASE)

            # 備份原始檔
            # 備份原始檔到 EXE 所在資料夾
            backup_path = os.path.join(EXE_DIR, "gamevariable.xml.bak")
            shutil.copy(target_path, backup_path)

            # 寫入新內容，使用原始檔案的編碼
            with open(target_path, "w", encoding=gamevar_encoding) as f:
               f.write(new_content)

            self.status_label.config(text="操作成功完成！", fg="green")
            messagebox.showinfo("成功", f"已將 {selected} 的海域資料插入 gamevariable.xml\n\n原檔已備份為：{os.path.basename(backup_path)}")

        except Exception as e:
            error_msg = f"處理失敗：{str(e)}"
            messagebox.showerror("錯誤", error_msg)
            self.status_label.config(text="操作失敗", fg="red")

# 主程式
if __name__ == "__main__":
    root = tk.Tk()
    app = SeaSelectorApp(root)
    root.mainloop()
