"""
PDFを画像に変換してAI分析するプログラム
pdf2imageライブラリを使用してPDFファイルを画像（PNG/JPEG）に変換し、
AWS BedrockのClaudeで画像を分析
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
import boto3
import json
import base64
import io
from config import Config

class PDFToImageAIAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Image Converter with AI Analysis - テストプログラム")
        self.root.geometry("900x800")
        self.root.minsize(800, 700)
        
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
        
        # AI分析結果
        self.ai_analysis_results = []
        self.converted_images = []
        
        # AWS Bedrock設定
        try:
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=Config.AWS_DEFAULT_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
            )
            self.ai_enabled = True
        except Exception as e:
            print(f"AWS Bedrock設定エラー: {e}")
            self.ai_enabled = False
        
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
        title_label = ttk.Label(main_frame, text="PDF to Image Converter with AI Analysis", 
                              font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="PDFを画像に変換し、AI（Claude 3.5 Sonnet v2）で分析", 
                                 font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, columnspan=4, pady=(0, 20))
        
        # ファイル選択フレーム
        file_frame = ttk.LabelFrame(main_frame, text="PDFファイル選択", padding="10")
        file_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="PDFファイルを選択してください", 
                                  font=('Arial', 10))
        self.file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="ファイルを選択", 
                  command=self.select_file).grid(row=0, column=1)
        
        # 設定フレーム
        settings_frame = ttk.LabelFrame(main_frame, text="変換設定", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        button_frame.grid(row=4, column=0, columnspan=4, pady=(0, 10))
        
        self.convert_button = ttk.Button(button_frame, text="画像変換を開始", 
                                       command=self.start_conversion, state='disabled')
        self.convert_button.grid(row=0, column=0, padx=(0, 10))
        
        self.ai_analyze_button = ttk.Button(button_frame, text="AI分析を開始", 
                                          command=self.start_ai_analysis, state='disabled')
        self.ai_analyze_button.grid(row=0, column=1, padx=(0, 10))
        
        self.combined_button = ttk.Button(button_frame, text="変換+AI分析", 
                                       command=self.start_combined_process, state='disabled')
        self.combined_button.grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(button_frame, text="出力フォルダを開く", 
                  command=self.open_output_folder).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(button_frame, text="結果をクリア", 
                  command=self.clear_results).grid(row=0, column=4)
        
        # プログレスバー
        self.progress_var = tk.StringVar(value="待機中...")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=5, column=0, columnspan=4, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 結果表示フレーム（タブ形式）
        result_frame = ttk.LabelFrame(main_frame, text="結果表示", padding="10")
        result_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Notebook（タブ）を作成
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 変換結果タブ
        self.conversion_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.conversion_frame, text="変換結果")
        
        self.conversion_text = tk.Text(self.conversion_frame, height=8, width=80, wrap=tk.WORD)
        conversion_scrollbar = ttk.Scrollbar(self.conversion_frame, orient=tk.VERTICAL, command=self.conversion_text.yview)
        self.conversion_text.configure(yscrollcommand=conversion_scrollbar.set)
        
        self.conversion_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        conversion_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # AI分析結果タブ
        self.ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_frame, text="AI分析結果")
        
        self.ai_text = tk.Text(self.ai_frame, height=8, width=80, wrap=tk.WORD)
        ai_scrollbar = ttk.Scrollbar(self.ai_frame, orient=tk.VERTICAL, command=self.ai_text.yview)
        self.ai_text.configure(yscrollcommand=ai_scrollbar.set)
        
        self.ai_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        ai_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=8, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # グリッドの重み設定
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        file_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        self.conversion_frame.columnconfigure(0, weight=1)
        self.conversion_frame.rowconfigure(0, weight=1)
        self.ai_frame.columnconfigure(0, weight=1)
        self.ai_frame.rowconfigure(0, weight=1)
    
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
            if self.ai_enabled:
                self.ai_analyze_button.config(state='normal')
                self.combined_button.config(state='normal')
            self.status_var.set(f"ファイル選択完了: {filename}")
            
            # ファイル情報を表示
            self.show_file_info(file_path)
    
    def show_file_info(self, file_path):
        """ファイル情報を表示"""
        try:
            # PDFのページ数を取得
            images = convert_from_path(file_path, first_page=1, last_page=1)
            temp_images = convert_from_path(file_path)
            page_count = len(temp_images)
            
            info_text = f"""
ファイル情報:
- ファイル名: {os.path.basename(file_path)}
- ファイルサイズ: {os.path.getsize(file_path):,} bytes
- ページ数: {page_count} ページ
- 出力フォルダ: {os.path.abspath(self.output_dir)}
- AI機能: {'有効' if self.ai_enabled else '無効'}
"""
            self.conversion_text.delete(1.0, tk.END)
            self.conversion_text.insert(1.0, info_text)
            
        except Exception as e:
            self.conversion_text.delete(1.0, tk.END)
            self.conversion_text.insert(1.0, f"ファイル情報の取得に失敗しました: {str(e)}")
    
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
    
    def start_ai_analysis(self):
        """AI分析処理を開始"""
        if not self.selected_file:
            messagebox.showerror("エラー", "PDFファイルを選択してください。")
            return
        
        if not self.ai_enabled:
            messagebox.showerror("エラー", "AI機能が利用できません。AWS設定を確認してください。")
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
        self.ai_analyze_button.config(state='disabled')
        
        # プログレスバーを開始
        self.progress_bar.start()
        self.progress_var.set("AI分析中...")
        self.status_var.set("AI分析を開始しました...")
        
        # 別スレッドで処理を実行
        thread = threading.Thread(target=self.run_ai_analysis)
        thread.daemon = True
        thread.start()
    
    def start_combined_process(self):
        """変換+AI分析の統合処理を開始"""
        if not self.selected_file:
            messagebox.showerror("エラー", "PDFファイルを選択してください。")
            return
        
        if not self.ai_enabled:
            messagebox.showerror("エラー", "AI機能が利用できません。AWS設定を確認してください。")
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
        self.combined_button.config(state='disabled')
        
        # プログレスバーを開始
        self.progress_bar.start()
        self.progress_var.set("変換+AI分析中...")
        self.status_var.set("変換+AI分析を開始しました...")
        
        # 別スレッドで処理を実行
        thread = threading.Thread(target=self.run_combined_process)
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
            
            # 変換された画像を保存
            self.converted_images = images
            
            # UIの更新（メインスレッドで実行）
            self.root.after(0, lambda: self.conversion_completed(saved_files))
            
        except Exception as e:
            error_msg = f"変換処理中にエラーが発生しました: {str(e)}"
            self.root.after(0, lambda: self.conversion_error(error_msg))
    
    def run_ai_analysis(self):
        """AI分析処理の実行（別スレッド）"""
        try:
            # PDFを画像に変換
            self.progress_var.set("PDFを画像に変換中...")
            images = convert_from_path(
                self.selected_file, 
                dpi=self.conversion_settings['dpi'],
                fmt=self.conversion_settings['format'].lower()
            )
            
            # ページ範囲の設定
            first_page = self.conversion_settings['first_page']
            last_page = self.conversion_settings['last_page']
            
            if first_page:
                images = images[first_page-1:]
            if last_page:
                images = images[:last_page-first_page+1] if first_page else images[:last_page]
            
            # 各画像をAIで分析
            self.ai_analysis_results = []
            for i, image in enumerate(images):
                page_num = i + 1
                if first_page:
                    page_num = first_page + i
                
                self.progress_var.set(f"ページ {page_num} をAI分析中...")
                
                # 画像をbase64エンコード
                img_buffer = io.BytesIO()
                image.save(img_buffer, format=self.conversion_settings['format'])
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
                # AI分析
                analysis_result = self.analyze_image_with_claude(img_base64, page_num)
                self.ai_analysis_results.append({
                    'page': page_num,
                    'analysis': analysis_result
                })
            
            # UIの更新（メインスレッドで実行）
            self.root.after(0, self.ai_analysis_completed)
            
        except Exception as e:
            error_msg = f"AI分析中にエラーが発生しました: {str(e)}"
            self.root.after(0, lambda: self.ai_analysis_error(error_msg))
    
    def run_combined_process(self):
        """変換+AI分析の統合処理の実行（別スレッド）"""
        try:
            # PDFを画像に変換
            self.progress_var.set("PDFを画像に変換中...")
            images = convert_from_path(
                self.selected_file, 
                dpi=self.conversion_settings['dpi'],
                fmt=self.conversion_settings['format'].lower()
            )
            
            # ページ範囲の設定
            first_page = self.conversion_settings['first_page']
            last_page = self.conversion_settings['last_page']
            
            if first_page:
                images = images[first_page-1:]
            if last_page:
                images = images[:last_page-first_page+1] if first_page else images[:last_page]
            
            # 画像を保存
            self.progress_var.set("画像を保存中...")
            saved_files = []
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = Path(self.selected_file).stem
            
            for i, image in enumerate(images):
                page_num = i + 1
                if first_page:
                    page_num = first_page + i
                
                filename = f"{base_name}_page_{page_num:03d}_{timestamp}.{self.conversion_settings['format'].lower()}"
                filepath = os.path.join(self.output_dir, filename)
                
                # 画像を保存
                if self.conversion_settings['format'].upper() == 'JPEG':
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image.save(filepath, 'JPEG', quality=self.conversion_settings['quality'])
                else:
                    image.save(filepath)
                
                saved_files.append(filepath)
            
            # 各画像をAIで分析
            self.progress_var.set("AI分析を実行中...")
            self.ai_analysis_results = []
            for i, image in enumerate(images):
                page_num = i + 1
                if first_page:
                    page_num = first_page + i
                
                self.progress_var.set(f"ページ {page_num} をAI分析中...")
                
                # 画像をbase64エンコード
                img_buffer = io.BytesIO()
                image.save(img_buffer, format=self.conversion_settings['format'])
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
                # AI分析
                analysis_result = self.analyze_image_with_claude(img_base64, page_num)
                self.ai_analysis_results.append({
                    'page': page_num,
                    'analysis': analysis_result
                })
            
            # 変換された画像を保存
            self.converted_images = images
            
            # UIの更新（メインスレッドで実行）
            self.root.after(0, lambda: self.combined_process_completed(saved_files))
            
        except Exception as e:
            error_msg = f"統合処理中にエラーが発生しました: {str(e)}"
            self.root.after(0, lambda: self.combined_process_error(error_msg))
    
    def analyze_image_with_claude(self, image_base64, page_num):
        """Claude 3.5 Sonnet v2で画像を分析"""
        try:
            prompt = f"""
以下のPDFページ（ページ {page_num}）の画像を分析してください。

画像の内容について以下の観点で分析し、詳細な報告をしてください：

1. 文書の種類・目的
2. レイアウト・構成
3. テキスト内容の概要
4. 画像・図表の有無と内容
5. 校正すべき点（誤字脱字、レイアウト問題、表現の不自然さなど）
6. 改善提案

日本語で回答してください。
"""

            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{self.conversion_settings['format'].lower()}",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            })

            response = self.bedrock_client.invoke_model(
                modelId=Config.BEDROCK_MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=body
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            return f"AI分析エラー: {str(e)}"
    
    def conversion_completed(self, saved_files):
        """変換完了時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("変換完了！")
        self.status_var.set(f"変換完了 - {len(saved_files)}個の画像ファイル")
        
        # 結果を表示
        self.display_conversion_results(saved_files)
        
        # ボタンを有効化
        self.convert_button.config(state='normal')
        
        messagebox.showinfo("完了", f"変換が完了しました。\n{len(saved_files)}個の画像ファイルが生成されました。")
    
    def ai_analysis_completed(self):
        """AI分析完了時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("AI分析完了！")
        self.status_var.set(f"AI分析完了 - {len(self.ai_analysis_results)}ページ分析")
        
        # 結果を表示
        self.display_ai_results()
        
        # ボタンを有効化
        self.ai_analyze_button.config(state='normal')
        
        messagebox.showinfo("完了", f"AI分析が完了しました。\n{len(self.ai_analysis_results)}ページを分析しました。")
    
    def combined_process_completed(self, saved_files):
        """統合処理完了時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("変換+AI分析完了！")
        self.status_var.set(f"統合処理完了 - {len(saved_files)}個の画像ファイル、{len(self.ai_analysis_results)}ページ分析")
        
        # 結果を表示
        self.display_conversion_results(saved_files)
        self.display_ai_results()
        
        # ボタンを有効化
        self.combined_button.config(state='normal')
        
        messagebox.showinfo("完了", f"変換+AI分析が完了しました。\n{len(saved_files)}個の画像ファイルが生成され、{len(self.ai_analysis_results)}ページを分析しました。")
    
    def conversion_error(self, error_msg):
        """変換エラー時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("エラーが発生しました")
        self.status_var.set("エラーが発生しました")
        
        # ボタンを有効化
        self.convert_button.config(state='normal')
        
        messagebox.showerror("エラー", error_msg)
    
    def ai_analysis_error(self, error_msg):
        """AI分析エラー時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("エラーが発生しました")
        self.status_var.set("エラーが発生しました")
        
        # ボタンを有効化
        self.ai_analyze_button.config(state='normal')
        
        messagebox.showerror("エラー", error_msg)
    
    def combined_process_error(self, error_msg):
        """統合処理エラー時の処理"""
        self.progress_bar.stop()
        self.progress_var.set("エラーが発生しました")
        self.status_var.set("エラーが発生しました")
        
        # ボタンを有効化
        self.combined_button.config(state='normal')
        
        messagebox.showerror("エラー", error_msg)
    
    def display_conversion_results(self, saved_files):
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
        
        self.conversion_text.delete(1.0, tk.END)
        self.conversion_text.insert(1.0, result_text)
    
    def display_ai_results(self):
        """AI分析結果を表示"""
        result_text = f"""
AI分析完了！

分析設定:
- フォーマット: {self.conversion_settings['format']}
- DPI: {self.conversion_settings['dpi']}
- ページ範囲: {self.conversion_settings['first_page'] or '1'} ～ {self.conversion_settings['last_page'] or '最後'}
- AI: Claude 3.5 Sonnet v2

分析結果:
"""
        
        for result in self.ai_analysis_results:
            result_text += f"\n=== ページ {result['page']} ===\n"
            result_text += f"{result['analysis']}\n"
            result_text += "-" * 50 + "\n"
        
        self.ai_text.delete(1.0, tk.END)
        self.ai_text.insert(1.0, result_text)
    
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
        self.conversion_text.delete(1.0, tk.END)
        self.ai_text.delete(1.0, tk.END)
        self.selected_file = None
        self.file_label.config(text="PDFファイルを選択してください")
        self.convert_button.config(state='disabled')
        self.ai_analyze_button.config(state='disabled')
        self.combined_button.config(state='disabled')
        self.ai_analysis_results = []
        self.converted_images = []
        self.status_var.set("結果をクリアしました")
        self.progress_var.set("待機中...")

def main():
    """メイン関数"""
    root = tk.Tk()
    app = PDFToImageAIAnalyzer(root)
    
    # ウィンドウの終了処理
    def on_closing():
        if messagebox.askokcancel("終了", "アプリケーションを終了しますか？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
