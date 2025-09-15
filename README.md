# PDF校正システム

AWS Bedrock Claude 3.5 Sonnet v2を使用したPDF校正システムです。

## 機能

- **誤字脱字チェック**: テキストの誤字脱字を自動検出
- **画像配置チェック**: 画像の配置ミスや不適切な配置を検出
- **エクセル出力**: 校正結果をエクセルファイルで出力
- **Web UI**: ブラウザで簡単に操作可能
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

### 4. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、以下の内容を設定してください：

```bash
cp .env.example .env
```

`.env`ファイルを編集して、実際の値を設定：

```env
# AWS認証情報
AWS_ACCESS_KEY_ID=your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
AWS_DEFAULT_REGION=ap-northeast-3

# Flask設定
SECRET_KEY=your_actual_secret_key
FLASK_DEBUG=False

# 認証設定
LOGIN_ID=your_login_id
LOGIN_PASSWORD=your_password
```

### 5. アプリケーションの起動

```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

## 使用方法

1. ログインページで認証情報を入力
2. PDFファイルをドラッグ&ドロップまたは選択してアップロード
3. AIが自動的に校正を実行（最大3ページまで）
4. 校正結果を確認し、エクセルファイルをダウンロード

## 技術スタック

- **Backend**: Python Flask
- **AI**: AWS Bedrock Claude 3.5 Sonnet v2
- **PDF処理**: PyPDF2, pdfplumber
- **画像処理**: Pillow
- **Excel出力**: openpyxl
- **Frontend**: Bootstrap 5
- **デプロイ**: AWS Elastic Beanstalk

## デプロイ

AWS Elastic Beanstalkでのデプロイ方法については、[README_AWS_DEPLOY.md](README_AWS_DEPLOY.md)を参照してください。

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
