"""
PDF校正システム - GUI版
tkinterを使用したデスクトップアプリケーション
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from datetime import datetime
import webbrowser
from pdf_corrector_module import PDFCorrector
from config import Config

class PDFCorrectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF校正システム - GUI版")
        self.root.geometry("805x600")    # 最適なサイズ
        self.root.minsize(800, 600)      # 最小サイズを調整
        self.root.maxsize(1400, 1000)    # 最大サイズを調整
        
        # 変数の初期化
        self.selected_file = None
        self.corrector = None
        self.corrections = []
        self.excel_file = None
        
        # スタイルの設定
        self.setup_styles()
        
        # UIの構築
        self.create_widgets()
        
        # ウィンドウの中央配置
        self.center_window()
        
        # ウィンドウサイズ変更のイベント設定（サイズ表示なし）
        # self.root.bind('<Configure>', self.on_window_resize)
    
    def setup_styles(self):
        """スタイルの設定"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # カスタムスタイル
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Info.TLabel', foreground='blue')
    
    def create_widgets(self):
        """UIコンポーネントの作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="PDF校正システム", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="AI（Claude 3.5 Sonnet v2）による自動校正", 
                                 font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # ファイル選択フレーム
        file_frame = ttk.LabelFrame(main_frame, text="ファイル選択", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="PDFファイルを選択してください", 
                                  font=('Arial', 10))
        self.file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="ファイルを選択", 
                  command=self.select_file).grid(row=0, column=1)
        
        # 処理ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="校正を開始", 
                                       command=self.start_correction, state='disabled')
        self.process_button.grid(row=0, column=0, padx=(0, 10))
        
        self.download_button = ttk.Button(button_frame, text="Excelファイルをダウンロード", 
                                        command=self.download_excel, state='disabled')
        self.download_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="結果をクリア", 
                  command=self.clear_results).grid(row=0, column=2)
        
        # プログレスバー
        self.progress_var = tk.StringVar(value="待機中...")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=4, column=0, columnspan=3, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 結果表示フレーム
        result_frame = ttk.LabelFrame(main_frame, text="校正結果", padding="10")
        result_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 結果表示用のNotebook（タブ）
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 校正結果タブ
        self.result_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.result_frame, text="校正結果")
        
        # 校正結果の表示用Treeview
        columns = ('ページ', 'タイプ', '内容', '校正結果')
        self.result_tree = ttk.Treeview(self.result_frame, columns=columns, show='headings', height=8)
        
        # 列の設定
        self.result_tree.heading('ページ', text='ページ')
        self.result_tree.heading('タイプ', text='タイプ')
        self.result_tree.heading('内容', text='内容')
        self.result_tree.heading('校正結果', text='校正結果')
        
        self.result_tree.column('ページ', width=60)
        self.result_tree.column('タイプ', width=80)
        self.result_tree.column('内容', width=200)
        self.result_tree.column('校正結果', width=400)
        
        # スクロールバー
        scrollbar_y = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        scrollbar_x = ttk.Scrollbar(self.result_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.result_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 詳細表示タブ
        self.detail_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.detail_frame, text="詳細表示")
        
        self.detail_text = scrolledtext.ScrolledText(self.detail_frame, height=8, width=80)
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 結果ツリーの選択イベント
        self.result_tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # グリッドの重み設定
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        file_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(0, weight=1)
        self.detail_frame.columnconfigure(0, weight=1)
        self.detail_frame.rowconfigure(0, weight=1)
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
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
            self.process_button.config(state='normal')
            self.status_var.set(f"ファイル選択完了: {filename}")
    
    def start_correction(self):
        """校正処理を開始"""
        if not self.selected_file:
            messagebox.showerror("エラー", "PDFファイルを選択してください。")
            return
        
        # ボタンを無効化
        self.process_button.config(state='disabled')
        self.download_button.config(state='disabled')
        
        # プログレスバーを開始
        self.progress_bar.start()
        self.progress_var.set("校正処理中...")
        self.status_var.set("校正処理を開始しました...")
        
        # 別スレッドで処理を実行
        thread = threading.Thread(target=self.run_correction)
        thread.daemon = True
        thread.start()
    
    def run_correction(self):
        """校正処理の実行（別スレッド）"""
        try:
            # 出力ディレクトリの作成
            os.makedirs('outputs', exist_ok=True)
            
            # PDF校正処理
            self.corrector = PDFCorrector()
            self.corrections = self.corrector.process_pdf(
                self.selected_file, 
                progress_callback=self.update_progress
            )
            
            # エクセルファイルの生成
            excel_filename = f"校正結果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            excel_path = os.path.join('outputs', excel_filename)
            self.corrector.export_to_excel(excel_path)
            self.excel_file = excel_filename
            
            # UIの更新（メインスレッドで実行）
            self.root.after(0, self.correction_completed)
            
        except Exception as e:
            error_msg = f"校正処理中にエラーが発生しました: {str(e)}"
            self.root.after(0, lambda: self.correction_error(error_msg))
    
    def update_progress(self, message):
        """プログレス更新（別スレッドから呼び出し）"""
        self.root.after(0, lambda: self.progress_var.set(message))
    
    def correction_completed(self):
        """校正完了時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("校正完了！")
        self.status_var.set(f"校正完了 - {len(self.corrections)}件の結果")
        
        # 結果を表示
        self.display_results()
        
        # ボタンを有効化
        self.process_button.config(state='normal')
        self.download_button.config(state='normal')
        
        messagebox.showinfo("完了", f"校正が完了しました。\n{len(self.corrections)}件の校正結果が見つかりました。")
    
    def correction_error(self, error_msg):
        """校正エラー時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("エラーが発生しました")
        self.status_var.set("エラーが発生しました")
        
        # ボタンを有効化
        self.process_button.config(state='normal')
        
        messagebox.showerror("エラー", error_msg)
    
    def display_results(self):
        """校正結果を表示"""
        # 既存の結果をクリア
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 結果を追加
        for correction in self.corrections:
            self.result_tree.insert('', 'end', values=(
                correction['page'],
                'テキスト' if correction['type'] == 'text' else '画像',
                correction['content'],
                correction['correction'][:100] + '...' if len(correction['correction']) > 100 else correction['correction']
            ))
    
    def on_item_select(self, event):
        """結果アイテムが選択された時の処理"""
        selection = self.result_tree.selection()
        if selection:
            item = self.result_tree.item(selection[0])
            values = item['values']
            
            # 詳細表示を更新
            self.detail_text.delete(1.0, tk.END)
            detail_text = f"""
ページ: {values[0]}
タイプ: {values[1]}
内容: {values[2]}

校正結果:
{values[3]}
"""
            self.detail_text.insert(1.0, detail_text)
    
    def download_excel(self):
        """Excelファイルをダウンロード"""
        if not self.excel_file:
            messagebox.showwarning("警告", "ダウンロード可能なファイルがありません。")
            return
        
        try:
            excel_path = os.path.join('outputs', self.excel_file)
            if os.path.exists(excel_path):
                # ファイルを開く
                os.startfile(excel_path)
                self.status_var.set(f"Excelファイルを開きました: {self.excel_file}")
            else:
                messagebox.showerror("エラー", "Excelファイルが見つかりません。")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルを開けませんでした: {str(e)}")
    
    def clear_results(self):
        """結果をクリア"""
        # 結果をクリア
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.detail_text.delete(1.0, tk.END)
        
        # 変数をリセット
        self.corrections = []
        self.excel_file = None
        self.corrector = None
        
        # ボタンを無効化
        self.download_button.config(state='disabled')
        
        # ステータスを更新
        self.status_var.set("結果をクリアしました")
        self.progress_var.set("待機中...")

def main():
    """メイン関数"""
    root = tk.Tk()
    app = PDFCorrectorGUI(root)
    
    # ウィンドウの終了処理
    def on_closing():
        if messagebox.askokcancel("終了", "アプリケーションを終了しますか？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
