from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import os
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pdf_corrector_module import PDFCorrector
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY


def login_required(f):
    """ログインが必要なページのデコレータ"""
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        if user_id == Config.LOGIN_ID and password == Config.LOGIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='IDまたはパスワードが正しくありません')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/robots.txt')
def robots_txt():
    return send_file('static/robots.txt', mimetype='text/plain')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            # 一時ファイルとして保存
            filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(filepath)
            
            # PDF校正処理（テキスト分析と画像分析を並列実行）
            corrector = PDFCorrector()
            
            # 並列処理でテキスト分析と画像分析を同時実行
            text_corrections = []
            image_corrections = []
            
            def run_text_analysis():
                """テキスト分析の実行"""
                return corrector.process_pdf(filepath)
            
            def run_image_analysis():
                """画像分析の実行"""
                return corrector.run_image_analysis(filepath)
            
            # 並列処理
            with ThreadPoolExecutor(max_workers=2) as executor:
                text_future = executor.submit(run_text_analysis)
                image_future = executor.submit(run_image_analysis)
                
                text_corrections = text_future.result()
                image_corrections = image_future.result()
            
            # AIでテキスト分析と画像分析の結果を統合
            corrections = corrector.integrate_analysis_results(text_corrections, image_corrections)
            
            # エクセル出力
            excel_filename = f"校正結果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            excel_path = os.path.join('outputs', excel_filename)
            os.makedirs('outputs', exist_ok=True)
            
            # 統合結果をcorrectorのcorrectionsに設定
            corrector.corrections = corrections
            corrector.export_to_excel(excel_path)
            
            # 一時ファイル削除
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'corrections': corrections,
                'excel_file': excel_filename,
                'max_pages': Config.MAX_PDF_PAGES,
                'message': f'PDF校正が完了しました（テキスト分析+画像分析の統合結果、最大{Config.MAX_PDF_PAGES}ページまで処理）'
            })
        
        return jsonify({'error': 'PDFファイルをアップロードしてください'}), 400
    
    except Exception as e:
        print(f"アップロードエラー: {str(e)}")
        return jsonify({'error': f'アップロード中にエラーが発生しました: {str(e)}'}), 500

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_file(os.path.join('outputs', filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
