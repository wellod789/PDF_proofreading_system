# PDF校正システム

AWS Bedrock Claude 3.5 Sonnet v2を使用した高度なPDF校正システムです。テキスト分析と画像分析を統合し、AIが最適化された校正結果を提供します。

## 機能

### 🔍 **統合校正機能**
- **テキスト分析**: 誤字脱字、文法ミス、表現の不自然さを検出
- **画像分析**: 不要な線、マーク、編集痕跡、レイアウト問題を検出
- **AI統合**: テキスト分析と画像分析の結果を統合し、重複を排除
- **並列処理**: テキスト分析と画像分析を同時実行で高速化

### 📊 **出力機能**
- **Excel出力**: 統合された校正結果をExcelファイルで出力
- **詳細表示**: ページごとの詳細な校正結果を表示
- **プログレス表示**: リアルタイムの処理状況表示

### 🖥️ **UI/UX**
- **Web版**: ブラウザで簡単に操作可能
- **GUI版**: デスクトップアプリケーション
- **認証機能**: ログイン認証によるセキュアなアクセス

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/pdf-kousei-system.git
cd pdf-kousei-system
```

### 2. 仮想環境の作成と有効化

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 認証情報の設定（環境別管理）

このプロジェクトでは環境別認証情報管理を採用しています：

**Windows:**
```powershell
.\setup_local.bat
```

**Linux/Mac:**
```bash
chmod +x setup_local.sh
./setup_local.sh
```

**Pythonから直接実行:**
```bash
python setup_local.py
```

これにより、`config/credentials.local.env`を元に`.env`ファイルが作成されます。

その後、`.env`ファイルを編集して実際の認証情報を設定してください：

```env
# AWS設定
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=ap-northeast-3

# Bedrock設定
BEDROCK_MODEL_ID=apac.anthropic.claude-3-5-sonnet-20241022-v2:0

# Flask設定
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True

# 認証設定
LOGIN_ID=your-login-id
LOGIN_PASSWORD=your-password
```

**環境別認証情報の管理:**
- **ローカル開発**: `config/credentials.local.env`
- **ステージング**: `config/credentials.staging.env.example` を参考に環境変数を設定
- **本番環境**: `config/credentials.production.env.example` を参考に環境変数を設定

詳細は [`config/README.md`](config/README.md) を参照してください。

### 5. アプリケーションの起動

**Web版:**
```bash
python app.py
```
ブラウザで `http://localhost:5000` にアクセスしてください。

**GUI版:**
```bash
python pdf_corrector_gui.py
```

## 使用方法

### Web版
1. ログインページで認証情報を入力
2. PDFファイルをドラッグ&ドロップまたは選択してアップロード
3. AIが自動的にテキスト分析と画像分析を並列実行
4. 統合された校正結果を確認し、Excelファイルをダウンロード

### GUI版
1. アプリケーションを起動
2. 「ファイルを選択」ボタンでPDFファイルを選択
3. 「校正を開始」ボタンをクリック
4. リアルタイムでプログレスを確認
5. 校正結果を確認し、Excelファイルをダウンロード

## 技術スタック

### Backend
- **Web版**: Python Flask
- **GUI版**: Python tkinter
- **AI**: AWS Bedrock Claude 3.5 Sonnet v2
- **並列処理**: concurrent.futures

### PDF・画像処理
- **PDF処理**: PyPDF2, pdfplumber
- **画像変換**: pdf2image
- **画像処理**: Pillow
- **Excel出力**: openpyxl

### AI設定
- **温度差設定**: 一貫性と創造性の調整
- **Top-p/Top-k**: サンプリング制御
- **統合処理**: テキストと画像分析の最適化

### Frontend & Deployment
- **Web版**: Bootstrap 5
- **GUI版**: tkinter (ネイティブ)
- **デプロイ**: EC2直接 / Elastic Beanstalk

## ドキュメント

- **[EC2デプロイガイド](README_EC2_DEPLOY.md)**: EC2インスタンスへの直接デプロイ手順（推奨）
- **[Elastic Beanstalkデプロイガイド](README_AWS_DEPLOY.md)**: AWS Elastic Beanstalkへのデプロイ手順
- **[GUI版ガイド](README_GUI.md)**: デスクトップアプリケーションの使用方法
- **[プログラム仕様書](プログラム仕様書.md)**: システムの詳細仕様

## セキュリティ

- ログイン認証が必要
- 環境変数による設定管理
- 機密情報は`.env`ファイルで管理（`.gitignore`に含まれています）

## 注意事項

- AWS Bedrockの利用には適切な権限が必要です
- 大きなPDFファイルの処理には時間がかかる場合があります
- 処理結果は一時的にサーバーに保存されます
- 本番環境では強力なパスワードを使用してください

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。
