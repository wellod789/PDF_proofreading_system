"""
PDFを画像に変換するテストプログラム
pdf2imageライブラリを使用してPDFファイルを画像（PNG/JPEG）に変換
"""
import os
import sys
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from datetime import datetime

class PDFToImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Image Converter - テストプログラム")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        
        # 変数の初期化
        self.selected_file = None
        self.output_dir = "converted_images"
        self.conversion_settings = {
            'format': 'PNG',
            'dpi': 200,
            'first_page': None,
            'last_page': None,
            'quality': 95
        }
        
        # UIの構築
        self.create_widgets()
        
        # 出力ディレクトリの作成
        os.makedirs(self.output_dir, exist_ok=True)
        
        # ウィンドウの中央配置
        self.center_window()
    
    def create_widgets(self):
        """UIコンポーネントの作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="PDF to Image Converter", 
                              font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # ファイル選択フレーム
        file_frame = ttk.LabelFrame(main_frame, text="PDFファイル選択", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="PDFファイルを選択してください", 
                                  font=('Arial', 10))
        self.file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="ファイルを選択", 
                  command=self.select_file).grid(row=0, column=1)
        
        # 設定フレーム
        settings_frame = ttk.LabelFrame(main_frame, text="変換設定", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 画像フォーマット
        ttk.Label(settings_frame, text="画像フォーマット:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.format_var = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(settings_frame, textvariable=self.format_var, 
                                   values=["PNG", "JPEG"], state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # DPI設定
        ttk.Label(settings_frame, text="DPI:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.dpi_var = tk.StringVar(value="200")
        dpi_combo = ttk.Combobox(settings_frame, textvariable=self.dpi_var, 
                                values=["150", "200", "300", "600"], state="readonly", width=10)
        dpi_combo.grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=2)
        
        # ページ範囲
        ttk.Label(settings_frame, text="ページ範囲:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.first_page_var = tk.StringVar(value="")
        ttk.Entry(settings_frame, textvariable=self.first_page_var, width=8).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(settings_frame, text="～").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        self.last_page_var = tk.StringVar(value="")
        ttk.Entry(settings_frame, textvariable=self.last_page_var, width=8).grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        ttk.Label(settings_frame, text="（空白の場合は全ページ）", font=('Arial', 8)).grid(row=1, column=4, sticky=tk.W, padx=(10, 0), pady=2)
        
        # 処理ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.convert_button = ttk.Button(button_frame, text="変換を開始", 
                                       command=self.start_conversion, state='disabled')
        self.convert_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="出力フォルダを開く", 
                  command=self.open_output_folder).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="結果をクリア", 
                  command=self.clear_results).grid(row=0, column=2)
        
        # プログレスバー
        self.progress_var = tk.StringVar(value="待機中...")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=4, column=0, columnspan=3, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 結果表示フレーム
        result_frame = ttk.LabelFrame(main_frame, text="変換結果", padding="10")
        result_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 結果表示用のテキストエリア
        self.result_text = tk.Text(result_frame, height=8, width=70, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # グリッドの重み設定
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        file_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def select_file(self):
        """ファイル選択ダイアログ"""
        file_path = filedialog.askopenfilename(
            title="PDFファイルを選択",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"選択されたファイル: {filename}")
            self.convert_button.config(state='normal')
            self.status_var.set(f"ファイル選択完了: {filename}")
            
            # ファイル情報を表示
            self.show_file_info(file_path)
    
    def show_file_info(self, file_path):
        """ファイル情報を表示"""
        try:
            from pdf2image import convert_from_path
            # PDFのページ数を取得
            images = convert_from_path(file_path, first_page=1, last_page=1)
            # 実際のページ数を取得するために一時的に変換
            temp_images = convert_from_path(file_path)
            page_count = len(temp_images)
            
            info_text = f"""
ファイル情報:
- ファイル名: {os.path.basename(file_path)}
- ファイルサイズ: {os.path.getsize(file_path):,} bytes
- ページ数: {page_count} ページ
- 出力フォルダ: {os.path.abspath(self.output_dir)}
"""
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, info_text)
            
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, f"ファイル情報の取得に失敗しました: {str(e)}")
    
    def start_conversion(self):
        """変換処理を開始"""
        if not self.selected_file:
            messagebox.showerror("エラー", "PDFファイルを選択してください。")
            return
        
        # 設定を取得
        self.conversion_settings['format'] = self.format_var.get()
        self.conversion_settings['dpi'] = int(self.dpi_var.get())
        
        # ページ範囲の設定
        first_page = self.first_page_var.get().strip()
        last_page = self.last_page_var.get().strip()
        
        if first_page:
            try:
                self.conversion_settings['first_page'] = int(first_page)
            except ValueError:
                messagebox.showerror("エラー", "開始ページ番号が無効です。")
                return
        
        if last_page:
            try:
                self.conversion_settings['last_page'] = int(last_page)
            except ValueError:
                messagebox.showerror("エラー", "終了ページ番号が無効です。")
                return
        
        # ボタンを無効化
        self.convert_button.config(state='disabled')
        
        # プログレスバーを開始
        self.progress_bar.start()
        self.progress_var.set("変換処理中...")
        self.status_var.set("変換処理を開始しました...")
        
        # 別スレッドで処理を実行
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
    
    def run_conversion(self):
        """変換処理の実行（別スレッド）"""
        try:
            # 変換設定
            convert_kwargs = {
                'dpi': self.conversion_settings['dpi'],
                'fmt': self.conversion_settings['format'].lower()
            }
            
            if self.conversion_settings['first_page']:
                convert_kwargs['first_page'] = self.conversion_settings['first_page']
            if self.conversion_settings['last_page']:
                convert_kwargs['last_page'] = self.conversion_settings['last_page']
            
            # PDFを画像に変換
            self.progress_var.set("PDFを読み込み中...")
            images = convert_from_path(self.selected_file, **convert_kwargs)
            
            # 画像を保存
            self.progress_var.set("画像を保存中...")
            saved_files = []
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = Path(self.selected_file).stem
            
            for i, image in enumerate(images):
                page_num = i + 1
                if self.conversion_settings['first_page']:
                    page_num = self.conversion_settings['first_page'] + i
                
                filename = f"{base_name}_page_{page_num:03d}_{timestamp}.{self.conversion_settings['format'].lower()}"
                filepath = os.path.join(self.output_dir, filename)
                
                # 画像を保存
                if self.conversion_settings['format'].upper() == 'JPEG':
                    # JPEGの場合はRGBモードに変換
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image.save(filepath, 'JPEG', quality=self.conversion_settings['quality'])
                else:
                    image.save(filepath)
                
                saved_files.append(filepath)
            
            # UIの更新（メインスレッドで実行）
            self.root.after(0, lambda: self.conversion_completed(saved_files))
            
        except Exception as e:
            error_msg = f"変換処理中にエラーが発生しました: {str(e)}"
            self.root.after(0, lambda: self.conversion_error(error_msg))
    
    def conversion_completed(self, saved_files):
        """変換完了時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("変換完了！")
        self.status_var.set(f"変換完了 - {len(saved_files)}個の画像ファイル")
        
        # 結果を表示
        self.display_results(saved_files)
        
        # ボタンを有効化
        self.convert_button.config(state='normal')
        
        messagebox.showinfo("完了", f"変換が完了しました。\n{len(saved_files)}個の画像ファイルが生成されました。")
    
    def conversion_error(self, error_msg):
        """変換エラー時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("エラーが発生しました")
        self.status_var.set("エラーが発生しました")
        
        # ボタンを有効化
        self.convert_button.config(state='normal')
        
        messagebox.showerror("エラー", error_msg)
    
    def display_results(self, saved_files):
        """変換結果を表示"""
        result_text = f"""
変換完了！

変換設定:
- フォーマット: {self.conversion_settings['format']}
- DPI: {self.conversion_settings['dpi']}
- ページ範囲: {self.conversion_settings['first_page'] or '1'} ～ {self.conversion_settings['last_page'] or '最後'}
- 出力フォルダ: {os.path.abspath(self.output_dir)}

生成されたファイル:
"""
        
        for filepath in saved_files:
            filename = os.path.basename(filepath)
            file_size = os.path.getsize(filepath)
            result_text += f"- {filename} ({file_size:,} bytes)\n"
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, result_text)
    
    def open_output_folder(self):
        """出力フォルダを開く"""
        try:
            if os.path.exists(self.output_dir):
                os.startfile(self.output_dir)
                self.status_var.set("出力フォルダを開きました")
            else:
                messagebox.showwarning("警告", "出力フォルダが存在しません。")
        except Exception as e:
            messagebox.showerror("エラー", f"フォルダを開けませんでした: {str(e)}")
    
    def clear_results(self):
        """結果をクリア"""
        self.result_text.delete(1.0, tk.END)
        self.selected_file = None
        self.file_label.config(text="PDFファイルを選択してください")
        self.convert_button.config(state='disabled')
        self.status_var.set("結果をクリアしました")
        self.progress_var.set("待機中...")

def main():
    """メイン関数"""
    root = tk.Tk()
    app = PDFToImageConverter(root)
    
    # ウィンドウの終了処理
    def on_closing():
        if messagebox.askokcancel("終了", "アプリケーションを終了しますか？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
